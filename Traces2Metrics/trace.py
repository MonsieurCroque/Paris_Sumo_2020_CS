###################################################################
######################## PREPROCESSING DATA #######################
###################################################################

########################## libraries ##############################

from xml.etree.cElementTree import iterparse
import pandas as pd
from shapely.geometry import Point, Polygon, LineString
import sumolib
import matplotlib.pyplot as plt
from math import sin, cos, sqrt, atan2, radians
import re
from scipy.spatial import Voronoi

########################### functions ##############################

def check_each_points_xy(polygon, bnd_inf, bnd_sup):
    for point in polygon:
        if not ((point[0] < bnd_inf[0]) or (point[0] > bnd_sup[0]) or (point[1] < bnd_inf[1]) or (point[1] > bnd_sup[1])):
           return True
    return False

#check if Point is in Polygon
def check_if_in(container, point):
    return container.distance(point) < 1e-8

#convert a geometry object to a polygon
def extract_coordinates_list_from_string(string):
    vect = re.findall("[0-9.]+", string)
    result = []
    for i in range(len(vect)):
        if i % 2 == 0:
            lon = float(vect[i])
        else:
            lat = float(vect[i])
            result.append(net.convertLonLat2XY(lon, lat))
    return result

def lane_2_length(lane_id):
    try:
        lanes = net.getLane(lane_id)
        return lanes.getLength()
    except:
        return 0

def get_location_from_xy(x, y, location_in_scope):
    point = Point(x,y)
    location_names = list(location_in_scope.keys())
    location = location_names[0]
    i = 1
    while i < len(location_names) and not check_if_in(location_in_scope[location], point):
        location = location_names[i]
        i += 1
   
    if  check_if_in(location_in_scope[location], point):
        return location
    else:
        return 'notinscope'

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

def dist(p1,p2):
    return math.sqrt((p1[0]-p2[0])**2+(p1[1]-p2[1])**2)

############################# metrics ##############################

# Compute the distance of between the far_most points and its neibourghs 
def farmost_points_distance(points):
    vor = Voronoi(points)
    vor.vertices
    voronoi_point_desc={}
    
    # Initialise a matrix voronoi_point -> ((x,y),dist)
    for id_dep in range(len(vor.point_region)):
        reg=vor.point_region[id_dep]
        for id_voronoi in vor.regions[reg]:
            if id_voronoi !=-1 and id_voronoi not in voronoi_point_desc:
                voronoi_point_desc[id_voronoi]=(vor.vertices[id_voronoi],dist(vor.points[id_dep],vor.vertices[id_voronoi]))
    
    return list(voronoi_point_desc.values())

# Distance traveled per time_slot
def distance_traveled_per_time_slot(total_length_covered_by_timeslot, time, duration, lane_id):
    add_to_list(total_length_covered_by_timeslot, int(time/duration), lane_2_length(lane_id))

#number of different lanes explored by timestep
def lane_explorer(lane_id, lane_already_explored, time, duration):
    if not lane_id in lane_already_explored:
        add_to_list(nb_lanes_explored_by_timeslot,int(time/duration), 1)

#to get duration of trips by vehicle_id
def trip_duration(vehicle_begin, vehicle_end, vehicle_id):
    if not vehicle_id in vehicle_begin.keys():
        vehicle_begin[vehicle_id] = time
    else:
        vehicle_end[vehicle_id] = time

# Find the most used lanes
def get_most_used_lanes(lane_id, most_used_lanes):
    increment_dict_value(lane_id, most_used_lanes)

#Match with any road_type that contains (x,y) and then add the trip length to this road          
def total_trip_length_by_road_type(x, y, polygons_of_roads_in_scope, total_length_by_road_surface):
    road = get_location_from_xy(x, y, polygons_of_roads_in_scope)
    total_length_by_road_surface[road] += 1

#Set value to 1 if vehicle goes through peripherique
def count_vehicle_passing_through_peripherique(x, y, polygons_of_roads_in_scope, vehicule_is_in_location):
    road = get_location_from_xy(x, y, polygons_of_roads_in_scope)
    if "Périphérique" in road:
        vehicule_is_in_location[(new_lign['id'],"Périphérique")]=1

#Compute the total distance
def total_distance(total_length, lane_id, lane_2_length):
    total_length += lane_2_length(lane_id)

#Match with any city that contains (x,y) and then add the trip length to this city
def trip_length_to_commune(lane_id, polygons_of_communes_in_scope, x, y, commmunes_2_length):
    commune = get_location_from_xy(x, y, polygons_of_communes_in_scope)
    commmunes_2_length[commune] += lane_2_length(lane_id)

def save_points_for_voronoi_distance(x, y, points):
    points.append((x,y))

