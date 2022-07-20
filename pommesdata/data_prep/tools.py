# -*- coding: utf-8 -*-
"""
General description
-------------------
This module contains some tools used in the data preparation notebook.

The functions serve to

- load bidding zone shape files,
- calculate (shortest) distances between coordinates,
- assign efficiency values to power plants,
- assign gradient values and minimum loads to power plants,
- assign time-dependent NTC values,
- convert data into the structure of oemof.solph,
- load ENTSO-E data and transfer it to the format needed,
- extract capacities from the TYNDP 2018 scenario data set,
- reindex timeseries data for another year of choice.

Licensing information and Disclaimer
------------------------------------
This software is provided under MIT License (see licensing file).

@author: Yannick Werner, Johannes Kochems
"""
from math import atan2, cos, sin, sqrt

import geopandas as gpd
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt


def load_bidding_zone_shape(country, zone, path_folder):
    """Function to load the bidding zone shape file into geopandas"""
    return gpd.read_file(path_folder + country + "-" + zone + ".json").replace(
        {country + "-" + zone: zone}
    )


def calc_dist(lat1, lon1, lat2, lon2):
    """Calculate the geodesic distance between two coordinates

    See https://stackoverflow.com/questions/19412462/
    getting-distance-between-two-points-based-on-latitude-longitude
    for the code and https://janakiev.com/blog/gps-points-distance-python/
    for an extensive explanation (both links 2020-08-01)

    Parameters
    ----------
    lat1 : float
        latitude of the first point

    lon1 : float
        longitude of the first point

    lat2 : float
        latitude of the second point

    lon2 : float
        longitude of the second point

    Returns
    -------
    distance : float
        distance between the two points
    """
    R = 6373.0

    lat1, lon1, lat2, lon2 = np.radians(np.array([lat1, lon1, lat2, lon2]))

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c

    return distance


def assign_eff_el_interpol(year, tech_fuel, eff_matrix):
    """Assign efficiency based on commissioning year and efficiency matrix

    Parameters
    ----------
    year : str
        The commissioning year

    tech_fuel : str
        A combination of technology and fuel, e.g. 'GT_natgas'

    eff_matrix : pd.DataFrame
        An efficiency matrix with the years as rows and the tech_fuel
        combinations as columns

    Returns
    -------
    efficiency : float
        The electrical efficiency
    """
    if year >= 1950:
        efficiency = np.round(eff_matrix.at[int(year), tech_fuel], 4)
    else:
        efficiency = np.round(eff_matrix.at[1990, tech_fuel], 4)

    return efficiency


def assign_gradients_and_min_loads(pp_df, min_load_dict):
    """Convert gradients and assign minimum loads

    Gradients are converted from %/min to MW/hour and expressed as relative
    shares of nominal capacity. Minimum loads are determined by fuel.

    Also does some renaming and drops columns not needed anymore ('tech_fuel'
    and 'load_gradient_relative').

    Parameters
    ----------
    pp_df : pandas.DataFrame
        The power plants DataFrame

    min_load_dict : dict
        Dictionary with fuel names (str) as keys and relative minimum load
        values (float) in percentage share of nominal capacity as values

    Returns
    -------
    pp_df : pandas.DataFrame
        The modified DataFrame
    """
    pp_df["grad_pos"] = np.minimum(1, 60 * pp_df["load_grad_relative"])
    pp_df["grad_neg"] = np.minimum(1, 60 * pp_df["load_grad_relative"])
    pp_df = pp_df.rename(columns={"min_load_LP": "min_load_factor"}).drop(
        columns=["tech_fuel", "load_grad_relative"]
    )

    for fuel in min_load_dict.keys():
        pp_df.loc[
            (pp_df["country"] == "DE")
            & (pp_df["fuel"] == fuel)
            & (pp_df["type"] == "emb"),
            "min_load_factor",
        ] = min_load_dict[fuel]

    return pp_df


