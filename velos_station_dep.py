# -*- coding: utf-8 -*-
"""
Created on Wed Feb  5 15:30:05 2020

@author: wassim
"""
from pandas import DataFrame
from xml.etree.cElementTree import iterparse

file = 'generated_bicycle_input.xml'

# get an iterable and turn it into an iterator
context = iter(iterparse(file, events=("start", "end")))

# get the root element
event, root = next(context)

listdep=[]
for event, elem in context:
    if event == "end" and elem.tag == "trip":
        idtrip = elem.attrib['from']
        listdep.append(idtrip)
        root.clear()
        
len(set(listdep))


if not ('bounds' in locals() or 'bounds' in globals()):
    global bounds
    global bound_inf
    global bound_sup
    bounds = net.getBBoxXY()
    bound_inf = net.convertXY2LonLat(bounds[0][0],bounds[0][1])
    bound_sup = net.convertXY2LonLat(bounds[1][0],bounds[1][1])
    print('boundaries successfully calculated')
else:
    print('boundaries already calculated')
    

parisbike = pd.read_csv('velib-paris.csv',sep=';')

parisbike2=parisbike[parisbike["Nombre de bornes disponibles"]!=0]
list_stations = parisbike2["Code de la station"].unique()
list_geo = parisbike2["geo"].unique()

df1 = DataFrame({'key':[1]*len(list_stations), 'station_dep':list_stations,'geo_dep':list_geo})

df1['geo_depx']=df1['geo_dep'].apply(lambda x: float(x.split(',')[0])) 
df1['geo_depy']=df1['geo_dep'].apply(lambda x: float(x.split(',')[1]))

df1 = df1[df1['geo_depy'] > bound_inf[0]]
df1 = df1[df1['geo_depy'] < bound_sup[0]]
df1 = df1[df1['geo_depx'] > bound_inf[1]]
df1 = df1[df1['geo_depx'] < bound_sup[1]]
