import pandas as pd
import matplotlib.pyplot as plt
import glob
import re

def read_openfoam_vector_dat(filepath):
    """Reads OpenFOAM .dat file and parses '(x y z)' vector strings."""
    data = []
    with open(filepath, 'r') as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            clean_line = line.replace('(', '').replace(')', '').strip()
            parts = re.split(r'\s+', clean_line)
            data.append([float(p) for p in parts])
    
    df = pd.DataFrame(data, columns=['Time', 'Ux', 'Uy', 'Uz'])
    return df

def read_openfoam_scalar_dat(filepath):
    """Reads standard scalar .dat files."""
    df = pd.read_csv(filepath, sep='\s+', comment='#', header=None)
    df.columns = ['Time', 'Value']
    return df

# File discovery
uniformity_path = glob.glob('CFD/WindTunnel_CFD/postProcessing/velocityUniformity/0/surfaceFieldValue.dat')[0]
mean_vel_path = glob.glob('CFD/WindTunnel_CFD/postProcessing/meanVelocity/0/surfaceFieldValue.dat')[0]

df_u = read_openfoam_scalar_dat(uniformity_path)
df_v = read_openfoam_vector_dat(mean_vel_path)

# Get final values
final_time = df_u['Time'].iloc[-1]
final_unif = df_u['Value'].iloc[-1]
final_ux = df_v['Ux'].iloc[-1]
final_uy = df_v['Uy'].iloc[-1]
final_uz = df_v['Uz'].iloc[-1]

# Print summary to console
print("-" * 30)
print(f"FINAL VALUES at t = {final_time}s")
print("-" * 30)
print(f"Uniformity Index: {final_unif:.4f}")
print(f"Mean Ux:         {final_ux:.4f} m/s")
print(f"Mean Uy:         {final_uy:.4f} m/s")
print(f"Mean Uz:         {final_uz:.4f} m/s")
print("-" * 30)

# Plotting
fig, ax1 = plt.subplots(figsize=(12, 7))

# Plot Uniformity (Left)
color1 = 'tab:blue'
ax1.set_xlabel('Time (s)')
ax1.set_ylabel('Velocity Uniformity Index', color=color1)
line_unif = ax1.plot(df_u['Time'], df_u['Value'], color=color1, label='Uniformity', linewidth=2)
ax1.tick_params(axis='y', labelcolor=color1)

# Plot Mean Velocity Components (Right)
ax2 = ax1.twinx()
line_ux = ax2.plot(df_v['Time'], df_v['Ux'], label='Ux', linestyle='-')
line_uy = ax2.plot(df_v['Time'], df_v['Uy'], label='Uy', linestyle='--')
line_uz = ax2.plot(df_v['Time'], df_v['Uz'], label='Uz', linestyle=':')

# Set Y-axis ticks from absolute min to absolute max
v_min = df_v[['Ux', 'Uy', 'Uz']].min().min() - 1
v_max = df_v[['Ux', 'Uy', 'Uz']].max().max() + 1
ax2.set_ylim(v_min * 0.95, v_max * 1.05) # Add 5% padding so text isn't cut off
ax2.set_yticks([v_min, v_max])
ax2.set_ylabel('Mean Velocity Components (m/s)')

# Formatting
plt.title(f'Velocity Statistics (Final Time: {final_time}s)')
ax1.grid(True, linestyle='--', alpha=0.4)
fig.tight_layout()

# Legend
lns = line_unif + line_ux + line_uy + line_uz
labs = [l.get_label() for l in lns]
ax1.legend(lns, labs, loc='upper left')

plt.show()