#imports

import pandas as pd
import numpy as np
import time
import datetime
import json
import itertools as it

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


def get_json_name():
    path = "Dumps/"
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H-%M-%S')
    return path+st+".json"

def product_dict(**kwargs):
    output = []
    keys = kwargs.keys()
    vals = kwargs.values()
    for instance in it.product(*vals):
        output.append(dict(zip(keys, instance)))
    return output

def tsa_tune(obs, param_grid, estimator = {"enforce_stationarity" : False, "enforce_invertibility" : False}):
    
    """Function that will run a GridSearch Like model comparison using AIC Score
    Parameters:
    --------
    df : Pandas Series
        Series object with datetime index cointaining the timeseries
    
    estimator: dict
        constant SARIMAX model parameters that will not be optimized in gridsearch
    
    param_grid : dict
        Parameter specification using key : value pairs values mist be passed as iterables
        Parameters must be compatible with statsmodels SARIMAX model
        
        Parameters
        ----------
        order : tuple (list, list, list)
            Containing the order values (p,d,q) to check
        
        seasonal_order : tuple(list,list,list,list)
            Containing the seasonal order values (p,d,q,S) to check
    
    Returns:
    --------
    scorings: dict
        Dictionary containing AIC scores and model Parameters
        
    """
    #get time stamp for json object that will store the results
    json_name = get_json_name()
    
    if not estimator:
        print("No estimator given")
        estimator = {
        "enforce_stationarity" : [False], 
        "enforce_invertibility" : [False]
        }
    else:
        print("Refactoring Estimator")
        estimator = estimator.copy()
        for key in estimator.keys():
            estimator[key] = [estimator[key]]
    param_grid = param_grid.copy()   
    scorings = []
    i= 1
    #create parameters combinations
    
    ##extract order values from nested lists
    param_grid["order"] = list(it.product(*[x for x in param_grid["order"]]))
    try:
        param_grid["seasonal_order"] = list(it.product(*[x for x in param_grid["seasonal_order"]]))
    except:
        print("No seasonal_order given --> running ARIMA-model")
    
    ##get all parameter combinations
    param_grid.update(estimator)
    params = product_dict(**param_grid)
    
    ##iterate through params
    print(f"Starting Modeling with {len(params)} jobs")
    
    ## and fit model
    for param in params:
        print(f"Fit {i}/{len(params)}")#, end = "\r")
        print (param)
        try:
            model = sm.tsa.SARIMAX(obs, **param, dates=obs.index)
            output = model.fit()
            res = output.aic
            print(res)
        except:
            res = "Error"
        i+=1
        param.update({"AIC": res})
        scorings.append(param)
    
    with open(json_name, "w") as f:
        json.dump(scorings, f)
    
    return scorings

def best_estimator(results_list, scoring = "AIC", highest = False):
    """Finding the best scoring model in a tsa_tune dictionary
    Parameters:
    --------
    results_list : list
        list of dictionaries derived by running the tsa_tune function
    
    scoring: str
        type of the scoring, being used to evaluate model performances
        Currently suppoted:
        - "AIC"
    
    highest : bool
        whether or not to look for the highest or lowest scoring
   
    Returns:
    --------
    best_model: dict
        Dictionary containing the best model's parameters"""
    if highest:
        dir_func = max
    else:
        dir_func = min
    extreme = dir_func([model[scoring] for model in results_list])
    output = list(filter(lambda x: x[scoring] == extreme, results_list))[0].copy()
    
    return output , output.pop(scoring)