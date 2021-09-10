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
- load ENTSO-E data and transfer it to the format needed.

Licensing information and Disclaimer
------------------------------------
This software is provided under MIT License (see licensing file).

@author: Yannick Werner

Contributor: Johannes Kochems
"""
from math import sin, cos, sqrt, atan2

import geopandas as gpd
import numpy as np
import pandas as pd


def load_bidding_zone_shape(country, zone, path_folder):
    """Function to load the bidding zone shape file into geopandas"""
    return gpd.read_file(path_folder + country + '-' + zone + '.json').replace(
        {country + '-' + zone: zone})


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
    pp_df = pp_df.rename(columns={'min_load_LP': 'min_load_factor'}).drop(
        columns=['tech_fuel', 'load_grad_relative'])

    for fuel in min_load_dict.keys():
        pp_df.loc[(pp_df['country'] == 'DE')
                  & (pp_df['fuel'] == fuel)
                  & (pp_df['type'] == 'emb'),
                  'min_load_factor'] = min_load_dict[fuel]

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
        if ic.at[ind, 'wind_from'] <= value_wind <= ic.at[ind, 'wind_to']:
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
        if ((ic.at[ind, 'wind_from'] <= value_wind <= ic.at[ind, 'wind_to'])
            and (ic.at[ind, 'load_from'] <= value_demand
                 <= ic.at[ind, 'load_to'])):
            return ic.at[ind, year]


def nodes_to_oemof(df, to="_bus_el", component=None,
                   component_suffix_var=None):
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
            msg = (f"{component_suffix_var} is not "
                   + "in the columns of the DataFrame.")
            raise KeyError(msg)

    df.set_index("label", inplace=True)
    return df


def load_entsoe_generation_data(country=None,
                                path="./raw_data_input/hydro/inputs/",
                                filename=None):
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
                index_col=1)
        else:
            df = pd.read_csv(path + filename, index_col=1)

        if len(df) == 8760 * 4 + 1 * 4:
            df.drop(
                index=df.loc[
                      "26.03.2017 02:00 - 26.03.2017 02:15 (CET)":
                      "26.03.2017 02:45 - 26.03.2017 03:00 (CET)"].index,
                inplace=True)

            df.index = pd.date_range(start="2017-01-01 00:00:00",
                                     end="2017-12-31 23:45:00", freq="15min")
            df = df.resample("H").mean()

        elif len(df) == 8760 + 1:
            df.drop(index="26.03.2017 02:00 - 26.03.2017 03:00 (CET)",
                    inplace=True)

            df.index = pd.date_range(start="2017-01-01 00:00:00",
                                     end="2017-12-31 23:00:00", freq="H")

        else:
            raise ValueError(f"Bidding zone {country} did not work properly.")

        df = df.interpolate(axis=0)
        return df

    except (ValueError, KeyError):
        msg = f"Failed loading data for bidding zone {country}."
        raise ValueError(msg)


def load_entsoe_transmission_data(country,
                                  path="./raw_data_input/Interconnectors/"):
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
            path + "Cross-Border Physical Flow_201701010000-201801010000_DE"
            + country + ".csv",
            index_col=0)
        df.drop(index="26.03.2017 02:00 - 26.03.2017 03:00", inplace=True)
        df = df.fillna(0)
        df[~df[df == "n/e"].isna().any(axis=1)] = 0
        df.index = pd.date_range(start="2017-01-01 00:00:00",
                                 end="2017-12-31 23:00:00", freq='H')
        df.columns = [country + "_link_DE", "DE_link_" + country]

        df = df.astype(int)
        return df

    except ValueError:
        msg = f"Could not process flow data between DE and {country}."
        raise ValueError(msg)