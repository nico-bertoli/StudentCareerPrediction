from __future__ import print_function
from tpot import  TPOTClassifier

from sklearn.model_selection import train_test_split
import sys,tempfile, urllib, os

#   cose di base
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

#grafici
import seaborn

import sklearn
# matrice di confusione
from sklearn.metrics import confusion_matrix, accuracy_score

#gestione date
import datetime
from datetime import datetime

#ignoro i warnings
import warnings
warnings.filterwarnings("ignore")

#voglio che mi vengano stampate sempre tutte le colonne della tabella
pd.options.display.max_columns = None
# pd.set_option('display.max_columns', 500)

import lime
import lime.lime_tabular

from sklearn.model_selection import cross_val_score

import tensorflow as tf