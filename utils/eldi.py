import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt






## Hægt að breyta
def calcEscapeEvents(data,ITERS, EVENTS_PER_YEAR):
    # Reiknar fjölda atburða per ár ITERS ár
    escSchedule = np.random.poisson(EVENTS_PER_YEAR, ITERS)
    return escSchedule

def splitEvents(data,escSchedule, ITERS):
    # Skiptir atburðum niður á eldisstaði eftir eldismagni
    farmNumbers = data['eldi'].index.to_numpy()
    stocks = data['eldi']['Stock'].to_numpy()
    stocksProbabilities = stocks/np.sum(stocks)
    farmEvents = pd.DataFrame(0, index=np.arange(ITERS), columns=farmNumbers)
    for i in range(ITERS):
        for j in range(escSchedule[i]):
            farm = np.random.choice(farmNumbers,p=stocksProbabilities)
            farmEvents.loc[i,farm] += 1
    return farmEvents

def splitFarmEvents(data,farmEvents,ITERS, SIZE_PROPORTION):
    # Skiptir atburðum niður eftir stærð stokulaxa

    farmEventsEarly, farmEventsLate = pd.DataFrame(0, index=np.arange(ITERS), columns=farmEvents.columns), pd.DataFrame(0, index=np.arange(ITERS), columns=farmEvents.columns)
    for i in range(ITERS):
        for farm in farmEvents.columns:
            for j in range(farmEvents.loc[i,farm]):
                if np.random.uniform(0,1) > SIZE_PROPORTION:
                    farmEventsLate.loc[i,farm] += 1
                else:
                    farmEventsEarly.loc[i,farm] += 1
    return farmEventsEarly, farmEventsLate

def getSizeOfEvents(data,farmEventsEarly, farmEventsLate, ESCAPES_PER_TON, EVENTS_PER_YEAR):
    # Reiknar meðalstærð atburða á eldisstað
    def getSizeOfEvents(numberOfEvents):
        # slembifall sem gefur stærð strokatburðar
        number = 0
        farmTotal = np.sum(data['eldi']['Stock'].to_numpy())
        expected = ESCAPES_PER_TON*farmTotal*1000/EVENTS_PER_YEAR
        for i in range(numberOfEvents):
            number += np.random.exponential(expected)
        return number
    

    farmNumbersEarly = farmEventsEarly.map(getSizeOfEvents)
    farmNumbersLate = farmEventsLate.map(getSizeOfEvents)

    return farmNumbersEarly, farmNumbersLate


def getNumberOfReturners(data,farmNumbersEarly, farmNumbersLate, ITERS, LATE_RETURNS_PROP, EARLY_RETURNS_PROP, EARLY_YEARLY_DISTR):
    farmEarlyReturns = pd.DataFrame(0, index=np.arange(ITERS), columns=farmNumbersEarly.columns)
    farmLateReturns = farmNumbersLate.map(lambda x: round(x*LATE_RETURNS_PROP))
    # Reiknar fjölda stokulaxa
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
