from geopy.distance import vincenty
import networkx as nx
from scipy.cluster.hierarchy import dendrogram, linkage
import Parameters as P

def hierarchical_cluster(X_lat_lon, Z):
    clusters = {}
    i = 1
    for item in Z:
        if (item[0]<len(X_lat_lon)) and (item[1]<len(X_lat_lon)):
            clusters.update({i:[int(item[0]),int(item[1])]})
            i += 1
        elif (item[0]<len(X_lat_lon)) and (item[1]>=len(X_lat_lon)):
            ind_new = int(item[1]-len(X_lat_lon)+1)
            old = clusters[ind_new]
            new = old + [int(item[0])]
            clusters.update({i:(new)})
            i += 1
        elif (item[0]>=len(X_lat_lon)) and (item[1]<len(X_lat_lon)):
            ind_new = int(item[0]-len(X_lat_lon)+1)
            old = clusters[ind_new]
            new=old + [int(item[1])]
            clusters.update({i:new})
            i += 1 
        elif (item[0]>=len(X_lat_lon)) and (item[1]>=len(X_lat_lon)):
            ind_new_1 = int(item[0]-len(X_lat_lon)+1)
            ind_new_2 = int(item[1]-len(X_lat_lon)+1)
            old_1 = clusters[ind_new_1]
            old_2 = clusters[ind_new_2]
            new = old_1 + old_2
            clusters.update({i:new})
            i += 1 
    return clusters

def distance(lat_lon1, latlon2):
    dist = vincenty(lat_lon1, latlon2).meters
    return dist

def create_tree(X_lat_lon_to_check, query_point):
    tree = spatial.KDTree(X_lat_lon_to_check)
    dist, index = tree.query(query_point, k=len(X_lat_lon_to_check))
    return dist, index

def populate_Graph(G, start, data):
    G.add_node(start)
    for destination in G.nodes():
        dist = vincenty(data.iloc[int(start)]['lat_lon'], data.iloc[int(destination)]['lat_lon']).meters
        G.add_edge(start, destination, weight=dist)

def find_MST_distance(G):
    MST_edges = nx.minimum_spanning_edges(G, weight='weight')
    edgelist=list(MST_edges)
    MST_distance = 0
    MST_distance = sum(list(map(lambda t: t[2].get('weight', 1), edgelist)))
    return MST_distance

def ground_elevation(building_elevation, totals_elevation):
    min_elev = min(building_elevation,totals_elevation)
    max_elev = max(building_elevation,totals_elevation)
    elev_diff = max_elev-min_elev
    return elev_diff #m

def ground_elevation_energy(building_elevation, totals_elevation):
    elev_diff = ground_elevation(building_elevation, totals_elevation)
    pump = elev_diff*P.water_weight/1000 #MJ/m3
    return pump #MJ/m3

def pump_energy_building(floors):
    elev_diff = floors*3
    pump = elev_diff*P.water_weight/1000 #MJ/m3
    return pump #MJ/m3

def calc_flow(building_pop, totals_pop):
    peop1 = building_pop
    peop2 = totals_pop
    flow_tot = (peop1+peop2)*P.water_demand #m3/day
    return flow_tot #m3/day

def find_treatment_energy(building_pop, totals_pop):
    flow = calc_flow(building_pop, totals_pop)
    #Find embodied energy function
    treat_energy = 9.5*(flow)**(-0.3)*3.6
    return treat_energy

def find_treatment_embodied_energy(building_pop, totals_pop,  ttype = False):
    if ttype == False:
        treat_energy = 0
    else:
        flow = calc_flow(building_pop, totals_pop)
        treat_energy = 9.5*(flow)**(-0.3)*3.6
        #treat_energy = 8*(flow)**(-0.1)*3.6
    return treat_energy

def find_conveyance_energy(building_elevation, totals_elevation, floors):
    pump = ground_elevation_energy(building_elevation, totals_elevation)
    pump_building = pump_energy_building(floors)
    energy = pump + pump_building
    return energy

def find_infrastructure_energy(building_pop, totals_pop, piping):
    flow = calc_flow(building_pop, totals_pop) #m3/day
    flow_s = flow/(24*3600)
    pipe = piping*P.piping_embodied/P.pipe_lifetime #MJ/m
    pipe_m3 = pipe/(flow*365) #MJ/m3
    return pipe_m3
