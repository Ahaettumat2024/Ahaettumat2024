import pandas as pd



def getRivers():
    rivers = pd.read_csv('./data/ar.csv')
    if 'std' not in rivers.columns:
        rivers['std'] = 10
    return rivers

def getFarms():
    farms = pd.read_csv('./data/eldisstadir.csv')
    return farms

def getSetings():
    return None