import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

## Hægt að breyta
@st.cache_data
def stofnstaerdir(ITERS):
    # Dregur stofnstærðarþróun áa fyrir ITERS ár út frá meðalstofnstærð og staðalfrávikum
    FjoldiAa = st.session_state['rivers'].shape
    temp = np.random.normal(0, 1, [FjoldiAa[0], ITERS])
    std = st.session_state['rivers']['std'].to_numpy()
    temp = np.multiply(temp, std[:, np.newaxis])
    stofnar = temp + st.session_state['rivers']['Meðalfjöldi'].to_numpy()[:, np.newaxis]
    stofnar = pd.DataFrame(stofnar).round(0).clip(lower=0)
    stofnar.index = st.session_state['rivers']['nafn']
    
    return stofnar.T



## Óþarfi að breyta
def plotStofnstaerdir(ax,stofnstaerdir, row, plotType, ITERS):
    # plottar fyrir valda á
    stofn = stofnstaerdir.copy()
    stofn.loc[:,'Heild'] = stofn.sum(numeric_only=True, axis=1)
    medaltal = stofn.loc[:,row].mean()
    if plotType == 'Tímalína':
        ax.plot(np.arange(0,ITERS),stofn.loc[:,row])
        ax.axhline(medaltal, color='r', linestyle='dashed', linewidth=1)
        ax.text(ITERS+ITERS/20,medaltal,'Meðaltal',rotation=0,color='r')
        ax.set_ylabel('Stofnstærð')
        ax.set_xlabel('Ár')
    else:
        ax.hist(stofn.loc[:,row] )#bins = round(medaltal/20))
        ax.axvline(medaltal, color='r', linestyle='dashed', linewidth=1)
        ax.text(medaltal+0.2,1,'Meðaltal',rotation=0,color='r',)
        ax.set_xlabel('Stofnstærð')
        ax.set_ylabel('Fjöldi ára')
    ax.set_title(f'Stofnstærð fyrir {row}')
    return ax