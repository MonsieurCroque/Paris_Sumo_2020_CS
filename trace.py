###################################################################
######################## PREPROCESSING DATA #######################
###################################################################

########################## libraries ##############################

import xml.etree.ElementTree as ET
import pandas as pd
from shapely.geometry import Point, Polygon, LineString
import sumolib
import matplotlib.pyplot as plt
import math

########################### functions ##############################

def check_each_points_xy(polygon, bnd_inf, bnd_sup):
    for point in polygon:
        if not ((point[0] < bnd_inf[0]) or (point[0] > bnd_sup[0]) or (point[1] < bnd_inf[1]) or (point[1] > bnd_sup[1])):
           return True
    return False

#check if Point is in Polygon
def check_if_in_polygon(polygon, point):
    return polygon.contains(point)


#convert a geometry object to a polygon
def json_2_Polygon_in_xy(json):
    vect = json[37:].split('[')
    result = []
    for pos in vect:
        if pos != "":
            inte = pos.split(']')[0]
            coord = inte.split(",")
            lon = float(coord[0])
            lat = float(coord[1])
            result.append(net.convertLonLat2XY(lon, lat))
    return result

def json_2_Polygon_in_xy_bis(json):
    vect = json[12:-2].split(', ')
    result = []
    for pos in vect:
        if pos != "":
            coord = pos.split(' ')
            lon = float(coord[0])
            lat = float(coord[1])
            result.append(net.convertLonLat2XY(lon, lat))
    return result

def lane_2_length(stuff):
    try:
        lanes = net.getLane(stuff)
        return lanes.getLength()
    except:
        return 0

def get_location_from_xy(x, y, location_in_scope):
    point = Point(x,y)
    location_names = list(location_in_scope.keys())
    location = location_names[0]
    i = -1
    while not check_if_in_polygon(location_in_scope[location], point):
        if i<len(location_names)-2:
            i += 1
            location = location_names[i]
        else:
            return 'notinscope'
            
    return location

def add_to_list(list_to_be_added, i, value):
    if len(list_to_be_added) <= i:
        list_to_be_added.append(value)
    else:
        list_to_be_added[i] += value    

def increment_dict_value(id_to_increment, dic):
    if id_to_increment in dic.keys():
        dic[id_to_increment] += 1
    else:
        dic[id_to_increment] = 1

from math import sin, cos, sqrt, atan2, radians

def latlon_2_distance(lat1,lon1,lat2,lon2):
    
    R = 6373.0
    
    lat1=radians(lat1)
    lat2=radians(lat2)
    lon1=radians(lon1)
    lon2=radians(lon2)
    
    
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    return R * c

def distxy(x1,y1,x2,y2):
    lon1,lat1=net.convertXY2LonLat(x1,y1)
    lon2,lat2=net.convertXY2LonLat(x2,y2)
    return latlon_2_distance(lat1,lon1,lat2,lon2)
########################### variables ##############################

path2 = 'C:/Users/simon/Documents/Supélec Projet 3A/'
path = 'C:/Users/wassim/Desktop/Paris_Sumo_2020_CS/'
tracefile2 = 'Paris-sans-tp/trucksTrace.xml'
tracefile = 'trace_voitures.xml'
tracefile = 'trucksTrace.xml'

#for timeslot
duration = 5*60 #seconds

########################### sources ###############################

#import network
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

#import communes shape
communes = pd.read_csv(path +'les-communes-generalisees-dile-de-france.csv', sep=";")

#fill with polygons of communes in scope
polygons_of_communes_in_scope = {}

for n in range(len(communes)):
    coord = json_2_Polygon_in_xy(communes["Geo Shape"][n])
    if check_each_points_xy(coord, bound_inf, bound_sup):
        polygons_of_communes_in_scope[communes['insee'][n]] = Polygon(coord)

#list of communes postal codes in scope
communes_in_scope = list(polygons_of_communes_in_scope.keys())

#import roads shapes and names
roads = pd.read_csv(path +'shape_idf.csv')

#fill with polygons of roads
polygons_of_roads_in_scope = {}

