import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import statsmodels.api as sm
from statsmodels.formula.api import ols
import warnings
warnings.filterwarnings('ignore')

np.random.seed(42)

# Metadata table
dim_trial = pd.DataFrame({
    'trial_id': ['T2026-01'],
    'trial_name': ['Low-Protein Feed Efficacy Trial'],
    'start_date': ['2026-01-15'],
    'end_date': ['2026-03-15'],
    'water_source': ['Fjord'],
    'tank_size_m3': [500],
    'salmon_strain': ['AquaGen QTL-5'],
    'starting_weight_avg_kg': [0.8],
    'trial_duration_days': [60]
})

dim_tank = pd.DataFrame({
    'tank_id': ['Tank_A1', 'Tank_A2', 'Tank_B1', 'Tank_B2', 'Tank_C1', 'Tank_C2'],
    'trial_id': ['T2026-01'] * 6,
    'treatment_group': ['Control'] * 2 + ['NewFeed_Low'] * 2 + ['NewFeed_High'] * 2,
    'fish_count': [200, 200, 200, 200, 200, 200],
    'depth_m': [5, 5, 5, 5, 5, 5],
    'oxygen_system': ['Standard'] * 4 + ['Enhanced'] * 2
})

dim_feed_batch = pd.DataFrame({
    'feed_batch_id': ['FB-C-01', 'FB-C-02', 'FB-NL-01', 'FB-NL-02', 'FB-NH-01', 'FB-NH-02'],
    'feed_type': ['Control'] * 2 + ['NewFeed_Low'] * 2 + ['NewFeed_High'] * 2,
    'batch_date': ['2026-01-10', '2026-02-10', '2026-01-12', '2026-02-12', '2026-01-14', '2026-02-14'],
    'protein_pct': [42.0, 41.8, 38.5, 38.2, 35.0, 34.7],
    'lipid_pct': [18.0, 18.2, 22.0, 22.3, 25.0, 25.4],
    'carbohydrate_pct': [12.0, 12.0, 10.5, 10.5, 9.0, 9.0],
    'energy_mj_kg': [18.5, 18.6, 19.8, 19.9, 21.0, 21.1],
    'supplier': ['Skretting'] * 6
})

