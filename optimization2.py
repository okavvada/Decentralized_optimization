from __future__ import print_function
from sys import stderr
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
import time

from functions import *
import Parameters as P

data_all = readBuildings('../GIS_data/combined_buildings_2.csv')

if len(data_all)>500:
	k = 500
else:
	k = len(data_all)

X_lat_lon = list(zip(data_all['y_lat'],data_all['x_lon']))

tree = spatial.KDTree(X_lat_lon)

def getServiceArea(queryPoint, path, a, b, c, d, e, f, g, h):
	t2 = time.time()

	begin_time = time.time() - t2

	t_tree = time.time()

	dist, index_select = tree.query(queryPoint, k=k)

	elapsed_tree = time.time() - t_tree

	t_s = time.time()

	data = findN_DataFrame(index_select, data_all)

	elapsed_query = time.time() - t_s

	#X_lat_lon_select = list(data['lat_lon'])
	# Z = linkage(X_lat_lon_select, 'ward')
	data = data.reset_index()
	# clusters = hierarchical_cluster(X_lat_lon_select, Z)
	index_0 = data[(data['y_lat'] - queryPoint[0])<0.0001].index.tolist()[0]

	t_dataframe = time.time()
	#initialize
	num_buildings = 1
	SUM_pop_residential = data.iloc[int(index_0)]['SUM_pop_residential']
	SUM_pop_commercial = data.iloc[int(index_0)]['SUM_pop_commercial']
	building_sqft = data.iloc[int(index_0)]['Area_m2']
	MIN_ELEV = data.iloc[int(index_0)]['ELEV_treat']
	inbuilding_floors = data.iloc[int(index_0)]['num_floor']
	deque_length = 150
	mydeque = collections.deque(maxlen=deque_length)
	data['energy'] = 0
	data['accept'] = 'start'	

	for i in range(deque_length):
		mydeque.append(False)

	elapsed_dataframe = time.time() - t_dataframe

	t_init_calc = time.time()

	#initial parameters
	total_dist = building_sqft*P.in_builing_piping_sf
	inbuilding_pumping = pump_energy_building(inbuilding_floors, SUM_pop_residential, SUM_pop_commercial)
	inbuilding_treatment_energy = find_treatment_energy(SUM_pop_residential, SUM_pop_commercial, 0, 0, a, b, c, d) + find_treatment_embodied_energy(SUM_pop_residential, SUM_pop_commercial, 0, 0, e, f, g, h, ttype = True)
	infrastructure = find_infrastructure_energy(SUM_pop_residential, SUM_pop_commercial, 0, 0, total_dist)
	total_energy = inbuilding_pumping+inbuilding_treatment_energy+infrastructure

	cluster_points = pd.DataFrame()
	#not_selected = pd.DataFrame()
	seen = pd.DataFrame()
	#log_energy_array = []
	#accept = []
	cluster_points = cluster_points.append(data.iloc[int(index_0)])

	X_lat_lon_to_check = []

	totals = {'num_buildings':num_buildings, 'SUM_pop_residential':SUM_pop_residential, 'SUM_pop_commercial':SUM_pop_commercial  ,'ELEV_treat':MIN_ELEV, 'total_dist':total_dist, 'inbuilding_pumping':inbuilding_pumping, 'total_energy':total_energy }
	#accept.append('yes')
	#log_energy_array.append(total_energy)

	elapsed_init = time.time() - t_init_calc

	distance = 0

	graph_time = 0
	MST_time = 0
	calc_time = 0

	G = nx.Graph()
	G.add_node(index_0, pos=data.iloc[int(index_0)]['lat_lon'])

	for index, row in data[1:].iterrows():
		t = time.time()
	   
		populate_Graph(G, index, data)

		elapsed = time.time() - t
		graph_time += elapsed

		t1 = time.time()

		MST_distance = find_MST_distance(G, index, distance)

		elapsed1 = time.time() - t1
		MST_time += elapsed1

		calc_t3 = time.time() 


		building_floors = row['num_floor']
		building_sqft = row['Area_m2']
		building_elevation = row['ELEV_treat']
		building_population_residential = row['SUM_pop_residential']
		building_population_commercial = row['SUM_pop_commercial']
		piping_distance = 2*MST_distance + building_sqft*P.in_builing_piping_sf

		conveyance_energy = find_conveyance_energy(building_elevation, totals['ELEV_treat'], building_floors, building_population_residential, building_population_commercial, totals['SUM_pop_residential'], totals['SUM_pop_commercial'])
		treatment_energy = find_treatment_energy(building_population_residential, building_population_commercial, totals['SUM_pop_residential'], totals['SUM_pop_commercial'],  a, b, c, d)
		treatment_embodied = find_treatment_embodied_energy(building_population_residential, building_population_commercial, totals['SUM_pop_residential'], totals['SUM_pop_commercial'], e, f, g, h, ttype = True)
		infrastructure = find_infrastructure_energy(building_population_residential, building_population_commercial, totals['SUM_pop_residential'], totals['SUM_pop_commercial'], piping_distance)
		total_energy = conveyance_energy + treatment_energy + infrastructure + treatment_embodied

		seen = seen.append(row)


		if total_energy < totals['total_energy']:
			arg = False
			acc = 'yes'
			cluster_points = cluster_points.append(row)
			totals['num_buildings'] += 1
			totals['SUM_pop_residential'] = totals['SUM_pop_residential'] + building_population_residential
			totals['SUM_pop_commercial'] = totals['SUM_pop_commercial'] + building_population_commercial
			totals['ELEV_treat'] = min(totals['ELEV_treat'], building_elevation)
			totals['total_dist'] = totals['total_dist'] + piping_distance
			totals['total_energy'] = total_energy
			distance = MST_distance
			#accept.append('yes')

		else:
			arg = True
			acc = 'no'
			G.remove_node(int(index))
			#not_selected = not_selected.append(row)
			#accept.append('no')

		data.loc[int(index),'energy'] = total_energy
		data.loc[int(index),'accept'] = acc

		#data.set_value(index,'energy',total_energy)
		#data.set_value(index,'accept',acc)

		#log_energy_array.append(total_energy)
		mydeque.append(arg)

		elapsed_calc = time.time() - calc_t3
		calc_time += elapsed_calc


		if all(mydeque):
			break

	out_t3 = time.time() 
    

	#output_points = findNClosest(cluster_points, data)
	#not_output_points = findNClosest(not_selected, data) 
	#seen_points = findNClosest(seen, data)

	cluster_points.to_csv('../GIS_data/test_results/output_points.csv')
	data.to_csv('../GIS_data/test_results/all_points.csv')
	#not_selected.to_csv('../GIS_data/test_results/not_output_points.csv')
	seen.to_csv('../GIS_data/test_results/seen_points.csv')

	sum_population = int(cluster_points['SUM_pop_residential'].sum()+cluster_points['SUM_pop_commercial'].sum())
	num_houses = int(cluster_points['SUM_pop_residential'].count())

	data['population'] = sum_population
	data['houses'] = num_houses	

	polygon_properties= []

	cols = ['index', 'SUM_pop_residential','SUM_pop_commercial', 'energy', 'accept', 'num_floor', 'population', 'houses']
	geojson = df_to_geojson(data, cols)
	point_properties = geojson

	elapsed2 = time.time() - t2
	elapsed_out = time.time() - out_t3

	print("begin time %s "%begin_time, file=stderr)
	print("tree time %s "%elapsed_tree, file=stderr)
	print("init query %s "%elapsed_query, file=stderr)
	print("init dataf %s "%elapsed_dataframe, file=stderr)
	print("init time %s "%elapsed_init, file=stderr)
	print("Grpah time %s "%graph_time, file=stderr)
	print("MST time %s "%MST_time, file=stderr)
	print("calc time %s "%calc_time, file=stderr)
	print("out time %s "%elapsed_out, file=stderr)
	print("loop time %s "%elapsed2, file=stderr)

	with open(path,'a') as f:
	    writer=csv.writer(f)
	    writer.writerow([])
	    writer.writerow([queryPoint,sum_population])

	return polygon_properties, point_properties
