import pandas as pd



def getRivers():
    rivers = pd.read_csv('./data/ar.csv')
    if 'std' not in rivers.columns:
        rivers['std'] = 10
    rivers.sort_values(by=['fjarlægð'],inplace=True)
    return rivers

def getFarms():
    farms = pd.read_csv('./data/eldisstadir.csv')
    farms.sort_values(by=['staðsetning'],inplace=True)
    return farms

def getSetings():
    return None