import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt



STROK = [3,13,65000,4,2307,3,13500,5,2,3,7,15,3,8421,2,5047,1246,3,2,994,2,4,4,50,2,25,200,10,2,8,16,20,26,9,160,10,4,2,150,4,84,5,41,100,35385,2,180,2878,2,8,11,3,2,1137,8976,2,3,7303,2,10,16,4,2,2,60,222,2,38638,8,5,27,50,3,5620,19824,240,882,1141,15,4,8,100,11510,4825,7,10,5,3,3,20,318,4,2,39,4,171,9,8,3,19,3,7,858,15,500,8895,40,9,6248,2778,3,500,6500,2540,114,2798,19,2028,2,858,100,1907,3,2100,4,17,17200,13535,50,6,29,812,12,4800,179491,3,83,49626,1000,19,15,347,6,17,50,100,6969,20,20,2,129,890,11,3,20,20,400,15887,6,100,5765,20065,1428,641,15,38,52743,54000,6911,15,15,3475,2,20,16,5,20,1660,1270,15,3,1901,6000,6,2753,9,5,8420,2960,400,10766,5,40,50,2938,6,8753,5,5764,18,3,10,7,36701,10,49468,15,200,20,15,9,1231,5000,500,2000,6,36,3500,24,2000,18672,900,20,200,250,1415,5,6000,2000,60,1000,193,500,120,2,35000,20,13611,3500,6531,2217,51707,14292,10,67,2,500,10,100,5,2,10,3741,300,10,500,200,11100,100,15844,50,10,300,1736,48319,300,6,5,400,6,3174,1000,50,47043,9158,8830,68000,30000,60528,3570,350,90,1929,2,40,8661,40,24800,100,8504,26673,3,20,15,61,2761,1983,2267,54134,60000,29932,8000,2,2020,1973,100,500,150,12824,173156,110,48,9917,3644,76170,5000,50090,2,2,4688,3612,60,9,26492,353,25782,9352,7,650,281,41904,100,25,15,24000,12,23238,4,5,4,6,1138,3,1000,800,1000,30667,20000,300,1000,2,18012,119,30285,2688,234,81074,5,80,200,5248,21000,5250,300,10,1000,82000,3500]


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
        '''
        farmTotal = np.sum(data['eldi']['Stock'].to_numpy())
        expected = ESCAPES_PER_TON*farmTotal*1000/EVENTS_PER_YEAR
        for i in range(numberOfEvents):
            number += np.random.exponential(expected)
        '''
        for i in range(numberOfEvents):
            number += np.random.choice(STROK, 1)[0]
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
