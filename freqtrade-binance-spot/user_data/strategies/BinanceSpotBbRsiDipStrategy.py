# pragma pylint: disable=missing-docstring, invalid-name
# flake8: noqa: F401
# isort: skip_file

from pandas import DataFrame

from freqtrade.strategy import IStrategy, merge_informative_pair

import talib.abstract as ta
from technical import qtpylib


class BinanceSpotBbRsiDipStrategy(IStrategy):
    """
    Swing mean-reversion in an uptrend:
    - Trade TF: 2h
    - Optional HTF filter: 4h
    """

    INTERFACE_VERSION = 3

    can_short: bool = False
    timeframe = "2h"

    informative_timeframe = "4h"
    use_higher_timeframe_filter = True

    minimal_roi = {
        "1440": 0.0,
        "720": 0.01,
        "240": 0.02,
        "0": 0.03,
    }

    stoploss = -0.12
    trailing_stop = False

    process_only_new_candles = True
    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False

    startup_candle_count: int = 400

    @property
    def protections(self):
        return [
            {
                "method": "CooldownPeriod",
                "lookback_period_candles": 1,
                "stop_duration_candles": 1,
            },
            {
                "method": "StoplossGuard",
                "lookback_period_candles": 24,
                "trade_limit": 2,
                "stop_duration_candles": 12,
                "only_per_pair": True,
            },
            {
                "method": "MaxDrawdown",
                "lookback_period_candles": 72,
                "trade_limit": 10,
                "stop_duration_candles": 12,
                "max_allowed_drawdown": 0.2,
            },
        ]

    def informative_pairs(self):
        if not self.use_higher_timeframe_filter or not self.dp:
            return []
        pairs = self.dp.current_whitelist()
        return [(pair, self.informative_timeframe) for pair in pairs]

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["ema_fast"] = ta.EMA(dataframe, timeperiod=50)
        dataframe["ema_slow"] = ta.EMA(dataframe, timeperiod=200)
        dataframe["rsi"] = ta.RSI(dataframe, timeperiod=14)

        bb = qtpylib.bollinger_bands(qtpylib.typical_price(dataframe), window=20, stds=2)
        dataframe["bb_lower"] = bb["lower"]
        dataframe["bb_mid"] = bb["mid"]
        dataframe["bb_upper"] = bb["upper"]

        if self.use_higher_timeframe_filter and self.dp:
            informative = self.dp.get_pair_dataframe(
                pair=metadata["pair"], timeframe=self.informative_timeframe
            )
            informative["ema_fast"] = ta.EMA(informative, timeperiod=50)
            informative["ema_slow"] = ta.EMA(informative, timeperiod=200)
            dataframe = merge_informative_pair(
                dataframe,
                informative,
                self.timeframe,
                self.informative_timeframe,
                ffill=True,
            )

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        conditions = (
            (dataframe["ema_fast"] > dataframe["ema_slow"])
            & (dataframe["close"] < dataframe["bb_lower"])
            & (dataframe["rsi"] < 35)
            & (dataframe["volume"] > 0)
        )

        if self.use_higher_timeframe_filter:
            ema_fast_htf = f"ema_fast_{self.informative_timeframe}"
            ema_slow_htf = f"ema_slow_{self.informative_timeframe}"
            if ema_fast_htf in dataframe.columns and ema_slow_htf in dataframe.columns:
                conditions &= dataframe[ema_fast_htf] > dataframe[ema_slow_htf]

        dataframe.loc[conditions, "enter_long"] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (
                    qtpylib.crossed_above(dataframe["close"], dataframe["bb_mid"])
                    | qtpylib.crossed_above(dataframe["rsi"], 50)
                    | qtpylib.crossed_below(dataframe["ema_fast"], dataframe["ema_slow"])
                )
                & (dataframe["volume"] > 0)
            ),
            "exit_long",
        ] = 1
        return dataframe