for n in range(len(roads)):
    if ('Périphérique' in str(roads['name'][n])):
        nameid=roads['name'][n]+'_'+str(roads['osm_id'][n])
        coord = json_2_Polygon_in_xy_bis(roads["geometry"][n])
        if check_each_points_xy(coord, bound_inf, bound_sup):
            polygons_of_roads_in_scope[nameid] = Polygon(LineString(coord).buffer(10))


#list of roads in scope
roads_in_scope = list(polygons_of_roads_in_scope.keys())

######################### analysing ############################

#open xml file
tree = ET.parse(path + tracefile)
root = tree.getroot()

#check last position to avoid counting twice
last_positions = {}
last_positions_xy = {}

#total length
total_length = 0
total_length2 = 0

#all explored lanes
lane_already_explored = []

#length by lane
most_used_lanes = {}

#by timeslot
total_length_covered_by_timeslot = []
nb_lanes_explored_by_timeslot = []

#to get average duration by vehicle
vehicle_begin = {}
vehicle_end = {}


#length on periph
total_length_by_road_surface={}
total_length_by_road_surface["notinscope"]=0
for road in roads_in_scope:
    total_length_by_road_surface[road] = 0

#Create a dictionnary that tells if a vehicule has already visited this road. (vehicule,location): 0 (if not visited) or  1 (if visited)

vehicule_is_in_location={}


#length on communes
commmunes_2_length = {}
commmunes_2_length["notinscope"]=0
for commune in communes_in_scope:
    commmunes_2_length[commune] = 0

#iterate through xml
for timestep in root.iter('timestep'):
    time = float(timestep.get('time'))
    for vehicle in timestep.iter('vehicle'):
    #if there is a vehicle
        if not vehicle is None:
            new_lign = vehicle.attrib
		    #check if first time in lane
            if (not new_lign['id'] in last_positions.keys()) or (last_positions[new_lign['id']] != new_lign['lane']):
			#update metrics
                #Compute the total distance
                total_length += lane_2_length(new_lign['lane'])
                
                #From a x,y in vehicule -> Match with any city that contains (x,y) and then add the trip length to this city
                commune = get_location_from_xy(float(new_lign['x']), float(new_lign['y']), polygons_of_communes_in_scope)
                commmunes_2_length[commune] += lane_2_length(new_lign['lane'])
                
                #From a x,y in vehicule -> Match with any road_type that contains (x,y) and then add the trip length to this road
                road = get_location_from_xy(float(new_lign['x']), float(new_lign['y']), polygons_of_roads_in_scope)
                total_length_by_road_surface[road] += 1
                if "Périphérique" in road:
                    vehicule_is_in_location[(new_lign['id'],"Périphérique")]=1
                
                # Find the most used lanes
                increment_dict_value(new_lign['lane'] ,most_used_lanes)
                
                # Hold in memory the last position
                last_positions[new_lign['id']] = new_lign['lane']
                last_positions_xy[new_lign['id']] = (float(new_lign['x']),float(new_lign['y']))
                
                # Distance traveled per time_slot
                add_to_list(total_length_covered_by_timeslot, int(time/duration), lane_2_length(new_lign['lane']))
                if not new_lign['lane'] in lane_already_explored:
                    add_to_list(nb_lanes_explored_by_timeslot,int(time/duration), 1)
                if not new_lign['lane'] in vehicle_begin.keys():
                    vehicle_begin[new_lign['lane']] = time
                else:
                    vehicle_end[new_lign['lane']] = time

#print histogram for bikes
hist_bike = []

#Make smthing
for edge_id in vehicle_end.keys():
    hist_bike.append(round((vehicle_end[edge_id]-vehicle_begin[edge_id])/60))

#print result
print(total_length_by_road_surface)
print(commmunes_2_length)
print(total_length)
print(sorted(most_used_lanes)[:10])
plt.plot(total_length_covered_by_timeslot)
plt.plot(nb_lanes_explored_by_timeslot)
plt.hist(hist_bike, bins=50)
