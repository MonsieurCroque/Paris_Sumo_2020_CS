###################################################################
######################## PREPROCESSING DATA #######################
###################################################################

########################## libraries ##############################

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

#convert a geometry object to a polygon
def json_2_Polygon(json):
    vect = json[37:].split('[')
    result = []
    for pos in vect:
        if pos != "":
            inte = pos.split(']')[0]
            coord = inte.split(",")
            lon = float(coord[0])
            lat = float(coord[1])
            result.append((lon, lat))
    return result

#check if vehicle belongs to edge
def filter_type_node(edge,vehicule_type):
    return edge[0].allows(vehicule_type)

########################### variables ##############################

nb_hour = 2
path = 'C:/Users/simon/Documents/Supélec Projet 3A'

########################### sources ###############################

#import network
if not ('net' in locals() or 'net' in globals()):
    global net
    net = sumolib.net.readNet(path + '\Paris-sans-tp\osm.net.xml')
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

#document INSEE
raw_data = pd.read_csv(path + '/flux.csv')

#from Open data ile de france
communes = pd.read_csv(path + '/les-communes-generalisees-dile-de-france.csv', sep=";")

########################## processing #############################

#fill with polygons of communes in scope
polygons_in_scope = {}

for n in range(len(communes)):
    coord = json_2_Polygon(communes["Geo Shape"][n])
    if check_each_points(coord, bound_inf, bound_sup):
        polygons_in_scope[communes['insee'][n]] = Polygon(coord)

#list of communes postal codes in scope
communes_in_paris = list(polygons_in_scope.keys())

#create a dictionary
communes_2_edges = {}
for commune in communes_in_paris:
    communes_2_edges[str(commune)] = []

#fill dictionary with corresponding edges
for edge in net.getEdges():
    bndbox = edge.getBoundingBox()
    X_dep, Y_dep = bndbox[0], bndbox[1]
    point_dep = Point(net.convertXY2LonLat(X_dep, Y_dep))
    X_arr, Y_arr = bndbox[2], bndbox[3]
    point_arr = Point(net.convertXY2LonLat(X_arr,Y_arr))
    commune = communes_in_paris[0]
    i = 0
    if filter_type_node(edge, "passenger"):
        while not (check_if_in_polygon(polygons_in_scope[commune], point_arr) or check_if_in_polygon(polygons_in_scope[commune], point_dep)):
            i += 1
            commune = communes_in_paris[i]
        communes_2_edges[str(commune)].append(edge.getID())

communes_2_edges = {str(k) : v for k,v in communes_2_edges.items() if len(v) != 0}

######################################################################
######################## GENERATING OD MATRIX ########################
######################################################################

#get list of communes in scope
communes_in_scope = communes_2_edges.keys()

#car are represented by passenger class
veh_type = "passenger"

#fill xml file
trip_lines = []

for n in range(len(raw_data)):
   
    print("processing " + str(round(n/len(raw_data)*100)) + "%")
    
    # check if origin postal code is in scope
    if raw_data['CODGEO'][n] in communes_in_scope:
        
        # check if destination postal code is in scope
        dest_code_postal = raw_data[raw_data['LIBGEO'] == raw_data['L_DCLT'][n]]['CODGEO']
        if len(dest_code_postal) > 0:
            dest_code_postal = dest_code_postal.iloc[0]
            if dest_code_postal in communes_in_scope:
                
                #generate the right number of cars
                for nb in range(round(float(raw_data['NBFLUX_C16_ACTOCC15P'][n])*scale_factor*car_ratio)):
                    
                    #fill xml line
                    startname = cleaner(raw_data['LIBGEO'][n])
                    endname = cleaner(raw_data['L_DCLT'][n])
                    starttime = round(random.uniform(0.00 , 3600.00*nb_hour),2)
                    idedgestart = random.choice(communes_2_edges[raw_data['CODGEO'][n]])
                    idedgeend = random.choice(communes_2_edges[dest_code_postal])
                    new_trip_line = "<trip id=\""+veh_type+str(startname)+"_"+str(endname)+"_"+str(n)+"_"+str(nb)+"\" type=\"veh_"+veh_type+"\" depart=\""+str(starttime)+"\" departLane=\"best\" from=\""+str(idedgestart)+"\" to=\""+str(idedgeend)+"\"/>"
                    trip_lines.append((starttime,new_trip_line))

#export to xml file in folder
output_file = open(path + '\Paris-sans-tp\generated_car_input.xml', 'w')
output_file.write('<?xml version="1.0" encoding="UTF-8"?>')
output_file.write('<routes xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/routes_file.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">')
output_file.write('<vType id="veh_'+veh_type+'" vClass="'+veh_type+'"/>')
trips = sorted(trip_lines)
for trip in trips:
    output_file.write(trip[1])
    output_file.write("\n")
output_file.write('</routes>')
output_file.close()