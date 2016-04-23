import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import pickle
import Aalen_KMF_plots as akplt

'''This program loads a list of trained bootstrap model, calculate their cumulative hazard functions, and plot them.
Each figure represents n bootstrap models of a hazard.  The spread of the function nicely illustrates the variance
between the functions.
'''

#Load the pickled list of n bootstrap trained models
filename = 'AAF_100.p'
fileobject = open(filename, 'rb')
AAF_list_100 = pickle.load(fileobject)
fileobject.close()

#Pass the list to the following function to be plotted. 
akplt.plot_cum_haz_functions(AAF_list_100, 10)
