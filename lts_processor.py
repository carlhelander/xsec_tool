"""
==============================================================================
lts_processor v0.2.0
Carl Helander carl.helander@mq.edu.au
------------------------------------------------------------------------------
Changelog:
    v0.1.1 - Added ordered station list attribute to Job class instance
    v0.1.2 - Changed output file name to "station_..." instead of "survey_..."
           - Minor improvements to the .export() method for Station class
    v0.2.0 - Added functionality to correct coordinates to a particular
             location
    
------------------------------------------------------------------------------
Help on lts_processor (lp) module:

NAME
    lts_processor

DESCRIPTION
    Module for handling single-station topographic transects with 
    Leica TCR-705 total station.

FUNCTIONS
    process_all(self)
        Do stuff. I'll write this later.
        
------------------------------------------------------------------------------
Quick start:
    1. Create a Job object by calling lp.Job("path/to/total-station/file.txt").
    2. Call .process_all() method on Job object to process all transects
    contained within it.
    3. Call .export_all() method on Job object to export all stations to 
    separate objects.
==============================================================================
"""
import os
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import math


def euc_dist(x1 = None, x2 = None, y1 = None, y2 = None):
    return math.sqrt((x2-x1) ** 2 + (y2-y1) ** 2)


class Station:
    def __init__(self, data = None, info = None, colnames = None):
        self.data = data
        self.info = info
        self.colnames = colnames
        self.station_id = self.info[0][0]
        self.station_easting = self.info[0][1]
        self.station_northing = self.info[0][2]
        self.station_elevation = self.info[0][3]
        self.station_height = self.info[0][4]
        self.df = pd.DataFrame(self.data, 
                               columns = self.colnames)\
            .apply(pd.to_numeric, errors = 'ignore')
        self.processed = False
    

    def plot(self):
        if self.processed is True:
            fig, axs = plt.subplots()
            axs.plot(self.df['cum_distance'], self.df['elevation'])
            axs.plot(self.df['cum_distance'], self.df['elevation'], 'k+')
            axs.set_xlabel('Transect distance (m)')
            axs.set_ylabel('Elevation (m)')
            axs.set_title("Transect {}".format(self.station_id))
            plt.show()
        else:
            self.process()
            self.plot()
        print("Plotted station '{}'".format(self.station_id))
        
    
    def process(self):
        if self.processed is False:
            self.df['x_dist'] = 0
            self.df['cum_distance'] = 0
            for n in range(1, len(self.df)): # For each index value in the each row of the DataFrame except first
                self.df.loc[n, "x_dist"] = euc_dist(x2 = self.df.loc[n-1, 
                                                                     "easting"],
                                                    x1 = self.df.loc[n, 
                                                                     "easting"],
                                                    y2 = self.df.loc[n, 
                                                                     "northing"],
                                                    y1 =  self.df.loc[n-1, 
                                                                      "northing"])
    
                self.df.loc[n, "cum_distance"] = (self.df.loc[n, 
                                                              "x_dist"] + self.df.loc[n-1, "cum_distance"])
                self.horizontaldistance = self.df['cum_distance'].max()
                self.mirror()
            print("Processed station '{}'".format(self.station_id))
            self.processed = True
            
    
    def correct_to(self, manual = True):  
        if manual is True:
            ct_easting = float(input(f"Enter corrected easting (x) for first point of station '{self.station_id}': "))
            ct_northing = float(input(f"Enter corrected northing (y) for first point of station '{self.station_id}': "))
            ct_elevation = float(input(f"Enter corrected elevation (z) for first point of station '{self.station_id}': "))
            x_offset =  ct_easting - self.df.iloc[0]["easting"]
            y_offset = ct_northing - self.df.iloc[0]["northing"]
            z_offset = ct_elevation - self.df.iloc[0]["elevation"]
            print(f"x offset: {x_offset}\ny offset: {y_offset}\nz offset: {z_offset}")
            self.df["corrected_easting"] = self.df['easting'] + x_offset
            self.df["corrected_northing"] = self.df['northing'] + y_offset
            self.df["corrected_elevation"] = self.df['elevation'] + z_offset
        else:
            pass
            #corrections_df = pd.read_csv(fp_locs, index = "station")
            #corrections_df.set_index("station")
            #print(corrections_df.iloc(self.station_id))
            
        

    def mirror(self):
        self.df['mirrored'] = 0 - self.df['cum_distance'] + self.horizontaldistance

        
    def export(self):
        self.df.to_csv("station_{}.csv".format(self.station_id))
        print("Exported station '{}'".format(self.station_id))


class Job:
    """This class contains methods for in"""
    def __init__(self, fpath):
        self.processed = False
        self.data_dict = {}
        self.fpath = fpath
        self.fname = self.fpath.split("/")[-1]
        self.station_list = []
        # Open the dataset
        os.chdir(self.fpath.replace(self.fname, ''))   
        with open(self.fname) as file:
            self.data_str = ''.join(line for line in file)\
                .replace("\n\n\n", "\n\n").split("\n\n")
            
        for count, chunk in enumerate(self.data_str): # Call data blocks in txt file chunks
            if chunk.count('\n') > 2: # Get chunks that are just data
                header = [line.split(',') for line in self.data_str[count-1].replace(' ', '').split('\n')]
                data = [line.split(',')[0:5] for line in chunk.replace(' ', '').split('\n')]
                self.data_dict[header[0][0]] = Station(data = data, info = header, colnames = ["pt_id",
                                                                                              "easting",
                                                                                              "northing",
                                                                                              "elevation",
                                                                                              "trg_height"])
                self.station_list.append(header[0][0])
        self.n_stations = len(self.data_dict)
        print("Imported '{}' ({} stations)".format(self.fname, self.n_stations))
        
        
    def process_all(self):
        for count, t in enumerate(self.data_dict):
            print("Processing station '{}' ({}/{})...".format(t,
                                                              count+1, 
                                                              self.n_stations))
            self.data_dict[t].process()
        
        
    def plot_all(self, individual=True):
        pass
            
    def correct_all(self):
        for count, t in enumerate(self.data_dict):
            print("Correcting station '{}' ({}/{})...".format(t,
                                                            count+1, 
                                                            self.n_stations))
            self.data_dict[t].correct_to()                          
        
            
    def export_all(self):
        output_dir = "lts_automator_outputs"
        try:
            os.chdir(output_dir)
        except Exception:
            os.mkdir(output_dir)
            os.chdir(output_dir)
            print(f"Created new output directory ('{output_dir}') in: {os.getcwd()}")
        cdir = '{}_{}'.format(self.fname.split(".")[0], dt.datetime.now().strftime("%Y%m%d-%H%M%S"))
        os.mkdir(cdir)
        os.chdir(cdir)
        for count, t in enumerate(self.data_dict):
            print("Exporting station '{}' ({}/{})...".format(t,
                                                             count+1, 
                                                             self.n_stations))
            self.data_dict[t].export() 

