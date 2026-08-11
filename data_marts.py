# ============================================
# DATA MARTS - User-Specific Views
# ============================================

print("\n" + "="*60)
print(" CREATING DATA MARTS")
print("="*60)

# Mart 1: Operations Dashboard (for Farm Manager)
def create_ops_mart(fact_observations, dimension_tables):
    """
    Create an operations data mart focused on daily tank performance.
    """
    print("\n Creating Operations Mart...")
    
    # Merge with dimensions
    ops_mart = fact_observations.merge(
        dimension_tables['dim_tank'][['tank_key', 'tank_id', 'treatment_group', 'fish_count']],
        on='tank_key'
    ).merge(
        dimension_tables['dim_date'][['date_key', 'date', 'trial_day', 'trial_week']],
        on='date_key'
    )
    
    # Select key operational metrics
    ops_cols = ['date', 'tank_id', 'treatment_group', 'fish_count', 'trial_day']
    
    # Add available parameters
    for col in fact_observations.columns:
        if col in ['water_temp_c', 'do_pct', 'dissolved_oxygen_pct', 'ph_level', 'salinity_ppt', 'ammonia_mg_l']:
            ops_cols.append(col)
        elif 'weight' in col:
            ops_cols.append(col)
    
    # Filter to only columns that exist
    existing_cols = [col for col in ops_cols if col in ops_mart.columns]
    ops_mart = ops_mart[existing_cols]
    
    # Save ops mart
    ops_mart.to_csv('ops_mart_daily_performance.csv', index=False)
    print(f"    Operations Mart: {len(ops_mart)} rows saved to 'ops_mart_daily_performance.csv'")
    print(f"    Columns: {ops_mart.columns.tolist()}")
    
    return ops_mart

# Mart 2: Research Mart (for Scientists)
def create_research_mart(fact_observations, dimension_tables, staged_data):
    """
    Create a research mart with detailed, flexible data for scientists.
    """
    print("\n Creating Research Mart...")
    
    # Research mart uses detailed data - keep the EAV format for flexibility
    # Include both sensor and lab data with all details
    research_mart = staged_data.copy()
    
    # Add tank details
    research_mart = research_mart.merge(
        dimension_tables['dim_tank'][['tank_id', 'treatment_group', 'fish_count', 'depth_m', 'oxygen_system']],
        on='tank_id',
        how='left'
    )
    
    # Add date details
    research_mart['date'] = pd.to_datetime(research_mart['timestamp']).dt.floor('D')
    research_mart = research_mart.merge(
        dimension_tables['dim_date'][['date', 'trial_day', 'trial_week']],
        on='date',
        how='left'
    )
    
    # Save research mart (as CSV for now, would be a database table in production)
    research_mart.to_csv('research_mart_detailed.csv', index=False)
    print(f"    Research Mart: {len(research_mart):,} rows saved to 'research_mart_detailed.csv'")
    print(f"    Columns: {research_mart.columns.tolist()}")
    
    return research_mart

# Mart 3: Admin Mart (for Station Manager)
def create_admin_mart(fact_observations, dimension_tables):
    """
    Create an administrative mart with summary metrics for management.
    """
    print("\n Creating Admin Mart...")
    
    # Aggregate to weekly level for high-level summary
    admin_mart = fact_observations.merge(
        dimension_tables['dim_tank'][['tank_key', 'tank_id', 'treatment_group', 'fish_count']],
        on='tank_key'
    ).merge(
        dimension_tables['dim_date'][['date_key', 'date', 'trial_week']],
        on='date_key'
    )
    
    # Group by week and treatment
    weekly_summary = admin_mart.groupby(['trial_week', 'treatment_group']).agg({
        'tank_id': 'nunique',  # Number of tanks
        'fish_count': 'first',  # Fish per tank
    })
    
    # Add any numeric metrics if they exist
    for col in admin_mart.columns:
        if col in ['weight_kg', 'water_temp_c', 'do_pct', 'dissolved_oxygen_pct']:
            weekly_summary[col] = admin_mart.groupby(['trial_week', 'treatment_group'])[col].mean()
    
    # Reset index
    weekly_summary = weekly_summary.reset_index()
    weekly_summary.columns = ['trial_week', 'treatment_group', 'tank_count', 'fish_count'] + \
                            [col for col in weekly_summary.columns if col not in ['trial_week', 'treatment_group', 'tank_count', 'fish_count']]
    
    # Save admin mart
    weekly_summary.to_csv('admin_mart_weekly_summary.csv', index=False)
    print(f"    Admin Mart: {len(weekly_summary)} rows saved to 'admin_mart_weekly_summary.csv'")
    print(f"    Columns: {weekly_summary.columns.tolist()}")
    
    return weekly_summary

# Create all data marts
ops_mart = create_ops_mart(fact_observations, dimension_tables)
research_mart = create_research_mart(fact_observations, dimension_tables, staged_data)
admin_mart = create_admin_mart(fact_observations, dimension_tables)

print("\n" + "="*60)
print(" ALL DATA MARTS CREATED SUCCESSFULLY!")
print("="*60)

print("\n Final Data Marts Summary:")
print(f"   • Operations Mart: {len(ops_mart):,} rows → For Farm Manager")
print(f"   • Research Mart: {len(research_mart):,} rows → For Scientists")
print(f"   • Admin Mart: {len(admin_mart)} rows → For Station Manager")