def find_ntc_wind(ic, value_wind, year):
    """Return actual capacity value for NTC based on wind infeed

    Parameters
    ----------
    ic : pandas.DataFrame
        DataFrame with technical profile for interconnector

    value_wind : float
        wind capacity threshold for NTC values

    year : int
        year considered

    Returns
    -------
    capacity values for every index
    """
    for ind in ic.index:
        if ic.at[ind, "wind_from"] <= value_wind <= ic.at[ind, "wind_to"]:
            return ic.at[ind, year]


def find_ntc_load_and_wind(ic, value_wind, value_demand, year):
    """Return actual capacity value for NTC based on wind infeed and demand

    Parameters
    ----------
    ic : pandas.DataFrame
        DataFrame with technical profile for interconnector

    value_wind : float
        wind capacity threshold for NTC values

    value_demand : float
        demand capacity threshold for NTC values

    year : int
        year considered

    Returns
    -------
    capacity values for every index
    """
    for ind in ic.index:
        if (
            ic.at[ind, "wind_from"] <= value_wind <= ic.at[ind, "wind_to"]
        ) and (
            ic.at[ind, "load_from"] <= value_demand <= ic.at[ind, "load_to"]
        ):
            return ic.at[ind, year]


def nodes_to_oemof(
    df, to="_bus_el", component=None, component_suffix_var=None
):
    r"""Transforms input data to a structure used by oemof.solph

    Parameters
    ----------
    df : pd.DataFrame
        The input DataFrame

    to : str
        The bus / component which is target of the components outflow
        (defaults to '_bus_el')

    component : str
        The component type (e.g. source, sink)

    component_suffix_var : str
        A suffix for the component name obtained from input data
        information (e.g. technology)

    Returns
    -------
    df : pd.DataFrame
        The manipulated input DataFrame
    """
    df["to"] = df["country"] + to

    if component_suffix_var is None:
        df["label"] = df["country"] + component
    else:
        try:
            df["label"] = df["country"] + component + df[component_suffix_var]
        except KeyError:
            msg = (
                f"{component_suffix_var} is not "
                + "in the columns of the DataFrame."
            )
            raise KeyError(msg)

    df.set_index("label", inplace=True)
    return df


def load_entsoe_generation_data(
    country=None, path="../raw_data_input/hydro/inputs/", filename=None
):
    """Loads and preprocesses generation data from ENTSO-E

    Removes hour with NAs for annual time shift
    (summer/winter) and interpolates where data contains NAs.

    Parameters
    ----------
    country : str
        Bidding zone name

    path : str
        relative path to the input file

    filename : str
        filename of the input file (.csv)

    Returns
    -------
    df : pd.DataFrame
        The manipulated input DataFrame
    """
    try:
        if filename is None:
            df = pd.read_csv(
                path + "entsoe_generation_" + country + "_26012020.csv",
                index_col=1,
            )
        else:
            df = pd.read_csv(path + filename, index_col=1)

        if len(df) == 8760 * 4 + 1 * 4:
            df.drop(
                index=df.loc[
                    "26.03.2017 02:00 - 26.03.2017 02:15 (CET)":"26.03.2017 02:45 - 26.03.2017 03:00 (CET)"
                ].index,
                inplace=True,
            )

            df.index = pd.date_range(
                start="2017-01-01 00:00:00",
                end="2017-12-31 23:45:00",
                freq="15min",
            )
            df = df.resample("H").mean()

        elif len(df) == 8760 + 1:
            df.drop(
                index="26.03.2017 02:00 - 26.03.2017 03:00 (CET)", inplace=True
            )

            df.index = pd.date_range(
                start="2017-01-01 00:00:00",
                end="2017-12-31 23:00:00",
                freq="H",
            )

        else:
            raise ValueError(f"Bidding zone {country} did not work properly.")

        df = df.interpolate(axis=0)
        return df

    except (ValueError, KeyError):
        msg = f"Failed loading data for bidding zone {country}."
        raise ValueError(msg)


