###################################################################
######################## PREPROCESSING DATA #######################
###################################################################

########################## libraries ##############################

import pandas as pd
import numpy as np
import os

########################### variable ##############################

path = 'C:/Users/simon/Documents/Supélec Projet 3A'

########################### sources ###############################

# raw data from https://dataratp2.opendatasoft.com/explore/dataset/offre-transport-de-la-ratp-format-gtfs/information/
dir_list = next(os.walk(path + '/RATP_GTFS_LINES/.'))[1]

# dataframe with processed result
preprocessed_data = pd.DataFrame(columns=['stop_id', 'stop_code', 'stop_name', 'stop_desc', 'stop_lat',
       'stop_lon', 'location_type', 'parent_station', 'trip_id',
       'arrival_time', 'departure_time', 'stop_id', 'stop_sequence',
       'stop_headsign', 'shape_dist_traveled', 'num', 'Index'])

#explore each subfolder
for dir_name in dir_list:
    #extract info from subfolder name
    split_vect = dir_name.split("_")
    type_vehicle = split_vect[2]
    num_vehicle = split_vect[3]
    
    #check if bus
    if type_vehicle == 'BUS':
        
        #extract timetable data from subfolder
        rawdata_times = pd.read_csv(path + "/RATP_GTFS_LINES/" + dir_name+"/stop_times.txt")
        #add num with line number
        rawdata_times = rawdata_times.assign(num=lambda x: num_vehicle)
        
        #take first trip between 8:00 to 10:00
        rawdata_timetable_selected = rawdata_times[rawdata_times.arrival_time.str.contains(r"09\:..\:00|08\:..\:00")]
        rawdata_timetable_selected = rawdata_timetable_selected.drop_duplicates(subset=["stop_sequence"], keep='first', inplace=False)
        
        #reindex order
        rawdata_timetable_selected['stop_sequence'] =  rawdata_timetable_selected['stop_sequence'].apply(lambda x : x-1)
        rawdata_timetable_selected['Index'] = rawdata_timetable_selected['stop_sequence']
        rawdata_timetable_selected = rawdata_timetable_selected.set_index(rawdata_timetable_selected['Index'])
        
        #match station timetable with station names
        rawdata_station_names = pd.read_csv(path + "/RATP_GTFS_LINES/" + dir_name + "/stops.txt")
        rawdata_station_names = rawdata_station_names[:len(rawdata_timetable_selected)]
        
        #add bus line
        new_bus_line = pd.concat([rawdata_station_names, rawdata_timetable_selected], axis=1, sort=False)
        preprocessed_data = preprocessed_data.append(new_bus_line)

# export preprocessed data to csv file
preprocessed_data.to_csv(path + "/tp_frequence.csv")

########################## processing #############################

preprocessed_data = pd.read_csv(path + "/tp_frequence.csv")
num_lignes = list(set(preprocessed_data["num"].values))
processed_data = pd.DataFrame(columns=["starttime", "start station longitude", "start station latitude", "start nom", 'end station longitude', 'end station latitude', "end nom"])

for n in num_lignes:
   #get n bus lign
   lign = preprocessed_data[preprocessed_data["num"] == n]
   
   #first station of the n lign
   temp = lign[lign["stop_sequence"] == 0]
   
   #arrival station
   arr_lat = temp["stop_lat"].values[0]
   arr_lon = temp["stop_lon"].values[0]
   arr_name = temp["stop_name"].values[0]
   
   for e in range(1,len(lign)):
       
       #get next station of n lign
       temp = lign[lign["stop_sequence"] == e]
       
       #convert departure time in seconds
       hr_min_sec = temp["departure_time"].values[0].split(":")
       dep_time = int(hr_min_sec[0])*3600+int(hr_min_sec[1])*60+int(hr_min_sec[2])
       
       #departure and arrival points
       dep_lat = arr_lat
       dep_lon = arr_lon
       dep_name = arr_name
       arr_lat = temp["stop_lat"].values[0]
       arr_lon = temp["stop_lon"].values[0]
       arr_name = temp["stop_name"].values[0]
       
       #append lign to preprocessed data
       df = pd.DataFrame(np.array([[dep_time, dep_lon, dep_lat, dep_name, arr_lon, arr_lat, arr_name]]), columns = ["starttime", "start station longitude", "start station latitude", "start nom", 'end station longitude', 'end station latitude', "end nom"])
       processed_data = processed_data.append(df)

# sort by departure time
processed_data = processed_data.sort_values('starttime')

# export preprocessed data to csv file
processed_data.to_csv(path + "/tp_before_sumo.csv")

######################################################################
######################## GENERATING OD MATRIX ########################
######################################################################

#variables
radius = 200
veh_type = "bus"
path = 'C:/Users/simon/Documents/Supélec Projet 3A'

#import processed data
data = pd.read_csv(path + '/tp_before_sumo.csv', sep=",")

#run OD_2_sumo.py before running this line
OD_2_sumo(radius, path, veh_type, data)
