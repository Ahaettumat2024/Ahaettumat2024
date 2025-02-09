import pandas as pd



def getRivers():
    rivers = pd.read_csv('./data/ahaetta.csv', sep=';', decimal=',')                 
    rivers = rivers[rivers.ath != 'ut']
    if 'std' not in rivers.columns:
        rivers['std'] = 0.5
    rivers.sort_values(by=['fjarlægð'],inplace=True)

    return rivers

def getFarms():
    farms = pd.read_csv('./data/eldisstadir.csv')
    farms.sort_values(by=['staðsetning'],inplace=True)
    return farms

def getDistances():
    distances = pd.read_csv('./data/distances.csv')
    distances.sort_values(by=['Arn'],inplace=True)
    rivers = getRivers()
    distances.index = rivers['nafn']
    return distances
