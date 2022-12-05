# -*- coding: utf-8 -*-
"""
General description
-------------------
This module contains some tools for hydro plants used in the data preparation.

The functions serve to load and slightly adjust hydro generation data and
hydro reservoir data as well as resampling the corresponding time series.

Licensing information and Disclaimer
------------------------------------
This software is provided under MIT License (see licensing file).

@author: Yannick Werner

Contributor: Johannes Kochems
"""
import numpy as np
import pandas as pd


def load_hydro_generation_data(
    bidding_zone=None, path="./raw_data_input/hydro/inputs/", filename=None
):
    """Loads and preprocesses hydro generation data from ENTSO-E.

    Removes hour with NAs for annual time shift
    (summer/winter) and interpolates where data contains NAs.

    Parameters
    ----------
    bidding_zone : str
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
    df = pd.read_csv(
        path + filename,
        index_col=0,
        usecols=[
            "MTU",
            "Hydro Run-of-river and poundage  - Actual Aggregated [MW]",
            "Hydro Water Reservoir  - Actual Aggregated [MW]",
        ],
    )

    df.rename(
        columns={
            "Hydro Run-of-river and poundage  - Actual Aggregated [MW]": bidding_zone
            + "_source_"
            + "ROR",
            "Hydro Water Reservoir  - Actual Aggregated [MW]": bidding_zone
            + "_"
            + "Reservoir",
        },
        inplace=True,
    )

    # Ensure correct format; indices are the same, but named differently
    if bidding_zone == "IT":
        df.index = df.index.str.replace("CET/CEST", "CET")

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
            start="2017-01-01 00:00:00", end="2017-12-31 23:00:00", freq="H"
        )

    else:
        raise ValueError("Bidding zone {bidding_zone} did not work properly.")

    df = df.interpolate(axis=0)

    return df


def load_hydro_reservoir_data(
    bidding_zone=None,
    years=None,
    path="./raw_data_input/hydro/inputs/",
    filename=None,
):
    """Loads and returns weekly hydro reservoir storage filling rates

    Parameters
    ----------
    bidding_zone : str
        Bidding zone name

    years : list of str
        List of years to be evaluated

    path : str
        relative path to the input file

    Returns
    -------
    df : pd.DataFrame
        The manipulated input DataFrame

    """
    if not years:
        years = ["2017"]

    if bidding_zone not in ["AT", "IT"]:
        suffix = "BZN|" + bidding_zone
    elif bidding_zone == "AT":
        suffix = "Austria (AT)"
    elif bidding_zone == "IT":
        suffix = "Italy (IT)"
    else:
        raise ValueError("Invalid bidding zone specified.")

    df = pd.read_csv(
        path + filename,
        usecols=[
            "Stored Energy Value " + yr + " [MWh] - " + suffix for yr in years
        ],
        dtype=np.int32,
    )
    df.columns = [
        bidding_zone + "_hydro_storage_fillrate_" + yr for yr in years
    ]

    return df


def upsample_inflow(inflow_series):
    """Builds an hourly average for every week and returns it

    Parameters
    ----------
    inflow_series : pandas.Series
        inflow series

    Returns
    -------
    arr : np.array
        upsampled inflow values in hourly resolution
    """
    arr = np.empty(0)
    inflow_arr = inflow_series.to_numpy()
    step_size = 7 * 24

    for i in range(53):
        if i < 52:
            arr = np.append(
                arr,
                np.repeat(
                    inflow_arr[i * step_size : (i + 1) * step_size].mean(),
                    step_size,
                ),
            )
        else:
            arr = np.append(
                arr,
                np.repeat(
                    inflow_arr[i * step_size :].mean(),
                    len(inflow_arr[i * step_size :]),
                ),
            )

    return arr
