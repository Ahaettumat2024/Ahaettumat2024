import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


EVENTS_PER_YEAR = 1.75 # Average number of escape events per year
SIZE_PROPORTION = 0.67 # Proportion of Early vs Late escapees
ESCAPES_PER_TON = 0.5 # Amount of escapees per 1000 ton

LATE_RETURNS_PROP = 0.0018 # Proportion of Late escapees that return to rivers
EARLY_RETURNS_PROP = 0.0018 # Proportion of Early escapees that return to rivers
EARLY_YEARLY_DISTR = [0, 30/56, 17/56, 9/56] # Early returns distributed over four years



## Hægt að breyta
#@st.cache_data
def calcEscapeEvents(ITERS):
    # Number of events for ITERS years
    escSchedule = np.random.poisson(EVENTS_PER_YEAR, ITERS)
    return escSchedule

#@st.cache_data
def splitEvents(escSchedule, ITERS):
    # Divides events down to farm sites based on production
    farmNumbers = st.session_state['eldi'].index.to_numpy()
    stocks = st.session_state['eldi']['Stock'].to_numpy()
    stocksProbabilities = stocks/np.sum(stocks)
    farmEvents = pd.DataFrame(0, index=np.arange(ITERS), columns=farmNumbers)
    for i in range(ITERS):
        for j in range(escSchedule[i]):
            farm = np.random.choice(farmNumbers,p=stocksProbabilities)
            farmEvents.loc[i,farm] += 1
    return farmEvents

#@st.cache_data
def splitFarmEvents(farmEvents,ITERS):
    # Splits events into early / late

    farmEventsEarly, farmEventsLate = pd.DataFrame(0, index=np.arange(ITERS), columns=farmEvents.columns), pd.DataFrame(0, index=np.arange(ITERS), columns=farmEvents.columns)
    for i in range(ITERS):
        for farm in farmEvents.columns:
            for j in range(farmEvents.loc[i,farm]):
                if np.random.uniform(0,1) > SIZE_PROPORTION:
                    farmEventsLate.loc[i,farm] += 1
                else:
                    farmEventsEarly.loc[i,farm] += 1
    return farmEventsEarly, farmEventsLate

#@st.cache_data
def getSizeOfEvents(farmEventsEarly, farmEventsLate):
    # Calculates size of events
    def getSizeOfEvents(numberOfEvents):
        # A random function that returns size of events based on number of events
        number = 0
        farmTotal = np.sum(st.session_state['eldi']['Stock'].to_numpy())
        expected = ESCAPES_PER_TON*farmTotal*1000/EVENTS_PER_YEAR
        for i in range(numberOfEvents):
            number += np.random.exponential(expected)
        return number
    

    farmNumbersEarly = farmEventsEarly.map(getSizeOfEvents)
    farmNumbersLate = farmEventsLate.map(getSizeOfEvents)

    return farmNumbersEarly, farmNumbersLate

#@st.cache_data
def getNumberOfReturners(farmNumbersEarly, farmNumbersLate, ITERS):
    farmEarlyReturns = pd.DataFrame(0, index=np.arange(ITERS), columns=farmNumbersEarly.columns)
    farmLateReturns = farmNumbersLate.map(lambda x: round(x*LATE_RETURNS_PROP))
    # Calculates number of returners
    for i in range(ITERS):
        for farm in farmNumbersEarly.columns:
            for j in range(len(EARLY_YEARLY_DISTR)):
                if i+j < ITERS:
                    farmEarlyReturns.loc[i+j,farm] += round(farmNumbersEarly.loc[i,farm]*EARLY_RETURNS_PROP*EARLY_YEARLY_DISTR[j])

    return farmEarlyReturns, farmLateReturns

## Óþarfi að breyta
def updateEldi(key):
    st.session_state['eldi'].loc[st.session_state['eldi']['Stytting'] == key, 'Stock'] = st.session_state[key]

def plotEldi(ax, farm, plotType,farmEventsEarly, farmEventsLate,farmNumbersEarly, farmNumbersLate,farmEarlyReturns, farmLateReturns):
    if farm == 'Total':
        if plotType == 'Events':
            ax.bar(farmEventsEarly.iloc[0:100].index, farmEventsEarly.sum(axis=1).iloc[0:100], label='Early')
            ax.bar(farmEventsLate.iloc[0:100].index, farmEventsLate.sum(axis=1).iloc[0:100], bottom = farmEventsEarly.sum(axis=1).iloc[0:100], label='Late')
            ax.set_ylabel('Number of events')
        elif plotType == 'Escape numbers':
            ax.bar(farmNumbersEarly.iloc[0:100].index, farmNumbersEarly.sum(axis=1).iloc[0:100], label='Early')
            ax.bar(farmNumbersLate.iloc[0:100].index, farmNumbersLate.sum(axis=1).iloc[0:100], bottom = farmNumbersEarly.sum(axis=1).iloc[0:100], label='Late')
            ax.set_ylabel('Number of escapees')
        else:
            ax.bar(farmEarlyReturns.iloc[0:100].index, farmEarlyReturns.sum(axis=1).iloc[0:100], label='Early')
            ax.bar(farmLateReturns.iloc[0:100].index, farmLateReturns.sum(axis=1).iloc[0:100], bottom = farmEarlyReturns.sum(axis=1).iloc[0:100], label='Late')
            ax.set_ylabel('Number of returners')
    else:
        farmDict = pd.Series(st.session_state['eldi'].index, index=st.session_state['eldi']['Nafn'].values).to_dict()
        farmNo = farmDict[farm]

        if plotType == 'Events':
            ax.bar(farmEventsEarly.iloc[0:100].index, farmEventsEarly.iloc[0:100][farmNo], label='Early')
            ax.bar(farmEventsLate.iloc[0:100].index, farmEventsLate.iloc[0:100][farmNo], bottom = farmEventsEarly.iloc[0:100][farmNo], label='Late')
            ax.set_ylabel('Number of events')
        elif plotType == 'Escape numbers':
            ax.bar(farmNumbersEarly.iloc[0:100].index, farmNumbersEarly.iloc[0:100][farmNo], label='Early')
            ax.bar(farmNumbersLate.iloc[0:100].index, farmNumbersLate.iloc[0:100][farmNo], bottom = farmNumbersEarly.iloc[0:100][farmNo], label='Late')
            ax.set_ylabel('Number of escapees')
        else:
            ax.bar(farmEarlyReturns.iloc[0:100].index, farmEarlyReturns.iloc[0:100][farmNo], label='Early')
            ax.bar(farmLateReturns.iloc[0:100].index, farmLateReturns.iloc[0:100][farmNo], bottom = farmEarlyReturns.iloc[0:100][farmNo], label='Late')
            ax.set_ylabel('Number of returners')
    ax.legend()
    ax.set_title(f'{plotType} the first 100 years')
    ax.set_xlabel('Year')
    return ax
