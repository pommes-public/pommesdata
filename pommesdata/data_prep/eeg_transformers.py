# -*- coding: utf-8 -*-
"""
General description
-------------------
This module contains methods to add RES plants.

It is used to create a set of transformers that represent
renewable power plants with negative costs for use in POMMES. The negative
cost value corresponds to an approximation of the market premium, the plants
receive. Thus, it represents the plant operators opportunity cost rather.
The module contains routines for
- clustering eeg data,
- loading online extrapolation data,
- extraction of market values,
- creating capacity distributions for new installations and values applied,
- adding new-built res ans
- calculating LCOE for res based on cost projections


Licensing information and Disclaimer
------------------------------------
This software is provided under MIT License (see licensing file).

@author: Yannick Werner, Johannes Kochems
"""
import numpy as np
import pandas as pd
from scipy.stats import beta
from sklearn.cluster import KMeans


def create_ee_transformers(eeg_power_plants=None,
                           energy_source_dict=None,
                           cluster_no=20):
    """Creates renewable transformers from ee power plant data

    Performs a KMeans clustering by value applied for plants within the
    market premium model.

    Parameters
    ----------
    eeg_power_plants : pandas.DataFrame
        EEG power plant raw data

    energy_source_dict : dict
        Mapping for energy source names between raw data and names in POMMES

    cluster_no : int
        Number of clusters for each renewable energy source to be generated

    Returns
    -------
    ee_agg : tuple
        first entry is pandas.DataFrame containing aggregated EEG transformers;
        second entry is total capacity not aggregated
    """
    ee = eeg_power_plants.copy()

    if energy_source_dict is None:
        energy_source_dict = dict(
            Wind_Onshore="windonshore",
            Wind_Offshore="windoffshore",
            Solar="solarPV")

    ee.drop(
        index=ee[~ee["energy_source"].isin(energy_source_dict.keys())].index,
        inplace=True)
    ee.loc[:, "energy_source"] = ee.loc[:, "energy_source"].replace(
        energy_source_dict)

    # Convert capacity unit and calculate total capacity (needed later)
    ee.loc[:, "capacity"] /= 1000
    ee_total_capacity = ee.groupby("energy_source").agg({"capacity": sum})

    # Drop power plants that are not in the direct marketing support scheme
    ee.drop(index=ee[ee["support_scheme"] != "MP"].index, inplace=True)

    ee["cluster"] = 0
    for esource in ee["energy_source"].unique():
        ee.loc[ee["energy_source"] == esource, "cluster"] = KMeans(
            n_clusters=cluster_no).fit(
            ee.loc[ee["energy_source"] == esource,
                   "value_applied"].values.reshape(
                -1, 1)).labels_
    print("Usually a warning is thrown, since wind offshore and solar do not "
          + "have so many different values applied in the data")

    # Cluster and aggregate
    wm = lambda x: np.average(x, weights=ee.loc[x.index, "capacity"])

    ee_agg = ee.groupby(["energy_source", "cluster"]).agg(
        {"value_applied": wm, "capacity": "sum"}).droplevel("cluster")

    # Rename and order
    for esource in ee_agg.index:
        ee_agg.loc[esource, :] = ee_agg.loc[esource, :].sort_values(
            "value_applied")

        ee_agg.loc[esource, "number"] = np.arange(
            1, len(ee_agg.loc[esource]) + 1)
    ee_agg = ee_agg.astype({"number": int})

    # Indicate whether output in POMMES is fixed or not
    ee_agg["fixed"] = 0

    # Derive capacity of power plants that is modeled exogenously
    cap_modeled = ee_agg.groupby("energy_source").agg({"capacity": "sum"})
    cap_exogen = np.round(ee_total_capacity - cap_modeled).astype(int)[
        "capacity"].to_frame()
    cap_exogen["value_applied"] = 0
    cap_exogen["number"] = "exogenous"
    cap_exogen["fixed"] = 1
    ee_agg = pd.concat([ee_agg, cap_exogen])

    # Make ready for integration in POMMES
    ee_agg.reset_index(inplace=True)
    ee_agg = ee_agg.astype({"number": str})
    ee_agg["label"] = "DE_" + ee_agg["energy_source"] + "_cluster_" + ee_agg[
        "number"]
    ee_agg["from"] = "DE_bus_" + ee_agg["energy_source"]
    # Conversion of value applied from ct/kWh to EUR/MWh
    ee_agg.loc[:, "value_applied"] *= 10
    ee_agg.set_index("label", inplace=True)
    ee_agg = np.round(ee_agg[["from", "capacity", "fixed", "value_applied"]],
                      2)

    # No relevant operation constraints for RES transformers
    ee_agg["grad_pos"] = 100000
    ee_agg["grad_neg"] = 100000
    ee_agg["min_load_factor"] = 0

    return ee_agg


