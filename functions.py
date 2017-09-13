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

def findN_DataFrame(index, dataframe):
    data = dataframe.iloc[index,:]
    return data

def distance(lat_lon1, latlon2):
    dist = vincenty(lat_lon1, latlon2).meters
    return dist

def create_tree(X_lat_lon_to_check, query_point):
    tree = spatial.KDTree(X_lat_lon_to_check)
    dist, index = tree.query(query_point, k=len(X_lat_lon_to_check))
    return dist, index

def populate_Graph(G, start, data):
    G.add_node(start, pos=data.iloc[int(start)]['lat_lon'])
    position=nx.get_node_attributes(G,'pos')
    for destination in G.nodes():
        dist = vincenty(position[start], position[destination]).meters
        G.add_edge(start, destination, weight=dist)

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

def calc_water_flow(building_pop_residential, building_pop_commercial,  totals_pop_residential, totals_pop_commercial):
    peop_residential = building_pop_residential + totals_pop_residential
    peop_commercial = building_pop_commercial + totals_pop_commercial
    flow_tot = peop_residential*P.npr_water_demand_residential + peop_commercial*P.npr_water_demand_commercial #m3/day
    return flow_tot #m3/day

def calc_wastewater_flow(building_pop_residential, building_pop_commercial,  totals_pop_residential, totals_pop_commercial):
    peop_residential = building_pop_residential+totals_pop_residential
    peop_commercial = building_pop_commercial + totals_pop_commercial
    flow_tot = peop_residential*P.wastewater_demand_residential + peop_commercial*P.wastewater_demand_commercial #m3/day
    return flow_tot #m3/day

def ground_elevation_energy(building_elevation, totals_elevation, building_pop_residential, building_pop_commercial,  totals_pop_residential, totals_pop_commercial):
    elev_diff = ground_elevation(building_elevation, totals_elevation)
    flow_total = calc_water_flow(building_pop_residential, building_pop_commercial,  totals_pop_residential, totals_pop_commercial) #m3/day
    pump = elev_diff*P.water_weight*3.6/(3600*P.pump_efficiency) #MJ/m3
    return pump #MJ/m3

def pump_energy_building(floors, building_pop_residential, building_pop_commercial):
    elev_diff = floors*3
    flow_building = calc_water_flow(building_pop_residential, building_pop_commercial, 0, 0) #m3/day
    pump = elev_diff*P.water_weight*3.6/(3600*P.pump_efficiency) #MJ/m3
    return pump #MJ/m3


def find_treatment_energy(building_pop_residential, building_pop_commercial,  totals_pop_residential, totals_pop_commercial, a, b,c,d):
    flow = calc_wastewater_flow(building_pop_residential, building_pop_commercial,  totals_pop_residential, totals_pop_commercial)
    treat_energy = (a*(flow)**(b)+c*flow+d)*3.6
    return treat_energy 

def find_treatment_embodied_energy(ttype=False):
    if ttype == False:
        treat_energy = 0
    else:
        treat_energy = P.treatment_embodied_energy*3.6
    return treat_energy #MJ/m3


def find_conveyance_energy(building_elevation, totals_elevation, floors, building_pop_residential, building_pop_commercial,  totals_pop_residential, totals_pop_commercial):
    pump = ground_elevation_energy(building_elevation, totals_elevation, building_pop_residential, building_pop_commercial,  totals_pop_residential, totals_pop_commercial)
    pump_building = pump_energy_building(floors, building_pop_residential, building_pop_commercial)
    energy = pump + pump_building
    return energy

def find_infrastructure_energy(building_pop_residential, building_pop_commercial,  totals_pop_residential, totals_pop_commercial, piping):
    flow = calc_water_flow(building_pop_residential, building_pop_commercial,  totals_pop_residential, totals_pop_commercial) #m3/day
    pipe = piping*P.piping_embodied/P.pipe_lifetime #MJ
    pipe_m3 = pipe/(flow*365) #MJ/m3
    return pipe_m3


def pump_cost_building(floors, building_pop_residential, building_pop_commercial):
    energy = pump_energy_building(floors, building_pop_residential, building_pop_commercial) #MJ/m3
    cost = energy/3.6*P.electricity_cost #$/m3
    return cost

