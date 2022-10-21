# -*- coding: utf-8 -*-
"""
General description
-------------------
This module contains methods to aggregate transformer data.

It is used to create a set of transformers that represent
renewable power plants with negative costs for use in POMMES. The negative
cost value corresponds to an approximation of the market premium, the plants
receive. Thus, it represents the plant operators opportunity cost rather.

Licensing information and Disclaimer
------------------------------------
This software is provided under MIT License (see licensing file).

@author: Johannes Kochems, Yannick Werner
"""
import math
from multiprocessing.dummy import Value

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans


def cluster_transformers(
    transformers, by="efficiency_el", grouping="fuel", share_clusters=0.1
):
    """Cluster transformers data

    Clusters transformers from a given input DataFrame. Transformers are
    clustered by electrical efficiency by default. Thereby, clusters are
    created for plants of the same fuel resp. technology-fuel combination
    (tech_fuel) and the same (CHP) operation mode.

    Parameters
    ----------
    transformers : pandas.DataFrame
        DataFrame holding the transformers data

    by : str
        Column to cluster by (defaults to electrical efficiency)

    grouping : str
        Grouping option to use to create clusters within the defined groups

        Possible choices:

            * "fuel": cluster units of the same fuel
            * "tech_fuel": cluster units of the same technology-fuel
              combination

    share_clusters : float
        Percentage share of clusters on overall number of power plants per fuel
        and operation mode

    Returns
    -------
    transformers : pandas.DataFrame
        manipulated DataFrame now containing a cluster column
    """
    # Assign a code for (non) CHP status of power plants
    transformers["cluster"] = 0
    conditions = [transformers["type"] == "ipp", transformers["type"] == "chp"]
    choices = [1, 2]
    transformers["mode"] = np.select(conditions, choices, default=0)

    if grouping == "fuel":
        grouping_col = transformers["from"]
    elif grouping == "tech_fuel":
        grouping_col = transformers["tech_fuel"]
    else:
        raise ValueError(
            "Grouping option not defined. "
            + "Must be one of 'fuel' and 'tech_fuel'!"
        )

    x1, x2 = np.meshgrid(
        pd.unique(grouping_col), pd.unique(transformers["mode"])
    )

    increment = 1000

    for group, mode in zip(x1.flatten(), x2.flatten()):
        n = math.ceil(
            transformers.loc[
                (grouping_col == group) & (transformers["mode"] == mode)
            ].shape[0]
            * share_clusters
        )

        # Introduce a limitation for cluster numbers
        if (
            n
            > transformers.loc[
                (grouping_col == group)
                & (transformers["mode"] == mode),
                by,
            ].nunique()
        ):
            n = transformers.loc[
                (grouping_col == group)
                & (transformers["mode"] == mode),
                by,
            ].nunique()

        # Exclude the option of zero power plants to be clustered
        if (
            not transformers["cluster"]
            .loc[
                (grouping_col == group) & (transformers["mode"] == mode)
            ]
            .empty
        ):
            # Do the actual clustering
            transformers.loc[
                (grouping_col == group)
                & (transformers["mode"] == mode),
                "cluster",
            ] = (
                KMeans(n_clusters=n)
                .fit(
                    transformers.loc[
                        (grouping_col == group)
                        & (transformers["mode"] == mode),
                        by,
                    ].values.reshape(-1, 1)
                )
                .labels_
                + 1
            )
            transformers.loc[
                transformers["cluster"] != 0, "cluster"
            ] += increment

    return transformers


def group_power_plants(
    transformers, grouping_cols, mean_cols, sum_cols, other_cols
):
    """Group the transformer data by grouping cols (clusters)

    Groups power plants data from input DataFrame. Applies aggregation methods
    specified for each column and returns the grouped power plant data.

    Parameters
    ----------
    transformers : pd.DataFrame
        DataFrame holding the transformers data

    grouping_cols : list of str
        Columns used for grouping (i.e. the cluster information)

    mean_cols : list of str
        Columns for which a capacity weighted average is used
        as aggregation function

    sum_cols: list of str
        Columns for which the sum is used as aggregation function

    other_cols: :obj:`str`
        Columns for which no special aggregation function applies
        (0th value is taken)

    Returns
    -------
    transformers_grouped : pandas.DataFrame
        DataFrame containing the aggregated transformer data
    """
    wm = lambda x: np.average(x, weights=transformers.loc[x.index, "capacity"])

    tf_grouped_mean = (
        transformers[mean_cols + grouping_cols]
        .groupby(grouping_cols)
        .aggregate(wm)
    )
    tf_grouped_sum = (
        transformers[sum_cols + grouping_cols].groupby(grouping_cols).sum()
    )
    tf_grouped_other = (
        transformers[other_cols + grouping_cols].groupby(grouping_cols).nth(0)
    )

    transformers_grouped = pd.concat(
        [tf_grouped_other, tf_grouped_mean, tf_grouped_sum],
        axis=1,
        join="inner",
    ).reset_index()

    return transformers_grouped
