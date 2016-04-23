import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import pickle
import Aalen_KMF_plots as akplt



filename = 'cleaned_dataset.p'
fileobject = open(filename, 'rb')
donor_dataset= pickle.load(fileobject)
fileobject.close()

akplt.plot_Kaplan_Meier_overall(donor_dataset)
akplt.plot_Kaplan_Meier_feature(donor_dataset)
