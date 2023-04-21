import pandas as pd
from pandas.tseries.frequencies import to_offset


def resample_timeseries(
    timeseries, freq, aggregation_rule="sum", interpolation_rule="linear"
):
    """Resample a timeseries to the frequency provided

    The frequency of the given timeseries is determined at first and upsampling
    resp. downsampling are carried out afterwards. For upsampling linear
    interpolation (default) is used, but another method may be chosen.

    Time series indices ignore time shifts and can be interpreted as UTC time.
    Since they aren't localized, this cannot be detected by pandas and the
    correct frequency cannot be inferred. As a hack, only the first couple of
    time steps are checked, for which no problems should occur.

    Parameters
    ----------
    timeseries : :obj:`pd.DataFrame`
        The timeseries to be resampled stored in a pd.DataFrame

    freq : :obj:`str`
        The target frequency

    interpolation_rule : :obj:`str`
        Method used for interpolation in upsampling

    Returns
    -------
    resampled_timeseries : :obj:`pd.DataFrame`
        The resampled timeseries stored in a pd.DataFrame

    """
    # Ensure a datetime index
    try:
        timeseries.index = pd.DatetimeIndex(timeseries.index)
    except ValueError:
        raise ValueError(
            "Time series has an invalid index. "
            "A pd.DatetimeIndex is required."
        )

    try:
        original_freq = pd.infer_freq(timeseries.index, warn=True)
    except ValueError:
        original_freq = "AS"

    # Hack for problems with recognizing abolishing the time shift
    if not original_freq:
        try:
            original_freq = pd.infer_freq(timeseries.index[:5], warn=True)
        except ValueError:
            raise ValueError("Cannot detect frequency of time series!")

    # Introduce common timestamp to be able to compare different frequencies
    common_dt = pd.to_datetime("2000-01-01")

    if common_dt + to_offset(freq) > common_dt + to_offset(original_freq):
        # do downsampling
        resampled_timeseries = timeseries.resample(freq).agg(aggregation_rule)

    else:
        # do upsampling
        resampled_timeseries = timeseries.resample(freq).interpolate(
            method=interpolation_rule
        )

    cut_leap_days(resampled_timeseries)

    return resampled_timeseries


def cut_leap_days(time_series):
    """Take a time series index with real dates and cut the leap days out

    Actual time stamps cannot be interpreted. Instead consider 8760 hours
    of a synthetical year

    Parameters
    ----------
    time_series : pd.Series or pd.DataFrame
        original time series with real life time index

    Returns
    -------
    time_series : pd.Series or pd.DataFrame
        Time series, simply cutted down to 8 760 hours per year
    """
    years = sorted(list(set(getattr(time_series.index, "year"))))
    for year in years:
        if is_leap_year(year):
            try:
                time_series.drop(
                    time_series.loc[
                        (time_series.index.year == year)
                        & (time_series.index.month == 12)
                        & (time_series.index.day == 31)
                    ].index,
                    inplace=True,
                )
            except KeyError:
                continue

    return time_series


def is_leap_year(year):
    """Check whether given year is a leap year or not

    Parameters:
    -----------
    year: :obj:`int`
        year which shall be checked

    Returns:
    --------
    leap_year: :obj:`boolean`
        True if year is a leap year and False else
    """
    leap_year = False

    if year % 4 == 0:
        leap_year = True
    if year % 100 == 0:
        leap_year = False
    if year % 400 == 0:
        leap_year = True

    return leap_year
