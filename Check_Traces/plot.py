########################### libraries ##############################

# for plotting
import matplotlib.pyplot as plt
from xml.etree.cElementTree import iterparse
import numpy
import random
import sumolib

import os
os.environ["PROJ_LIB"] = "C:\\Users\\simon\\Anaconda3\\pkgs\\proj4-5.2.0-ha925a31_1\\Library\\share"

# for background map
from mpl_toolkits.basemap import Basemap

########################### functions ##############################

def generate_positions_for_testing(lane_id, count, x, y, positions, not_explored):
    no_progress = True
    if lane_id in positions.keys():
        positions[lane_id].append(net.convertXY2LonLat(x, y))
        no_progress = False
    elif not lane_id in not_explored and count < 101:
        if random.random() < 0.05:
            positions[lane_id] = [net.convertXY2LonLat(x, y)]
            count += 1
            no_progress = False
        else:
            not_explored.append(lane_id)
    return no_progress

########################### variables ##############################

path = 'C:/Users/simon/Documents/Supélec Projet 3A/'
path3 = 'C:/Users/simon/Documents/Supélec Projet 3A/Paris-sans-tp/'
tracefile = 'carTrace.xml'

#for timeslot
duration = 5*60 #seconds

#to check traces
global count
global positions
global not_explored
global last_positions

#check last position to avoid counting twice
last_positions = {}

#to check traces
count = 0
positions = {}
not_explored = []

########################### sources ###############################

#import network
if not ('net' in locals() or 'net' in globals()):
    global net
    net = sumolib.net.readNet(path3 + 'osm.net.xml')
    print('net successfully imported')
else:
    print('net already imported')

########################### plotting ##############################


# get an iterable and turn it into an iterator
context = iter(iterparse(path + tracefile, events=("start", "end")))

# get the root element
event, root = next(context)

for event, elem in context:
    
    if event == "end" and elem.tag == "timestep":
        time = int(float(elem.get('time')))
        no_progress = True
        count_veh = 0
        
        for vehicle in elem.iter('vehicle'):
            
            #if there is a vehicle
            if not vehicle is None:
                count_veh += 1
                new_lign = vehicle.attrib
                
                vehicle_id = new_lign['id']
                x = float(new_lign['x'])
                y = float(new_lign['y'])
       	        lane_id = new_lign['lane']
                
                #check if first time in lane
                if (not vehicle_id in last_positions.keys()) or (last_positions[vehicle_id] != new_lign['lane']):
                    
                    #hold in memory the last position
                    last_positions[lane_id] = vehicle_id
                    
                    #to check trace
                    no_progress = no_progress and generate_positions_for_testing(vehicle_id, count, x, y, positions, not_explored)
        if no_progress and count >= 101:
            break
    
    root.clear()

lign_ids = list(positions.keys())
dataLong = []
dataLat = []

print(lign_ids[4])

for pos in positions[lign_ids[4]]:
    dataLong.append(pos[0])
    dataLat.append(pos[1])

# adding background map
latMin = 48.774618 - 0.0005 # background map size
latMax = 48.952002 + 0.0005
longMin = 2.092213 - (latMax - latMin)/2
longMax = 2.582987 + (latMax - latMin)/2

m = Basemap(llcrnrlon=longMin, llcrnrlat= latMin, urcrnrlon=longMax, urcrnrlat=latMax, epsg = 4326,resolution='i',projection='merc')
m.arcgisimage(service='ESRI_StreetMap_World_2D', xpixels = 12000, verbose= True)

# adding GPS coordinates
m.plot(dataLong,dataLat,color="red",label="Datas")

#adding path
for e in range(len(dataLong)-1):
    morex = numpy.linspace(dataLong[e],dataLong[e+1], num = 500, endpoint = True)
    morey = numpy.linspace(dataLat[e],dataLat[e+1], num = 500, endpoint = True)
    m.plot(morex,morey,color="blue")

plt.show()