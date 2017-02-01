import pandas as pd
from scipy.cluster.hierarchy import dendrogram, linkage
from geopy.distance import vincenty
from scipy import spatial
import networkx as nx
import geopandas as gpd
import json
import csv
from geojson import Feature, Point, MultiPoint, FeatureCollection
#from shapely.geometry import Point

from functions import *
import Parameters as P

def getServiceArea(queryPoint):
	data_all = readBuildings('../GIS_data/building_all_null.csv')
	
	if len(data_all)>400:
		k = 400
	else:
	    k = len(data_all)

	X_lat_lon = list(data_all['lat_lon'])

	tree = spatial.KDTree(X_lat_lon)
	dist, index_select = tree.query(queryPoint, k=k)

	data = findNClosest(index_select,data_all)

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

	#initial parameters
	total_dist = building_sqft*P.in_builing_piping_sf
	inbuilding_pumping = pump_energy_building(inbuilding_floors)
	inbuilding_flow = SUM_pop*0.2
	inbuilding_treatment_energy = find_treatment_energy(SUM_pop, 0)
	infrastructure = find_infrastructure_energy(SUM_pop, 0, total_dist)
	total_energy = inbuilding_pumping+inbuilding_treatment_energy+infrastructure

	cluster_points = []
	log_energy = []
	cluster_points.append(index_0)
	points_checked = []
	treatment_log = []
	conveyance_log = []
	population_log = []
	X_lat_lon_to_check = []

	totals = {'num_buildings':num_buildings, 'SUM_pop':SUM_pop ,'ELEV_treat':MIN_ELEV, 'total_dist':total_dist, 'inbuilding_pumping':inbuilding_pumping, 'total_energy':total_energy }

	G = nx.Graph()
	points_checked.append(index_0)
	G.add_node(index_0)

	for index, row in data.iterrows():
	   
		points_checked.append(int(index))
		populate_Graph(G, index, data)
		MST_distance = find_MST_distance(G)
		building_floors = data.iloc[int(index)]['num_floor']
		building_sqft = data.iloc[int(index)]['Area_m2']
		building_elevation = data.iloc[int(index)]['ELEV_treat']
		building_population = data.iloc[int(index)]['SUM_pop']
		piping_distance = MST_distance + building_sqft*P.in_builing_piping_sf

		conveyance_energy = find_conveyance_energy(building_elevation, totals['ELEV_treat'], building_floors)
		treatment_energy = find_treatment_energy(building_population, totals['SUM_pop'])
		treatment_embodied = find_treatment_embodied_energy(building_population, totals['SUM_pop'],  ttype = False)
		infrastructure = find_infrastructure_energy(building_population, totals['SUM_pop'], piping_distance)
		total_energy = conveyance_energy + treatment_energy + infrastructure + treatment_embodied
		log_energy.append((index, total_energy))

		if total_energy < totals['total_energy']:
			cluster_points.append(index)
			totals['num_buildings'] += 1
			totals['SUM_pop'] = totals['SUM_pop'] + data.iloc[int(index)]['SUM_pop']
			totals['ELEV_treat'] = min(totals['ELEV_treat'], data.iloc[int(index)]['ELEV_treat'])
			totals['total_dist'] = totals['total_dist'] + piping_distance
			totals['total_energy'] = total_energy

		else:
			G.remove_node(int(index))
		    

	output_points = findNClosest(cluster_points, data)
	sum_population = output_points['SUM_pop'].sum()
	num_houses = int(output_points['SUM_pop'].count())
	coords = []
	for index, row in output_points.iterrows():
	    xy = (row['x_lon'], row['y_lat'])
	    coords.append(xy)  
	points = MultiPoint(coords)
	polygon = getPolygon(output_points)
	polygon_properties = Feature(geometry=polygon, properties={"population": sum_population,"houses": num_houses})
	point_properties = Feature(geometry=points, properties={"population": sum_population,"houses": num_houses})
	#all_data = [points, polygon]
	#collection = FeatureCollection(features = all_data, properties={"population": sum_population,"houses": num_houses})

	with open('../GIS_data/polygon_.geojson', 'w') as outfile: 
		json.dump(polygon, outfile)

	return polygon_properties, point_properties
