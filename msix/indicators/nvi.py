from indicators.ichimoku_cloud import IndicatorMixin
import pandas as pd
import numpy as np

class NegativeVolumeIndexIndicator(IndicatorMixin):
    """Negative Volume Index (NVI)
    http://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:negative_volume_inde
    Args:
        close(pandas.Series): dataset 'Close' column.
        volume(pandas.Series): dataset 'Volume' column.
        fillna(bool): if True, fill nan values with 1000.
    """

    def __init__(self, close: pd.Series, volume: pd.Series, fillna: bool = False):
        self._close = close
        self._volume = volume
        self._fillna = fillna
        self._run()

    def _run(self):
        price_change = self._close.pct_change()
        vol_decrease = self._volume.shift(1) > self._volume
        self._nvi = pd.Series(
            data=np.nan, index=self._close.index, dtype="float64", name="nvi"
        )
        self._nvi.iloc[0] = 1000
        for i in range(1, len(self._nvi)):
            if vol_decrease.iloc[i]:
                self._nvi.iloc[i] = self._nvi.iloc[i - 1] * (1.0 + price_change.iloc[i])
            else:
                self._nvi.iloc[i] = self._nvi.iloc[i - 1]

    def negative_volume_index(self) -> pd.Series:
        """Negative Volume Index (NVI)
        Returns:
            pandas.Series: New feature generated.
        """
        # IDEA: There shouldn't be any na; might be better to throw exception
        nvi = self._check_fillna(self._nvi, value=1000)
        return pd.Series(nvi, name="nvi")

def negative_volume_index(close, volume, fillna=False):

    return NegativeVolumeIndexIndicator(
        close=close, volume=volume, fillna=fillna
    ).negative_volume_index()