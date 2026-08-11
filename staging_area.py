
print("\n" + "="*60)
print("STAGING AREA: Data Cleaning & Validation")
print("="*60)

def stage_data_cleaning(raw_data):
    """
    Clean and validate raw data from the data lake.
    This simulates the staging area where data is prepared for the warehouse.
    """
    
    # Create a copy to avoid modifying original
    staged_data = raw_data.copy()
    
    print(f"\n📊 Initial data shape: {staged_data.shape}")
    print(f"📋 Initial columns: {staged_data.columns.tolist()}")
    
    # 1. Check for missing values
    print("\n🔍 Step 1: Checking for missing values...")
    missing_counts = staged_data.isnull().sum()
    if missing_counts.sum() > 0:
        print(f"   ⚠️ Found {missing_counts.sum()} missing values:")
        print(missing_counts[missing_counts > 0])
        # Drop rows with missing critical fields
        staged_data = staged_data.dropna(subset=['tank_id', 'timestamp', 'parameter', 'value'])
        print(f"   ✅ Dropped rows with missing critical fields. New shape: {staged_data.shape}")
    else:
        print("   ✅ No missing values found!")
    
    # 2. Validate data types
    print("\n🔍 Step 2: Validating data types...")
    staged_data['timestamp'] = pd.to_datetime(staged_data['timestamp'])
    staged_data['value'] = pd.to_numeric(staged_data['value'], errors='coerce')
    # Drop rows where value couldn't be converted to numeric
    before = len(staged_data)
    staged_data = staged_data.dropna(subset=['value'])
    after = len(staged_data)
    if before - after > 0:
        print(f"   ⚠️ Dropped {before - after} rows with invalid numeric values")
    print(f"   ✅ Data types validated")
    
    # 3. Remove duplicates
    print("\n🔍 Step 3: Removing duplicates...")
    before = len(staged_data)
    staged_data = staged_data.drop_duplicates(subset=['tank_id', 'timestamp', 'parameter', 'fish_id'] 
                                               if 'fish_id' in staged_data.columns 
                                               else ['tank_id', 'timestamp', 'parameter'])
    after = len(staged_data)
    print(f"   ✅ Removed {before - after} duplicate records")
    
    # 4. Validate parameter values against expected ranges
    print("\n🔍 Step 4: Validating parameter ranges...")
    
    # Define expected ranges for each parameter
    param_ranges = {
        'water_temperature_c': (0, 25),
        'dissolved_oxygen_pct': (0, 100),
        'ph_level': (6.5, 8.5),
        'salinity_ppt': (25, 40),
        'ammonia_mg_l': (0, 5),
        'weight_kg': (0.3, 5.0),
        'cortisol_ng_ml': (0, 50),
        'glucose_mg_dl': (30, 200)
    }
    
    # Flag out-of-range values
    def check_range(row):
        param = row['parameter']
        if param in param_ranges:
            min_val, max_val = param_ranges[param]
            if row['value'] < min_val or row['value'] > max_val:
                return 'out_of_range'
        return 'valid'
    
    staged_data['quality_flag'] = staged_data.apply(check_range, axis=1)
    
    # Separate valid and invalid records
    invalid_records = staged_data[staged_data['quality_flag'] == 'out_of_range']
    staged_data = staged_data[staged_data['quality_flag'] == 'valid']
    
    # Log invalid records (would be sent to error handling in production)
    if len(invalid_records) > 0:
        print(f"   ⚠️ Found {len(invalid_records)} out-of-range records:")
        print(invalid_records[['tank_id', 'parameter', 'value', 'quality_flag']].head())
        # In production, these would be logged to an error table
        invalid_records.to_csv('invalid_records.csv', index=False)
        print(f"   ✅ Invalid records saved to 'invalid_records.csv' for review")
    else:
        print(f"   ✅ All values within expected ranges!")
    
    # 5. Standardize parameter names
    print("\n🔍 Step 5: Standardizing parameter names...")
    # Add any parameter name standardization if needed
    parameter_mapping = {
        'water_temperature_c': 'water_temp_c',
        'dissolved_oxygen_pct': 'do_pct'
    }
    staged_data['parameter'] = staged_data['parameter'].replace(parameter_mapping)
    print(f"   ✅ Parameter names standardized")
    
    # 6. Add audit columns
    print("\n🔍 Step 6: Adding audit columns...")
    staged_data['etl_processed_date'] = datetime.now()
    staged_data['etl_batch_id'] = f'BATCH_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    print(f"   ✅ Audit columns added")
    
    print(f"\n📊 Final staged data shape: {staged_data.shape}")
    print(f"📋 Columns in staged data: {staged_data.columns.tolist()}")
    
    return staged_data, invalid_records

# Run the staging process
staged_data, invalid_records = stage_data_cleaning(raw_data_lake)

print(f"\n✅ Staging complete! Ready for warehouse loading.")
print(f"   • Valid records: {len(staged_data):,}")
print(f"   • Invalid records: {len(invalid_records):,}")
