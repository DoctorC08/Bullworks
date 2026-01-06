import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

file_path = 'CFD/WindTunnel_CFD/postProcessing/turbulenceIntensity/0/surfaceFieldValue.dat'

def plot_turbulence_intensity(file_path):
    # Load the data, skipping the OpenFOAM header lines (usually starts with #)
    try:
        data = pd.read_csv(file_path, sep='\t', comment='#', header=None)
    except FileNotFoundError:
        print(f"Error: {file_path} not found. Check your file path.")
        return

    # Read data
    time = data[0]

    coords = data[1].str.strip('()').str.split(expand=True).astype(float)
    ux = coords[0]
    uy = coords[1]
    uz = coords[2]

    k = data[2]

    u_mag = np.sqrt(ux**2 + uy**2 + uz**2)

    # I = sqrt((2/3)*k) / |U|
    intensity = (np.sqrt((2/3) * k) / u_mag) * 100

    # Plotting
    plt.figure(figsize=(10, 6))
    plt.plot(time, intensity, label='Turbulence Intensity (%)', color='blue', linewidth=2)
    
    plt.xlabel('Time [s]')
    plt.ylabel('Turbulence Intensity (%)')
    plt.title('Turbulence Intensity over Time (Cutting Plane)')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    
    plt.ylim(0, 2) 

    plt.savefig('turbulence_intensity_plot.png', dpi=300)
    plt.show()

if __name__ == "__main__":
    plot_turbulence_intensity(file_path)