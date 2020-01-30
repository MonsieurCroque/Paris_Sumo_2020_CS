###################################################################
######################## PREPROCESSING DATA #######################
###################################################################

########################## libraries ##############################

import pandas as pd
import numpy as np
from math import sin, cos, sqrt, atan2, radians
from pandas import DataFrame, merge
import random

########################### variables ##############################

nb_hour = 2
path = 'C:/Users/simon/Documents/Supélec Projet 3A'

########################### functions ##############################

#returns time using distance and average speed
def dist_to_time(dist,speed):
    return round(dist/speed)

#returns distance between two points
#geo_dep and geo_arr are string "lat,lon"
def latlon_2_distance(geo_dep,geo_arr):
    geo_dep_long,geo_dep_lat=tuple(map(float,geo_dep.split(',')))
    geo_arr_long,geo_arr_lat=tuple(map(float,geo_arr.split(',')))
    
    R = 6373.0

    lat1 = radians(geo_dep_lat)
    lon1 = radians(geo_dep_long)
    lat2 = radians(geo_arr_lat)
    lon2 = radians(geo_arr_long)
    
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    return R * c

#check if in dict deplacements
def in_dict_deplacements(com_dep,com_arr):
    traj=(com_dep,com_arr)
    if traj in dict_deplacements:
        return dict_deplacements[traj]
    else:
        return 0

########################### sources ###############################

#from Rapport de la ville de Paris 2016
nb_deplacements = 114421
ratio_heure = 0.125

#average speed
speed = 8/60 #(km/mins)

#raw data from https://www.citibikenyc.com/system-data
NYbikedata = pd.read_csv(path + '/JC-201909-citibike-tripdata.csv')

#convert duration from seconds to minutes
NYbikedata['tripdurationmn'] = NYbikedata['tripduration'].apply(lambda x: round(x/60))

#duration_2_factor that maps duration to a probability factor
duration_2_factor = np.zeros(200)
for duration in range(200):
    duration_2_factor[duration] = len(NYbikedata[NYbikedata['tripdurationmn'] == duration])/len(NYbikedata)

#document INSEE
Inseedata = pd.read_csv(path + '/flux.csv')

#coordinates and number of vélibs by stations
parisbike = pd.read_csv(path + '/velib-paris.csv',sep=';')

#get station names and localisation
commune_in_scope = set(parisbike['Commune'])
dict_deplacements = {}

for ville_depart in commune_in_scope:
    insee_dep = Inseedata[Inseedata['LIBGEO'] == ville_depart]
    set_arrival = set(insee_dep['L_DCLT'])
    
    for ville_arr in commune_in_scope.intersection(set_arrival):
        flux = insee_dep[insee_dep['L_DCLT'] == ville_arr]['NBFLUX_C16_ACTOCC15P'].iloc[0]
        dict_deplacements[(ville_depart,ville_arr)] = flux

list_stations = parisbike["Code de la station"].unique()
list_geo = parisbike["geo"].unique()

########################## processing #############################

station_ville = parisbike[["Code de la station","Commune","Importance"]]

#merge dataframe to have OD matrix
df1 = DataFrame({'key':[1]*len(list_stations), 'station_dep':list_stations,'geo_dep':list_geo})
df2 = DataFrame({'key':[1]*len(list_stations), 'station_arr':list_stations,'geo_arr':list_geo})

df_traj = merge(df1, df2,on='key')[['station_dep', 'station_arr','geo_dep','geo_arr']]
df_traj2 = df_traj.merge(station_ville, how='left', left_on='station_dep', right_on='Code de la station')
df_traj2 = df_traj2.rename(columns={"Importance": "Importance_dep", "Commune": "Commune_dep"})        
df_traj2 = df_traj2.merge(station_ville, how='left', left_on='station_arr', right_on='Code de la station')
df_traj2 = df_traj2.rename(columns={"Importance": "Importance_arr", "Commune": "Commune_arr"})

#INSEE factor
df_traj2['flux'] = df_traj2.apply(lambda x: in_dict_deplacements(x.Commune_dep, x.Commune_arr), axis=1)

#time factor using NYC histogram
df_traj2['distance'] = df_traj2.apply(lambda x: latlon_2_distance(x.geo_dep, x.geo_arr), axis=1)
df_traj2['temps'] = df_traj2.apply(lambda x: dist_to_time(x.distance, speed), axis=1)
df_traj2['facteur_temps'] = df_traj2.apply(lambda x: duration_2_factor[x.temps] if x.temps<200 else 0, axis=1)

#importance factor using nb of vélibs by station
df_traj2['facteur_total'] = df_traj2.apply(lambda x: x.facteur_temps*float(x.Importance_dep.strip('%'))*float(x.Importance_arr.strip('%'))*x.flux , axis=1)

#nb of vélibs after normalisation
coef = nb_deplacements/df_traj2['facteur_total'].sum()
df_traj2['facteur_total_normal'] = df_traj2['facteur_total']*coef

processed_data = pd.DataFrame(columns=["starttime", "start station longitude", "start station latitude", "start nom", 'end station longitude', 'end station latitude', "end nom"])

for index , trip in df_traj2[df_traj2['facteur_total_normal'] >= 0.01].iterrows():
    
    if index % 10000 == 0:
        print("preprocessing with "+str(index)+" done")
    
    #station localisations
    startlat, startlon = tuple(map(float,trip.geo_dep.split(',')))
    endlat, endlon = tuple(map(float,trip.geo_arr.split(',')))

    #station names
    start_dep = trip['Commune_dep']
    end_dep = trip['Commune_arr']
    
    #nb vélib generated
    qte = trip['facteur_total_normal']*ratio_heure
    Z_qte = np.random.poisson(lam=qte)
    
    for p in range(Z_qte):
        
        #depart time with uniform law
        departtime = round(random.uniform(0.00 , 3600.00*nb_hour),2)
        
        df = pd.DataFrame([[departtime,startlon,startlat,start_dep, endlon, endlat,end_dep]], columns = ["starttime", "start station longitude", "start station latitude", "start nom", 'end station longitude', 'end station latitude', "end nom"])
        processed_data = processed_data.append(df)

# sort by departure time
processed_data = processed_data.sort_values('starttime')

# export preprocessed data to csv file
processed_data.to_csv(path + "/bike_before_sumo.csv")

######################################################################
######################## GENERATING OD MATRIX ########################
######################################################################

#variables
radius = 200
veh_type = "bicycle"
path = 'C:/Users/simon/Documents/Supélec Projet 3A'

#import processed data
data = pd.read_csv(path + '/bike_before_sumo.csv', sep=",")

#run OD_2_sumo.py before running this line
OD_2_sumo(radius, path, veh_type, data)