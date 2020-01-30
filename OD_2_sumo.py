######################################################################
######################## GENERATING OD MATRIX ########################
######################################################################

########################### libraries ################################

import os, sys
import sumolib

########################### functions ################################

def cleaner(name):
    return name.replace("Î",'').replace("â",'').replace("'", '').replace('ê','e').replace(" ", '_').replace(",", '').replace('-','').replace("é", 'e').replace('è','e')

#check if vehicle belongs to edge
def filter_type_node(edge,vehicule_type):
    return edge[0].allows(vehicule_type)

#match position with edge
def match_pos_2_edge(lat, lon, radius_ini, veh_t):
    #convert latitude,longitude to x,y
    xstart, ystart = net.convertLonLat2XY(lon, lat)
    
    edgesstart = []
    radius = radius_ini
    
    #increase radius while there are no matching edge
    while len(edgesstart) == 0:
        edgesstart = net.getNeighboringEdges(xstart, ystart, radius)
        edgesstart = list(filter(lambda edge : filter_type_node(edge, veh_t), edgesstart))
        radius *= 2
    
    # pick the closest edge
    edgestart, distclosestEdgestart = edgesstart[0] 
    return edgestart.getID()

def OD_2_sumo(radius, path, veh_type, data):

    #append to path SUMO_HOME
    if 'SUMO_HOME' in os.environ:
         tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
         sys.path.append(tools)
    else:   
         sys.exit("please declare environment variable 'SUMO_HOME'")
    
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
    
    #dictionary to store past longitude latitude attribution
    if not ('lonlat_2_edge' in locals() or 'lonlat_2_edge' in globals()):
        global lonlat_2_edge
        lonlat_2_edge = {}
        print('lonlat_2_edge successfully created')
    else:
        print('lonlat_2_edge already created')
    
    #result
    trip_lines = []
    
    for trip_id in range(len(data)):
        
        print("preprocessing "+str(round(trip_id/len(data)*10000)/100)+"%")
        
        #extract from preprocessed data
        startlon = data.iloc[trip_id]['start station longitude']
        startlat = data.iloc[trip_id]['start station latitude']
        endlon = data.iloc[trip_id]['end station longitude']
        endlat = data.iloc[trip_id]['end station latitude']
        startname = cleaner(data.iloc[trip_id]['start nom'])
        endname = cleaner(data.iloc[trip_id]['end nom'])
        starttime = data.iloc[trip_id]['starttime']
        
       #check if positions are in scope
        if startlon < bound_inf[0] or startlon > bound_sup[0] or startlat < bound_inf[1] or startlat > bound_sup[1]:
            continue
        if endlon < bound_inf[0] or endlon > bound_sup[0] or endlat < bound_inf[1] or endlat > bound_sup[1]:
            continue
        
        #convert position to edge id
        if (str(startlon) + "," + str(startlat)) in lonlat_2_edge.keys():
            idedgestart = lonlat_2_edge[str(startlon) + "," + str(startlat)]
        else:
            idedgestart = match_pos_2_edge(startlat, startlon, radius, veh_type)
            lonlat_2_edge[str(startlon) + "," + str(startlat)] = idedgestart
        #convert position to edge id
        if (str(endlon) + "," + str(endlat)) in lonlat_2_edge.keys():
            idedgeend = lonlat_2_edge[str(endlon) + "," + str(endlat)]
        else:
            idedgeend = match_pos_2_edge(endlat, endlon, radius, veh_type)
            lonlat_2_edge[str(endlon) + "," + str(endlat)] = idedgeend
        
        #add new trip line
        new_trip_line = "<trip id=\""+veh_type+str(startname)+"_to_"+str(endname)+"_"+str(trip_id)+"\" type=\"veh_"+veh_type+"\" depart=\""+str(starttime)+"\" departLane=\"best\" from=\""+str(idedgestart)+"\" to=\""+str(idedgeend)+"\"/>"
        trip_lines.append(new_trip_line)
    
    #export to xml file in folder
    output_file = open(path + '\Paris-sans-tp\generated_'+veh_type+'_input.xml', 'w')
    output_file.write('<?xml version="1.0" encoding="UTF-8"?>')
    output_file.write('<routes xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/routes_file.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">')
    output_file.write('<vType id="veh_'+veh_type+'" vClass="'+veh_type+'"/>')
    for trip in trip_lines:
        output_file.write(trip)
        output_file.write("\n")
    output_file.write('</routes>')
    output_file.close()