def load_entsoe_german_generation_data(
    path="../raw_data_input/timeseries/", year=2017
):
    """Load generation for Germany, handle time shift and resample to hourly

    Parameters
    ----------
    path : str
        relative path to the input file

    year : int
        Year for which to evaluate generation
    """
    if year in range(2017, 2022):
        filename = f"entsoe_generation_DE_{year}0101-{year + 1}0101.csv"
    else:
        msg = f"year must be between 2017 and 2021. You specified {year}"
        raise ValueError(msg)

    generation = pd.read_csv(path + filename, index_col=1)
    generation.drop(columns="Area", inplace=True)
    # Columns for hour 2B are left empty; drop for time shift consideration
    generation = generation.dropna(how="all")

    generation.index = pd.date_range(
        start=f"{year}-01-01 00:00:00",
        end=f"{year}-12-31 23:45:00",
        freq="15min",
    )
    generation = generation.resample("H").mean()

    generation = generation[
        [
            "Nuclear  - Actual Aggregated [MW]",
            "Fossil Brown coal/Lignite  - Actual Aggregated [MW]",
            "Fossil Hard coal  - Actual Aggregated [MW]",
            "Fossil Gas  - Actual Aggregated [MW]",
        ]
    ]

    generation.rename(
        columns={
            "Nuclear  - Actual Aggregated [MW]": "uranium",
            "Fossil Brown coal/Lignite  - Actual Aggregated [MW]": "lignite",
            "Fossil Hard coal  - Actual Aggregated [MW]": "hardcoal",
            "Fossil Gas  - Actual Aggregated [MW]": "natgas",
        },
        inplace=True,
    )

    return generation


def load_entsoe_transmission_data(
    country, path="../raw_data_input/Interconnectors/"
):
    """Loads and preprocesses ENTSO-E data for cross-border physical flows

    Parameters
    ----------
    country : str
        Bidding zone name

    path : str
        relative path to the input file

    Returns
    -------
    df : pd.DataFrame
        The manipulated input DataFrame
    """
    try:
        df = pd.read_csv(
            path
            + "Cross-Border Physical Flow_201701010000-201801010000_DE"
            + country
            + ".csv",
            index_col=0,
        )
        df.drop(index="26.03.2017 02:00 - 26.03.2017 03:00", inplace=True)
        df = df.fillna(0)
        df[~df[df == "n/e"].isna().any(axis=1)] = 0
        df.index = pd.date_range(
            start="2017-01-01 00:00:00", end="2017-12-31 23:00:00", freq="H"
        )
        df.columns = [country + "_link_DE", "DE_link_" + country]

        df = df.astype(int)
        return df

    except ValueError:
        msg = f"Could not process flow data between DE and {country}."
        raise ValueError(msg)


