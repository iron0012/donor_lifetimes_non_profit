import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from sklearn.preprocessing import scale
from sklearn.utils import resample
from matplotlib.colors import colorConverter
from lifelines import AalenAdditiveFitter, KaplanMeierFitter
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
		for j in range(len(AAF_list)):
			aaf = AAF_list[j]
			plt.plot(aaf.cumulative_hazards_[hazard], alpha =1, c = colors[i])
		plt.xlabel('Years', size = 10)
		plt.ylabel('Cumulative hazard function', size = 10)
		plt.grid()
		plt.xlim(0, x_max)
		plt.show()
	#plt.close

def plot_Kaplan_Meier_overall(donor_dataset):
	'''Accepts a dataframe of donor data.  Plots the overall Kaplan-Meier curve based of the lifetime of the donors.  The active donors ('censored') will be excluded from the plot.

	Parameters:
	donor_dataset: Pandas dataframe which contain at least the columns 'Total-years' and 'censored'.  'Total_years' represents how many years the donors have been active.  'censored' indicates whether a donor is still active (True = active donor).

	Output:
	A Kaplan-Meier plot.

	This function does not return anything.

	'''
	T = regression_dataset['Total_years']
	C = regression_dataset['censored']

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
	ax.set_color_cycle(colors)
	ax.grid()
	ax.legend(loc = 'best', fontsize = 20)
	return

def plot_Kaplan_Meier_feature(donor_dataset):
	'''Accepts a dataframe of donor data.  For each feature (column), it plots the Kaplan-Meier curves of the donors based on whether the feature is true or false.  The active donors ('censored') will be excluded from the plot.

	Parameters:
	donor_dataset: Pandas dataframe which contain at least the columns 'Total-years' and 'censored'.  'Total_years' represents how many years the donors have been active.  'censored' indicates whether a donor is still active (True = active donor).

	Output:
	Kaplan-Meier plot(s).

	This function does not return anything.
	'''

	T = df_regress['Total_years']
	C = df_regress['censored']
	features_list = regression_dataset.columns
	#Remove the columns 'Total_years' and 'censored' from the dataframe because they are not features.
	features_list = donor_dataset.columns.remove(['Total_years', 'censored'])	

	for feature in features_list:
	    fig = plt.figure(figsize=(5, 5))
	    ax = fig.add_subplot(111)
	    kmf.fit(T[~Above_mean], C[~Above_mean], label = feature + ': True or > mean')
	    kmf.plot(ax=ax, linewidth = 2) 
	    kmf.fit(T[Above_mean], C[Above_mean], label = feature + ': False or < mean')
	    kmf.plot(ax=ax, linewidth = 2) 
	    ax.set_xlabel('Years', size = 10)
	    ax.set_ylabel('Surviving donor population', size = 10)
	    ax.set_xlim(0,40)
	    ax.set_ylim(0, 1)
	    ax.set_color_cycle(colors)
	    ax.grid()
	    ax.legend(loc = 'upper right', fontsize = 10)

