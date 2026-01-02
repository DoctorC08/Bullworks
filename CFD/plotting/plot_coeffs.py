import pandas as pd
import matplotlib.pyplot as plt

# Define path to data file
data_file = 'IBF_CFD/postProcessing/forceCoeffs1/0.01/coefficient.dat'
data_file = 'CFD/IBF_CFD/postProcessing/forceCoeffs1/0.01/coefficient.dat'

# Read data, skipping the non-data header lines (#)
# We plot column 1 (Time/Iteration) vs column 2 (Cd) and column 4 (Cl)
df = pd.read_csv(data_file, sep='\s+', skiprows=1, header=None, comment='#')

# Plotting
plt.figure(figsize=(10, 6))

# print(df)

# Column 0 (Time/Iteration) vs Column 1 (Cd)
plt.plot(df[0], df[1], label='$C_d$ (Drag Coefficient)', color='blue')

# Column 0 (Time/Iteration) vs Column 4 (Cl)
plt.plot(df[0], df[4], label='$C_l$ (Lift Coefficient)', color='red')

# Customize the plot
plt.title('Convergence of Force Coefficients')
plt.xlabel('Iteration / Pseudo-Time')
plt.ylabel('Coefficient Value')
plt.grid(True, linestyle='--')
plt.legend()

# Save the plot as a high-quality image file
plt.savefig('forceCoeffs_convergence.png')
plt.show()