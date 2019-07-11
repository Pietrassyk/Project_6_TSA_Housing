#imports
import pandas as pd
from statsmodels.tsa.stattools import adfuller

#Function definitions:

def preprocess(df, date_column = "DATE"):
    """This function will turn a dataframe into as timeseries DataFrame with monthly Frequency
    Paramerters
    -----------
    df : pandas DataFrame
        Raw Dataframe to process
    date_columms : String
        Column name that contains the date information and will be set as DateTimeIndex for the output DataFrame
    
    Returns
    ---------
    df : pandas DataFrame
        processed Dataframe"""
    df[date_column] = pd.to_datetime(df[date_column])
    df = df.set_index(date_column)
    df = df.resample("MS").ffill()
    return df

def eval_stationary(df, alpha = 0.05):
    """Evaluate the stationarity of a Series using the Dickey-Fuller Test
    Params:
    --------
    df : pandas DataFrame
        Series to test stationarity
    alpha : Float
        Confidence intervall to assume stationarity
    Returns:
    -------
    """
    p = round(adfuller(df.dropna())[1],3)
    out = ["No","Yes"]
    print(f"p-value for Dickey-Fuller test: {p}\nSeries is stationary?: {out[int(p<alpha)]}")