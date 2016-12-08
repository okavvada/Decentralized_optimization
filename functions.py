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

def create_tree(X_lat_lon_to_check, query_point):
    tree = spatial.KDTree(X_lat_lon_to_check)
    dist, index = tree.query(query_point, k=len(X_lat_lon_to_check))
    return dist, index

def populate_Graph(G, start, index, dist, data):
    for start in index:
        G.add_node(start)
        for destination in index:
            G.add_node(destination)
            dist = vincenty(data.iloc[start]['lat_lon'], data.iloc[destination]['lat_lon']).meters
            G.add_path([item, destination], weight=dist)

def find_MST_distance(G):
    MST_edges = nx.minimum_spanning_edges(G, weight='weight')
    edgelist=list(MST_edges)
    MST_distance = 0
    MST_distance = sum(list(map(lambda t: t[2].get('weight', 1), edgelist)))
    return MST_distance

def distance_lat_lon(df, index1, index2):
    p1 = df.iloc[int(index1)]['lat_lon']
    p2 = df.iloc[int(index2)]['lat_lon']
    distance = vincenty(p1, p2).meters
    return distance #m

def ground_elevation(df, index1, totals):
    min_elev = min(df.iloc[int(index1)]['ELEV_treat'],totals['ELEV_treat'])
    max_elev = max(df.iloc[int(index1)]['ELEV_treat'],totals['ELEV_treat'])
    elev_diff = max_elev-min_elev
    return elev_diff #m

def ground_elevation_energy(df, index1, totals):
    elev_diff = ground_elevation(df, index1, totals)
    pump = elev_diff/3600*1*3.6 #MJ/m3
    return pump #MJ/m3

def pump_energy_building(floors):
    elev_diff = floors*3
    pump = elev_diff/3600*1*3.6 #MJ/m3
    return pump #MJ/m3

def calc_flow(df, index1, totals):
    peop1 = df.iloc[int(index1)]['SUM_pop']
    peop2 = totals['SUM_pop']
    flow_tot = (peop1+peop2)*0.2 #m3/day
    return flow_tot #m3/day

def find_treatment_energy(df, index1, totals):
    flow = calc_flow(df, index1, totals)
    #Find embodied energy function
    treat_energy = 8*(flow)**(-0.1)*3.6*0.8
    return treat_energy

def find_treatment_embodied_energy(df, index1, totals,  ttype = False):
    if type = False:
        treat_energy = 0
    else:
        flow = calc_flow(df, index1, totals)
        #treat_energy = 9.5*(flow)**(-0.3)*3.6
        treat_energy = 8*(flow)**(-0.1)*3.6
    return treat_energy

def find_conveyance_energy(df, index1, totals, piping, floors):
    pump = ground_elevation_energy(df, index1, totals)
    pump_building = pump_energy_building(floors)
    energy = pipe_m3+pump+pump_building
    return energy

def find_infrastructure_energy(df, index1, totals, piping):
    flow = calc_flow(df, index1, totals) #m3/day
    flow_s = flow/(24*3600)
    pipe = piping*P.piping_embodied #MJ/d
    pipe_m3 = pipe/flow #MJ/m3
    return pipe_m3
