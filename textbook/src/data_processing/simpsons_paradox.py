import numpy as np
import pandas as pd

np.random.seed(42)

num_points = 100
gradient = -1    
x_noise_std = 1 
y_noise_std = 4 

x_A_start = 7
x_A_end = 12
intercept_A = 30

x_B_start = 9
x_B_end = 14
intercept_B = 40

x_A = np.linspace(x_A_start, x_A_end, num_points) + np.random.uniform(-x_noise_std, x_noise_std, num_points)
x_B = np.linspace(x_B_start, x_B_end, num_points) + np.random.uniform(-x_noise_std, x_noise_std, num_points)

y_A = gradient * x_A + intercept_A + np.random.normal(0, y_noise_std, num_points)
y_B = gradient * x_B + intercept_B + np.random.normal(0, y_noise_std, num_points)

data_A = pd.DataFrame({
    'Group': ['A'] * num_points,
    'X': x_A,
    'Y': y_A
})

data_B = pd.DataFrame({
    'Group': ['B'] * num_points,
    'X': x_B,
    'Y': y_B
})

combined_data = pd.concat([data_A, data_B], ignore_index=True)

combined_data = combined_data.sample(frac=1, random_state=42).reset_index(drop=True)

combined_data.to_csv('simpsons_paradox_data.csv', index=False)