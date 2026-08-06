# Synthetic data (raw sensor data generation-EAV format)
def generate_sensor_data(tank_ids, days=60, readings_per_day=6):
    """
    Simulate raw sensor readings in EAV (Entity-Attribute-Value) format.
    This mimics CSV files being dumped into AWS S3.
    """
    records = []
    start_date = datetime(2026, 1, 15, 0, 0, 0)

    for tank in tank_ids:
        # Each tank has slightly different baseline conditions
        base_temp = np.random.normal(12.5, 0.5)
        base_oxygen = np.random.normal(85, 3)
        base_ph = np.random.normal(7.2, 0.1)
        base_salinity = np.random.normal(32, 1)
        
        # it determines treatment effect for this tank
        treatment = dim_tank[dim_tank['tank_id'] == tank]['treatment_group'].iloc[0]
        if 'NewFeed' in treatment:
            feed_effect = np.random.normal(1.5, 0.3)  # New feed increases metabolism
        else:
            feed_effect = 0
        
        for day in range(days):
            for reading in range(readings_per_day):
                timestamp = start_date + timedelta(days=day, hours=reading*4)
                
                # Simulate daily cycles and random noise
                daily_cycle = 0.5 * np.sin(2 * np.pi * (reading / readings_per_day))
                temp = base_temp + daily_cycle + np.random.normal(0, 0.3)
                oxygen = base_oxygen - 0.5 * daily_cycle + np.random.normal(0, 1.5)
                
                # Simulate a stress event mid-trial (days 25-30)
                if 25 <= day <= 30:
                    temp += 2.0 + np.random.normal(0, 0.5)
                    oxygen -= 8.0 + np.random.normal(0, 2)
                
                # Oxygen drops slightly with higher feed (more metabolism)
                if 'NewFeed' in treatment:
                    oxygen -= feed_effect * 0.5
                
                # Record each parameter as a separate row (EAV format)
                parameters = [
                    ('water_temperature_c', temp, '°C'),
                    ('dissolved_oxygen_pct', oxygen, '%'),
                    ('ph_level', base_ph + np.random.normal(0, 0.05), ''),
                    ('salinity_ppt', base_salinity + np.random.normal(0, 0.2), 'ppt'),
                    ('ammonia_mg_l', np.random.exponential(0.5) + 0.1, 'mg/L'),
                ]
                
                for param_name, value, unit in parameters:
                    records.append({
                        'tank_id': tank,
                        'trial_id': 'T2026-01',
                        'timestamp': timestamp,
                        'parameter': param_name,
                        'value': round(value, 2),
                        'unit': unit,
                        'data_source': 'sensor'  # Distinguish from manual lab data
                    })
                    
        return pd.DataFrame(records)

sensor_data = generate_sensor_data(dim_tank['tank_id'].tolist(), days=60, readings_per_day=6)

print(sensor_data.head())
