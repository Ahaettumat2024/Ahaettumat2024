import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

## Hægt að breyta
def stofnstaerdir(data, ITERS):
    stofnar = pd.DataFrame([])
    for i in range(ITERS):
        year = np.random.lognormal(data['rivers']['logMedal10'].to_numpy(), data['rivers']['std'].to_numpy())
        stofnar[i] = year
    stofnar = pd.DataFrame(stofnar).round(0).clip(lower=0)
    stofnar.index = data['rivers']['nafn']
    return stofnar.T




## Óþarfi að breyta
def plotStofnstaerdir(ax,stofnstaerdir, row, plotType, ITERS):
    # plottar fyrir valda á
    stofn = stofnstaerdir.copy()
    stofn.loc[:,'Total'] = stofn.sum(numeric_only=True, axis=1)
    medaltal = stofn.loc[:,row].median()
    if plotType == 'Timeline':
        ax.plot(np.arange(0,ITERS),stofn.loc[:,row])
        ax.axhline(medaltal, color='r', linestyle='dashed', linewidth=1, label='Average: '+str(round(medaltal)))
        ax.legend()
        ax.set_ylabel('Stock size')
        ax.set_xlabel('Year')
    else:
        ax.hist(stofn.loc[:,row] )#bins = round(medaltal/20))
        ax.axvline(medaltal, color='r', linestyle='dashed', linewidth=1, label='Average: '+str(round(medaltal)))
        ax.legend()
        ax.set_xlabel('Stock size')
        ax.set_ylabel('Number of years')
    ax.set_title(f'Stock size of {row}')
    return ax