def extract_tyndp_capacities(
    countries, no_dict, scenario="2030_DG", path="./"
):
    """Process the TYNDP RES projection and return manipulated data.

    Steps:
    - Read in the data
    - Aggregate / disaggregate market zones
    - Do some renaming
    - Separate fluctuating RES from the data set

    Parameters
    ----------
    countries: list
        List of European countries to be modelled

    no_dict:
        dict of capacity per Norwegian bidding zones to be considered

    scenario:
        TYNDP 2018 scenario to be used (options: "2025 BEST", "2030 DG",
        "2030 EUCO")

    path: str
        Path to input .xlsx file

    Returns
    -------
    pp_eu_target_year: pd.DataFrame
        A DataFrame containing the RES capacities for the considered target
        year (2025 or 2030)
    """
    pp_eu_tyndp = pd.read_excel(
        path, sheet_name=scenario, skiprows=2, index_col=0
    )

    pp_eu_tyndp = pp_eu_tyndp.filter(
        regex="|".join(list(countries.values())), axis=0
    )

    agg_list = {"DKw": ["DKw", "DKKF"], "FR": ["FR", "FR15"]}

    if scenario == "2025 BEST":
        agg_list["DKw"] = ["DKw", "DKkf"]

    for k, v in agg_list.items():
        pp_eu_tyndp.loc[k] = pp_eu_tyndp.loc[v[0]].add(pp_eu_tyndp.loc[v[1]])
        pp_eu_tyndp.drop(v[1], inplace=True)

    pp_eu_tyndp.rename(
        index={
            "DKe": "DK2",
            "DKw": "DK1",
            "NOs": "NO1+NO2+NO5",
            "NOm": "NO3",
            "NOn": "NO4",
        },
        inplace=True,
    )

    pp_eu_tyndp.rename(
        columns={
            "Biofuels": "biomass",
            "Gas": "natgas",
            "Hard coal": "hardcoal",
            "Hydro-pump": "PHES_capacity_pump",
            "Hydro-run": "PHES_capacity",
            "Hydro-turbine": "PHES_capacity_turbine",
            "Lignite": "lignite",
            "Nuclear": "uranium",
            "Oil": "oil",
            "Othernon-RES": "otherfossil",
            "Other RES": "otherRES",
            "Solar-thermal": "solarthermal",
            "Solar-\nPV": "solarPV",
            "Wind-\non-shore": "windonshore",
            "Wind-\noff-shore": "windoffshore",
        },
        inplace=True,
    )

    NO_cap_shares_dict = {}
    for k, v in no_dict.items():
        NO_cap_shares_dict[k] = float(v / sum(no_dict.values()))
        try:
            pp_eu_tyndp.loc[k] = (
                pp_eu_tyndp.loc["+".join(list(no_dict.keys()))].copy()
                * NO_cap_shares_dict[k]
            )
        except KeyError:
            pass

    pp_eu_tyndp.drop(
        index=["NO1", "+".join(list(no_dict.keys()))], inplace=True
    )
    pp_eu_tyndp.reset_index(inplace=True)

    pp_eu_target_year = pd.melt(
        pp_eu_tyndp, id_vars=["Country/Installed capacity (MW)"]
    )

    pp_eu_target_year = pp_eu_target_year[
        pp_eu_target_year["value"] != 0
    ].rename(
        columns={
            "Country/Installed capacity (MW)": "country",
            "variable": "fuel",
            "value": "capacity",
        }
    )

    return pp_eu_target_year


def reindex_time_series(df, year):
    """Reindex a time series given for 2017 by another year

    Parameters
    ----------
    df: pd.DataFrame
        original DataFrame

    year: int
        The year for reindexing

    Returns
    -------
    df_reindexed: pd.DataFrame
        the manipulated DataFrame
    """
    df.index = pd.DatetimeIndex(df.index)
    df.index.freq = "H"
    date_diff = df.index[0] - pd.Timestamp(
        "2017-01-01 00:00:00", tz=df.index.tz
    )
    ts_start = (
        pd.Timestamp(str(year) + "-01-01 00:00:00", tz=df.index.tz) + date_diff
    )
    # account for leap years
    if ts_start.month == 12:
        ts_start = ts_start + pd.Timedelta("1 days")
    new_index = pd.date_range(
        start=ts_start, periods=df.shape[0], freq=df.index.freq
    )
    df_reindexed = df.copy()
    df_reindexed.index = new_index

    return df_reindexed


def reformat_costs_values(costs, sources_commodity, index="bus"):
    """Reformat commodity cost values

    Parameters
    ----------
    costs: pd.DataFrame
        costs in annual resolution

    sources_commodity: pd.DataFrame
        Commodity sources of the model

    index: str
        Index to use for the costs; "bus" or "source"

    Returns
    -------
    reformatted_costs: pd.DataFrame
        Combination of historical and predicted costs indexed by
        commodity sources introduced by the model
    """
    reformatted_costs = costs.loc[sources_commodity["fuel"].values]
    if index == "bus":
        reformatted_costs.index = sources_commodity["to"].values
    elif index == "source":
        reformatted_costs.index = sources_commodity.index
    reformatted_costs.index.name = "label"
    reformatted_costs = reformatted_costs.astype("float64").round(2)

    return reformatted_costs


