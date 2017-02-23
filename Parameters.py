piping_embodied = 90 #MJ/m (diameter = 100 mm)
pipe_lifetime = 25 #years
water_weight = 9.8 #KN/m3
wastewater_demand_residential = 0.185 #m3/person-day http://www.sfwater.org/modules/showdocument.aspx?documentid=6543
wastewater_demand_commercial = 0.12 #m3/person-day  http://www.sfwater.org/modules/showdocument.aspx?documentid=6543 with 600,000 employees
npr_percent_residential = 0.5  # http://ggashrae.org/images/meeting/021116/paula_kehoe_ggashrae_02_11_2016.pdf
npr_percent_commercial = 0.95 # http://ggashrae.org/images/meeting/021116/paula_kehoe_ggashrae_02_11_2016.pdf
npr_water_demand_residential =  wastewater_demand_residential*npr_percent_residential#m3/person-day
npr_water_demand_commercial = wastewater_demand_commercial*npr_percent_commercial #m3/person-day
pump_efficiency = 0.45
in_builing_piping_sf = 0.06 #m/m2 #Hasik LCA building