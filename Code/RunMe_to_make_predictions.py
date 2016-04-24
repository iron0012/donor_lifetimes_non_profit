import pandas as pd
import numpy as np
import pickle
import AalenAdditiveModel as AAM


'''This program loads a pickled donor data set and a list of n bootstrap trained models.  Then it passes
the list of models and the censored part of the data set to the Aalen_predict_lifetimes functions, which
generates a mean and median predicted lifetimes for each censored donor.  The mean and median lifetimes
are combined with the data set as new columns and output as a csv file.
'''
#Load the pickled donor dataset
print 'Loading cleaned dataset...'
filename = 'cleaned_dataset.p'
fileobject = open(filename, 'rb')
donor_dataset= pickle.load(fileobject)
fileobject.close()
print 'Cleaned dataset loaded.'
print

#Select only the censored data to make predictions of.  These are donors who have not churned.  Note the model was trained on uncensored (churned) donors because they are the ones whose lifetimes are known.

censored_donor_dataset = donor_dataset[donor_dataset['censored'] == 1]

#Load the pickled list of Aalen models.
print 'Loading list of bootstrap trained models...'
filename = 'AAF_100.p'
fileobject = open(filename, 'rb')
AAF_100 = pickle.load(fileobject)
fileobject.close()
print 'bootstrap trained models loaded.'
print

#This calls the Aalen_predict_lifetimes function which uses the bootstrap models to predict
#the lifetimes of each line of data.  The mean and median lifetimes of each donor is added to
#as new columns to the dataframe and then returned.
print 'Calling Aalen_predicting_lifetimes to make predictions for lifetimes...'
df_lifetime = AAM.Aalen_predict_lifetimes(AAF_100, censored_donor_dataset)
print 'Predictions completed'
print

df_lifetime.to_csv('dataset_with_predicted_lifetimes.csv')

print
print 'DATA SET WITH PREDICTED LIFETIME COLUMNS HAS BEEN SAVED TO THIS FOLDER AS csv FILE.'
