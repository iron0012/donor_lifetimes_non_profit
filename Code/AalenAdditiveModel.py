import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from sklearn.preprocessing import scale
from sklearn.utils import resample
from matplotlib.colors import colorConverter
from lifelines import AalenAdditiveFitter
import pickle

'''This module contains the basic functions for 
    1. Instantiating aalen object from the AalenAdditiveFitter class.
    2. Performing bootstrapping on the dataset.
    '''

def Aalen_model(df, l2 = 0.01, coeff_pen = 0.1, smooth_pen = 0.1):
    '''Invokes the Aalen Additive Fitter class to creat an instance that fits the regression model:
    
    hazard(t)  = b_0(t) + b_1(t)*x_1 + ... + b_N(t)*x_N
	i.e., the hazard rate is a linear function of the covariates.
    
    Parameters
    df: Pandas dataframe.  The y column must be called "Total_years."  A column of Boolean values called 
        "censored" to indicate which row of data is censored, as indicated by True or False or 1 or 0.
    coeff_pen = 0.1: Attach a L2 penalizer to the size of the coeffcients during regression. This improves
        stability of the estimates and controls for high correlation between covariates.  For example, 
        this shrinks the absolute value of c_{i,t}. Recommended, even if a small value.
    Smoothing_penalizer = 0.1: Attach a L2 penalizer to difference between adjacent (over time) coefficents. For
        example, this shrinks the absolute value of c_{i,t} - c_{i,t+1}.
    
	Other built-in, unadjustable parameters:
    Intercept = False.  We suggest adding a column of 1 to model the baseline hazard.
    nn_cumulative_hazard = True:  In its True state, it forces the the negative hazard values to be zero 
    
    Output: aaf instance fitted to df'''
    aaf = AalenAdditiveFitter(fit_intercept=False, coef_penalizer=coeff_pen, smoothing_penalizer=smooth_pen, nn_cumulative_hazard=True)
    aaf.fit(df, 'Total_years', event_col='censored')
    return aaf 


def Bootstrap(df, bootstrap_count = 100):
    '''Accepts a pandas dataframe with a column called 'Total_years' which is y and 
    a column called 'censored' which indicates which column of data is censored.
   
    Performs bootstrap fitting with the Aalen model on a dataset df.  
    Draws n=number of rows samples from df with replacement. Trains a Aalen model by invoking the Aalen_model 
    function and append it into the list.  Repeat bootstrap_count times.  
    Returns a list of bootstrap_count of Aalen models each trained by a bootstrapped set of data.
    
    Parameters:
    df: A pandas dataframe with y = 'Total_years' and censored data = 'censored' and the rest of the columns are the features.
    bootstrap_count:  Number of bootstrapped model to train and append to the AAF_list

    Output: A list of length bootstrap_count of trained Aalen models.
    '''
    
    AAF_list = []  #This is a list to store the bootstrapped Aalen models
    for bootstrap_number in range(bootstrap_count):
        df_Bootstrap = resample(df)
        aaf = Aalen_model(df_Bootstrap)  #Calls the Aalen_model function to train a model aaf
        AAF_list.append(aaf)  #Appends aaf to AAF_list
    return AAF_list

def Aalen_predict_lifetimes(AAF_list, test_dataset):
    '''Accepts a list (AAF_list) containing m trained bootstrapped AAF models (trained by bootstrapping in the Bootstrap function) and a test data set (test_dataset).  Calculate the predicted lifetimes by each model for each donor.   Outputs the mean and median of lifetime for each donor.
    
    The overall scheme is to iterate through the m bootstrap models and generate m predictions and m hazard functions for each row of data.  The mean and median of the predictions are calculated and added back to the the dataset as new columns called 'Mean_Pred_Total_years' and 'Med_Pred_Total_years'

    Parameters:
    AAF_list: A list of trained models to make predictions based of the test_dataset
    test_dataset: A pandas dataframe with y column = 'Total_years'

    Output:  test_dataset with two columns 'Mean_Pred_Total_years' and 'Med_Pred_Total_years' added.
    '''
    aaf_predict = []

    for i, aaf in enumerate(AAF_list):
        #This informs the use the progress of the iteration 
        print 'i = ', i  
        #Generates predictions for the dataset and appends them to the aaf_predict list.
        aaf_predict.append(aaf.predict_expectation(test_dataset.astype(float)).values)

    #Calculation of mean and median of aaf_predict
    aaf_pred_array = np.asarray(aaf_predict) 
    test_dataset['Mean_Pred_Total_years'] = np.mean(aaf_pred_array, axis = 0)
    test_dataset['Med_Pred_Total_years'] = np.median(aaf_pred_array, axis = 0)
    
    return test_dataset

def Aalen_predict_donor_cum_haz(AAF_list, test_dataset):
    '''Accepts a list (AAF_list) containing m trained bootstrapped AAF models (trained by bootstrapping in the Bootstrap function) and a test data set (test_dataset).  Calculates the Aalen hazard function by each model for each donor.   Outputs a list of m dataframes, each of which is the donors' hazard functions for the nth model in the AAF_list.   

    Iterates through the list.  Plug in test_dataset into each model to produce
    1.  m sets of predicted lifetimes (one set for each model), which are store in the list aaf_predict.
    The mean and the median of the bootstrap model predictions are added back to test_dataset as new columns called
    'Mean_Pred_Total_years' and 'Med_Pred_Total_years'
    2.  m sets of hazard functions tailored for each user.  This functions are stored in the list aaf_pred_cum_haz.


    Parameters:
    AAF_list: A list of trained models to make predictions
    test_dataset: A pandas dataframe with y column = 'Total_years'

    Output:  
    aaf_predict_donor_cum_haz:  A list of dataframes each presenting the donors' hazard functions predicted by the models in AAF_list.
    '''
    aaf_predict_donor_cum_haz = []

    for i, aaf in enumerate(AAF_list):
        #This informs the use the progress of the iteration 
        print 'i = ', i  
        #Generates hazard functions that are tailored to each donor and append them to aaf_predict_cum_haz
        aaf_predict_cum_haz.append(aaf.predict_cumulative_hazard(test_dataset))
    
    return aaf_predict_donor_cum_haz
   
   def Aalen_cum_haz(AAF_list, test_dataset):
    '''Accepts a list (AAF_list) containing m trained bootstrapped AAF models (trained by bootstrapping in the Bootstrap function) and a test data set (test_dataset).  Iterates through the list.  Outputs the cumulative hazard function for each feature (hazard).  Store them in a list.  Note that these dataframes cannot be simply averaged because the time intervals are not always the same.  

    Parameters:
    AAF_list: A list of trained models to make predictions
    test_dataset: A pandas dataframe with y column = 'Total_years'

    Output:
    aaf_cum_haz:  A list of dataframes each presenting the hazard functions of the models in AAF_list.
    '''

    aaf_cum_haz = []
    for i, aaf in enumerate(AAF_list):
        #This informs the use the progress of the iteration 
        print 'i = ', i  
        aaf_cum_haz.append(aaf.cumulative_hazards_)
        #Generates hazard functions that are tailored to each donor and append them to aaf_predict_cum_haz
    
    return aaf_cum_haz
   