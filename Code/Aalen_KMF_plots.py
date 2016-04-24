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
	#This produces two data frames of the columns 'Total_years'
	#and 'censored.'  The former indicates how manay years a
	#donor has donoted before she/he churned.  The latter indicates
	#whether the donor is censored (not churned).  Only donor who
	#has churned (not censored) are used because we don't know the
	#'Total_years' of donors who have not churned yet.
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
    '''Accepts a list of (bootstrap) trained models, calculates each of their cumulative hazard functions,
	randomly selects number_of_donors (censored), and plots their hazard functions.

    Parameters:
    donor_dataset: Pandas dataframe which contain at least the columns 'Total-years' and 'censored'.
	'Total_years' represents how many years the donors have been active.
	'censored' indicates whether a donor is still active (True = active donor).

    Output:
    A plot of the cumulative hazard functions for the randomly selected donors.

    This function does not return anything.
    '''
	#Calls the Aalen_cum_haz function found in AalenAdditiveModel.py to
	#calculate the donor cumulative hazard functions.
	donor_cum_haz_functions_list = AAM.Aalen_cum_haz(AAF_list, donor_dataset)

	#This list of colors will be cycled through during the plotting.  If the number_of_donors > 8, the colors
	#will have to be repeated.
	colors = ['grey', 'lightgreen', 'blue','red', 'magenta', 'gold', 'green', 'orange']

	#Randomly selects a number_of_donors from the donor_dataset to be plotted.
	rows = random.sample(range(donor_cum_haz_functions_list[0].shape[1]), number_of_donors)

	#Iterates through the rows (donors selected) and then through all cumulative hazard functions
	#to plot them on the same figure.  Note that this order of iteraton must be maintained
	#so that the cum hazard function for each donor is plotted with the same color.
	for i, row in enumerate(rows):
		print row
		for donor_cum_haz_functions in donor_cum_haz_functions_list:
			plt.plot(donor_cum_haz_functions.T.iloc[row], alpha = lw, color = colors[i%8])
	plt.xlabel('Years', size = 10)
	plt.ylabel("Donor cumulative hazard function", size = 10)
	text = 'Cumulative hazards for ' + str(number_of_donors) + ' random censored donors.'
	plt.annotate(text, xy=(0, 0), xytext=(0.2, 2.8))
	plt.grid()
	plt.xlim(0, years)
	plt.ylim(0, y_max)
	plt.show()
	plt.close()
	return
