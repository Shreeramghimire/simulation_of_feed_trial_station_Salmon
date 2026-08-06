# Lab data (growth and blood samples)

def generate_lab_data(tank_ids, measurement_days=[0, 30, 60]):
    """
    Simulate manual lab measurements (fish weights, blood samples).
    These come from Excel sheets or lab equipment, not sensors.
    """
    records = []
    
    for tank in tank_ids:
        treatment = dim_tank[dim_tank['tank_id'] == tank]['treatment_group'].iloc[0]
        
        # Base growth rate depends on treatment
        if treatment == 'Control':
            base_growth = 0.035  # kg per day
            growth_variation = 0.008
        elif treatment == 'NewFeed_Low':
            base_growth = 0.042
            growth_variation = 0.009
        else:  # NewFeed_High
            base_growth = 0.048
            growth_variation = 0.010
        
        for day in measurement_days:
            # Sample 10 fish per tank per measurement day
            for fish in range(10):
                # Weight increases with day, with individual fish variation
                weight = 0.8 + (day * base_growth) + np.random.normal(0, growth_variation * 30)
                weight = max(0.5, weight)  # Minimum weight
                
                # Blood parameters (influenced by feed and day)
                if treatment == 'Control':
                    cortisol_base = 15
                    glucose_base = 80
                else:
                    cortisol_base = 12  # Lower stress with better nutrition
                    glucose_base = 75
                
                # Stress event impacts blood parameters
                if 25 <= day <= 30:
                    cortisol_base += 10
                    glucose_base += 15
                
                cortisol = cortisol_base + np.random.normal(0, 3)
                glucose = glucose_base + np.random.normal(0, 5)
                
                records.extend([
                    {
                        'tank_id': tank,
                        'trial_id': 'T2026-01',
                        'timestamp': datetime(2026, 1, 15, 8, 0, 0) + timedelta(days=day),
                        'parameter': 'weight_kg',
                        'value': round(weight, 3),
                        'unit': 'kg',
                        'data_source': 'manual_lab',
                        'fish_id': f'F{fish+1:03d}'
                    },
                    {
                        'tank_id': tank,
                        'trial_id': 'T2026-01',
                        'timestamp': datetime(2026, 1, 15, 8, 0, 0) + timedelta(days=day),
                        'parameter': 'cortisol_ng_ml',
                        'value': round(cortisol, 1),
                        'unit': 'ng/mL',
                        'data_source': 'manual_lab',
                        'fish_id': f'F{fish+1:03d}'
                    },
                    {
                        'tank_id': tank,
                        'trial_id': 'T2026-01',
                        'timestamp': datetime(2026, 1, 15, 8, 0, 0) + timedelta(days=day),
                        'parameter': 'glucose_mg_dl',
                        'value': round(glucose, 1),
                        'unit': 'mg/dL',
                        'data_source': 'manual_lab',
                        'fish_id': f'F{fish+1:03d}'
                    }
                ])
    
    return pd.DataFrame(records)

