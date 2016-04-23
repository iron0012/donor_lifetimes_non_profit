import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from sklearn.preprocessing import scale
from sklearn.utils import resample
from matplotlib.colors import colorConverter
from lifelines import AalenAdditiveFitter, KaplanMeierFitter
import AalenAdditiveModel as AAM
import random
import pickle

def plot_cum_haz_functions(AAF_list, x_max =40):
	'''Accepts a list of Aalen_model instances and plot the cumulative hazard function for all instances.
	This function does not return anythng.
	Parameters:
	AAF_list: a list of Aalen additive instances created by the AalenAdditiveFitter
	x_max = 40: maxiumum value of the x-axis.

	Output:
	Plots of the individual hazard functions for each specific hazard as a function of time.
	'''

	colors = ['grey', 'lightgreen', 'blue','red', 'magenta', 'gold', 'green', 'orange']	
	for i, hazard in enumerate(AAF_list[0].hazards_.columns):
		print 'hazard is', hazard
		fig = plt.figure(figsize=(5, 5))
		plt.subplot(111)

		#To avoid having a legend for each of the model (therefore leading having multiple labels of the
		#same data, we plot only the first model with legend here, and the rest of the model without legend)
		aaf = AAF_list[0]
		plt.plot(aaf.cumulative_hazards_[hazard], alpha =0.05, c = colors[i], label = hazard)
		plt.legend(loc = 'lower right', fontsize = 10)

		#These models are plotted without legend.
		for j in range(1, len(AAF_list)):
			aaf = AAF_list[j]
			plt.plot(aaf.cumulative_hazards_[hazard], alpha =0.05, c = colors[i], label = hazard)
		
		#Customize the axes, labels, etc.
		plt.xlabel('Years', size = 10)
		plt.ylabel('Cumulative hazard function', size = 10)
		plt.grid()
		plt.xlim(0, x_max)
		plt.show()
	plt.close

def plot_Kaplan_Meier_overall(donor_dataset):
	'''Accepts a dataframe of donor data.  Plots the overall Kaplan-Meier curve based of the lifetime of the donors.  The active donors ('censored') will be excluded from the plot.

	Parameters:
	donor_dataset: Pandas dataframe which contain at least the columns 'Total-years' and 'censored'.  'Total_years' represents how many years the donors have been active.  'censored' indicates whether a donor is still active (True = active donor).

	Output:
	A Kaplan-Meier plot.

	This function does not return anything.

	'''
	T = donor_dataset['Total_years']
	C = donor_dataset['censored']

	#Create KaplanMeierInstance
	kmf = KaplanMeierFitter()
	kmf.fit(T, C, label = 'Overall')

	#plot KM function
	fig = plt.figure(figsize=(5, 5))
	ax = fig.add_subplot(111)
	kmf.plot(ax=ax) 
	ax.set_xlabel('Years', size = 20)
	ax.set_ylabel('Surviving donor population', size = 20)
	ax.set_xlim(0,40)
	ax.set_ylim(0, 1)
	ax.grid()
	ax.legend(loc = 'best', fontsize = 20)
	plt.show()
	return

def plot_Kaplan_Meier_feature(donor_dataset):
    '''Accepts a dataframe of donor data.  For each feature (column), it plots the Kaplan-Meier curves of the donors based on whether the feature is true or false.  The active donors ('censored') will be excluded from the plot.

    Parameters:
    donor_dataset: Pandas dataframe which contain at least the columns 'Total-years' and 'censored'.  'Total_years' represents how many years the donors have been active.  'censored' indicates whether a donor is still active (True = active donor).

    Output:
    Kaplan-Meier plot(s).

    This function does not return anything.
    ''' 
    T = donor_dataset['Total_years']
    C = donor_dataset['censored']
    features = list(donor_dataset.columns)
    features.remove('Total_years')
    features.remove('censored')
    features.remove('Baseline')
    kmf = KaplanMeierFitter()
    for feature in features:
        Above_mean = donor_dataset[feature] > donor_dataset[donor_dataset['censored'] == 0][feature].mean()
        fig = plt.figure(figsize=(5, 5))
        ax = fig.add_subplot(111)
        kmf = KaplanMeierFitter()
        kmf.fit(T[Above_mean], C[Above_mean], label = feature + ': Yes or > mean')
        kmf.plot(ax=ax, linewidth = 2) 
        kmf.fit(T[~Above_mean], C[~Above_mean], label = feature + ': No or < mean')
        kmf.plot(ax=ax, linewidth = 2) 
        ax.set_xlabel('Years', size = 10)
        ax.set_ylabel('Surviving donor population', size = 10)
        ax.set_xlim(0,40)
        ax.set_ylim(0, 1)
        ax.grid()
        ax.legend(loc = 'upper right', fontsize = 10)
        plt.show()

def plot_donor_cum_haz(AAF_list, donor_dataset, number_of_donors = 8, years = 5, y_max = 5, lw = 0.01):
	donor_cum_haz_functions_list = AAM.Aalen_cum_haz(AAF_list, donor_dataset)
	colors = ['grey', 'lightgreen', 'blue','red', 'magenta', 'gold', 'green', 'orange']	
	rows = random.sample(range(donor_cum_haz_functions_list[0].shape[1]), number_of_donors)
	for i, row in enumerate(rows):
		print row
		for donor_cum_haz_functions in donor_cum_haz_functions_list:
			plt.plot(donor_cum_haz_functions.T.iloc[row], alpha = lw, color = colors[i%8])
	plt.xlabel('Years', size = 10)
	plt.ylabel("Donor cumulative hazard function", size = 10)
	plt.grid()
	plt.xlim(0, years)
	plt.ylim(0, y_max)
	plt.show()
	plt.close()
	return
