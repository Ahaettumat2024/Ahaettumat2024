
import streamlit as st
import pandas as pd
import numpy as np
from utils.stofn import *
from utils.eldi import *
from utils.dreifing import *
from utils.gogn import *
import random
st.set_page_config(layout="wide")

random.seed(0)
ITERS = 2500

SAFN_VESTUR_SIZE = 1
SAFN_AUSTUR_SIZE = 1

EVENTS_PER_YEAR = 1.75 # Average number of escape events per year
SIZE_PROPORTION = 0.67 # Proportion of Early vs Late escapees
ESCAPES_PER_TON = 0.5 # Amount of escapees per 1000 ton

LATE_RETURNS_PROP = 0.0016 # Proportion of Late escapees that return to rivers (0.16%)
EARLY_RETURNS_PROP = 0.0007 # Proportion of Early escapees that return to rivers (0.07%)
EARLY_YEARLY_DISTR = [0, 30/56, 17/56, 9/56] # Early returns distributed over four years

LATE_PROPORTION = 0.2
LATE_LENGTH = 240

EARLY_PROPORTION = 0.5
EARLY_LENGTH = 140

## Setup
if 'rivers' not in st.session_state:
    st.session_state['rivers'] = getRivers()
if 'eldi' not in st.session_state:
    st.session_state['eldi'] = getFarms()
if 'distances' not in st.session_state:
    st.session_state['distances'] = getDistances()
if 'calc' not in st.session_state:
    st.session_state['calc'] = False

st.header('GIRAF 2025')
tab1, tab2, tab3, tab4 = st.tabs(['Salmon stocks', 'Escape events', 'Distribution', 'Results'])

## Run calculation
if not st.session_state['calc']:
    if SAFN_VESTUR_SIZE > 1:
        st.session_state['rivers'].loc[st.session_state['rivers']['nafn']=='Safn Vestur','logMedal10']= np.log(SAFN_VESTUR_SIZE)
        st.session_state['rivers'].loc[st.session_state['rivers']['nafn']=='Safn Vestur','expMedal10']= SAFN_VESTUR_SIZE
    if SAFN_AUSTUR_SIZE > 1:
        st.session_state['rivers'].loc[st.session_state['rivers']['nafn']=='Safn Austur','logMedal10'] = np.log(SAFN_AUSTUR_SIZE)
        st.session_state['rivers'].loc[st.session_state['rivers']['nafn']=='Safn Austur','expMedal10'] = SAFN_AUSTUR_SIZE
    stofnar = stofnstaerdir(st.session_state,ITERS)
    escSchedule = calcEscapeEvents(st.session_state,ITERS, EVENTS_PER_YEAR)
    farmEvents = splitEvents(st.session_state,escSchedule, ITERS)
    farmEventsEarly, farmEventsLate = splitFarmEvents(st.session_state,farmEvents,ITERS,SIZE_PROPORTION)
    farmNumbersEarly, farmNumbersLate = getSizeOfEvents(st.session_state,farmEventsEarly, farmEventsLate, ESCAPES_PER_TON, EVENTS_PER_YEAR)
    farmEarlyReturns, farmLateReturns = getNumberOfReturners(st.session_state,farmNumbersEarly, farmNumbersLate, ITERS, LATE_RETURNS_PROP, EARLY_RETURNS_PROP, EARLY_YEARLY_DISTR)
    results = getResults(st.session_state,stofnar, farmEarlyReturns, farmLateReturns, ITERS,LATE_PROPORTION,EARLY_PROPORTION,LATE_LENGTH,EARLY_LENGTH )
    results[0].drop(columns=['Safn Austur','Safn Vestur'],inplace=True)
    results[1].drop(columns=['Safn Austur','Safn Vestur'],inplace=True)
    st.session_state['stofnar'] = stofnar
    st.session_state['escSchedule'] = escSchedule
    st.session_state['farmEvents'] = farmEvents
    st.session_state['farmEventsEarly'] = farmEventsEarly
    st.session_state['farmEventsLate'] = farmEventsLate
    st.session_state['farmNumbersEarly'] = farmNumbersEarly
    st.session_state['farmNumbersLate'] = farmNumbersLate
    st.session_state['farmEarlyReturns'] = farmEarlyReturns
    st.session_state['farmLateReturns'] = farmLateReturns
    st.session_state['results'] = results