def transform_costs_values_to_time_series(costs, end_year=2050):
    """Transform costs values to time series with annual frequency

    Parameters
    ----------
    costs: pd.DataFrame
        Costs to be indexed to a certain year

    end_year: int
        Last year for which there is data
    """
    costs_ts = costs.T
    try:
        costs_ts["date_index"] = pd.date_range(
            start="2017", end=str(end_year), freq="AS"
        )
    except ValueError:
        raise ValueError(
            f"Time series must range from 2017 to {end_year} (inclusively)!"
        )
    costs_ts.set_index("date_index", drop=True, inplace=True)

    return costs_ts


def add_study_to_comparison(parameter_data, study_data):
    """Add given study data to parameter comparison

    Parameters
    ----------
    parameter_data: pd.DataFrame
        parameter data collection

    study_data: pd.DataFrame
        data from study to be appended to parameter data

    Returns
    -------
    parameter_data: pd.DataFrame
        extended parameter data collection
    """
    parameter_data = pd.concat([parameter_data, study_data]).astype("float64")
    parameter_data = parameter_data.interpolate(how="linear", axis=1)

    return parameter_data


def plot_parameter_comparison(
    data, parameter, category, savefig=False, show=True
):
    """Create a plot to visually compare parameter distributions

    Parameters
    ----------
    data: pd.DataFrame
        Parameter data (subset per category) to be evaluated

    parameter: str
        Parameter to be evaluated

    category: str
        Category for which data shall be evaluated

    savefig: boolean
        If True, save figure to disk

    show: boolean
        If True, display the plot
    """
    fig, ax = plt.subplots(figsize=(8, 3))
    _ = sns.boxplot(data=data, ax=ax, color="lightgrey")
    _ = sns.swarmplot(data=data, ax=ax, color="black")
    _ = plt.title(f"{parameter} distribution for {category}")
    _ = plt.xticks(rotation=90)
    _ = plt.tight_layout()
    if savefig:
        plt.savefig(f"../graphics/{parameter}_{category}.png", dpi=300)
    if show:
        plt.show()
    plt.close()


def calculate_summary_statistics(
    data,
    path,
    parameter,
    category,
    save=True,
):
    """Calculate some summary statistics from data

    Parameters
    ----------
    data: pd.DataFrame
        Parameter data (subset per category) to be evaluated

    path: str
        Path where to store the output

    parameter: str
        Parameter to be evaluated

    category: str
        Category for which data shall be evaluated

    save: boolean
        If True, save to disk

    Returns
    -------
    stats_data: pd.DataFrame
        Data statistics (count, moments, etc.)
    """
    stats_data = data.describe()
    quantiles = {"5%": 0.05, "10%": 0.1, "90%": 0.9, "95%": 0.95}

    for key, val in quantiles.items():
        stats_data.loc[key] = data.quantile(val).values

    if save:
        stats_data.to_csv(f"{path}{parameter}_{category}.csv")

    return stats_data


def combine_parameter_estimates(
    data_sets, parameter, estimate, path, save=True
):
    """Re-combine parameter estimates

    Used to create data sets for unsecure future parameters.

    Parameters
    ----------
    data_sets: dict
        Dictionary holding data sets (i.e. DataFrames) of each category

    parameter: str
        Parameter to be evaluated

    estimate: str
        Estimate to be calculated (one of '5%', '50%', '95%')

    path: str
        Path where to store the output

    save: boolean
        If True, save to disk

    Returns
    -------
    overall_data_set: pd.DataFrame
        Data aggregation for given estimate
    """
    overall_data_set = pd.DataFrame(columns=list(range(2020, 2051)))
    for key, val in data_sets.items():
        overall_data_set.loc[key] = val.loc[estimate]

    if save:
        overall_data_set.to_csv(f"{path}{parameter}_{estimate}.csv")

    return overall_data_set
