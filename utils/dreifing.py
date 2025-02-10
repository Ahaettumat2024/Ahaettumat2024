import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


LATE_PROPORTION = 0.2
LATE_LENGTH = 240
LATE_LENGTH_2 = LATE_LENGTH*(1-LATE_PROPORTION)/LATE_PROPORTION

EARLY_PROPORTION = 0.5
EARLY_LENGTH = 140
EARLY_LENGTH_2 = EARLY_LENGTH*(1-EARLY_PROPORTION)/EARLY_PROPORTION

def lateDistribution(x):
    # Reiknar dreifingu síbúinna stokulaxa
    if x > 0:
        return np.exp(-(x/LATE_LENGTH_2)**2)
    else:
        return np.exp(-(x/LATE_LENGTH)**2)
    
def earlyDistribution(x):
    # Reiknar dreifingu snemmbúinna stokulaxa
    if x > 0:
        return np.exp(-(x/EARLY_LENGTH_2)**2)
    else:
        return np.exp(-(x/EARLY_LENGTH)**2)

@st.cache_data
def getEarlyFarmedDistribution(farmNo):
    farmName = st.session_state['eldi'].loc[farmNo,'Stytting']
    distances = st.session_state['distances'][farmName]

    distancesProb = distances.map(earlyDistribution).to_numpy()
    stofnstaerdirProb = np.sqrt(st.session_state['rivers']['expMedal10'].to_numpy())
    stofnstaerdirProb = stofnstaerdirProb/np.max(stofnstaerdirProb)

    distribution = distancesProb*stofnstaerdirProb
    distribution = distribution/np.sum(distribution)
    return distribution

@st.cache_data
def getLateFarmedDistribution(farmNo):
    # Reiknar hlutfall síbúinna stokulaxa sem fer í hverja á 
    farmName = st.session_state['eldi'].loc[farmNo,'Stytting']
    distances = st.session_state['distances'][farmName]

    distancesProb = distances.map(lateDistribution).to_numpy()
    distancesProb = distancesProb/np.max(distancesProb)
    stofnstaerdirProb = np.sqrt(st.session_state['rivers']['expMedal10'].to_numpy())
    stofnstaerdirProb = stofnstaerdirProb/np.max(stofnstaerdirProb)

    distribution = distancesProb*stofnstaerdirProb
    distribution = distribution/np.sum(distribution)
    return distribution

@st.cache_data
def getResults(stofnstaerdir, farmEarlyReturns, farmLateReturns, ITERS):
    # Reiknar niðurstöður
    stofn = stofnstaerdir.copy()
    results = stofn.copy()
    for i in farmEarlyReturns.index:
        print(i)
        for j in farmEarlyReturns.columns:
            if farmEarlyReturns.loc[i,j] > 0:
                results.loc[i] += farmEarlyReturns.loc[i,j]*getEarlyFarmedDistribution(j)
            if farmLateReturns.loc[i,j] > 0:
                results.loc[i] += farmLateReturns.loc[i,j]*getLateFarmedDistribution(j)
        results.loc[i,:] = 100*(results.loc[i,:].to_numpy()-stofn.loc[i,:].to_numpy())/(results.loc[i,:].clip(lower = 1)).to_numpy()
    return results

## Oþarfi að breyta
def plotDistribution(ax, type, farm):
    # Plottar dreyfingu
    farmDict = pd.Series(st.session_state['eldi'].index, index=st.session_state['eldi']['Nafn'].values).to_dict()
    farmNo = farmDict[farm]
    if type == 'Snemmbúnir':
        distribution = getEarlyFarmedDistribution(farmNo)
    else:
        distribution = getLateFarmedDistribution(farmNo)

    ax.bar(st.session_state['rivers']['nafn'], distribution)
    ax.set_xticks(ax.get_xticks())
    ax.set_xticklabels(st.session_state['rivers']['nafn'], rotation=90, ha='right',fontsize=5)
    return ax

def plotResult(ax, river, results):
    if river == 'Heild':
        results = results.mean(axis=0)
        ax.bar(results.index, results)
        ax.axhline(4, color='r', linestyle='dashed', linewidth=1)
        ax.set_title('Meðalhlutfall eldislaxa í á')
        ax.set_ylabel('Meðalhlutfall')
        ax.set_xticks(ax.get_xticks())
        ax.set_xticklabels(results.index, rotation=90, ha='right',fontsize=5)
    else:
        ax.hist(results.loc[:,river])
        ax.axvline(results.loc[:,river].mean(), color='g', linestyle='dashed', linewidth=1)
        ax.axvline(4, color='r', linestyle='dashed', linewidth=1)
        ax.text(results.loc[:,river].mean()+0.05,1,'Meðaltal',rotation=0,color='g')
        ax.set_title(f'Hlutfall eldislaxa í {river}')
        ax.set_xlabel('Hlutfall')
        ax.set_ylabel('Fjöldi ára')
    return ax
