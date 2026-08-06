# Combine all datasets into one

raw_data_lake = pd.concat([sensor_data, lab_data], ignore_index=True)
raw_data_lake.to_csv('lerang_raw_data_lake.csv', index=False)

