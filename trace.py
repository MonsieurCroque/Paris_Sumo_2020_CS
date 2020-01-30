###################################################################
######################## PREPROCESSING DATA #######################
###################################################################

########################## libraries ##############################

import xml.etree.ElementTree as ET
import pandas as pd
import random
from shapely.geometry import Point, Polygon
import sumolib

########################### functions ##############################

def cleaner(name):
    return name.replace("Î",a).replace("â",a).replace("'", '').replace('ê','e').replace(" ", '_').replace(",", '').replace('-','').replace("é", 'e').replace('è','e')

#check if there is a point from polygon in scope
def check_each_points(polygon, bnd_inf, bnd_sup):
    for point in polygon:
        if not ((point[0] < bnd_inf[0]) or (point[0] > bnd_sup[0]) or (point[1] < bnd_inf[1]) or (point[1] > bnd_sup[1])):
           return True
    return False

#check if Point is in Polygon
def check_if_in_polygon(polygon, point):
    return polygon.contains(point)

#convert dictionary to value lists
def to_list_without_nan(v):
    return [e for e in list(v.values()) if str(e) != 'nan']

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
        print(most_used_lanes.index[i])

def get_commune_from_xy(x, y, location_in_scope):
    point = Point(x,y)
    location = location_in_scope[0]
    i = 0
    while not (check_if_in_polygon(polygons_in_scope[shape_considered], point_arr) or check_if_in_polygon(polygons_in_scope[shape_considered], point_dep)):
        i += 1
        location = location_in_scope[i]
    return location


########################### variables ##############################

nb_hour = 2

########################### sources ###############################

#import network
if not ('net' in locals() or 'net' in globals()):
    global net
    net = sumolib.net.readNet('osm.net.xml')
    print('net successfully imported')
else:
    print('net already imported')

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

scale_factor = 0.15
car_ratio = 0.20

#communes_in_paris = ['Asnières-sur-Seine', 'Bobigny', 'Clamart', 'Issy-les-Moulineaux', 'Ivry-sur-Seine', 'Courbevoie', 'Nanterre', 'Montreuil', 'Montrouge', 'Pantin', 'Saint-Denis', 'Boulogne-Billancourt', 'Paris 1er Arrondissement', 'Paris 2e Arrondissement', 'Paris 3e Arrondissement', 'Paris 4e Arrondissement', 'Paris 5e Arrondissement', 'Paris 6e Arrondissement', 'Paris 7e Arrondissement', 'Paris 8e Arrondissement', 'Paris 9e Arrondissement', 'Paris 10e Arrondissement', 'Paris 11e Arrondissement', 'Paris 12e Arrondissement', 'Paris 13e Arrondissement', 'Paris 14e Arrondissement', 'Paris 15e Arrondissement', 'Paris 16e Arrondissement', 'Paris 17e Arrondissement', 'Paris 18e Arrondissement', 'Paris 19e Arrondissement', 'Paris 20e Arrondissement']
communes = pd.read_csv('les-communes-generalisees-dile-de-france.csv', sep=";")

#fill with polygons of communes in scope
polygons_in_scope = {}

for n in range(len(communes)):
    coord = json_2_Polygon(communes["Geo Shape"][n])
    if check_each_points(coord, bound_inf, bound_sup):
        polygons_in_scope[communes['insee'][n]] = Polygon(coord)

#list of communes postal codes in scope
location_in_scope = list(polygons_in_scope.keys())

######################### analysing ############################

tree = ET.parse(r'C:/Users/simon/Documents/Supélec Projet 3A/Paris-sans-tp/truckTrace.xml')
root = tree.getroot()

rawdata = pd.DataFrame(columns = ['id', 'x', 'y', 'angle', 'type', 'speed', 'pos', 'lane', 'slope', 'time'])
total_length = 0

locations_2_length = {}
for location in location_in_scope:
    locations_2_length[str(location)] = 0

for timestep in root.iter('timestep'):
    time = timestep.get('time')
    vehicle = timestep.find('vehicle')
    if not vehicle is None:
        new_lign = vehicle.attrib
        total_length += lane_2_length(new_lign['lane'])
        commune = get_commune_from_xy(float(new_lign['x']), float(new_lign['y']), polygons_in_scope)
        locations_2_length[commune] += lane_2_length(new_lign['lane']) 

"""most_used_lanes = rawdata.groupby('lane')['id'].nunique().sort_values(ascending=False)
total_surface_covered = 0
nodes = []

for i in range(len(most_used_lanes)):
    try:
        lanes = net.getLane(most_used_lanes.index[i])
        total_surface_covered += lanes.getLength() * most_used_lanes[i]
    except:
        nodes.append(most_used_lanes.index[i])

print(str(round(len(nodes)/len(most_used_lanes)*100)) + "% is not lane")
print(total_surface_covered)

most_used_lanes = rawdata.groupby('lane')['id'].nunique().sort_values(ascending=False)
total_surface_covered = 0

for i in range(len(most_used_lanes)):
    try:
        lanes = net.getLane(most_used_lanes.index[i])
        total_surface_covered += lanes.getLength() * most_used_lanes[i]
    except:
        print(most_used_lanes.index[i])

print(total_surface_covered)"""