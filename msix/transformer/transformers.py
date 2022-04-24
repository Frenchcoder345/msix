import ta

class Transformer:
    
    def __init__(self):
        pass
    
    @staticmethod
    def volatility_indicators(df):
        """Function to add all technical indicators without actually passing the columns"""
        df = ta.add_volatility_ta(df, high="high", low="low", close="close", fillna=True)
        return df
    
    @staticmethod
    def momentum_indicators(df):
        """Function to add all technical indicators without actually passing the columns"""
        df = ta.add_momentum_ta(df, high="high", low="low", close="close", volume='volume', fillna=True)
        return df
    
    @staticmethod
    def trend_indicators(df):
        """Function to add all technical indicators without actually passing the columns"""
        df = ta.add_trend_ta(df, high="high", low="low", close="close", fillna=True)
        return df
    
    @staticmethod
    def other_indicators(df):
        """Function to add all technical indicators without actually passing the columns"""
        df = ta.add_others_ta(df, close="adj_close", fillna=True)
        return df
    
    @staticmethod
    def volume_indicators(df):
        """Function to add all technical indicators without actually passing the columns"""
        df = ta.add_volume_ta(df, high="high", low="low", close="close",volume = "volume", fillna=True)
        return df
    
    @staticmethod
    def all_indicators(df):
        """Function to add all technical indicators without actually passing the columns"""
        df = ta.add_all_ta_features(df, open='open', high="high", low="low", close="close",volume = "volume", fillna=True)
        return df
