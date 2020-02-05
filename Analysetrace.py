# -*- coding: utf-8 -*-


########################### variables ##############################

path2 = 'C:/Users/simon/Documents/Supélec Projet 3A/'
path = 'C:/Users/wassim/Desktop/Paris_Sumo_2020_CS/'
tracefile2 = 'Paris-sans-tp/trucksTrace.xml'
#tracefile = 'bicycleTrace.xml'
tracefile = 'busTrace.xml'
#tracefile = 'truckTracev2.xml'

#for timeslot
duration = 5*60 #seconds

########################### sources ###############################


import pandas as pd
from shapely.geometry import Point, Polygon
import sumolib
import matplotlib.pyplot as plt
import math
import numpy as np
from scipy.spatial import Voronoi



idtotest=['busSURESNES_-_LONGCHAMP_MAIRIE_DESBASSAYNS_1809','busPORT_ROYAL_-_SAINT-JACQUES_JACQUES_BONSERGENT_3645',
          'busLE_BOURGET-RER_LANGEVIN_-_WALLON_5383','busPLACE_DE_LA_BOULE_-_LENINE_PONT_DE_SAINT-CLOUD_-_ALBERT_KAHN_6835',
          'busROND-POINT_PIERRE_TIMBAUD_PLACE_DEBAIN_398','busPORTE_DE_VINCENNES_NATION_-_TRONE_3212',
          'busPIERRELAIS_-_BLANCHARD_CHARTRES_-_BLANCHARD_2475']



"""
idtotest=['bicycleVanves_Malakoff_4004','bicycleParis_7e_Arrondissement_Paris_16e_Arrondissement_2785','bicycleParis_16e_Arrondissement_Puteaux_2409',
          'bicycleParis_19e_Arrondissement_Courbevoie_2741','bicycleParis_18e_Arrondissement_Paris_9e_Arrondissement_3552','bicycleVincennes_Montreuil_3690',
          'bicycleParis_1er_Arrondissement_Paris_10e_Arrondissement_2426']
"""

idtotrace={}

def analyse(vehicle):
    id_veh = str(vehicle.attrib['id'])
    if id_veh not in idtotest:
        return 0
    if id_veh not in idtotrace:
        print('Le véhicule'+id_veh+'est parti de x='+vehicle.attrib['x']+' y='+vehicle.attrib['y'])
        print(net.convertXY2LonLat(float(vehicle.attrib['x']),float(vehicle.attrib['y'])))
        print('-----------------------------------------')
        idtotrace[id_veh]=[]
    idtotrace[id_veh].append((float(vehicle.attrib['x']),float(vehicle.attrib['y'])))
    return 1
    
        
if not ('net' in locals() or 'net' in globals()):
    global net
    net = sumolib.net.readNet(path + 'osm.net.xml')
    print('net successfully imported')
else:
    print('net already imported')
    
    #scope of network
if not ('bounds' in locals() or 'bounds' in globals()):
    global bounds
    global bound_inf
    global bound_sup
    bounds = net.getBBoxXY()
    bound_inf = (bounds[0][0],bounds[0][1])
    bound_sup = (bounds[1][0],bounds[1][1])
    print('boundaries successfully calculated')
else:
    print('boundaries already calculated')
    
######################### analysing ############################

from xml.etree.cElementTree import iterparse

# get an iterable and turn it into an iterator
context = iter(iterparse(path + tracefile, events=("start", "end")))

# get the root element
event, root = next(context)

for event, elem in context:
    if event == "end" and elem.tag == "timestep":
        time = int(float(elem.get('time')))
        if not True:
            root.clear()
            continue
        for vehicle in elem.iter('vehicle'):
            cc=analyse(vehicle)
            root.clear()
            
            
color_list=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
i=0
for id_veh in idtotrace:
    color=color_list[i]
    X=[]
    Y=[]
    for x,y in idtotrace[id_veh]:
        X.append(x)
        Y.append(y)
    plt.scatter(X,Y,s=1,c=color)
    i+=1
plt.show()
        

