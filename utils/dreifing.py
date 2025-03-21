import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt





def lateDistribution(x,LATE_PROPORTION,LATE_LENGTH):
    # Reiknar dreifingu síbúinna stokulaxa
    LATE_LENGTH_2 = LATE_LENGTH*(1-LATE_PROPORTION)/LATE_PROPORTION
    if x > 0:
        return np.exp(-(x/LATE_LENGTH_2)**2)
    else:
        return np.exp(-(x/LATE_LENGTH)**2)
    
def earlyDistribution(x,EARLY_PROPORTION,EARLY_LENGTH):
    EARLY_LENGTH_2 = EARLY_LENGTH*(1-EARLY_PROPORTION)/EARLY_PROPORTION
    # Reiknar dreifingu snemmbúinna stokulaxa
    if x > 0:
        return np.exp(-(x/EARLY_LENGTH_2)**2)
    else:
        return np.exp(-(x/EARLY_LENGTH)**2)


def getEarlyFarmedDistribution(data,farmNo,EARLY_PROPORTION,EARLY_LENGTH):
    farmName = data['eldi'].loc[farmNo,'Stytting']
    distances = data['distances'][farmName]

    distancesProb = distances.apply(lambda x: earlyDistribution(x, EARLY_PROPORTION,EARLY_LENGTH)).to_numpy()
    stofnstaerdirProb = np.sqrt(data['rivers']['expMedal10'].to_numpy())
    stofnstaerdirProb = stofnstaerdirProb/np.max(stofnstaerdirProb)

    distribution = distancesProb*stofnstaerdirProb
    distribution = distribution/np.sum(distribution)
    return distribution

def getEarlyFarmedDistributionNumbers(data,farmNo, amount,EARLY_PROPORTION,EARLY_LENGTH):
    distribution = getEarlyFarmedDistribution(data,farmNo,EARLY_PROPORTION,EARLY_LENGTH)
    draws = np.random.choice(len(distribution), size=amount, p=distribution)
    counts = np.bincount(draws, minlength=len(distribution))
    return counts


def getLateFarmedDistribution(data,farmNo,LATE_PROPORTION,LATE_LENGTH):
    # Reiknar hlutfall síbúinna stokulaxa sem fer í hverja á 
    farmName = data['eldi'].loc[farmNo,'Stytting']
    distances = data['distances'][farmName]

    distancesProb = distances.apply(lambda x: lateDistribution(x, LATE_PROPORTION,LATE_LENGTH)).to_numpy()
    stofnstaerdirProb = np.sqrt(data['rivers']['expMedal10'].to_numpy())
    stofnstaerdirProb = stofnstaerdirProb/np.max(stofnstaerdirProb)

    distribution = distancesProb*stofnstaerdirProb
    distribution = distribution/np.sum(distribution)
    return distribution

def getLateFarmedDistributionNumbers(data,farmNo, amount,LATE_PROPORTION,LATE_LENGTH):
    distribution = getLateFarmedDistribution(data,farmNo,LATE_PROPORTION,LATE_LENGTH)
    draws = np.random.choice(len(distribution), size=amount, p=distribution)
    counts = np.bincount(draws, minlength=len(distribution))
    return counts

def getResults(data, stofnstaerdir, farmEarlyReturns, farmLateReturns, ITERS,LATE_PROPORTION,EARLY_PROPORTION,LATE_LENGTH,EARLY_LENGTH ):
    # Reiknar niðurstöður
    stofn = stofnstaerdir.copy()
    stofn3 = stofnstaerdir.copy()
    results = stofn.copy()
    for i in farmEarlyReturns.index:
        for j in farmEarlyReturns.columns:
            if farmEarlyReturns.loc[i,j] > 0:
                results.loc[i] += getEarlyFarmedDistributionNumbers(data,j, farmEarlyReturns.loc[i,j],EARLY_PROPORTION,EARLY_LENGTH)
            if farmLateReturns.loc[i,j] > 0:
                results.loc[i] += getLateFarmedDistributionNumbers(data,j, farmLateReturns.loc[i,j],LATE_PROPORTION,LATE_LENGTH)

    results3 = results.copy().rolling(3).sum()
    stofn3 = stofn.copy().rolling(3).sum()
    for i in results.index:
        results.loc[i,:] = 100*(results.loc[i,:].to_numpy()-stofn.loc[i,:].to_numpy())/(results.loc[i,:].clip(lower = 1)).to_numpy()
    for i in results3.index:
        results3.loc[i,:] = 100*(results3.loc[i,:].to_numpy()-stofn3.loc[i,:].to_numpy())/(results3.loc[i,:].clip(lower = 1)).to_numpy()
    return [results, results3]

