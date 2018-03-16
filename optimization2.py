from __future__ import print_function
import os,sys,inspect
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
import time

from functions import *
import Parameters as P


data_all = readBuildings('input_data/combined_buildings_2.csv')

if len(data_all)>500:
	k = 500
else:
	k = len(data_all)

X_lat_lon = list(zip(data_all['y_lat'],data_all['x_lon']))

tree = spatial.KDTree(X_lat_lon)

def getServiceArea(queryPoint, path, metric, a, b, c, d, direct, electricity_GHG):
	t2 = time.time()

	begin_time = time.time() - t2

	t_tree = time.time()

	dist, index_select = tree.query(queryPoint, k=k)

	elapsed_tree = time.time() - t_tree

	t_s = time.time()

	data = findN_DataFrame(index_select, data_all)

	elapsed_query = time.time() - t_s

	data = data.reset_index()

	index_0 = 0

	t_dataframe = time.time()
	#initialize
	num_buildings = 1
	SUM_pop_residential = data.iloc[int(index_0)]['SUM_pop_residential']
	SUM_pop_commercial = data.iloc[int(index_0)]['SUM_pop_commercial']
	square_footage = data.iloc[int(index_0)]['Area_m2']
	MIN_ELEV = data.iloc[int(index_0)]['ELEV_treat']
	inbuilding_floors = data.iloc[int(index_0)]['num_floor']
	deque_length = 40
	mydeque = collections.deque(maxlen=deque_length)
	data['metric'] = 0
	data['accept'] = 'start'	

	for i in range(deque_length):
		mydeque.append(False)

	elapsed_dataframe = time.time() - t_dataframe

	t_init_calc = time.time()

	#initial parameters
	total_dist = square_footage*P.in_builing_piping_sf

	#Calculate energy
	if metric == 'energy':
		inbuilding_pumping = pump_energy_building(inbuilding_floors, SUM_pop_residential, SUM_pop_commercial)
		inbuilding_treatment = find_treatment_energy(SUM_pop_residential, SUM_pop_commercial, 0, 0, a, b, c, d) 
		inbuilding_treatment_embodied = find_treatment_embodied_energy(ttype = True)
		infrastructure = find_infrastructure_energy(SUM_pop_residential, SUM_pop_commercial, 0, 0, total_dist)
		total_metric = inbuilding_pumping + inbuilding_treatment + inbuilding_treatment_embodied + infrastructure

	#Calculate cost
	if metric == 'cost':
		inbuilding_pumping = pump_cost_building(inbuilding_floors, SUM_pop_residential, SUM_pop_commercial)
		inbuilding_treatment_embodied, inbuilding_treatment = find_treatment_cost(SUM_pop_residential, SUM_pop_commercial, 0, 0) 
		infrastructure = find_infrastructure_cost(SUM_pop_residential, SUM_pop_commercial, 0, 0, total_dist)
		total_metric = inbuilding_pumping + inbuilding_treatment + inbuilding_treatment_embodied + infrastructure

	#Calculate GHG
	if metric == 'GHG':
		inbuilding_pumping = pump_GHG_building(inbuilding_floors, SUM_pop_residential, SUM_pop_commercial, electricity_GHG)
		inbuilding_treatment = find_treatment_GHG(SUM_pop_residential, SUM_pop_commercial, 0, 0, a, b, c, d, electricity_GHG) 
		inbuilding_treatment_embodied = find_treatment_embodied_GHG(ttype = True) + find_treatment_direct_GHG(direct)
		infrastructure = find_infrastructure_GHG(SUM_pop_residential, SUM_pop_commercial, 0, 0, total_dist)
		total_metric = inbuilding_pumping + inbuilding_treatment + inbuilding_treatment_embodied + infrastructure

	mydeque.append(True)

	cluster_points = pd.DataFrame()
	seen = pd.DataFrame()
	cluster_points = cluster_points.append(data.iloc[int(index_0)])

	X_lat_lon_to_check = []

	totals = {'num_buildings':num_buildings, 'SUM_pop_residential':SUM_pop_residential, 'SUM_pop_commercial':SUM_pop_commercial  ,'ELEV_treat':MIN_ELEV, 'total_dist':total_dist, 'pumping':inbuilding_pumping, 
	'treatment':inbuilding_treatment, 'treatment_embodied':inbuilding_treatment_embodied, 'infrastructure':infrastructure,'total_metric':total_metric}

	iteration_results = []
	iteration_results.append([0, SUM_pop_residential, SUM_pop_commercial, total_metric, inbuilding_pumping, inbuilding_treatment, inbuilding_treatment_embodied, infrastructure])

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
		square_footage = square_footage + building_sqft
		piping_distance = 2*MST_distance + square_footage*P.in_builing_piping_sf


		#Calculate energy
		if metric == 'energy':
			conveyance = find_conveyance_energy(building_elevation, totals['ELEV_treat'], building_floors, building_population_residential, building_population_commercial, totals['SUM_pop_residential'], totals['SUM_pop_commercial'], totals['pumping'])
			treatment = find_treatment_energy(building_population_residential, building_population_commercial, totals['SUM_pop_residential'], totals['SUM_pop_commercial'], a, b, c, d)
			treatment_embodied = find_treatment_embodied_energy(ttype = True)
			infrastructure = find_infrastructure_energy(building_population_residential, building_population_commercial, totals['SUM_pop_residential'], totals['SUM_pop_commercial'], piping_distance)
			total_metric = conveyance + treatment + infrastructure + treatment_embodied

		#Calculate cost
		if metric == 'cost':
			conveyance = totals['pumping'] + find_conveyance_cost(building_elevation, totals['ELEV_treat'], building_floors, building_population_residential, building_population_commercial, totals['SUM_pop_residential'], totals['SUM_pop_commercial'], totals['pumping'])
			treatment_embodied, treatment = find_treatment_cost(building_population_residential, building_population_commercial, totals['SUM_pop_residential'], totals['SUM_pop_commercial'])
			infrastructure = find_infrastructure_cost(building_population_residential, building_population_commercial, totals['SUM_pop_residential'], totals['SUM_pop_commercial'], piping_distance)
			total_metric = conveyance + treatment + infrastructure + treatment_embodied

		#Calculate GHG
		if metric == 'GHG':
			conveyance = totals['pumping'] + find_conveyance_GHG(building_elevation, totals['ELEV_treat'], building_floors, building_population_residential, building_population_commercial, totals['SUM_pop_residential'], totals['SUM_pop_commercial'], totals['pumping'], electricity_GHG)
			treatment = find_treatment_GHG(building_population_residential, building_population_commercial, totals['SUM_pop_residential'], totals['SUM_pop_commercial'], a, b, c, d, electricity_GHG)
			treatment_embodied = find_treatment_embodied_GHG(ttype = True)
			treatment_direct = find_treatment_direct_GHG(direct)
			infrastructure =  find_infrastructure_GHG(building_population_residential, building_population_commercial, totals['SUM_pop_residential'], totals['SUM_pop_commercial'], piping_distance)
			total_metric = conveyance + treatment + infrastructure + treatment_embodied + treatment_direct

		seen = seen.append(row)


		if total_metric < totals['total_metric']:
			arg = False
			acc = 'yes'
			cluster_points = cluster_points.append(row)
			totals['num_buildings'] += 1
			totals['SUM_pop_residential'] = totals['SUM_pop_residential'] + building_population_residential
			totals['SUM_pop_commercial'] = totals['SUM_pop_commercial'] + building_population_commercial
			totals['ELEV_treat'] = min(totals['ELEV_treat'], building_elevation)
			totals['total_dist'] = totals['total_dist'] + piping_distance
			totals['total_metric'] = total_metric
			totals['pumping'] = conveyance
			totals['treatment'] = treatment
			totals['treatment_embodied'] = treatment_embodied
			totals['infrastructure'] = infrastructure
			distance = MST_distance
			iteration_results.append([index, building_population_residential, building_population_commercial, total_metric, conveyance, treatment, treatment_embodied, infrastructure])

		else:
			arg = True
			acc = 'no'
			G.remove_node(int(index))
			total_metric = totals['total_metric']
			square_footage = square_footage - building_sqft

		data.loc[int(index),'metric'] = total_metric
		data.loc[int(index),'accept'] = acc
		mydeque.append(arg)

		elapsed_calc = time.time() - calc_t3
		calc_time += elapsed_calc


		if all(mydeque):
			break

	out_t3 = time.time() 

	sum_population = int(cluster_points['SUM_pop_residential'].sum()+cluster_points['SUM_pop_commercial'].sum())
	num_houses = int(cluster_points['SUM_pop_residential'].count())

	pumping_tot = totals['pumping']
	treatment_tot = totals['treatment']
	treatment_embodied_tot = totals['treatment_embodied']
	piping_tot = totals['infrastructure']

	data['population'] = sum_population
	data['houses'] = num_houses	

	cols = ['index', 'SUM_pop_residential','SUM_pop_commercial', 'metric', 'accept', 'num_floor', 'population', 'houses']
	geojson = df_to_geojson(data, cols)
	point_properties = geojson

	elapsed2 = time.time() - t2
	elapsed_out = time.time() - out_t3

	# print("begin time %s "%begin_time, file=stderr)
	# print("tree time %s "%elapsed_tree, file=stderr)
	# print("init query %s "%elapsed_query, file=stderr)
	# print("init dataf %s "%elapsed_dataframe, file=stderr)
	# print("init time %s "%elapsed_init, file=stderr)
	# print("Grpah time %s "%graph_time, file=stderr)
	# print("MST time %s "%MST_time, file=stderr)
	# print("calc time %s "%calc_time, file=stderr)
	# print("out time %s "%elapsed_out, file=stderr)
	# print("loop time %s "%elapsed2, file=stderr)

	with open(path,'a') as f:
	    writer=csv.writer(f)
	    writer.writerow([])
	    writer.writerow([queryPoint,sum_population,total_metric, pumping_tot, treatment_tot, treatment_embodied_tot, piping_tot])

	iteration_results_df = pd.DataFrame(iteration_results)
	iteration_results_df.to_csv('iteration_results.csv')

	return point_properties
