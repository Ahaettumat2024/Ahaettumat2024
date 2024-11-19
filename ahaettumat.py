import streamlit as st
import pandas as pd
import numpy as np
from utils.stofn import *
from utils.eldi import *
from utils.dreifing import *
from utils.gogn import *
import random
#st.set_page_config(layout="wide")

random.seed(0)
ITERS = 1000

## Setup
if 'rivers' not in st.session_state:
    st.session_state['rivers'] = getRivers()
if 'eldi' not in st.session_state:
    st.session_state['eldi'] = getFarms()
if 'settings' not in st.session_state:
    st.session_state['settings'] = getSetings()
if 'calc' not in st.session_state:
    st.session_state['calc'] = False

st.header('Áhættumat 2024')
tab1, tab2, tab3, tab4 = st.tabs(['Laxastofn', 'Strok', 'Dreifing', 'Niðurstaða'])

## Run calculation
if not st.session_state['calc']:
    stofnar = stofnstaerdir(ITERS)
    escSchedule = calcEscapeEvents(ITERS)
    farmEvents = splitEvents(escSchedule, ITERS)
    farmEventsEarly, farmEventsLate = splitFarmEvents(farmEvents,ITERS)
    farmNumbersEarly, farmNumbersLate = getSizeOfEvents(farmEventsEarly, farmEventsLate)
    farmEarlyReturns, farmLateReturns = getNumberOfReturners(farmNumbersEarly, farmNumbersLate, ITERS)
    results = getResults(stofnar, farmEarlyReturns, farmLateReturns, ITERS)
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
    st.session_state['calc'] = True

## Laxastofn
river = tab1.selectbox(
    "Veldu á",
    ['Heild'] + list( st.session_state['rivers']['nafn']),
)
riverPlotType = tab1.pills(
    "Tegund grafs",
    options=['Tímalína', 'Stuðlarit'],
    selection_mode="single",
    default = 'Tímalína'
)
f, ax = plt.subplots()
plotStofnstaerdir(ax, st.session_state['stofnar'], river, riverPlotType, ITERS)
tab1.pyplot(f)

## Strok
col31,col32 = tab2.columns([3, 1])
eldismagn = col32.expander('Eldismagn')
poisson = col32.expander('Meðaltímalengd milli atburða')
staerd = col32.expander('Stærð atburða')
eldisstudlar = col32.expander('Eldisstuðlar')

col311, col312, col313 = col31.columns([1, 1, 1])

for eldisIdx in st.session_state['eldi'].index:
    row = st.session_state['eldi'].iloc[eldisIdx]
    eldismagn.slider(row['Nafn'], 0.0, row['max'], row['Stock'], step = 0.5, key = row['Stytting'], on_change=updateEldi, args=(row['Stytting'],))

col311.metric('Meðalfjöldi atburða á ári',  st.session_state['escSchedule'].mean())
col312.metric('Meðalfjöldi stroka á ári', round(( st.session_state['farmNumbersEarly'].to_numpy().sum()+ st.session_state['farmNumbersLate'].to_numpy().sum())/1000))
col313.metric('Strok per þús. tonn', round(( st.session_state['farmNumbersEarly'].to_numpy().sum()+ st.session_state['farmNumbersLate'].to_numpy().sum())/(1000*1000*st.session_state['eldi'].loc[:,'Stock'].sum()),1))

f2, ax2 = plt.subplots()
eldi = col31.selectbox(
    "Veldu eldisstað",
    ['Heild'] + list( st.session_state['eldi']['Nafn']),
)
eldiPlotType = col31.pills(
    "Graf",
    options=['Atburðir', 'Strokfjöldi', 'Endurkomulaxar'],
    selection_mode="single",
    default = 'Atburðir'
)
ax2 = plotEldi(ax2, eldi, eldiPlotType, st.session_state['farmEventsEarly'], st.session_state['farmEventsLate'], st.session_state['farmNumbersEarly'], st.session_state['farmNumbersLate'], st.session_state['farmEarlyReturns'], st.session_state['farmLateReturns'])
col31.pyplot(f2)

## Dreifing

f3, ax3 = plt.subplots()
eldi2 = tab3.selectbox(
    "Veldu eldisstað",
    list( st.session_state['eldi']['Nafn']),
    key = 'eldi2'
)
dreifingPlotType = tab3.pills(
    "Graf",
    options=['Snemmbúnir', 'Síðbúnir'],
    selection_mode="single",
    default = 'Snemmbúnir'
)
plotDistribution(ax3, dreifingPlotType, eldi2)
tab3.pyplot(f3)



## Niðurstaða
f4, ax4 = plt.subplots()
river2 = tab4.selectbox(
    "Veldu á",
    ['Heild'] + list( st.session_state['rivers']['nafn']),
    key = 'river2'
)
plotResult(ax4, river2, st.session_state['results'])
tab4.pyplot(f4)