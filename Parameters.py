piping_embodied = 240 #MJ/m (diameter = 100 mm)
piping_cost = 500 # $/m ###CHECK Bradshaw
pipe_lifetime = 25 #years
water_weight = 9.8 #KN/m3
wastewater_demand_residential = 0.19 #m3/person-day http://www.sfwater.org/modules/showdocument.aspx?documentid=6543
wastewater_demand_commercial = 0.12 #m3/person-day  http://www.sfwater.org/modules/showdocument.aspx?documentid=6543 with 600,000 employees
npr_percent_residential = 0.5  # http://ggashrae.org/images/meeting/021116/paula_kehoe_ggashrae_02_11_2016.pdf
npr_percent_commercial = 0.95 # http://ggashrae.org/images/meeting/021116/paula_kehoe_ggashrae_02_11_2016.pdf
npr_water_demand_residential =  wastewater_demand_residential*npr_percent_residential#m3/person-day
npr_water_demand_commercial = wastewater_demand_commercial*npr_percent_commercial #m3/person-day
lifetime_WWTP = 30 #years Eggimann connection rates
pump_efficiency = 0.45
in_builing_piping_sf = 0.05 #m/m2 #Hasik LCA building
electricity_cost = 0.12 #$/kWh EIA
US_electricity_GHG = 0.59 #kgCO2/kWh (EIA for electricity mix and LCA emission factors Stokes and Horvath http://uc-ciee.org/downloads/Life-cycleHorvath.pdf)
treatment_embodied_GHG = 0.06 #kgCO2/m3 Kavvada
treatment_embodied_energy = 0.3 #kWh/m3 Kavvada
