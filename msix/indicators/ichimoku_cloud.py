class IchimokuIndicator(IndicatorMixin):
    """Ichimoku Kinkō Hyō (Ichimoku)
    http://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:ichimoku_cloud
    Args:
        high(pandas.Series): dataset 'High' column.
        low(pandas.Series): dataset 'Low' column.
        window1(int): n1 low period.
        window2(int): n2 medium period.
        window3(int): n3 high period.
        visual(bool): if True, shift n2 values.
        fillna(bool): if True, fill nan values.
    """

    def __init__(
        self,
        high: pd.Series,
        low: pd.Series,
        window1: int = 9,
        window2: int = 26,
        window3: int = 52,
        visual: bool = False,
        fillna: bool = False,
    ):
        self._high = high
        self._low = low
        self._window1 = window1
        self._window2 = window2
        self._window3 = window3
        self._visual = visual
        self._fillna = fillna
        self._run()

    def _run(self):
        min_periods_n1 = 0 if self._fillna else self._window1
        min_periods_n2 = 0 if self._fillna else self._window2
        self._conv = 0.5 * (
            self._high.rolling(self._window1, min_periods=min_periods_n1).max()
            + self._low.rolling(self._window1, min_periods=min_periods_n1).min()
        )
        self._base = 0.5 * (
            self._high.rolling(self._window2, min_periods=min_periods_n2).max()
            + self._low.rolling(self._window2, min_periods=min_periods_n2).min()
        )

    def ichimoku_conversion_line(self) -> pd.Series:
        """Tenkan-sen (Conversion Line)
        Returns:
            pandas.Series: New feature generated.
        """
        conversion = self._check_fillna(self._conv, value=-1)
        return pd.Series(
            conversion, name=f"ichimoku_conv_{self._window1}_{self._window2}"
        )

    def ichimoku_base_line(self) -> pd.Series:
        """Kijun-sen (Base Line)
        Returns:
            pandas.Series: New feature generated.
        """
        base = self._check_fillna(self._base, value=-1)
        return pd.Series(base, name=f"ichimoku_base_{self._window1}_{self._window2}")

    def ichimoku_a(self) -> pd.Series:
        """Senkou Span A (Leading Span A)
        Returns:
            pandas.Series: New feature generated.
        """
        spana = 0.5 * (self._conv + self._base)
        spana = (
            spana.shift(self._window2, fill_value=spana.mean())
            if self._visual
            else spana
        )
        spana = self._check_fillna(spana, value=-1)
        return pd.Series(spana, name=f"ichimoku_a_{self._window1}_{self._window2}")

    def ichimoku_b(self) -> pd.Series:
        """Senkou Span B (Leading Span B)
        Returns:
            pandas.Series: New feature generated.
        """
        spanb = 0.5 * (
            self._high.rolling(self._window3, min_periods=0).max()
            + self._low.rolling(self._window3, min_periods=0).min()
        )
        spanb = (
            spanb.shift(self._window2, fill_value=spanb.mean())
            if self._visual
            else spanb
        )
        spanb = self._check_fillna(spanb, value=-1)
        return pd.Series(spanb, name=f"ichimoku_b_{self._window1}_{self._window2}")

def ichimoku_conversion_line(
    high, low, window1=9, window2=26, visual=False, fillna=False
) -> pd.Series:
    """Tenkan-sen (Conversion Line)
    It identifies the trend and look for potential signals within that trend.
    http://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:ichimoku_cloud
    Args:
        high(pandas.Series): dataset 'High' column.
        low(pandas.Series): dataset 'Low' column.
        window1(int): n1 low period.
        window2(int): n2 medium period.
        visual(bool): if True, shift n2 values.
        fillna(bool): if True, fill nan values.
    Returns:
        pandas.Series: New feature generated.
    """
    return IchimokuIndicator(
        high=high,
        low=low,
        window1=window1,
        window2=window2,
        window3=52,
        visual=visual,
        fillna=fillna,
    ).ichimoku_conversion_line()


def ichimoku_base_line(
    high, low, window1=9, window2=26, visual=False, fillna=False
) -> pd.Series:
    """Kijun-sen (Base Line)
    It identifies the trend and look for potential signals within that trend.
    http://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:ichimoku_cloud
    Args:
        high(pandas.Series): dataset 'High' column.
        low(pandas.Series): dataset 'Low' column.
        window1(int): n1 low period.
        window2(int): n2 medium period.
        visual(bool): if True, shift n2 values.
        fillna(bool): if True, fill nan values.
    Returns:
        pandas.Series: New feature generated.
    """
    return IchimokuIndicator(
        high=high,
        low=low,
        window1=window1,
        window2=window2,
        window3=52,
        visual=visual,
        fillna=fillna,
    ).ichimoku_base_line()


def ichimoku_a(high, low, window1=9, window2=26, visual=False, fillna=False):
    """Ichimoku Kinkō Hyō (Ichimoku)
    It identifies the trend and look for potential signals within that trend.
    http://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:ichimoku_cloud
    Args:
        high(pandas.Series): dataset 'High' column.
        low(pandas.Series): dataset 'Low' column.
        window1(int): n1 low period.
        window2(int): n2 medium period.
        visual(bool): if True, shift n2 values.
        fillna(bool): if True, fill nan values.
    Returns:
        pandas.Series: New feature generated.
    """
    return IchimokuIndicator(
        high=high,
        low=low,
        window1=window1,
        window2=window2,
        window3=52,
        visual=visual,
        fillna=fillna,
    ).ichimoku_a()


def ichimoku_b(high, low, window2=26, window3=52, visual=False, fillna=False):
    """Ichimoku Kinkō Hyō (Ichimoku)
    It identifies the trend and look for potential signals within that trend.
    http://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:ichimoku_cloud
    Args:
        high(pandas.Series): dataset 'High' column.
        low(pandas.Series): dataset 'Low' column.
        window2(int): n2 medium period.
        window3(int): n3 high period.
        visual(bool): if True, shift n2 values.
        fillna(bool): if True, fill nan values.
    Returns:
        pandas.Series: New feature generated.
    """
    return IchimokuIndicator(
        high=high,
        low=low,
        window1=9,
        window2=window2,
        window3=window3,
        visual=visual,
        fillna=fillna,
    ).ichimoku_b()


