# Optimal Scale for Decentralized Water Reuse

This repository consists of the code base for the web tool developed under the publication:
The webtool can be found free of charge at:

If you wish to use the tool for your own analysis please provide proper attribution by citing the work:

''' '''

## Background
The core and integral criterion for sustainable non-potable reuse (NPR) implantation is the issue of system scale. Larger facilities can benefit from the increased "economies of scale" in treatment but in the context of water reuse a tradeoff occurs as in a centralized system the water would be further away from the point of demand which exacerbates the upgradient conveyance and distribution impacts. This project defines a modeling method for decentralized water reuse systems to estimate their economic and environmental impacts under real topographical and demographic conditions. The developed tool estimates both the financial cost and environmental impacts of NPR as a function of treatment scale and optimized conveyance networks. It is based on a heuristic modeling approach using geospatial algorithms to determine the optimal degree of decentralization. The webtool is developed to assess and visualize alternative NPR system designs considering topography, economies of scale and building size.

The developed tool is currently based on the data of the city of San Francisco. However, it is a generalizable tool as long as the required input data is given. See input data section for more details.


## Input Data
The main input data required for the tool to run is a csv with building data of the area of interest. An example dataset can be found under `input_data\combined_buildings_2.csv`. 
The required attributes in the csv file are:
- the lat, lon coordinates of each buildings (x_lon, y_lat), 
- a combined coordinates field in the form of `(lat, lon)`, 
- the building footprint area (Area_m2), 
- the number of floors (num_floor), 
- the building base elevation (ELEV_treat),
- the residential population of the building (SUM_pop_residential) and
- the commercial population of the building (SUM_pop_commercial)

The residential and commercial population attributes are shown how they can be calculated in the example jupyter notebooks found in `jupyter_notebooks` folder.

Other inputs in the model that can be customized are located in the `Parameters.py`. This file includes default parameters that are used in the analysis but can be overridden if better data of the specific location are known. 


## Algorithmic Process
The entire algorithmic process is included in the `optimization2.py` file. 
All the input buildings are loaded and a KD tree is constructed from their locations. The KD tree is used for optimal searching of the closest building to the user query point. 

## Structure