def load_online_extrapolation(energy_carrier, filename):
    """Read data of the online extrapolation (Online Hochrechnung) for RES """
    netztransparenz = pd.read_csv(
        '../raw_data_input/renewables/' + filename + '.csv',
        sep=';', encoding='cp1252', decimal=',', usecols=[3, 4, 5, 6])
    netztransparenz.name = 'netztransparenz'
    netztransparenz.index = pd.date_range(start='2017-01-01 00:00:00',
                                          end='2017-12-31 23:00:00', freq='H')
    netztransparenz.columns = (
        netztransparenz.columns.str.partition('(').get_level_values(0)
            .str.slice(stop=-1))
    netztransparenz.rename(columns={'TenneT TSO': 'TenneT'}, inplace=True)
    netztransparenz[energy_carrier] = netztransparenz.sum(axis=1)
    return netztransparenz[energy_carrier].values


def get_market_values(netztransparenz=False,
                      filename=None,
                      bus_names=None,
                      year=2017):
    """Load market values from netztransparenz.de and do some data preparations

    Parameters
    ----------
    netztransparenz: bool
        Indicates whether file is taken from netztransparenz.de
        or another source (model)

    filename: str
        Filename of market values file from netztransparenz.de (raw)

    bus_names: list of str
        List of names that represent buses in the model

    year: int
        Year which is modeled

    Returns
    -------
    market_values_ts: pandas.DataFrame
        Hourly market values for each energy source for the given year.
    """
    if bus_names is None:
        bus_names = ["DE_bus_windonshore", "DE_bus_windoffshore",
                     "DE_bus_solarPV"]
    if netztransparenz is True:
        mv_de = pd.read_csv(
            filepath_or_buffer=filename,
            index_col=0, low_memory=False,
            sep=";", decimal=",", encoding="cp1252")

        mv_de = mv_de.loc[mv_de.index.str.contains("MW", na=False)]
        mv_de.drop(
            index=["MW steuerbar",
                   "Monatsmittelwert Stundenkontrakte EPEX Spot (MW-EPEX)"],
            inplace=True)
        mv_de.index = bus_names
        mv_de = mv_de.T.reset_index(drop=True)

        mv_de = mv_de.apply(lambda x: x.str.lstrip())
        # Convert strings to float (workaround needed)
        mv_de = mv_de.apply(
            lambda x: x.apply(
                lambda x: float(x.split()[0].replace(",", ""))) / 100, axis=1)
        mv_de.index = range(1, 13)
    else:
        mv_de = pd.read_csv(filename, index_col=0)
        mv_de = mv_de[["Wind_Onshore", "Wind_Offshore", "Solar"]]
        mv_de.columns = bus_names

    # roll out market values for each hour of a month with the respective mv
    market_values_ts = pd.DataFrame(
        index=pd.date_range(start=str(year) + "-01-01 00:00:00",
                            end=str(year) + "-12-31 23:00:00",
                            freq="H"))
    market_values_ts["month"] = market_values_ts.index.month
    market_values_ts = market_values_ts.merge(mv_de,
                                              left_on="month",
                                              right_index=True,
                                              how="left").drop(
        columns="month")
    market_values_ts.index.name = "time"

    return market_values_ts


def create_cap_distribution_from_beta(LCOE_df,
                                      cols=['min', 'weighted_ave', 'max'],
                                      b=2, n=10):
    """Capacity distribution mapping of capacity shares and values applied

    The beta function is used, which is defined between [0,1] and
    can therefore be used to approximate distributions over an arbitrary closed
    interval compared to all of R.

    Parameters
    ----------
    LCOE_df: pandas.DataFrame
        DataFrame containing LCOE values for an energy carrier

    cols: list of str
        list of column names. These must have the correct ordering defined
        in the default values

    b: int
        parameter of the beta function

    n: int
        number of capacity slices

    Returns
    -------
    cap_dist_dict: dict of float
        A capacity distribution dict
    """
    cap_dist_dict = dict()
    for yr in LCOE_df.index:
        min_, mu_hat, max_ = LCOE_df.loc[yr, cols]

        # distribution parameters: b is set exogenously.
        # a is set endogenously in a way to fit the true mean with
        # that of the distribution
        mu = (mu_hat - min_) / (max_ - min_)
        a = mu * b / (1 - mu)

        # shares are determined using the cdf of the defined beta function
        # afterwards, the definition space is linear transformed to match
        # the min, max, avg interval given, while holding the shares constant
        x = np.linspace(0, 1, n + 1)
        value_applied = (x[:-1] + np.diff(x) / 2) * (max_ - min_) + min_
        shares = np.diff(beta.cdf(x, a, b))

        # write all numbers into a dict
        cap_dist_dict[yr] = {'shares': shares,
                             'value_applied': value_applied}

    return cap_dist_dict


