###################################################################
######################## PREPROCESSING DATA #######################
###################################################################

########################## libraries ##############################

import xml.etree.ElementTree as ET
import pandas as pd
from shapely.geometry import Point, Polygon
import sumolib

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

def lane_2_length(stuff):
    try:
        lanes = net.getLane(stuff)
        return lanes.getLength()
    except:
        return 0

def get_commune_from_xy(x, y, location_in_scope):
    point = Point(x,y)
    location_names = list(location_in_scope.keys())
    location = location_names[0]
    i = 0
    while not check_if_in_polygon(location_in_scope[location], point):
        i += 1
        location = location_names[i]
    return location

def increment_dict_value(id_to_increment, dic):
    if id_to_increment in dic.keys():
        dic[id_to_increment] += 1
    else:
        dic[id_to_increment] = 1

########################### variables ##############################

nb_hour = 2
path2 = 'C:/Users/simon/Documents/Supélec Projet 3A/'
path = 'C:/Users/wassim/Desktop/Paris_Sumo_2020_CS/'
tracefile2 = 'Paris-sans-tp/trucksTrace.xml'
tracefile = 'trace_voitures.xml'

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

communes = pd.read_csv(path +'les-communes-generalisees-dile-de-france.csv', sep=";")

#fill with polygons of communes in scope
polygons_of_communes_in_scope = {}

for n in range(len(communes)):
    coord = json_2_Polygon_in_xy(communes["Geo Shape"][n])
    if check_each_points_xy(coord, bound_inf, bound_sup):
        polygons_of_communes_in_scope[communes['insee'][n]] = Polygon(coord)

#list of communes postal codes in scope
communes_in_scope = list(polygons_of_communes_in_scope.keys())

######################### analysing ############################

tree = ET.parse(path + tracefile)
root = tree.getroot()

rawdata = pd.DataFrame(columns = ['id', 'x', 'y', 'angle', 'type', 'speed', 'pos', 'lane', 'slope', 'time'])
total_length = 0

last_positions = {}
most_used_lanes = {}

commmunes_2_length = {}
for commune in communes_in_scope:
    commmunes_2_length[commune] = 0

for timestep in root.iter('timestep'):
    time = timestep.get('time')
    vehicle = timestep.find('vehicle')
    if not vehicle is None:
        new_lign = vehicle.attrib
        if (not new_lign['id'] in last_positions.keys()) or (last_positions[new_lign['id']] != new_lign['lane']):
            total_length += lane_2_length(new_lign['lane'])
            commune = get_commune_from_xy(float(new_lign['x']), float(new_lign['y']), polygons_of_communes_in_scope)
            commmunes_2_length[commune] += lane_2_length(new_lign['lane'])
            increment_dict_value(new_lign['lane'] ,most_used_lanes)
            last_positions[new_lign['id']] = new_lign['lane']

print(commmunes_2_length)
print(total_length)
print(sorted(most_used_lanes)[:10])