def getSplitResults(data, stofnstaerdir, farmEarlyReturns, farmLateReturns, ITERS,LATE_PROPORTION,EARLY_PROPORTION,LATE_LENGTH,EARLY_LENGTH):
    # Reiknar niðurstöður
    stofn = stofnstaerdir.copy()
    stofn3 = stofnstaerdir.copy()
    results = pd.DataFrame(0, index=stofn.columns, columns=farmEarlyReturns.columns)
    for i in farmEarlyReturns.index:
        for j in farmEarlyReturns.columns:
            if farmEarlyReturns.loc[i,j] > 0:
                results.loc[:,j] += getEarlyFarmedDistributionNumbers(data,j, farmEarlyReturns.loc[i,j],EARLY_PROPORTION,EARLY_LENGTH)/ITERS
            if farmLateReturns.loc[i,j] > 0:
                results.loc[:,j] += getLateFarmedDistributionNumbers(data,j, farmLateReturns.loc[i,j],LATE_PROPORTION,LATE_LENGTH)/ITERS
    return results


## Oþarfi að breyta
def plotDistribution(data, ax, type, farm,LATE_PROPORTION,LATE_LENGTH,EARLY_PROPORTION,EARLY_LENGTH):
    # Plottar dreyfingu
    farmDict = pd.Series(st.session_state['eldi'].index, index=st.session_state['eldi']['Nafn'].values).to_dict()
    farmNo = farmDict[farm]
    if type == 'Early':
        distribution = getEarlyFarmedDistribution(data, farmNo,EARLY_PROPORTION,EARLY_LENGTH)
    else:
        distribution = getLateFarmedDistribution(data, farmNo,LATE_PROPORTION,LATE_LENGTH)

    ax.bar(st.session_state['rivers']['nafn'][distribution>0.0001], distribution[distribution>0.0001])
    ax.set_xticks(ax.get_xticks())
    ax.set_xticklabels(st.session_state['rivers']['nafn'].loc[distribution>0.0001], rotation=45, ha='right',fontsize=3.5)
    return ax

def plotResult(ax, river, type, results):
    if river == 'Total':
        if type == 'Average':
            resultsT = results[0].mean(axis=0)
            ax.bar(resultsT.index, resultsT)
            ax.axhline(4, color='r', linestyle='dashed', linewidth=1)
            ax.set_title('Average percentage of farmed salmon in river')
            ax.set_ylabel('Average percent')
            ax.set_xticks(ax.get_xticks())
            ax.set_xticklabels(resultsT.index, rotation=45, ha='right',fontsize=3.5)
        elif type == 'Percentage of years over 4%':
            resultsT = ((results[0]>4)*1).mean(axis=0)*100
            ax.axhline(5, color='r', linestyle='dashed', linewidth=1)
            ax.bar(resultsT.index, resultsT)
            ax.set_title('Percentage of years over 4%')
            ax.set_ylabel('Average percent')
            ax.set_xticks(ax.get_xticks())
            ax.set_xticklabels(resultsT.index, rotation=45, ha='right',fontsize=3.5)
        else:
            resultsT = ((results[1]>4)*1).mean(axis=0)*100
            ax.bar(resultsT.index, resultsT)
            ax.set_title('Percentage of 3-year averages over 4%')
            ax.axhline(5, color='r', linestyle='dashed', linewidth=1)
            ax.set_ylabel('Average percent')
            ax.set_xticks(ax.get_xticks())
            ax.set_xticklabels(resultsT.index, rotation=45, ha='right',fontsize=3.5)
        
    else:
        ax.hist(results[0].loc[:,river])
        ax.axvline(results[0].loc[:,river].mean(), color='g', linestyle='dashed', linewidth=1, label='Average: '+str(round(results.loc[:,river].mean(),2)))
        ax.axvline(4, color='r', linestyle='dashed', linewidth=1)
        ax.legend(loc='upper right')
        ax.set_title(f'Proportion of farmed salmons in {river}')
        ax.set_xlabel('Proportion')
        ax.set_ylabel('Number of years')
    return ax