def add_new_built_res(cap_distribution, new_built_df, annual_cap_expansion,
                      source, capacity_col='capacity', indexed_by_years=False):
    """Create new-built RES plants and append them to new-built DataFrame

    Parameters
    ----------
    cap_distribution : dict
        a nested dict with the years as keys and the distribution shares
        of the beta function as well as the corresponding values applied in
        the inner dict

    new_built_df : pd.DataFrame
        DataFrame containing the (artificial) units to be added

    annual_cap_expansion : pd.DataFrame
        DataFrame containing annual capacity expansion values

    source : str
        name of the energy source

    capacity_col : str
        Name of the capacity column ('capacity', 'capacity_awarded', 'MP')

    indexed_by_years : boolean
        If True, annual_cap_expansion has to be indexed by years, else, it
        is indexed by energy sources (constant value for every year)

    Returns
    -------
    new_built_df : pd.DataFrame
        Manipulated DataFrame including the generated artificial
        new-built units
    """
    energy_source_dict = dict(Wind_Onshore='windonshore',
                              Wind_Offshore='windoffshore',
                              Solar='solarPV')

    for year in cap_distribution.keys():

        if indexed_by_years:
            cap_to_use = annual_cap_expansion.at[year, capacity_col]
        else:
            cap_to_use = annual_cap_expansion.at[energy_source_dict[source],
                                                 capacity_col]

        for i in range(len(cap_distribution[year]['shares'])):
            new_built_df.loc[
                energy_source_dict[source] + '_new_' + str(i + 1) + '_' + str(
                    year),
                ['capacity', 'energy_source',
                 'value_applied', 'support_scheme', 'commissioning_year']] = (
                [cap_distribution[year]['shares'][i] * cap_to_use, source,
                 cap_distribution[year]['value_applied'][i], 'MP', year])

    return new_built_df


def ppv(wacc, lifetime):
    """Returns the pension present value factor for given wacc and lifetime

    German: Rentenbarwertfaktor

    Parameters
    ----------
    wacc: float
        weighted average cost of capital

    lifetime: int
        lifetime for calculating the ppv

    Returns
    -------
    the pension present value factor (ppv)
    """
    return ((1 + wacc) ** lifetime - 1) / ((1 + wacc) ** lifetime * wacc)


def lcoe_fix_var(capex, opex_fix, opex_var, flh, wacc, lifetime, capacity=1):
    """Returns the LCOE using constant payments and opex as fixed and variable

    Parameters
    ----------
    capex: float
        capital expenditures

    opex_fix: float
        fixed operational expenditures

    opex_var: float
        variable operational expenditures

    flh: float
        full load hours of the technology considered

    wacc: float
        weighted average cost of capital

    lifetime: int
        lifetime for calculating the ppv

    capacity: float
        capacity of technology considered

    Returns
    -------
    the calculated lcoe
    """
    return (((capex + opex_fix * ppv(wacc, lifetime))
             + flh * capacity * opex_var * ppv(wacc, lifetime))
            / (flh * capacity * ppv(wacc, lifetime)))


def estimate_lcoe_ise21(df, energy_carriers):
    """ Calculate the LCOE for a given energy carrer

    Parameters
    ----------
    df: dict
        Dictionary containing the cost data and parameters needed for LCOE calculation

    energy_carriers: list of str
        The energy carriers to be filtered for

    Returns
    -------
    LCOE_df: pd.DataFrame
        A DataFrame indexed by years containing the lower, middle
        and upper estimate for the LCOEs
    """
    cols_to_keep = []
    for ec in energy_carriers:
        df[(ec, 'LCOE_low')] = (
            np.vectorize(lcoe_fix_var)(df[(ec, 'capex_low')],
                                       df[(ec, 'opex_fix')],
                                       df[(ec, 'opex_var')],
                                       df[(ec, 'flh_high')],
                                       df[(ec, 'wacc_real')] / 100,
                                       df[(ec, 'lifetime')]))

        df[(ec, 'LCOE_middle')] = (
            np.vectorize(lcoe_fix_var)(df[(ec, 'capex_middle')],
                                       df[(ec, 'opex_fix')],
                                       df[(ec, 'opex_var')],
                                       df[(ec, 'flh_middle')],
                                       df[(ec, 'wacc_real')] / 100,
                                       df[(ec, 'lifetime')]))
        df[(ec, 'LCOE_high')] = (
            np.vectorize(lcoe_fix_var)(df[(ec, 'capex_high')],
                                       df[(ec, 'opex_fix')],
                                       df[(ec, 'opex_var')],
                                       df[(ec, 'flh_low')],
                                       df[(ec, 'wacc_real')] / 100,
                                       df[(ec, 'lifetime')]))

        cols_to_keep.extend(
            [(ec, "LCOE_low"), (ec, "LCOE_middle"), (ec, "LCOE_high")])

    LCOE_df = df.loc[[str(el) for el in range(2020, 2031)], cols_to_keep]
    LCOE_df.index = LCOE_df.index.astype(int)

    # LCOE calculation gives €/kWh while remainder of the data is ct/kWh
    LCOE_df = LCOE_df.astype(float).interpolate('linear').mul(100)

    return LCOE_df
