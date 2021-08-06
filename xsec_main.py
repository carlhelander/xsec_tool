import tkinter as tk
import os
from tkinter import filedialog
import pandas as pd
import numpy as np
import lts_processor as lp
 

class App(tk.Tk):
    def __init__(self): 
        super().__init__()
        self.geometry("1500x768")
        self.title("Cross-section analyser v0.0")
        self.iconphoto(False, tk.PhotoImage(file='C:/Users/Carl/Desktop/window_icon.bmp'))
        
        
        # Menubar
        self.menubar = tk.Menu(self)
        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Open comma-separated values (CSV)", command=self.open_file)
        self.filemenu.add_command(label="Open total station output file", command=self.open_file)
        self.menubar.add_cascade(label="File", menu=self.filemenu)
        self.helpmenu = tk.Menu(self.menubar, tearoff=0)
        self.helpmenu.add_command(label="About...", command=self.donothing)
        self.menubar.add_cascade(label="Help", menu=self.helpmenu)
        self.config(menu=self.menubar)
        self.configure(bg='darkgrey')
        
        
        # tkvars
        self.tk_vars = {"tkv_CHANNELAREA": tk.DoubleVar(),
                        "tkv_CHANNELWIDTH": tk.DoubleVar(),
                        "tkv_CHANNELWDRATIO": tk.DoubleVar(),
                        "tkv_CHANNELDEPTH": tk.DoubleVar(),
                        "tkv_DISCHARGE": tk.DoubleVar(),
                        "tkv_FLOWVELOCITY": tk.DoubleVar(),
                        "tkv_SLOPE": tk.DoubleVar(),
                        "tkv_MANNINGS": tk.DoubleVar(),
                        "tkv_LHB_x": tk.DoubleVar(),
                        "tkv_RHB_x": tk.DoubleVar(),
                        "tkv_CURSOR_x": tk.DoubleVar(),
                        "tkv_CURSOR_y": tk.DoubleVar(),
                        "tkv_LHB_y": tk.DoubleVar(),
                        "tkv_RHB_y": tk.DoubleVar(),
                        "tkv_CANVAS_xytag": tk.StringVar(),
                        "tkv_SNAP": tk.BooleanVar(False),
                        "tkv_SELECTEDBANK": tk.IntVar(),
                        "tkv_UNITSTREAMPOWER": tk.DoubleVar(),
                        "tkv_XVALSVARNAME": tk.StringVar(),
                        "tkv_YVALSVARNAME": tk.StringVar(),
                        "tkv_FILENAME": tk.StringVar(value="None"),
                        "tkv_JOB": tk.StringVar(value="None"),
                        "tkv_NSTATIONS": tk.StringVar(value="None")}
        
        
        # Canvas
        self.canvas_PLOT = tk.Canvas(self, 
                                     bg="lightgray", 
                                     height = 600, 
                                     width = 1000,
                                     cursor = "none",
                                     background = 'black')
        self.canvas_PLOT.grid(column=1, row=0, rowspan=2)
        self.canvas_PLOT.grid_propagate(False)
        
        
        # Labelframe channel metrics
        self.labelframe_CHANNELMETRICS = tk.LabelFrame(master = self,
                                                       text = "Channel metrics and discharge estimation",
                                                       width = 40,
                                                       bg="darkgrey")
        self.labelframe_CHANNELMETRICS.grid(column = 2, row = 0, sticky='nw', padx=10, pady=10)
        self.label_CHANNELWIDTH = tk.Label(master = self.labelframe_CHANNELMETRICS,
                                           text = 'Channel width: ',
                                           anchor = "w",
                                           bg="darkgrey").grid(row = 0, column = 0, sticky = 'w')
        self.label_CHANNELDEPTH = tk.Label(master = self.labelframe_CHANNELMETRICS,
                                           text = 'Channel depth: ',
                                           anchor = "w",
                                           bg="darkgrey").grid(row = 1, column = 0, sticky = 'w')
        self.label_CHANNELWDRATIO = tk.Label(master = self.labelframe_CHANNELMETRICS,
                                             text = 'Channel W/D: ',
                                             anchor = "w",
                                             bg="darkgrey").grid(row = 2, column = 0, sticky = 'w')
        self.label_CHANNELAREA = tk.Label(master = self.labelframe_CHANNELMETRICS,
                                          text = 'Channel area: ',
                                          anchor = "w",
                                          bg="darkgrey").grid(row = 3, column = 0, sticky = 'w')
        self.label_MANNINGS = tk.Label(master = self.labelframe_CHANNELMETRICS, 
                                       text = "Manning's n value: ",
                                       bg="darkgrey").grid(row = 4, column=0, sticky = 'w')
        self.label_SLOPE = tk.Label(master = self.labelframe_CHANNELMETRICS, 
                                    text = "Channel bed slope: ",
                                    bg="darkgrey").grid(row = 5, column = 0, sticky = 'w')
        self.button_ESTIMATEDISCHARGE = tk.Button(master = self.labelframe_CHANNELMETRICS, 
                                                  text = "Estimate discharge...",
                                                  command = self.press_discharge_button,
                                                  bg="darkgrey").grid(row = 9, column = 0, sticky='w')
        self.label_FLOWVELOCITY = tk.Label(master = self.labelframe_CHANNELMETRICS, 
                                           text = "Flow velocity (u/sec): ",
                                           bg="darkgrey").grid(row = 6, column = 0, sticky = 'w')
        self.label_DISCHARGE = tk.Label(master = self.labelframe_CHANNELMETRICS, 
                                        text = "Discharge (u^3/sec): ",
                                        bg="darkgrey").grid(row = 7, column = 0, sticky = 'w')
        self.entry_SLOPE = tk.Entry(master = self.labelframe_CHANNELMETRICS, 
                                    width=6)
        self.entry_SLOPE.grid(row = 4, column = 1, sticky = 'w')
        self.entry_MANNINGS = tk.Entry(master = self.labelframe_CHANNELMETRICS, 
                                       width=6)
        self.entry_MANNINGS.grid(row = 5, column = 1, sticky = 'w')
        # Column 1: values
        self.label_CHANNELWIDTH_VAL = tk.Label(master = self.labelframe_CHANNELMETRICS,
                                               textvariable = self.tk_vars["tkv_CHANNELWIDTH"],
                                               anchor = "w",
                                               bg="darkgrey").grid(row = 0, column=1, sticky = 'w')
        self.label_CHANNELDEPTH_VAL = tk.Label(master = self.labelframe_CHANNELMETRICS,
                                               textvariable = self.tk_vars["tkv_CHANNELDEPTH"],
                                               anchor = "w",
                                               bg="darkgrey").grid(row = 1, column=1, sticky = 'w')
        self.label_CHANNELWDRATIO_VAL = tk.Label(master = self.labelframe_CHANNELMETRICS,
                                                 textvariable = self.tk_vars["tkv_CHANNELWDRATIO"],
                                                 anchor = "w",
                                                 bg="darkgrey").grid(row = 2, column=1, sticky = 'w')
        self.label_CHANNELAREA_VAL = tk.Label(master = self.labelframe_CHANNELMETRICS,
                                              textvariable = self.tk_vars["tkv_CHANNELAREA"],
                                              anchor = "w",
                                              bg="darkgrey").grid(row = 3, column=1, sticky = 'w')
        self.label_CHANNELFLOWVELOCITY_VAL = tk.Label(master = self.labelframe_CHANNELMETRICS,
                                                      textvariable = self.tk_vars["tkv_FLOWVELOCITY"],
                                                      anchor = "w",
                                                      bg="darkgrey").grid(row = 6, column=1, sticky = 'w')
        self.label_CHANNELDISCHARGE_VAL = tk.Label(master = self.labelframe_CHANNELMETRICS,
                                                   textvariable = self.tk_vars["tkv_DISCHARGE"],
                                                   anchor = "w",
                                                   bg="darkgrey").grid(row = 7, column=1, sticky = 'w')


        # Labelframe canvas options
        self.labelframe_CANVASOPTIONS = tk.LabelFrame(master = self,
                                                      text = "Plot options",
                                                      width = 40,
                                                      bg="darkgrey")
        self.labelframe_CANVASOPTIONS.grid(row=0, column=0, padx = 10, pady = 10, sticky = 'nw')
        self.checkbutton_SNAP = tk.Checkbutton(master = self.labelframe_CANVASOPTIONS,
                                               variable=self.tk_vars["tkv_SNAP"],
                                               text="Snap to points",
                                               bg="darkgrey",
                                               ).grid(row=1, column=0, sticky='w', columnspan=3)
        self.checkbutton_KEEPWATERSURFACEFLAT = tk.Checkbutton(master = self.labelframe_CANVASOPTIONS,
                                               variable=self.tk_vars["tkv_SNAP"],
                                               text="Keep water surface flat",
                                               bg="darkgrey").grid(row=2, column=0, columnspan=3, sticky='w')
        self.radiobutton_DEFINELHB = tk.Radiobutton(self.labelframe_CANVASOPTIONS, 
                                                    variable = self.tk_vars["tkv_SELECTEDBANK"], 
                                                    value=0, 
                                                    text = "Left",
                                                    bg="darkgrey").grid(row = 0, column=1, sticky='w')
        self.radiobutton_DEFINERHB = tk.Radiobutton(self.labelframe_CANVASOPTIONS, 
                                                    variable = self.tk_vars["tkv_SELECTEDBANK"], 
                                                    value=1, 
                                                    text = "Right",
                                                    bg="darkgrey").grid(row = 0, column=2, sticky='w')
        self.label_DEFINE = tk.Label(master = self.labelframe_CANVASOPTIONS,
                                     text = 'Define bank: ',
                                     anchor = "w",
                                     bg="darkgrey").grid(row=0, column=0, sticky='w')
        self.label_FILE = tk.Label(master = self.labelframe_CANVASOPTIONS,
                                   text = "File: ",
                                   anchor = 'w',
                                   bg="darkgrey").grid(row = 3, column = 0, sticky = 'w')
        self.label_XVALUES = tk.Label(master = self.labelframe_CANVASOPTIONS,
                                   text = "X values: ",
                                   anchor = 'w',
                                   bg="darkgrey").grid(row = 4, column = 0, sticky = 'w')
        self.label_YVALUES = tk.Label(master = self.labelframe_CANVASOPTIONS,
                                   text = "Y values: ",
                                   anchor = 'w',
                                   bg="darkgrey").grid(row = 5, column = 0, sticky = 'w')
        self.options = ("", "")
        self.optionmenu_SELECTXVAR = tk.OptionMenu(self.labelframe_CANVASOPTIONS, 
                                                   self.tk_vars["tkv_XVALSVARNAME"], 
                                                   *self.options)
        self.optionmenu_SELECTXVAR.configure(bg="darkgrey")
        self.optionmenu_SELECTYVAR = tk.OptionMenu(self.labelframe_CANVASOPTIONS,
                                                   self.tk_vars["tkv_YVALSVARNAME"], 
                                                   *self.options)
        self.optionmenu_SELECTYVAR.configure(bg="darkgrey")
        self.optionmenu_SELECTXVAR.grid(row=4,column=1, columnspan=2, sticky='w')
        self.optionmenu_SELECTYVAR.grid(row=5,column=1, columnspan=2, sticky='w')
        self.label_SELECTEDFILE_VAL = tk.Label(master = self.labelframe_CANVASOPTIONS,
                                               textvariable = self.tk_vars["tkv_FILENAME"],
                                               bg="darkgrey").grid(column=1,row=3, sticky="w",columnspan=2)
        self.button_PLOT = tk.Button(master = self.labelframe_CANVASOPTIONS, 
                                     text = "Plot...",
                                     command = self.plot,
                                     bg="darkgrey").grid(row = 6, column = 0, sticky='w')
        self.canvaspolygon_CHANNEL = self.canvas_PLOT.create_polygon(1, 1, 1, 1, 1, 1, fill="blue")                                                                                        
        self.canvasline_VTCROSSHAIR = self.canvas_PLOT.create_line(500, 0, 500, 600, fill = 'gray')
        self.canvasline_HZCROSSHAIR = self.canvas_PLOT.create_line(0, 300, 1000, 300, fill = 'gray')
        

        # Labelframe bank XY
        self.labelframe_BANKXY = tk.LabelFrame(self, text = "Bank XY coordinates", width=40, bg="darkgrey")
        self.label_LHBX = tk.Label(master = self.labelframe_BANKXY, text = "LHB x: ", bg="darkgrey")
        self.label_LHBY = tk.Label(master = self.labelframe_BANKXY, text = "LHB y: ", bg="darkgrey")
        self.label_RHBX = tk.Label(master = self.labelframe_BANKXY, text = "RHB x: ", bg="darkgrey")
        self.label_RHBY = tk.Label(master = self.labelframe_BANKXY, text = "RHB y: ", bg="darkgrey")
        self.label_LHBX_VAL = tk.Label(master = self.labelframe_BANKXY, textvariable = self.tk_vars["tkv_LHB_x"], bg="darkgrey")
        self.label_LHBY_VAL = tk.Label(master = self.labelframe_BANKXY, textvariable = self.tk_vars["tkv_LHB_y"], bg="darkgrey")
        self.label_RHBX_VAL = tk.Label(master = self.labelframe_BANKXY, textvariable = self.tk_vars["tkv_RHB_x"], bg="darkgrey")
        self.label_RHBY_VAL = tk.Label(master = self.labelframe_BANKXY, textvariable = self.tk_vars["tkv_RHB_y"], bg="darkgrey")
        self.labelframe_BANKXY.grid(row = 1, column = 2, stick='sw', padx = 10, pady = 0)
        self.label_LHBX.grid(row=0, column=0)
        self.label_LHBY.grid(row=1, column=0)
        self.label_RHBX.grid(row=2, column=0)
        self.label_RHBY.grid(row=3, column=0)
        self.label_LHBX_VAL.grid(row=0, column=1)
        self.label_LHBY_VAL.grid(row=1, column=1)
        self.label_RHBX_VAL.grid(row=2, column=1)
        self. label_RHBY_VAL.grid(row=3, column=1)
        
        
        #Labelframe job
        self.labelframe_TSJOB = tk.LabelFrame(self, text = "Total station job", width=40, bg="darkgrey")
        self.label_JOB = tk.Label(master = self.labelframe_TSJOB, text = "Job: ", bg="darkgrey").grid(row=0, column=0, sticky = "w")
        self.label_NSTATIONS = tk.Label(master = self.labelframe_TSJOB, text = "Stations: ", bg="darkgrey").grid(row=1, column=0, sticky = "w")
        self.label_NSTATIONS_VAL = tk.Label(master = self.labelframe_CHANNELMETRICS,
                                      textvariable = self.tk_vars["tkv_NSTATIONS"],
                                      anchor = "w",
                                      bg="darkgrey").grid(row = 1, column=1, sticky = 'w')
        self.label_JOB_VAL = tk.Label(master = self.labelframe_CHANNELMETRICS,
                                      textvariable = self.tk_vars["tkv_JOB"],
                                      anchor = "w",
                                      bg="darkgrey").grid(row = 0, column=1, sticky = 'w')
        self.labelframe_TSJOB.grid(row = 1, column=0, sticky="sw", padx = 10, pady = 0)
        

    def press_discharge_button(self):
        """Calculates the discharge and flow velocity once the button is pressed"""

        self.tk_vars["tkv_MANNINGS"].set(self.entry_MANNINGS.get())
        self.tk_vars["tkv_SLOPE"].set(self.entry_SLOPE.get())
        self.tk_vars["tkv_FLOWVELOCITY"].set(self.calc_flow_velocity(self.tk_vars["tkv_CHANNELDEPTH"].get(),
                                                self.tk_vars["tkv_SLOPE"].get(), 
                                                self.tk_vars["tkv_MANNINGS"].get()))
        self.tk_vars["tkv_DISCHARGE"].set(self.calc_discharge(self.tk_vars["tkv_CHANNELAREA"].get(),
                                                   self.tk_vars["tkv_FLOWVELOCITY"].get()))


    def calc_discharge(self, area, flow_velocity):
        return area*flow_velocity
    
    
    def calc_flow_velocity(self, depth, slope, mannings):
        return depth**(0.66666) * slope**(0.5) / mannings


    def load_data(self, x_array, y_array):
        self.x_array = x_array
        self.y_array = y_array
        self.y_array_flipped = (self.y_array - self.y_array.max()).abs() 
        self.x_array_map = (self.x_array - self.x_array.min()) * (1000 / (self.x_array.max() - self.x_array.min())) + 1
        self.y_array_flipped_map = (self.y_array_flipped - self.y_array_flipped.min()) * (600 / (self.y_array_flipped.max() - self.y_array_flipped.min())) + 2


    def donothing(self):
        pass
    
    def transform_map_to_data(self, map_x, map_y):
        data_x = map_x / 1000 * (self.x_array.max()-self.x_array.min()) + self.x_array.min()
        data_y = -map_y / 600 * (self.y_array.max()-self.y_array.min()) + self.y_array.max()
        return data_x, data_y
    
    def transform_data_to_map(self, data_x, data_y):
        map_x = (data_x - self.x_array.min()) * (1000/(self.x_array.max()-self.x_array.min())) + 1
        map_y = -((data_y - self.y_array.min()) * (600/(self.y_array.max()-self.y_array.min()))) + 601
        return map_x, map_y

    def open_file(self):
        self.fpath = filedialog.askopenfilename(initialdir = os.getcwd(),
                                                title = "Select file...",
                                                filetypes = (("CSV files", "*.csv*"),
                                                             ("All files", "*.*")))
        self.tk_vars["tkv_FILENAME"].set(self.fpath.split("/")[-1])
        self.df = pd.read_csv(self.fpath)
        for var in self.df.columns:
            self.optionmenu_SELECTXVAR['menu'].add_command(label=var, command=tk._setit(self.tk_vars["tkv_XVALSVARNAME"], var))
            self.optionmenu_SELECTYVAR['menu'].add_command(label=var, command=tk._setit(self.tk_vars["tkv_YVALSVARNAME"], var))

    def find_nearest(self, v, vals):
        return min(vals, key=lambda x:abs(x-v))

    def find_surrounding(self, v, li):
        return max(x for x in li if x < v), min(x for x in li if x > v)

    def motion(self, event):
        self.canvas_PLOT.coords(self.canvasline_VTCROSSHAIR, event.x, 1, event.x, 601)
        self.canvas_PLOT.coords(self.canvasline_HZCROSSHAIR, 1, event.y, 1000, event.y)
    
    def interpolate_y(self, x):
        x1, x2 = self.find_surrounding(x, list(self.x_array))
        y1 = list(self.y_array)[list(self.x_array).index(x1)]
        y2 = list(self.y_array)[list(self.x_array).index(x2)]
        slope = (y2 - y1) / (x2 - x1)
        intercept = y1 - slope * x1
        return slope * x + intercept
    
    def interpolate_x(self, y):
        y1, y2 = self.find_surrounding(y, list(self.y_array))
        x1 = self.x_array[list(self.y_array).index(y1)]
        x2 = self.x_array[list(self.y_array).index(y2)]
        slope = (x2 - x1) / (y2 - y1)
        intercept = x1 - slope * y1
        return slope * y + intercept
        
    def click(self, event):
        map_x, map_y = event.x+1, event.y+1
        data_x, data_y = self.transform_map_to_data(event.x, event.y)
        print(data_x, data_y)
        if self.tk_vars["tkv_SNAP"].get():
            data_x = self.find_nearest(data_x, list(self.x_array))
            map_x = self.transform_data_to_map(data_x, data_y)[0]

        if self.tk_vars['tkv_SELECTEDBANK'].get() == 0:
            self.canvas_PLOT.coords(self.canvasline_LHB, map_x, 1, map_x, 601)
            self.canvas_PLOT.coords(self.canvaslabel_LHB, map_x, 1)
            self.tk_vars["tkv_LHB_x"].set(data_x)
            if self.tk_vars["tkv_SNAP"].get():
                self.tk_vars["tkv_LHB_y"].set(list(self.y_array)[list(self.x_array).index(data_x)])
            else:
                self.tk_vars["tkv_LHB_y"].set(self.interpolate_y(data_x))
            
        if self.tk_vars['tkv_SELECTEDBANK'].get() == 1:
            self.canvas_PLOT.coords(self.canvasline_RHB, map_x, 1, map_x, 601)
            self.canvas_PLOT.coords(self.canvaslabel_RHB, map_x, 1)
            self.tk_vars["tkv_RHB_x"].set(data_x)
            if self.tk_vars["tkv_SNAP"].get():
                self.tk_vars["tkv_RHB_y"].set(list(self.y_array)[list(self.x_array).index(data_x)])
            else:
                self.tk_vars["tkv_RHB_y"].set(self.interpolate_y(data_x))
            
        self.tk_vars["tkv_CHANNELWIDTH"].set(round(self.tk_vars["tkv_RHB_x"].get() - self.tk_vars["tkv_LHB_x"].get(), 4))
        self.tk_vars["tkv_CHANNELDEPTH"].set(round(min(self.tk_vars["tkv_LHB_y"].get(), self.tk_vars["tkv_RHB_y"].get()) - self.y_array.min(), 4)) # THIS NEEDS TO BE FIXED TO ONLY INCLUDE POINTS BETWEEN A CERTAIN RANGE
        self.tk_vars["tkv_CHANNELWDRATIO"].set(round(self.tk_vars["tkv_CHANNELWIDTH"].get()/self.tk_vars["tkv_CHANNELDEPTH"].get(), 4))
        self.get_channel_coordinates()
    
    def PolyArea(self, x,y):
        return 0.5*np.abs(np.dot(x,np.roll(y,1))-np.dot(y,np.roll(x,1)))

    def get_channel_coordinates(self):
        self.df_plot = pd.DataFrame({"x_vals": self.x_array, 
                                     "y_vals": self.y_array})
        self.df_plot = self.df_plot[(self.df_plot['x_vals'] > self.tk_vars["tkv_LHB_x"].get()) & (self.df_plot['x_vals'] < self.tk_vars["tkv_RHB_x"].get())]
        self.df_plot.loc[-1] = [self.tk_vars["tkv_LHB_x"].get(), self.tk_vars["tkv_LHB_y"].get()]
        self.df_plot.index = self.df_plot.index + 1
        self.df_plot = self.df_plot.sort_index() 
        self.df_plot = self.df_plot.append({'x_vals': self.tk_vars["tkv_RHB_x"].get(),
                                            'y_vals': self.tk_vars["tkv_RHB_y"].get()}, ignore_index=True)
        

        self.tk_vars["tkv_CHANNELAREA"].set(round(self.PolyArea(self.df_plot['x_vals'], 
                                                          self.df_plot['y_vals']), 4))
        self.ca_x_map, self.ca_y_map = self.transform_data_to_map(self.df_plot["x_vals"].to_numpy(), self.df_plot["y_vals"].to_numpy())
        self.all_map_ca_vals = []
        for count, val in enumerate(list(self.ca_x_map)):
            self.all_map_ca_vals.append(val)
            self.all_map_ca_vals.append(self.ca_y_map[count])
        self.canvas_PLOT.coords(self.canvaspolygon_CHANNEL, *self.all_map_ca_vals)


    def plot(self):
        """Draws the points on a tk Canvas object"""
        self.canvas_PLOT.delete("all")
        self.canvaspolygon_CHANNEL = self.canvas_PLOT.create_polygon(1, 1, 1, 1, 1, 1, fill="blue")  
        self.canvasline_VTCROSSHAIR = self.canvas_PLOT.create_line(500, 0, 500, 600, fill = 'gray')
        self.canvasline_HZCROSSHAIR = self.canvas_PLOT.create_line(0, 300, 1000, 300, fill = 'gray')
        self.canvasline_LHB = self.canvas_PLOT.create_line(0, 0, 0, 600, fill = 'yellow', dash=(10, 10))
        self.canvasline_RHB = self.canvas_PLOT.create_line(1100, 0, 1100, 600, fill = 'yellow', dash=(10, 10))
        self.canvaslabel_LHB = self.canvas_PLOT.create_text(0, 2000, text = "LHB", anchor=tk.NW, fill='yellow')
        self.canvaslabel_RHB = self.canvas_PLOT.create_text(0, 2000, text = "RHB", anchor=tk.NW, fill='yellow')
        self.load_data(self.df[self.tk_vars["tkv_XVALSVARNAME"].get()].dropna(),
                       self.df[self.tk_vars["tkv_YVALSVARNAME"].get()].dropna())
        line_points = []
        for count, coordinate in enumerate(self.x_array_map):
            y = self.y_array_flipped_map[count]
            line_points.append(coordinate)
            line_points.append(y)
            self.canvas_PLOT.create_rectangle(coordinate-2, y-2, coordinate+2, y+2, fill = 'white')
        self.canvasline_PLOT = self.canvas_PLOT.create_line(*line_points, fill='white')
    
    
        
        


        
       

if __name__ == "__main__": 
    app = App()
    app.canvas_PLOT.bind('<Motion>', app.motion)
    app.canvas_PLOT.bind('<Button-1>', app.click)
    app.mainloop()