def farthest_points_distance(points):
    vor=Voronoi(points)
    vor.vertices
    voronoi_point_desc={}
    # Initialise a matrix voronoi_point -> ((x,y),dist)

    # Update it
    for id_dep in range(len(vor.point_region)):
        reg=vor.point_region[id_dep]
        for id_voronoi in vor.regions[reg]:
            if id_voronoi !=-1 and id_voronoi not in voronoi_point_desc:
                voronoi_point_desc[id_voronoi]=(vor.vertices[id_voronoi],dist(vor.points[id_dep],vor.vertices[id_voronoi]))
    return list(voronoi_point_desc.values())


def get_voronoi_distance(points, fpd_timestep):

    if len(points) > 8:
        fcd={}
        for point, distance in farthest_points_distance(points):
            x = p[0]
            y = p[1] 
            
            commune = get_location_from_xy(x, y, polygons_of_communes_in_scope))
            
            if commune not in fcd.keys():
                fcd[commune] = d
            else:
                fcd[commune] = max(fcd[commune],d)
            fcd_timestep.append(fcd)

########################### variables ##############################

path = 'C:/Users/simon/Documents/Supélec Projet 3A/'
path2 = 'C:/Users/wassim/Desktop/Paris_Sumo_2020_CS/'
path3 = 'C:/Users/simon/Documents/Supélec Projet 3A/Paris-sans-tp/'
tracefile = 'trace_voitures.xml'
tracefile = 'truckTrace.xml'

#for timeslot
duration = 5*60 #seconds

########################### sources ###############################

#import network
if not ('net' in locals() or 'net' in globals()):
    global net
    net = sumolib.net.readNet(path3 + 'osm.net.xml')
    print('net successfully imported')
else:
    print('net already imported')

#scope of network
if not ('bounds' in locals() or 'bounds' in globals()):
    global bounds
    global bound_inf
    global bound_sup
    bounds = net.getBBoxXY()
    bound_inf = (bounds[0][0], bounds[0][1])
    bound_sup = (bounds[1][0], bounds[1][1])
    print('boundaries successfully calculated')
else:
    print('boundaries already calculated')

#import communes shape
communes = pd.read_csv(path +'les-communes-generalisees-dile-de-france.csv', sep=";")

#fill with polygons of communes in scope
polygons_of_communes_in_scope = {}

for n in range(len(communes)):
    coord = extract_coordinates_list_from_string(communes["Geo Shape"][n])
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
        coord = extract_coordinates_list_from_string(roads["geometry"][n])
        if check_each_points_xy(coord, bound_inf, bound_sup):
            polygons_of_roads_in_scope[nameid] = LineString(coord)

#list of roads in scope
roads_in_scope = list(polygons_of_roads_in_scope.keys())

######################### initializing ############################

#global variable
if not ('last_positions' in locals() or 'last_positions' in globals()):
    global last_positions
    global total_length
    global lane_already_explored
    global most_used_lanes
    global total_length_covered_by_timeslot
    global nb_lanes_explored_by_timeslot
    global vehicle_begin
    global vehicle_end
    global total_length_by_road_surface
    global vehicule_is_in_location
    global commmunes_2_length
    global points
    global fpd_timestep

#check last position to avoid counting twice
last_positions = {}

#total length
total_length = 0

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
total_length_by_road_surface["notinscope"] = 0
for road in roads_in_scope:
    total_length_by_road_surface[road] = 0

#Create a dictionnary that tells if a vehicule has already visited this road. (vehicule,location): 0 (if not visited) or  1 (if visited)
vehicule_is_in_location = {}

#length on communes
commmunes_2_length = {}
commmunes_2_length["notinscope"] = 0
for commune in communes_in_scope:
    commmunes_2_length[commune] = 0
    
#Voronoi
fpd_timestep = []

######################### analysing ############################

# get an iterable and turn it into an iterator
context = iter(iterparse(path + tracefile, events=("start", "end")))

# get the root element
event, root = next(context)

for event, elem in context:
    
    if event == "end" and elem.tag == "timestep":
        time = int(float(elem.get('time')))
        
        #Voronoi
        points = []
    
        for vehicle in elem.iter('vehicle'):
            
            #if there is a vehicle
            if not vehicle is None:
                new_lign = vehicle.attrib
                
                vehicle_id = new_lign['id']
                lane_id = new_lign['lane']
                x = float(new_lign['x'])
                y = float(new_lign['y'])
       	        
                #check if first time in lane
                if (not lane_id in last_positions.keys()) or (last_positions[new_lign['id']] != new_lign['lane']):
                    
                    #hold in memory the last position
                    last_positions[new_lign['id']] = lane_id
                    
            		#update metrics
                    total_distance(total_length, lane_id, lane_2_length)
                    total_trip_length_by_road_type(x, y, polygons_of_roads_in_scope, total_length_by_road_surface)
                    count_vehicle_passing_through_peripherique(x, y, polygons_of_roads_in_scope, vehicule_is_in_location)
                    distance_traveled_per_time_slot(total_length_covered_by_timeslot, time, duration, lane_id)
                    lane_explorer(lane_id, lane_already_explored, time, duration)
                    trip_duration(vehicle_begin, vehicle_end, vehicle_id)
                    get_most_used_lanes((lane_id, most_used_lanes))

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