## Laxastofn
river = tab1.selectbox(
    "Select a river",
    ['Total'] + list( st.session_state['rivers']['nafn']),
)
riverPlotType = tab1.pills(
    "Type of plot",
    options=['Timeline', 'Histogram'],
    selection_mode="single",
    default = 'Timeline'
)
f, ax = plt.subplots()
plotStofnstaerdir(ax, st.session_state['stofnar'], river, riverPlotType, ITERS)
tab1.pyplot(f)

## Strok
col31,col32 = tab2.columns([3, 1])
eldismagn = col32.expander('Farm sizes')

col311, col312, col313 = col31.columns([1, 1, 1])

for eldisIdx in st.session_state['eldi'].index:
    row = st.session_state['eldi'].iloc[eldisIdx]
    eldismagn.metric(row['Nafn'], row['Stock'])

col311.metric('Average number of events per year',  st.session_state['escSchedule'].mean())
col312.metric('Average escapes per year', round(( st.session_state['farmNumbersEarly'].to_numpy().sum()+ st.session_state['farmNumbersLate'].to_numpy().sum())/ITERS))
col313.metric('Escapes per 1000 tons', round(( st.session_state['farmNumbersEarly'].to_numpy().sum()+ st.session_state['farmNumbersLate'].to_numpy().sum())/(ITERS*ITERS*st.session_state['eldi'].loc[:,'Stock'].sum()),1))

f2, ax2 = plt.subplots()
eldi = col31.selectbox(
    "Select a farm",
    ['Total'] + list( st.session_state['eldi']['Nafn']),
)
eldiPlotType = col31.pills(
    "Plot",
    options=['Events', 'Escape numbers', 'Returners'],
    selection_mode="single",
    default = 'Events'
)
ax2 = plotEldi(ax2, eldi, eldiPlotType, st.session_state['farmEventsEarly'], st.session_state['farmEventsLate'], st.session_state['farmNumbersEarly'], st.session_state['farmNumbersLate'], st.session_state['farmEarlyReturns'], st.session_state['farmLateReturns'])
col31.pyplot(f2)

## Dreifing

f3, ax3 = plt.subplots()
eldi2 = tab3.selectbox(
    "Select a farm",
    list( st.session_state['eldi']['Nafn']),
    key = 'eldi2'
)
dreifingPlotType = tab3.pills(
    "Plot",
    options=['Early', 'Late'],
    selection_mode="single",
    default = 'Early'
)
plotDistribution(st.session_state, ax3, dreifingPlotType, eldi2,LATE_PROPORTION,LATE_LENGTH,EARLY_PROPORTION,EARLY_LENGTH)
tab3.pyplot(f3)



## Niðurstaða
f4, ax4 = plt.subplots(figsize=[11,6])
river2 = tab4.selectbox(
    "Select a river",
    ['Total'] + list( st.session_state['rivers']['nafn']),
    key = 'river2'
)
if river2 == 'Total':
    resultPlotType = tab4.pills(
        "Plot",
        options=['Average', 'Percentage of years over 4%', 'Percentage of  3 years over 4%'],
        selection_mode="single",
        default = 'Average'
    )
else:
    resultPlotType = 'Average'
    tab4.metric('Percentage of years over 4%',  (results[0].loc[:,river2]>4).mean()*100)
    tab4.metric('Percentage of  3 years over 4%', (results[1].loc[:,river2]>4).mean()*100)


plotResult(ax4, river2, resultPlotType, st.session_state['results'])
tab4.pyplot(f4)
