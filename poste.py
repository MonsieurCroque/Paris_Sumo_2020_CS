###################################################################
######################## PREPROCESSING DATA #######################
###################################################################

########################## libraries ##############################

import pandas as pd
import numpy as np
from random import random 
import sumolib

########################### variable ##############################

path = 'C:/Users/simon/Documents/Supélec Projet 3A'

########################### sources ###############################

#import network
if not ('net' in locals() or 'net' in globals()):
    global net
    net = sumolib.net.readNet(path + '/Paris-sans-tp/osm.net.xml')
    print('net successfully imported')
else:
    print('net already imported')

# raw data from https://datanova.laposte.fr/explore/dataset/laposte_poincont2/information/?disjunctive.caracteristique_du_site&disjunctive.code_postal&disjunctive.localite&disjunctive.code_insee&disjunctive.precision_du_geocodage
raw_data = pd.read_csv(path + "/laposte_poincont2.csv", sep=";")

#   https://www.docaufutur.fr/2017/03/05/a-decouverte-de-plateforme-industrielle-de-courrier-de-wissous/
#   https://fr.m.wikipedia.org/wiki/Plateforme_industrielle_du_courrier
#   Pour déplacer les PICs dans la carte :
#       https://www.bing.com/maps?&cp=48.819931~2.214436&lvl=10&osid=bb7f3961-b5e8-49bd-9c1e-7fc591b063ef&v=2&sV=2&form=S00027

# PIC Paris Sud
sudlat, sudlon, sudnom = 48.801846, 2.342904, "PIC_SUD"

# PIC Paris Nord
nordlat, nordlon, nordnom = 48.933346, 2.372138, "PIC_NORD"

########################## processing #############################
    
#scope of network
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

# dataframe with preprocessing result
preprocessed_data = pd.DataFrame(columns=["start station longitude", "start station latitude", 'start nom',"end station longitude", "end station latitude", 'end nom'])

for n in range(len(raw_data)):
   
    # check if postal office in scope
    if (not np.isnan(raw_data['Latitude'][n])) and (not np.isnan(raw_data['Longitude'][n])):
        if not ((raw_data['Longitude'][n] < bound_inf[0]) or (raw_data['Longitude'][n] > bound_sup[0]) or (raw_data['Latitude'][n] < bound_inf[1]) or (raw_data['Latitude'][n] > bound_sup[1])):
            
            # check if postal office is in North area
            if raw_data['Code_postal'][n] in [75008,75009,75010,75011,75002,75003,75017,75018,75019,75020]:
                startlat,startlon,startnom = nordlat, nordlon, nordnom
                df = pd.DataFrame(np.array([[startlon,startlat,startnom,raw_data['Longitude'][n], raw_data['Latitude'][n], raw_data['Libellé_du_site'][n]]]), columns = ["start station longitude", "start station latitude", 'start nom',"end station longitude", "end station latitude", 'end nom'])
                preprocessed_data = preprocessed_data.append(df)
            # or in South area
            elif raw_data['Code_postal'][n] in [75014,75015,75013,75005,75006,75007,75016,75116,75001,75004,75012]:
                startlat,startlon,startnom = sudlat, sudlon, sudnom
                df = pd.DataFrame(np.array([[startlon,startlat,startnom,raw_data['Longitude'][n], raw_data['Latitude'][n], raw_data['Libellé_du_site'][n]]]), columns = ["start station longitude", "start station latitude", 'start nom',"end station longitude", "end station latitude", 'end nom'])
                preprocessed_data = preprocessed_data.append(df)

#divide trucks every 30 min
preprocessed_data['starttime'] =[(round((random()*10 + int(i/len(preprocessed_data)*4)*30)*6000)/100) for i in range(len(preprocessed_data))]

# sort by departure time
preprocessed_data = preprocessed_data.sort_values('starttime')

# export preprocessed data to csv file
preprocessed_data.to_csv(path + "/poste_list.csv", index=False, index_label = None)

######################################################################
######################## GENERATING OD MATRIX ########################
######################################################################

#variables
radius = 200
veh_type = "truck"
path = 'C:/Users/simon/Documents/Supélec Projet 3A'

#import preprocessed data
data = pd.read_csv(path + '/poste_list.csv', sep=",")

#run OD_2_sumo.py before running this line
OD_2_sumo(radius, path, veh_type, data)
