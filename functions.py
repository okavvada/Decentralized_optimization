from geopy.distance import vincenty
import networkx as nx
import pandas as pd
from scipy.cluster.hierarchy import dendrogram, linkage
from shapely.geometry import Point
from geojson import Polygon, Feature
from scipy.spatial import ConvexHull
import json
import Parameters as P


def readBuildings(path):
	data_all = pd.read_csv(path)
	return data_all


# def findN_DataFrame(index, dataframe):
# 	data = pd.DataFrame()
# 	for i in index:
# 	    select_row = dataframe.iloc[[i]]
# 	    data = data.append(select_row)
# 	return data

def findN_DataFrame(index, dataframe):
    data = dataframe.iloc[index,:]
    return data


# def hierarchical_cluster(X_lat_lon, Z):
#     clusters = {}
#     i = 1
#     for item in Z:
#         if (item[0]<len(X_lat_lon)) and (item[1]<len(X_lat_lon)):
#             clusters.update({i:[int(item[0]),int(item[1])]})
#             i += 1
#         elif (item[0]<len(X_lat_lon)) and (item[1]>=len(X_lat_lon)):
#             ind_new = int(item[1]-len(X_lat_lon)+1)
#             old = clusters[ind_new]
#             new = old + [int(item[0])]
#             clusters.update({i:(new)})
#             i += 1
#         elif (item[0]>=len(X_lat_lon)) and (item[1]<len(X_lat_lon)):
#             ind_new = int(item[0]-len(X_lat_lon)+1)
#             old = clusters[ind_new]
#             new=old + [int(item[1])]
#             clusters.update({i:new})
#             i += 1 
#         elif (item[0]>=len(X_lat_lon)) and (item[1]>=len(X_lat_lon)):
#             ind_new_1 = int(item[0]-len(X_lat_lon)+1)
#             ind_new_2 = int(item[1]-len(X_lat_lon)+1)
#             old_1 = clusters[ind_new_1]
#             old_2 = clusters[ind_new_2]
#             new = old_1 + old_2
#             clusters.update({i:new})
#             i += 1 
#     return clusters

def distance(lat_lon1, latlon2):
    dist = vincenty(lat_lon1, latlon2).meters
    return dist

def create_tree(X_lat_lon_to_check, query_point):
    tree = spatial.KDTree(X_lat_lon_to_check)
    dist, index = tree.query(query_point, k=len(X_lat_lon_to_check))
    return dist, index

# def populate_Graph(G, start, data):
#     G.add_node(start)
#     for destination in G.nodes():
#         dist = vincenty(data.iloc[int(start)]['lat_lon'], data.iloc[int(destination)]['lat_lon']).meters
#         G.add_edge(start, destination, weight=dist)

def populate_Graph(G, start, data):
    G.add_node(start, pos=data.iloc[int(start)]['lat_lon'])
    position=nx.get_node_attributes(G,'pos')
    for destination in G.nodes():
        dist = vincenty(position[start], position[destination]).meters
        G.add_edge(start, destination, weight=dist)

# def find_MST_distance(G, start, previous_dist):
#     MST_edges = nx.minimum_spanning_edges(G, weight='weight')
#     edgelist=list(MST_edges)
#     MST_distance = 0
#     MST_distance = sum(list(map(lambda t: t[2].get('weight', 1), edgelist)))
#     return MST_distance

def find_MST_distance(G, start, previous_dist):
    distance = 9999999999
    for i in G.edge[start]:
        if i!=start and G.edge[start][i].get('weight', 1)<distance:
            distance = G.edge[start][i].get('weight', 1)
    MST_distance = previous_dist + distance
    return MST_distance

def ground_elevation(building_elevation, totals_elevation):
    min_elev = min(building_elevation,totals_elevation)
    max_elev = max(building_elevation,totals_elevation)
    elev_diff = max_elev-min_elev
    return elev_diff #m

def calc_water_flow(building_pop, totals_pop):
    peop1 = building_pop
    peop2 = totals_pop
    flow_tot = (peop1+peop2)*P.water_demand #m3/day
    return flow_tot #m3/day

def calc_wastewater_flow(building_pop, totals_pop):
    peop1 = building_pop
    peop2 = totals_pop
    flow_tot = (peop1+peop2)*P.wastewater_demand #m3/day
    return flow_tot #m3/day

def ground_elevation_energy(building_elevation, totals_elevation, building_pop, totals_pop):
    elev_diff = ground_elevation(building_elevation, totals_elevation)
    flow_total = calc_water_flow(building_pop, totals_pop) #m3/day
    pump = elev_diff*P.water_weight*3.6/(3600*P.pump_efficiency) #MJ/m3
    return pump #MJ/m3

def pump_energy_building(floors, building_pop):
    elev_diff = floors*3
    flow_building = calc_water_flow(building_pop, 0) #m3/day
    pump = elev_diff*P.water_weight*3.6/(3600*P.pump_efficiency) #MJ/m3
    return pump #MJ/m3


def find_treatment_energy(building_pop, totals_pop, a, b,c,d):
    flow = calc_wastewater_flow(building_pop, totals_pop)
    #Find embodied energy function
    treat_energy = (a*(flow)**(b)+c*flow+d)*3.6
    #treat_energy = -0.047*(flow)+(2)
    return treat_energy

def find_treatment_embodied_energy(building_pop, totals_pop, a, b, c, d, ttype=False):
    if ttype == False:
        treat_energy = 0
    else:
        flow = calc_wastewater_flow(building_pop, totals_pop)
        treat_energy = (a*(flow)**(b)+c*flow+d)*3.6
    return treat_energy

def find_conveyance_energy(building_elevation, totals_elevation, floors, building_pop, totals_pop):
    pump = ground_elevation_energy(building_elevation, totals_elevation, building_pop, totals_pop)
    pump_building = pump_energy_building(floors, building_pop)
    energy = pump + pump_building
    return energy

def find_infrastructure_energy(building_pop, totals_pop, piping):
    flow = calc_water_flow(building_pop, totals_pop) #m3/day
    pipe = piping*P.piping_embodied/P.pipe_lifetime #MJ
    pipe_m3 = pipe/(flow*365) #MJ/m3
    return pipe_m3


def df_to_geojson(df, properties, lat='y_lat', lon='x_lon'):
    geojson = {'type':'FeatureCollection', 'features':[]}
    for _, row in df.iterrows():
        feature = {'type':'Feature',
                   'properties':{},
                   'geometry':{'type':'Point',
                               'coordinates':[]}}
        feature['geometry']['coordinates'] = [row[lon],row[lat]]
        for prop in properties:
            feature['properties'][prop] = row[prop]
        geojson['features'].append(feature)
    return geojson