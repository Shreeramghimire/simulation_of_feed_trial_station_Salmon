# Simulation_of_feed_trial_station_Salmon

This repo presents a simulation of the movement of data and management of data in a typical trial station doing a feed trial on Atlantic Salmon in Norwegian waters. 

In this simulation we gonna test a new feed with low protein and high protein level against control diet. So, there will be two test groups and one control group. Each group will have two treatments, so the total number of treatments is six. 
The trial will start on 15.1.2026 and end on 15.03.2026. 

**Number of days = 60**

**Number of treatments = 6**

**Number of parameters = 5**

**Number of readings per day = 6**

**Total number of rows = 10800**

Parameters are: **water_temperature(celcius)**,  **oxygen_saturation_level(percentage)**, **pH**, **salinity(ppt)**, and **ammonia(mg/L)**.

Baseline conditions: 

**water_temperature** = 12.5 ± 0.5

**oxygen_saturation_level** = 85 ± 3

**pH** = 7.2 ± 0.1

**salinity** = 32 ± 1

**ammonia** = np.random.exponential(0.5) + 0.1