def find_treatment_cost(building_pop_residential, building_pop_commercial,  totals_pop_residential, totals_pop_commercial):
    flow = calc_wastewater_flow(building_pop_residential, building_pop_commercial,  totals_pop_residential, totals_pop_commercial) #m3/day
    total_people = building_pop_residential+ building_pop_commercial+totals_pop_residential+totals_pop_commercial
    if total_people<=50:
        treat_cost = 601.52*total_people**(-0.361) * total_people #$/y Eggimann connection rates
        treat_cost_m3 = treat_cost/(flow*365) #$/m3
        treat_cap_cost_m3 = treat_cost_m3*0.05 #$/m3 5% capital costs Montoya 2015
        treat_oper_cost_m3 = treat_cost_m3*0.95 #$/m3
    else:
        capex = (9512.8*total_people**(-0.209))*total_people/P.lifetime_WWTP #$/y Eggimann decentralization scale
        opex = (243.45*total_people**(-0.171))*total_people  #$/y Eggimann decentralization scale
        treat_cost_cap = capex+opex #$/y Eggimann decentralization scale
        treat_cap_cost_m3 = capex/(flow*365) #$/m3
        treat_oper_cost_m3 = opex/(flow*365) #$/m3
    return treat_cap_cost_m3, treat_oper_cost_m3

def find_infrastructure_cost(building_pop_residential, building_pop_commercial,  totals_pop_residential, totals_pop_commercial, piping):
    flow = calc_water_flow(building_pop_residential, building_pop_commercial,  totals_pop_residential, totals_pop_commercial) #m3/day
    pipe = piping*P.piping_cost/P.pipe_lifetime #$
    pipe_m3 = pipe/(flow*365) #$/m3
    return pipe_m3


def find_conveyance_cost(building_elevation, totals_elevation, floors, building_pop_residential, building_pop_commercial,  totals_pop_residential, totals_pop_commercial):
    pump_energy = find_conveyance_energy(building_elevation, totals_elevation, floors, building_pop_residential, building_pop_commercial,  totals_pop_residential, totals_pop_commercial)
    pumping_cost = pump_energy/3.6*P.electricity_cost #$/m3
    return pumping_cost


def pump_GHG_building(floors, building_pop_residential, building_pop_commercial):
    energy = pump_energy_building(floors, building_pop_residential, building_pop_commercial) #MJ/m3
    pump_GHG = energy/3.6*P.electricity_GHG #kg/m3
    return pump_GHG #kg/m3

def find_treatment_GHG(building_pop_residential, building_pop_commercial,  totals_pop_residential, totals_pop_commercial, a, b, c, d):
    treat_energy = find_treatment_energy(building_pop_residential, building_pop_commercial,  totals_pop_residential, totals_pop_commercial, a, b, c, d)
    treat_GHG = treat_energy/3.6*P.electricity_GHG 
    return treat_GHG #kg/m3

def find_treatment_embodied_GHG(ttype=False):
    if ttype == False:
        treat_GHG = 0
    else:
        treat_GHG = P.treatment_embodied_GHG
    return treat_GHG

def find_treatment_direct_GHG(direct):
    return direct #kg/m3

def find_infrastructure_GHG(building_pop_residential, building_pop_commercial,  totals_pop_residential, totals_pop_commercial, piping):
    flow = calc_water_flow(building_pop_residential, building_pop_commercial,  totals_pop_residential, totals_pop_commercial) #m3/day
    pipe = piping*P.piping_embodied/3.6*P.US_electricity_GHG/P.pipe_lifetime #kg/y
    pipe_m3 = pipe/(flow*365) #kg/m3
    return pipe_m3

def find_conveyance_GHG(building_elevation, totals_elevation, floors, building_pop_residential, building_pop_commercial,  totals_pop_residential, totals_pop_commercial):
    pump_energy = find_conveyance_energy(building_elevation, totals_elevation, floors, building_pop_residential, building_pop_commercial,  totals_pop_residential, totals_pop_commercial)
    pumping_GHG = pump_energy/3.6*P.electricity_GHG #$/m3
    return pumping_GHG


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