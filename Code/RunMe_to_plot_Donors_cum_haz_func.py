
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import pickle
import random

#These are in the same folder
import AalenAdditiveModel as AAM
import Aalen_KMF_plots as AKp

'''This program invokes the plot_donor_cum_haz function from Aalen_KMF_plots.py to
plot the cumulative hazard functions for a random number of chosen donors.  NB: This is
the hazard function individually customized for each donor, depending on her/his features.
'''

#First load the pickled trained models
filename = 'AAF_100.p'
fileobject = open(filename, 'rb')
AAF_list_100 = pickle.load(fileobject)
fileobject.close()

#Then load the cleaned dataset to be fitted.  Note this dataset contains both the uncensored
#(churned) and censored data.  Only the censored data will be use for prediction because the
#uncensored data was used to train the model.
filename = 'cleaned_dataset.p'
fileobject = open(filename, 'rb')
donor_dataset= pickle.load(fileobject)
fileobject.close()

#This is to obtain a dataset which only includes the censored data.
censored_donor_dataset = donor_dataset[donor_dataset['censored'] == 1]

#This is the number of random censored donors whose cumulative hazard function is to be plotted.
number_donors_to_be_plotted = 2
#These are the parameters for the figures.
years = 5
y_max = 3
lw = 0.03
#Call the function to plot the donors' cumulative hazard function.
AKp.plot_donor_cum_haz(AAF_list_100, donor_dataset, number_donors_to_be_plotted, years, y_max, lw)
