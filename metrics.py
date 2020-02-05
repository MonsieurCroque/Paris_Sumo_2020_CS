# -*- coding: utf-8 -*-
"""
Created on Fri Jan 31 16:16:48 2020

@author: wassim
"""

########################### variables ##############################

path2 = 'C:/Users/simon/Documents/Supélec Projet 3A/'
path = 'C:/Users/wassim/Desktop/Paris_Sumo_2020_CS/'
tracefile2 = 'Paris-sans-tp/trucksTrace.xml'
#tracefile = 'bicycleTrace.xml'
#tracefile = 'trucksTrace.xml'
tracefile = 'carTrace.xml'

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


# Compute the distance of between the far_most points and its neibourghs 

def dist(p1,p2):
    return math.sqrt((p1[0]-p2[0])**2+(p1[1]-p2[1])**2)

def farmost_points_distance(points):
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

def check_each_points_xy(polygon, bnd_inf, bnd_sup):
    for point in polygon:
        if not ((point[0] < bnd_inf[0]) or (point[0] > bnd_sup[0]) or (point[1] < bnd_inf[1]) or (point[1] > bnd_sup[1])):
           return True
    return False

#check if Point is in Polygon
def check_if_in_polygon(polygon, point):
    return polygon.contains(point)

def in_which_commune(polygons_of_communes_in_scope,point):
    for commune,polygon in polygons_of_communes_in_scope.items():
        if polygon.contains(Point(p)):
            return commune
    return 'notfound'
    

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

fpd_timestep=[]
# get an iterable and turn it into an iterator
context = iter(iterparse(path + tracefile, events=("start", "end")))

# get the root element
event, root = next(context)

for event, elem in context:
    if event == "end" and elem.tag == "timestep":
        time = int(float(elem.get('time')))
        if not time%60==59 or time>8000:
            root.clear()
            continue
        print(time)
        points=[]
        for vehicle in elem.iter('vehicle'):
            pos=[float(vehicle.attrib['x']),float(vehicle.attrib['y'])]
            points.append(pos)
        if len(points)<=8:
            root.clear()
            continue
        fpd=farmost_points_distance(points)
        fpd_timestep.append(fpd)
        root.clear()

communes = pd.read_csv(path +'les-communes-generalisees-dile-de-france.csv', sep=";")

polygons_of_communes_in_scope = {}

for n in range(len(communes)):
    coord = json_2_Polygon_in_xy(communes["Geo Shape"][n])
    if check_each_points_xy(coord, bound_inf, bound_sup):
        polygons_of_communes_in_scope[communes['insee'][n]] = Polygon(coord)


fcd_timestep=[]
for fpd in fpd_timestep:
    print(len(fcd_timestep))
    fcd={}
    for p,d in fpd:
        commune=in_which_commune(polygons_of_communes_in_scope,p)
        if commune not in fcd:
            fcd[commune]=d
        else:
            fcd[commune]=max(fcd[commune],d)
    fcd_timestep.append(fcd)
    
fcd_timestep=pd.DataFrame(fcd_timestep)

fcd_timestep.to_csv("farmost_pt_car.csv")
