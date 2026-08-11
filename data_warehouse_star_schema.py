# DATA WAREHOUSE - Star Schema Creation


print("\n" + "="*60)
print(" DATA WAREHOUSE: Building Star Schema")
print("="*60)

def build_dimension_tables(staged_data, dim_tank):
    """
    Build dimension tables for the star schema.
    These are the descriptive tables that provide context to the facts.
    """
    
    print("\n Building Dimension Tables...")
    
    # 1. DIM_DATE (Time dimension)
    print("   • Create DIM_DATE: ")
    # Get all unique timestamps from the data
    all_dates = pd.date_range(
        start=staged_data['timestamp'].min().floor('D'),
        end=staged_data['timestamp'].max().ceil('D'),
        freq='D'
    )
    
    dim_date = pd.DataFrame({
        'date_key': range(1, len(all_dates) + 1),
        'date': all_dates,
        'year': all_dates.year,
        'month': all_dates.month,
        'day': all_dates.day,
        'day_of_week': all_dates.dayofweek,
        'weekday_name': all_dates.day_name(),
        'quarter': all_dates.quarter,
        'is_weekend': all_dates.dayofweek.isin([5, 6]),
        'trial_day': (all_dates - pd.Timestamp('2026-01-15')).days + 1
    })
    
    # Add trial week
    dim_date['trial_week'] = ((dim_date['trial_day'] - 1) // 7) + 1
    
    print(f"      Created {len(dim_date)} date records")
    
    # 2. DIM_TANK (Tank dimension from metadata)
    print("   • Creating DIM_TANK...")
    dim_tank_warehouse = dim_tank[['tank_id', 'treatment_group', 'fish_count', 'depth_m', 'oxygen_system']].copy()
    dim_tank_warehouse['tank_key'] = range(1, len(dim_tank_warehouse) + 1)
    print(f"      Created {len(dim_tank_warehouse)} tank records")
    
    # 3. DIM_FEED (Feed dimension from metadata)
    print("   • Creating DIM_FEED...")
    dim_feed = dim_feed_batch[['feed_batch_id', 'feed_type', 'protein_pct', 'lipid_pct', 
                               'carbohydrate_pct', 'energy_mj_kg', 'supplier']].copy()
    dim_feed['feed_key'] = range(1, len(dim_feed) + 1)
    print(f"      Created {len(dim_feed)} feed records")
    
    # 4. DIM_FISH (Fish dimension - if available)
    print("   • Creating DIM_FISH...")
    if 'fish_id' in staged_data.columns:
        unique_fish = staged_data[['fish_id']].drop_duplicates().copy()
        unique_fish['fish_key'] = range(1, len(unique_fish) + 1)
        dim_fish = unique_fish
        print(f"      Created {len(dim_fish)} fish records")
    else:
        dim_fish = None
        print(f"      No fish_id data available - skipping DIM_FISH")
    
    # 5. DIM_PARAMETER (Parameter dimension)
    print("   • Creating DIM_PARAMETER...")
    unique_params = staged_data[['parameter', 'unit']].drop_duplicates().copy()
    unique_params['parameter_key'] = range(1, len(unique_params) + 1)
    dim_parameter = unique_params
    print(f"      Created {len(dim_parameter)} parameter records")
    
    return {
        'dim_date': dim_date,
        'dim_tank': dim_tank_warehouse,
        'dim_feed': dim_feed,
        'dim_fish': dim_fish,
        'dim_parameter': dim_parameter
    }

# Build dimension tables
dimension_tables = build_dimension_tables(staged_data, dim_tank)

# Display dimensions
print("\n Dimension Tables Summary:")
for dim_name, dim_df in dimension_tables.items():
    if dim_df is not None:
        print(f"   • {dim_name}: {len(dim_df)} rows")

def build_fact_observations(staged_data, dimension_tables):
    """
    Build the fact table in star schema format.
    This creates a wide table with all measures in one row per time-tank combination.
    """
    
    print("\n Building Fact Table...")
    
    # 1. Pivot the EAV data to wide format
    print("   • Pivoting EAV data to wide format...")
    
    # Create pivot - handle both sensor and lab data
    if 'fish_id' in staged_data.columns:
        # For lab data with fish IDs - average by tank and timestamp
        pivot_data = staged_data.pivot_table(
            index=['tank_id', 'timestamp'],
            columns='parameter',
            values='value',
            aggfunc='mean'  # Average across fish
        ).reset_index()
    else:
        # For sensor data
        pivot_data = staged_data.pivot_table(
            index=['tank_id', 'timestamp'],
            columns='parameter',
            values='value',
            aggfunc='first'
        ).reset_index()
    
    # Clean up column names
    pivot_data.columns = [str(col).strip() for col in pivot_data.columns]
    print(f"      ✅ Pivoted to {pivot_data.shape[0]} rows × {pivot_data.shape[1]} columns")
    
    # 2. Add dimension keys
    print("   • Adding dimension keys...")
    
    # Add date key
    pivot_data['date'] = pd.to_datetime(pivot_data['timestamp']).dt.floor('D')
    date_key_mapping = dimension_tables['dim_date'].set_index('date')['date_key']
    pivot_data['date_key'] = pivot_data['date'].map(date_key_mapping)
    
    # Add tank key
    tank_key_mapping = dimension_tables['dim_tank'].set_index('tank_id')['tank_key']
    pivot_data['tank_key'] = pivot_data['tank_id'].map(tank_key_mapping)
    
    # Add feed key (simplified - assuming feed batch based on date)
    # In reality, this would be more complex
    pivot_data['feed_key'] = 1  # Default feed key
    
    # 3. Ensure all numeric columns are properly typed
    print("   • Converting to appropriate data types...")
    numeric_cols = pivot_data.select_dtypes(include=[np.number]).columns
    pivot_data[numeric_cols] = pivot_data[numeric_cols].round(4)
    
    # 4. Rename columns to standard names
    print("   • Standardizing column names...")
    # Keep column names as they are (they're already descriptive)
    
    # 5. Select final columns for fact table
    # Include all parameter columns plus dimension keys
    param_cols = [col for col in pivot_data.columns if col not in ['tank_id', 'timestamp', 'date', 'date_key', 'tank_key', 'feed_key']]
    
    fact_columns = ['date_key', 'tank_key', 'feed_key', 'timestamp'] + param_cols
    fact_observations = pivot_data[fact_columns]
    
    # Add a unique fact key
    fact_observations['fact_key'] = range(1, len(fact_observations) + 1)
    
    print(f"   ✅ Final Fact Table: {fact_observations.shape[0]} rows × {fact_observations.shape[1]} columns")
    
    return fact_observations

# Build the fact table
fact_observations = build_fact_observations(staged_data, dimension_tables)

print("\n📊 Fact Table Preview:")
print(fact_observations.head())
