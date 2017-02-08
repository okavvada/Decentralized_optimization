import pandas as pd
from scipy.cluster.hierarchy import dendrogram, linkage
from geopy.distance import vincenty
from scipy import spatial
import networkx as nx
import geopandas as gpd
import json
import csv
import collections
from geojson import Feature, Point, MultiPoint, FeatureCollection
#from shapely.geometry import Point

from functions import *
import Parameters as P

def getServiceArea(queryPoint, a, b, c, d, e, f, g, h):
	data_all = readBuildings('../GIS_data/building_all_null.csv')
	
	if len(data_all)>500:
		k = 500
	else:
	    k = len(data_all)

	X_lat_lon = list(data_all['lat_lon'])

	tree = spatial.KDTree(X_lat_lon)
	dist, index_select = tree.query(queryPoint, k=k)

	data = findNClosest(index_select, data_all)

	X_lat_lon_select = list(data['lat_lon'])
	# Z = linkage(X_lat_lon_select, 'ward')
	data = data.reset_index()
	# clusters = hierarchical_cluster(X_lat_lon_select, Z)
	index_0 = data[(data['y_lat'] - queryPoint[0])<0.0001].index.tolist()[0]

	#initialize
	num_buildings = 1
	SUM_pop = data.loc[int(index_0)]['SUM_pop']
	building_sqft = data.loc[int(index_0)]['Area_m2']
	MIN_ELEV = data.loc[int(index_0)]['ELEV_treat']
	inbuilding_floors = data.loc[int(index_0)]['num_floor']
	mydeque = collections.deque(maxlen=50)
	data['energy'] = 0
	data['accept'] = 'no'	

	for i in range(50):
		mydeque.append(False)

	#initial parameters
	total_dist = building_sqft*P.in_builing_piping_sf
	inbuilding_pumping = pump_energy_building(inbuilding_floors, SUM_pop)
	inbuilding_treatment_energy = find_treatment_energy(SUM_pop, 0, a, b, c, d) + find_treatment_embodied_energy(SUM_pop, 0, e, f, g, h, ttype = True)
	infrastructure = find_infrastructure_energy(SUM_pop, 0, total_dist)
	total_energy = inbuilding_pumping+inbuilding_treatment_energy+infrastructure

	cluster_points = []
	not_selected = []
	seen = []
	log_energy_array = []
	accept = []
	cluster_points.append(index_0)
	treatment_log = []
	conveyance_log = []
	population_log = []
	checks = []
	X_lat_lon_to_check = []

	totals = {'num_buildings':num_buildings, 'SUM_pop':SUM_pop ,'ELEV_treat':MIN_ELEV, 'total_dist':total_dist, 'inbuilding_pumping':inbuilding_pumping, 'total_energy':total_energy }
	#accept.append('yes')
	#log_energy_array.append(total_energy)

	G = nx.Graph()
	G.add_node(index_0)

	for index, row in data[1:].iterrows():
	   
		populate_Graph(G, index, data)
		MST_distance = find_MST_distance(G)
		building_floors = data.iloc[int(index)]['num_floor']
		building_sqft = data.iloc[int(index)]['Area_m2']
		building_elevation = data.iloc[int(index)]['ELEV_treat']
		building_population = data.iloc[int(index)]['SUM_pop']
		piping_distance = 2*MST_distance + building_sqft*P.in_builing_piping_sf

		conveyance_energy = find_conveyance_energy(building_elevation, totals['ELEV_treat'], building_floors, building_population, totals['SUM_pop'])
		treatment_energy = find_treatment_energy(building_population, totals['SUM_pop'], a, b, c, d)
		treatment_embodied = find_treatment_embodied_energy(building_population, totals['SUM_pop'], e, f, g, h, ttype = True)
		infrastructure = find_infrastructure_energy(building_population, totals['SUM_pop'], piping_distance)
		total_energy = conveyance_energy + treatment_energy + infrastructure + treatment_embodied

		seen.append(index)

		if total_energy < totals['total_energy']:
			arg = False
			acc = 'yes'
			cluster_points.append(index)
			totals['num_buildings'] += 1
			totals['SUM_pop'] = totals['SUM_pop'] + data.iloc[int(index)]['SUM_pop']
			totals['ELEV_treat'] = min(totals['ELEV_treat'], data.iloc[int(index)]['ELEV_treat'])
			totals['total_dist'] = totals['total_dist'] + piping_distance
			totals['total_energy'] = total_energy
			accept.append('yes')

		else:
			arg = True
			acc = 'no'
			G.remove_node(int(index))
			not_selected.append(int(index))
			accept.append('no')

		data.set_value(index,'energy',total_energy)
		data.set_value(index,'accept',acc)

		#log_energy_array.append(total_energy)
		mydeque.append(arg)

		if all(mydeque):
			break

	#data['energy'] = log_energy_array
	#data['accept'] = accept	    

	output_points = findNClosest(cluster_points, data)
	not_output_points = findNClosest(not_selected, data) 
	seen_points = findNClosest(seen, data)

	output_points.to_csv('../GIS_data/test_results/output_points.csv')
	data.to_csv('../GIS_data/test_results/all_points.csv')
	not_output_points.to_csv('../GIS_data/test_results/not_output_points.csv')
	seen_points.to_csv('../GIS_data/test_results/seen_points.csv')

	sum_population = int(output_points['SUM_pop'].sum())
	num_houses = int(output_points['SUM_pop'].count())

	data['population'] = sum_population
	data['houses'] = num_houses	

	#polygon = getPolygon(output_points)
	#polygon_properties = Feature(geometry=polygon, properties={"population": sum_population,"houses": num_houses})
	polygon_properties= []

	cols = ['index', 'SUM_pop', 'energy', 'accept', 'num_floor', 'population', 'houses']
	geojson = df_to_geojson(data, cols)
	point_properties = geojson
	#point_properties = Feature(geometry=points, properties={"population": sum_population,"houses": num_houses})
	#all_data = [points, polygon]
	#collection = FeatureCollection(features = all_data, properties={"population": sum_population,"houses": num_houses})

	#with open('../GIS_data/polygon_.geojson', 'w') as outfile: 
		#json.dump(polygon, outfile)

	return polygon_properties, point_properties
