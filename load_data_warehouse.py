# ============================================
# LOAD DATA WAREHOUSE
# ============================================

print("\n" + "="*60)
print(" LOADING DATA WAREHOUSE")
print("="*60)

def load_warehouse(dimension_tables, fact_observations):
    """
    Simulate loading the data warehouse.
    In production, this would write to tables in Snowflake/Redshift/BigQuery.
    """
    
    print("\n Loading dimension tables: ")
    
    # Save each dimension table as CSV (simulating warehouse load)
    for dim_name, dim_df in dimension_tables.items():
        if dim_df is not None:
            filename = f'warehouse_{dim_name}.csv'
            dim_df.to_csv(filename, index=False)
            print(f"    Loaded {dim_name}: {filename}")
    
    print("\n Loading fact table:")
    fact_observations.to_csv('warehouse_fact_observations.csv', index=False)
    print(f"    Loaded fact_observations: warehouse_fact_observations.csv")
    
    print("\n" + "="*60)
    print(" DATA WAREHOUSE LOAD COMPLETE!")
    print("="*60)
    
    return {
        'dimension_tables': dimension_tables,
        'fact_table': fact_observations
    }

# Load the warehouse
warehouse = load_warehouse(dimension_tables, fact_observations)

# Summary statistics
print("\n Warehouse Summary:")
print(f"   • Fact table rows: {len(warehouse['fact_table']):,}")
print(f"   • Fact table columns: {len(warehouse['fact_table'].columns)}")
print(f"   • Date dimension: {len(warehouse['dimension_tables']['dim_date'])} days")
print(f"   • Tank dimension: {len(warehouse['dimension_tables']['dim_tank'])} tanks")
print(f"   • Feed dimension: {len(warehouse['dimension_tables']['dim_feed'])} feed batches")
print(f"   • Parameter dimension: {len(warehouse['dimension_tables']['dim_parameter'])} parameters")
