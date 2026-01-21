# Universal plotting class for OpenFOAM CFD results

import pandas as pd
from pandas.api.types import is_float_dtype
import matplotlib.pyplot as plt
import glob
import re

class openFoamPlotter:
    def __init__(self):
        self.data = pd.DataFrame()
    
    def gather_data(self, file_names):
        df = pd.DataFrame()
        for file in file_names: 
            new_df = self.read_file(file)
            df = pd.concat([df, new_df], axis=1)
        df = df.loc[:, ~df.columns.duplicated()]
        self.data = df
        return df

    # Class utils
    def read_file(self, file_path):
        col_names = self.get_cols(file_path)
        data = pd.read_csv(file_path, sep='\t', comment='#', header=None, index_col=0)
        data.columns = col_names
        print(col_names)

        for col_name in data.columns.tolist():
            if not is_float_dtype(data[col_name]):
                # print(data[col_name].dtype, file_path)
                # if not float assume it's vector
                print("attempting to spilt vectors:", col_name)
                coords = data[col_name].str.strip('()').str.split(expand=True).astype(float)
                data = data.drop(col_name, axis=1)
                data[f'x_{col_name}'] = coords[0]
                data[f'y_{col_name}'] = coords[1]
                data[f'z_{col_name}'] = coords[2]
                # print("coords", coords)
                # print(data)
        return data 

    def get_cols(self, file_path):
        col_names = []
        with open(file_path, 'r') as f:
            for line in f:
                if line.startswith('# Time'):
                    names = re.split(r'\s+', line.strip())
                    # print(names)
                    for name in names:
                        if name != '#' and name != 'Time':
                            col_names.append(name)
        
        return col_names
    
    # plotting utils
    def plot(self, col_name, lims=None):
        
        col_data = self.data[col_name]
        plt.figure(figsize=(10, 6))
        plt.plot([i for i in range(len(col_data))], col_data, label=f'{col_name}', color='blue', linewidth=2)
        
        plt.xlabel('Time [s]')
        plt.ylabel(f'{col_name}')
        plt.title(f'{col_name} over Time (Cutting Plane)')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend()
        
        if lims is not None:
            plt.ylim(*lims) 

        plt.show()
                    

if __name__ == '__main__':
    file_paths = ['CFD/WindTunnel_CFD/postProcessing/turbulenceIntensity/0/surfaceFieldValue.dat', 
                  'CFD/WindTunnel_CFD/postProcessing/meanVelocity/0/surfaceFieldValue.dat', 
                  'CFD/WindTunnel_CFD/postProcessing/velocityUniformity/0/surfaceFieldValue.dat']

    plotter = openFoamPlotter()
    data = plotter.gather_data(file_paths)
    print(data)
    plotter.plot('uniformity(U)', lims=[0.975, 1])
