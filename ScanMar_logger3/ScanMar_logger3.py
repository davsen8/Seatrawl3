# -*- coding: utf-8 -*-

#
# ScanMar_logger3.py   D.Senciall  August 2017
#
"""
Some Elements BASED ON CODE SAMPLE FROM: matplotlib-with-wxpython-guis by E.Bendersky
Eli Bendersky (eliben@gmail.com)
License: this code is in the public domain
Last modified: 31.07.2008

"""
import os
#import pprint
#import random
import sys
import wx
try:
    import wx.adv
except:
        pass
from collections import OrderedDict
import time
import serial
from  datetime import datetime, timedelta
#import json
#from math import radians, cos, sin, asin, sqrt

# The recommended way to use wx graphics and matplotlib (mpl) is with the WXAgg
# backend.
#
import matplotlib
matplotlib.use('WXAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigCanvas
#from mpl_toolkits.axes_grid.parasite_axes import HostAxes, ParasiteAxes   DEPRECIATED
#from mpl_toolkits.axes_grid1.parasite_axes import HostAxes, ParasiteAxes
from mpl_toolkits.axisartist.parasite_axes import HostAxes, ParasiteAxes
import numpy as np

from ScanMar_Serial_Tools import *
from ScanMar_Nmea3 import SMN_TOOLS
from ScanMar_Window_Tools3 import *
from ScanMar_Data_Tools3 import StatusVars,DataVars
import wxSerialConfigDialog


ID_START_RT = wx.NewId()
ID_STOP_RT = wx.NewId()
ID_START_ARC = wx.NewId()
ID_STOP_ARC = wx.NewId()
ID_SER_CONF = wx.NewId()

VERSION = "V3.03 March 19 2019"
TITLE = "ScanMar_Logger3"


# ###################################################################
#   GraphFrame  -  Build the main frame of the application
# ####################################################################
class GraphFrame(wx.Frame):

    def __init__(self,parent,title=""):
        super (GraphFrame,self).__init__(parent,title=title)

#    def __init__(self):
#        wx.Frame.__init__(self, None, -1, self.title)

        self.SetBackgroundColour('WHITE')

        self.panel= wx.Panel(self)  # Create a Panel instance
        try:
            self.panel.SetBackgroundColour(wx.Colour("WHEAT"))
        except:
            self.panel.SetBackgroundColour(wx.NamedColour("WHEAT")) # wxpython pre v4

        self.statusbar = self.create_status_bar()

        # storage for the data
#        self.data = dict(Pres=[0], Temp=[0], Cond=[0], Sal=[0], F1=[0], F2=[0], L=[0], V=[0], Rate=[0], Et=[0])
        #data variables and associated utitles for data and files

        # these tools process the nema messages
        self.smn_tools = SMN_TOOLS()

        # status and state variables
        self.status = StatusVars()

        #data variables and associated utitles for data and files
        self.data = DataVars(self,self.status)


        #build the display
        self.menubar = wx.MenuBar()
        self.populate_menu()
        self.create_graph_panel()

        self.populate_main_panel()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.panel,0,wx.EXPAND|wx.ALL,border=10)


        # directory to store recorded data and logs
#        if not os.path.exists(self.data.dataDir):
#            os.makedirs(self.data.dataDir)

        # we need a serial instance to allow the  serial config dialogue to function
        self.ser = serial.Serial()

         # queue that will feed the data blocks back to this display system within the re-draw loop
        self.BQueue = queue.Queue()

        # get the last basename, and serial port parameters
        # if there is no pre-existing file ScanMar.CFG a new one is name with default starting basename
        # for the mission and the serial configuration dialogue is displayed to get setup
        if not self.data.read_cfg(self.ser):
            self.data.set_default_com_cfg(self.ser)
            self.on_ser_config(-1)

        self.data.set_FileNames()

#        self.disp_BaseName.Data_text.SetValue(str(self.data.basename))
        self.set_plot_title()

        # the redraw timer is used to add new data to the plot and update any changes via
        # the on_redraw_timer method
        #  1000 ms; ie check  once a second;  since data rate is ~1 second per block (multiple nmea lines)
        self.redraw_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_redraw_timer, self.redraw_timer)
        self.redraw_timer.Start(100)

#        self.redraw_timer.Stop()

# **************************** End of GraphFrame Init **********************
# *** GraphFrame Methods ***************************************************

    def create_graph_panel(self):

#        self.panel = wx.Panel(self)  # Create a Panel instance
        self.data.intial_plot_parms()
        # The Plot-  init_pot sets up the MatPlotLib graph
        self.init_plot()

        # Create a Canvas  make plot area background light gray
#        self.fig.patch.set_facecolor("lightgray")
        self.canvas = FigCanvas(self.panel, -1, self.fig)

        self.set_plot_title()

    # ***********************************************************
    # *********** Setup MatPlotLib graph of data ****************
    def init_plot(self):
        self.dpi = 100
        self.fig = Figure((3.0, 4.5), dpi=self.dpi)
        self.fig.patch.set_facecolor("lightgray")




# plot 0 is host 1-5 are parasites
        self.p_axis_list = [i for i in range(6)]    # empty list to hold dictionaries of parasite axis objects
        self.axis_plot = [i for i in range(6)]    # empty list to hold plots (o will be used for host

        self.host = HostAxes(self.fig, [0.15, 0.12, 0.65, 0.8])
        # create paarsite axis on host axis; sharing common x parameter
        for i in range (1,6,1):
            self.p_axis_list[i] = ParasiteAxes(self.host, sharex=self.host)

        # attache parasite axis to host axis
        for i in range (1,6,1):
            self.host.parasites.append(self.p_axis_list[i])

        # set the color of the graph area
        self.host.set_facecolor([0.7,0.7,0.7])  # a medium gray graph area color

        self.host.tick_params(axis='left', which='major', labelsize=6)

        self.host.axis["right"].set_visible(False)  #turn of right side labels
        self.host.axis["left"].major_ticklabels.set_size(8)

        self.host.set_ylabel(self.data.host_axis["LABEL"], fontweight='bold', fontsize=14)

        self.host.set_xlabel(self.data.x_axis["LABEL"], fontweight='bold', fontsize=10)

        self.host.axis["bottom"].major_ticklabels.set_size(8)
        self.host.xaxis.set_label_coords(self.data.x_axis["OFFSET"][0],self.data.x_axis["OFFSET"][1])
        self.host.set_ylabel(self.data.host_axis["LABEL"], fontweight='bold', fontsize=14)




        #        self.host.set_edgecolor('gray')
#        self.host.set_title('Bongo trace file= ' + self.LogFileName, size=10)
#        self.par1.axis["right"].set_visible(True)
#        self.par1.axis["left"].set_visible(False)
#        self.par1.set_ylabel(u"Net Opening (m)", fontweight='bold', fontsize=14)
        #        self.host.axis["left"].label.set_size(12)
#       self.par1.axis["right"].major_ticklabels.set_visible(True)
#       self.par1.axis["right"].label.set_visible(True)



#        self.par1.axis["right"].major_ticklabels.set_size(8)


        for i in range (1,6,1):
            self.p_axis_list[i].set_ylabel(self.data.p_axis[i]["LABEL"], fontweight='bold', fontsize=14)
            location = self.data.p_axis[i]["SIDE"]
            new_axisline = self.p_axis_list[i]._grid_helper.new_fixed_axis
            self.p_axis_list[i].axis[location] = new_axisline(loc=location, axes=self.p_axis_list[i],
                                                    offset=self.data.p_axis[i]["OFFSET"])
            self.p_axis_list[i].axis[location].major_ticklabels.set_size(8)




        self.fig.add_axes(self.host)
        self.host.axes.grid(True, color='gray')

    # axis plot 0 is host 1-5 are parasites
    # setup the traces, initialize with a single 0 data point pair, and set their color
        self.host.xaxis.set_label_coords(0.5, -0.06)
        clr = self.data.host_axis["COLOR"]
        self.axis_plot[0]= self.host.plot([0.0,0.0],linewidth=1,color=clr,)[0]

        self.host.axis[self.data.host_axis["SIDE"]].label.set_color(self.axis_plot[0].get_color())
        self.host.axis[self.data.host_axis["SIDE"]].label.set_color(clr)
        self.host.tick_params(axis='y', colors=clr)

        self.host.axis[self.data.host_axis["SIDE"]].line.set_color(self.axis_plot[0].get_color())
        self.host.axis[self.data.host_axis["SIDE"]].major_ticks.set_color(self.axis_plot[0].get_color())
        self.host.axis[self.data.host_axis["SIDE"]].major_ticklabels.set_color(self.axis_plot[0].get_color())

        self.host.set_xbound(lower=self.data.x_axis["MIN"] , upper=self.data.x_axis["MAX"])
        self.host.set_ybound(lower=self.data.host_axis["MIN"] - 10.0, upper=self.data.host_axis["MAX"])

    # assign the trace colors to the axis labels and ticks
        for i in range (1,6,1):

            clr = self.data.p_axis[i]["COLOR"]
            self.axis_plot[i] = self.p_axis_list[i].plot([0.0, 0.0], linewidth=1, color=clr, )[0]


            self.p_axis_list[i].axis[self.data.p_axis[i]["SIDE"]].label.set_color(clr) # axis label
            self.p_axis_list[i].axis[self.data.p_axis[i]["SIDE"]].line.set_color(self.axis_plot[i].get_color())
            self.p_axis_list[i].axis[self.data.p_axis[i]["SIDE"]].major_ticks.set_color(self.axis_plot[i].get_color())
            self.p_axis_list[i].axis[self.data.p_axis[i]["SIDE"]].major_ticklabels.set_color(self.axis_plot[i].get_color())




            self.p_axis_list[i].set_xbound(lower=self.data.x_axis["MIN"], upper=self.data.x_axis["MAX"])
            self.p_axis_list[i].set_ybound(lower=self.data.p_axis[i]["MIN"], upper=self.data.p_axis[i]["MAX"])


    # *************** Enf of Init_Plot ***************************


##################################################################################
    def populate_menu(self):

        menu_file = wx.Menu()
        menu_file.AppendSeparator()

        m_ser_config = menu_file.Append(ID_SER_CONF, "Serial Config", "Serial Config")
        self.Bind(wx.EVT_MENU, self.on_ser_config, m_ser_config)
        menu_file.AppendSeparator()
        menu_file.AppendSeparator()
        m_exit = menu_file.Append(wx.ID_EXIT, "E&xit\tCtrl-X", "Exit")
        self.Bind(wx.EVT_MENU, self.on_exit, m_exit)

        # responds to exit symbol x on frame title bar
        self.Bind(wx.EVT_CLOSE, self.on_exit)

        menu_realtime = wx.Menu()
        m_rtstart = menu_realtime.Append(ID_START_RT, "Start", "Start realtime data")
        self.Bind(wx.EVT_MENU, self.on_start_rt, m_rtstart)
        menu_realtime.AppendSeparator()
        m_rtstop = menu_realtime.Append(ID_STOP_RT, "End", "End realtime data")
        self.Bind(wx.EVT_MENU, self.on_stop_rt, m_rtstop)

        menu_archived = wx.Menu()
        m_arcstart = menu_archived.Append(ID_START_ARC, "Start", "Start archived data")
        self.Bind(wx.EVT_MENU, self.on_start_arc, m_arcstart)
        menu_archived.AppendSeparator()
        m_arcstop = menu_archived.Append(ID_STOP_ARC, "End", "End archived data")
        self.Bind(wx.EVT_MENU, self.on_stop_arc, m_arcstop)

        menu_option = wx.Menu()
        m_basehead = menu_option.Append(-1, "Set ship year trip stn", "shipyeartripstn")
        self.Bind(wx.EVT_MENU, self.on_set_base_header, m_basehead)


        menu_help = wx.Menu()
#        m_help = menu_help.Append(-1, "help", "help")
#        self.Bind(wx.EVT_MENU, self.on_help, m_help)
#        menu_help.AppendSeparator()
        m_about = menu_help.Append(-1, "About", "About ScanMar_Logger")
        self.Bind(wx.EVT_MENU, self.OnAbout, m_about)
        
        self.menubar.Append(menu_file, "&File")
        self.menubar.Append(menu_realtime, "RealTime")
        self.menubar.Append(menu_archived, "Archived")
        self.menubar.Append(menu_option, "Trip Options")
        self.menubar.Append(menu_help, "Help")
        self.SetMenuBar(self.menubar)

#        self.SPW_tick.Check(True)
        m_rtstop.Enable(False)
        m_arcstop.Enable(False)
#        m_term.Enable(False)  # leave off for now
        m_basehead.Enable(True)

# ***********************************************************************************
    def populate_main_panel(self):

#       Create a Canvas
#       self.canvas = FigCanvas(self.panel, -1, self.fig)
#       self.r_text = RollingDialBox(self.panel, -1, "Spare)", '0',50)

        self.populate_button_strip(self.panel)

        self.populate_logger_strip(self.panel)

        self.populate_rolling_display_legacy(self.panel)

        self.assemble_display(self.panel)


# ###################################################################################

    def populate_button_strip(self,apanel):

        buttonfont = wx.Font(14, wx.DECORATIVE, wx.ITALIC, wx.BOLD)

        # IN WATER BUTTON
        self.LoggerStart_button = wx.Button(apanel, -1, " - Doors In -\nStart Logging\n(F3)")
        self.LoggerStart_button.SetFont(buttonfont)
        self.LoggerStart_button.SetForegroundColour("FOREST GREEN")  # set text back color
        self.Bind(wx.EVT_BUTTON, self.on_LoggerStart_button, self.LoggerStart_button)

        # ON BOTTOM BUTTON
        self.BottomStart_button = wx.Button(apanel,-1, "On Bottom\nMark Start Fishing\n(F4)")
        self.BottomStart_button.SetFont(buttonfont)
#       self.monitor_button.SetBackgroundColour((255, 155, 0))  # set text back color
        self.BottomStart_button.SetForegroundColour("FOREST GREEN")  # set text back color
        self.Bind(wx.EVT_BUTTON, self.on_BottomStart_button, self.BottomStart_button)

        # WARP ENTRY IS A NESTED SET OF OBJECTS
        self.warpbox = wx.BoxSizer(wx.HORIZONTAL)

        # WARP ENTER BUTTON
        warpfont = wx.Font(12, wx.DECORATIVE,wx.NORMAL, wx.BOLD)
        self.Warp_button  = wx.Button(apanel, -1, "Enter WarpOut(m)\n(F8)  ")
        self.Warp_button.SetFont(warpfont)
        self.Warp_button.SetForegroundColour("FOREST GREEN")  # set text back color
        self.warpbox.Add(self.Warp_button, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 0)
        self.Warp_text = wx.TextCtrl(self.panel,style = wx.TE_PROCESS_ENTER,validator=CharValidator('no-alpha'))

        # WARP TEXT ENTER BOX
        warpTxtfont = wx.Font(18, wx.DECORATIVE, wx.NORMAL, wx.BOLD)
        self.Warp_text.SetFont(warpTxtfont)
        self.Warp_text.SetMaxLength(4)
        self.warpbox.Add(self.Warp_text, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 0)
        self.Warp_text.Bind( wx.EVT_TEXT_ENTER,self.OnWarpTyped)
        self.Bind(wx.EVT_BUTTON, self.on_Warp_button, self.Warp_button)

#        self.WRPbox = wx.BoxSizer(wx.VERTICAL)
#        self.WRPbox.AddSpacer(2)
#        self.WRPbox.Add(self.warpbox, 0, flag=wx.ALIGN_LEFT | wx.TOP)

        # OFF BOTTOM BUTTON
        self.BottomEnd_button = wx.Button(apanel, -1,   "Off Bottom Mark \nEnd Fishing\n(F5)")
        self.BottomEnd_button.SetFont(buttonfont)
#       self.monitor_button.SetBackgroundColour((255, 155, 0))  # set text back color
        self.BottomEnd_button.SetForegroundColour("FOREST GREEN")  # set text back color
        self.Bind(wx.EVT_BUTTON, self.on_BottomEnd_button, self.BottomEnd_button)

        # OUT OF WATER BUTTON
        self.LoggerEnd_button = wx.Button(apanel,-1,   " - Doors Out - \nEnd Logging\n(F6)")
        self.LoggerEnd_button.SetFont(buttonfont)
        self.LoggerEnd_button.SetForegroundColour("FOREST GREEN")  # set text back color
        self.Bind(wx.EVT_BUTTON, self.on_LoggerEnd_button, self.LoggerEnd_button)

        # ABORT BUTTON
        self.Abort_button = wx.Button(apanel, -1, "Abort\n(F10)")
        self.Abort_button.SetFont(buttonfont)
        self.Abort_button.SetForegroundColour("FOREST GREEN")  # set text back color
        self.Bind(wx.EVT_BUTTON, self.on_Abort_button, self.Abort_button)

        # INITIALIZE BUTTON TO DISABLED STATE
        self.LoggerStart_button.Enable(False)
        self.BottomStart_button.Enable(False)
        self.Warp_button.Enable(False)
        self.Warp_text.Enable(False)
        self.BottomEnd_button.Enable(False)
        self.LoggerEnd_button.Enable(False)
        self.Abort_button.Enable(False)

        # SET UP BINDING OFF BUTTONS TO F Keys
        F3_id = wx.NewId()
        F4_id = wx.NewId()
        F5_id = wx.NewId()
        F6_id = wx.NewId()
        F8_id = wx.NewId()
        F10_id = wx.NewId()

        self.Bind(wx.EVT_MENU, self.on_LoggerStart_button, id=F3_id)
        self.Bind(wx.EVT_MENU, self.on_BottomStart_button, id=F4_id)
        self.Bind(wx.EVT_MENU, self.on_Warp_button, id=F8_id)
        self.Bind(wx.EVT_MENU, self.on_BottomEnd_button, id=F5_id)
        self.Bind(wx.EVT_MENU, self.on_LoggerEnd_button, id=F6_id)
        self.Bind(wx.EVT_MENU, self.on_Abort_button, id=F10_id)

        accel_tbl = wx.AcceleratorTable(  [(wx.ACCEL_NORMAL, wx.WXK_F3, F3_id),
                                                (wx.ACCEL_NORMAL, wx.WXK_F4, F4_id),
                                                (wx.ACCEL_NORMAL, wx.WXK_F8, F8_id),
                                                (wx.ACCEL_NORMAL, wx.WXK_F5, F5_id),
                                                (wx.ACCEL_NORMAL, wx.WXK_F6, F6_id),
                                                (wx.ACCEL_NORMAL, wx.WXK_F10, F10_id)
                                               ]
                                            )

        self.SetAcceleratorTable(accel_tbl)

        # standard database colours  http://xoomer.virgilio.it/infinity77/wxPython/Widgets/wx.ColourDatabase.html

        # HORIZONTAL BOX 0 (hb0) HOLDS THE BUTTONS
        self.hb0 = wx.StaticBox(apanel,-1,"Buttons")
        self.hb0.SetBackgroundColour("WHEAT")  # set text back color
        self.hb0.SetForegroundColour((0, 0, 0))  # set text back color
        self.hbox0 = wx.StaticBoxSizer(self.hb0, wx.HORIZONTAL)

        self.hbox0.AddSpacer(5)
        self.hbox0.Add(self.LoggerStart_button, border=5, flag=wx.ALL | wx.ALIGN_CENTER_HORIZONTAL)
        self.hbox0.Add(self.BottomStart_button, border=5, flag=wx.ALL | wx.ALIGN_CENTER_HORIZONTAL)
        self.hbox0.AddSpacer(5)

        self.hbox0.Add(self.warpbox, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
#        self.hbox0.Add(self.WRPbox, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        self.hbox0.AddSpacer(5)
        self.hbox0.Add(self.BottomEnd_button, border=5, flag=wx.ALL | wx.ALIGN_CENTER_HORIZONTAL)
        self.hbox0.Add(self.LoggerEnd_button, border=5, flag=wx.ALL | wx.ALIGN_CENTER_HORIZONTAL)
        self.hbox0.AddSpacer(8)
        self.hbox0.Add(self.Abort_button, border=5, flag=wx.ALL | wx.ALIGN_CENTER_HORIZONTAL)


    def populate_logger_strip(self,apanel):

        # Row 0 - the data monitor display
        x = 1200
        y = 150
        style = wx.TE_MULTILINE | wx.TE_READONLY | wx.SUNKEN_BORDER | wx.VSCROLL

        label = wx.StaticText(apanel,
                label="STATION            DATE       TIME         EVENT       BTM-D   TRL_D   LATITUDE   LONGITUDE  INFO")

        # SCREEN_LOG WILL BE UPDATED DURING RUN
        self.screen_log = wx.TextCtrl(apanel, wx.ID_ANY, size=(x, y), style=style)

        logfont = wx.Font(14, wx.MODERN, wx.NORMAL, wx.BOLD)
        self.screen_log.SetFont(logfont)
        label.SetFont(logfont)

        hbox_EL= wx.GridBagSizer(2, 2)
        hbox_EL.Add(label, (0, 1))
        hbox_EL.Add(self.screen_log, (1, 1))

        EVbx = wx.StaticBox(apanel,-1,"Event Log")
        self.ELbox = wx.StaticBoxSizer(EVbx, wx.VERTICAL)
        self.ELbox.Add(hbox_EL, 0, flag=wx.ALIGN_LEFT | wx.TOP)

    def populate_rolling_display_legacy(self,apanel):

        afontsize = 10
        afontmiddle = 18
        afontbigger = 26

        self.disp_text = OrderedDict()
        hbox = {}

        # DOOR AND WING SENSORS
        hbox[1] = wx.BoxSizer(wx.HORIZONTAL)

        # NOTE: build from a sequence of tuples so that the order of the Dictionary is preserved
        # (normal a:b notation will not work to preserve order when passed into the OrderedDict )

#        timelabel=OrderedDict([("0",u"Current"),("1",u"1 scan Ago"),("2",u"2 scan Ago"),("3",u"3 scan Ago"),
#                                        ("4",u"4 scan Ago")]) # 5 line display

        timelabel=OrderedDict([("0",u"Current")]) # single line display

        disp_label= RollingDialBox_multi_static(apanel, -1,"---- Log ----", timelabel, '0',80,
                                        wx.BLUE,wx.VERTICAL,afontsize)

        disp_text1=OrderedDict([("DVTLAM_P",''),("DVTLAM_R",''),("DVTLAS_P",''),("DVTLAS_R",''),
                                ("DVTLAM_S",''),("CVTLAM_S",'')])

        # xx sets the left side labels and is also used to indicate the number of lines to generate in RollingBox_multi
        xx =OrderedDict([("0",'0'), ("1", '0'),( "2", '0'),( "3", '0'),("4", '0')]) # orgian 5 line display

        xx =OrderedDict([("0",'0')]) # single line display


        x2 = OrderedDict([("DVTLAM_P", 'Port-Pitch'), ("DVTLAM_R", 'Port-Roll'), ("DVTLAS_P",'Stbd-Pitch'),
                        ("DVTLAS_R",'Stbd-Roll'),("DVTLAM_S", 'Door-Spread'),("CVTLAM_S", 'Wing-Spread')])

        # build the data boxes,,  access as disp_text["DVTLAM"].Data_text["R"].SetValue(xxxx)
        for x in disp_text1 :
            disp_text1[x] = RollingDialBox_multi(apanel, -1, x2[x],xx, '-',50,wx.BLACK,wx.VERTICAL,afontsize)
        hbox[1].Add(disp_label, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        for x in disp_text1:
            hbox[1].Add(disp_text1[x], border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)


        # TILT SENSOR
        hbox[2] = wx.BoxSizer(wx.HORIZONTAL)
        disp_text2 = OrderedDict([("TLT_P", ''), ("TLT_R", '')])

        x2 = OrderedDict([("TLT_P", 'Pitch'), ("TLT_R", 'Role')])

        for x in disp_text2:
            disp_text2[x] = RollingDialBox_multi(apanel, -1, x2[x], xx, '-', 50, wx.BLACK, wx.VERTICAL,
                                                          afontsize)
                #        self.hbox3.Add(self.disp_label3, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        for x in disp_text2:
            hbox[2].Add(disp_text2[x], border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

#        self.disp_text2 = OrderedDict([ ("TLT", '')])
#        xxy =OrderedDict([("R",'r'), ("P", 'p'),( "A", 'a'),( "B", 'b')])
#        self.disp_text2["TLT"] = RollingDialBox_multi(self.panel, -1, "Tilt", xxy, '0', 50,wx.BLACK,wx.VERTICAL)

#        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
#        self.hbox2.Add(self.disp_label2, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
#        self.hbox2.Add(self.disp_text2["TLT"], border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        # TRAWL SPEED
        hbox[3] = wx.BoxSizer(wx.HORIZONTAL)
        disp_text3 = OrderedDict([ ("TSP_X", ''),("TSP_Y",'')])

        x2 = OrderedDict([("TSP_X", 'Cross'), ("TSP_Y", 'Along')])

        for x in disp_text3 :
            disp_text3[x] = RollingDialBox_multi(apanel, -1, x2[x],xx, '-',50,wx.BLACK,wx.VERTICAL,afontsize)
#        self.hbox3.Add(self.disp_label3, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        for x in disp_text3:
            hbox[3].Add(disp_text3[x], border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        # TRAWL SOUNDER
        hbox[4] = wx.BoxSizer(wx.HORIZONTAL)
        disp_text4 = OrderedDict([ ("TS_H", ''),("TS_O",''),("TS_C",'')])

        x2 = OrderedDict([("TS_H", 'Height'), ("TS_O", 'Opening'), ("TS_C", 'Clear')])
        for x in disp_text4:
            disp_text4[x] = RollingDialBox_multi(apanel, -1, x2[x], xx, '-', 60, wx.BLACK, wx.VERTICAL,afontsize)
            #        self.hbox3.Add(self.disp_label3, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        for x in disp_text4:
            hbox[4].Add(disp_text4[x], border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

#        self.disp_text4["TS"] = RollingDialBox_multi(self.panel, -1, "TS (m)", xxw, '0', 50,wx.BLACK,wx.VERTICAL)
#        self.hbox4 = wx.BoxSizer(wx.VERTICAL)
#        self.hbox4.Add(self.disp_label4, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
#        self.hbox4.Add(self.disp_text4["TS"], border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        # TRAWL SOUNDER/TEMP
        hbox[5] = wx.BoxSizer(wx.HORIZONTAL)
        disp_text5 = OrderedDict([ ("DPTM_D", ''), ("DPTM_T", '')])

        x2 = OrderedDict([("DPTM_D", 'TrawlDepth'), ("DPTM_T", 'TrawlTemp')])
        for x in disp_text5:
            disp_text5[x] = RollingDialBox_multi(apanel, -1, x2[x], xx, '-', 60, wx.BLACK, wx.VERTICAL, afontsize)
                #        self.hbox3.Add(self.disp_label3, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        for x in disp_text5:
            hbox[5].Add(disp_text5[x], border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        #        self.disp_text4["TS"] = RollingDialBox_multi(self.panel, -1, "TS (m)", xxw, '0', 50,wx.BLACK,wx.VERTICAL)
        #        self.hbox4 = wx.BoxSizer(wx.VERTICAL)
        #        self.hbox4.Add(self.disp_label4, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        #        self.hbox4.Add(self.disp_text4["TS"], border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        # TIME DATE


#        zone = time.tzname[time.daylight]

#        self.hbox6a = wx.BoxSizer(wx.HORIZONTAL)
#        disp_text6a = OrderedDict([("TIMEDATE", '')])
#        xxw = OrderedDict([("DATE", '00-00-00'), ("TIME", '00:00:00')])

#        disp_text6a["TIMEDATE"] = RollingDialBox_multi(apanel, -1, "PC TIME", xxw, '-', 155,
#                                                            wx.BLACK, wx.HORIZONTAL, afontmiddle)
#        hbox[6].Add(disp_text6a["TIMEDATE"], border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        #ET-DIST
        hbox[6] = wx.BoxSizer(wx.HORIZONTAL)
        disp_text6 = OrderedDict([ ("ET_BTM", ''), ("DIST", '')])

        x2 = OrderedDict([("ET_BTM", 'ElapseTime'), ("DIST", 'Dist (Nm)')])
#        xxw = OrderedDict([('00:00:00'),("00.000")])
        for x in disp_text6:
            disp_text6[x] = RollingDialBox_multi(apanel, -1, x2[x], xx, '00.00', 160, wx.BLACK, wx.VERTICAL, afontbigger)
                #        self.hbox3.Add(self.disp_label3, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        for x in disp_text6:
            hbox[6].Add(disp_text6[x], border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        self.disp_label2= RollingDialBox_multi_static(apanel, -1,"---- Log ----", timelabel, '-',80,wx.BLUE,
                                                      wx.VERTICAL,afontsize)

        # GPS DATA
        hbox[8] = wx.BoxSizer(wx.HORIZONTAL)

        disp_text8 = OrderedDict([("GPS_TIME",''),("LAT_DM",''),("LON_DM",''),("VTG_COG",''),("VTG_SPD",'')])
        disp_text8_size = OrderedDict([("GPS_TIME",70),("LAT_DM",90),("LON_DM",100),("VTG_COG",60),("VTG_SPD",60)])

        x2 = OrderedDict([("GPS_TIME",'GMT (GPS)'),("LAT_DM", 'Latitude'), ("LON_DM", 'Longitude'),("VTG_COG","COG"), ("VTG_SPD", 'Speed (kn)')])

        # build the data boxes,,  access as disp_text["DVTLAM"].Data_text["R"].SetValue(xxxx)
        for x in disp_text8:
            disp_text8[x] = RollingDialBox_multi(apanel, -1, x2[x], xx, '-', disp_text8_size[x], wx.BLACK, wx.VERTICAL,afontsize)
        hbox[8].Add(self.disp_label2, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        for x in disp_text8:
            hbox[8].Add(disp_text8[x], border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        # DEPTH BELLOW SHIP
        hbox[11] = wx.BoxSizer(wx.HORIZONTAL)
        disp_text11 = OrderedDict([("DBS", '')])

        x2 = OrderedDict([("DBS", 'Depth (m)')])
        disp_text11["DBS"] = RollingDialBox_multi(apanel, -1, x2["DBS"], xx, '-', 80, wx.BLACK, wx.VERTICAL,
                                                      afontsize)
        hbox[11].Add(disp_text11["DBS"], border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        # STATION ID
#        self.disp_BaseName = RollingDialBox(apanel, -1, "-- Ship ----- Year ------ Trip ---- Set -- ",
#                                            "XXX-2018-000-000", 220,"FOREST GREEN",wx.HORIZONTAL,afontmiddle)

#        print self.BaseName

    # add the dictionaries onto the main dictionary (adds them onto the dis_text dictionary)
        self.disp_text.update(disp_text1)
        self.disp_text.update(disp_text2)
        self.disp_text.update(disp_text3)
        self.disp_text.update(disp_text4)
        self.disp_text.update(disp_text5)
        self.disp_text.update(disp_text6)
        self.disp_text.update(disp_text8)
        self.disp_text.update(disp_text11)

    # Put it all together
        DWSBx = wx.StaticBox(apanel,-1,"Door & Wing Sensors")
        self.DWbox = wx.StaticBoxSizer(DWSBx, wx.HORIZONTAL)
        self.DWbox.Add(hbox[1], 0, flag=wx.ALIGN_LEFT | wx.TOP)

#        InfoBx = wx.StaticBox(apanel,-1,"INFO")
#        self.Infobox = wx.StaticBoxSizer(InfoBx, wx.HORIZONTAL)
#        self.Infobox = wx.BoxSizer( wx.HORIZONTAL)
#        self.Infobox.Add(hbox[6], 0, flag=wx.ALIGN_LEFT | wx.TOP)
#        self.Infobox.Add(self.disp_BaseName, 0, flag=wx.ALIGN_LEFT | wx.TOP)

#        EtDistBx = wx.StaticBox(apanel,-1,"EtDist")
#        self.EtDistbox = wx.StaticBoxSizer(EtDistBx, wx.HORIZONTAL)
#        self.EtDistbox.Add(hbox[7], 0, flag=wx.ALIGN_LEFT | wx.TOP)
#        self.EtDistbox = hbox[7]

        TLTbx = wx.StaticBox(apanel,-1,"Tilt Sensor")
        self.TLTbox = wx.StaticBoxSizer(TLTbx, wx.HORIZONTAL)
        self.TLTbox.Add(hbox[2], 0, flag=wx.ALIGN_LEFT | wx.TOP)

        TSPbx = wx.StaticBox(apanel,-1,"Trawl Speed")
        self.TSPbox = wx.StaticBoxSizer(TSPbx, wx.VERTICAL)
        self.TSPbox.Add(hbox[3], 0, flag=wx.ALIGN_LEFT | wx.TOP)

        TSbx = wx.StaticBox(apanel,-1,"Trawl Sounder/ Trawl Eye")
        self.TSbox = wx.StaticBoxSizer(TSbx, wx.VERTICAL)
        self.TSbox.Add(hbox[4], 0, flag=wx.ALIGN_LEFT | wx.TOP)

        DPTMbx = wx.StaticBox(apanel,-1,"Depth Temp Sensor")
        self.DTbox = wx.StaticBoxSizer(DPTMbx, wx.VERTICAL)
        self.DTbox.Add(hbox[5], 0, flag=wx.ALIGN_LEFT | wx.TOP)

        DBSbx = wx.StaticBox(apanel,-1,"Ship Sounder")
        self.DBSbox = wx.StaticBoxSizer(DBSbx, wx.VERTICAL)
        self.DBSbox.Add(hbox[11], 0, flag=wx.ALIGN_LEFT | wx.TOP)

        GPSbx = wx.StaticBox(apanel,-1,"GPS")
        self.GPSbox = wx.StaticBoxSizer(GPSbx, wx.HORIZONTAL)
        self.GPSbox.Add(hbox[8], 0, flag=wx.ALIGN_LEFT | wx.TOP)

        EtDistbx = wx.StaticBox(apanel,-1,"Tow Time-Distance")
        self.EtDistbox = wx.StaticBoxSizer(EtDistbx, wx.HORIZONTAL)
        self.EtDistbox.Add(hbox[6], 0, flag=wx.ALIGN_LEFT | wx.TOP)


    def assemble_display(self,apanel):

        # LEFT TO RIGHT BOXES FOR ROW 1
        LRbox = wx.BoxSizer(wx.HORIZONTAL)
        LRbox.AddSpacer(4)
        LRbox.Add(self.DWbox, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        LRbox.AddSpacer(4)
        LRbox.Add(self.TSbox, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        LRbox.AddSpacer(4)
        LRbox.Add(self.DTbox, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        LRbox.AddSpacer(4)
        LRbox.Add(self.TLTbox, 0, flag=wx.ALIGN_LEFT | wx.TOP)

        # LEFT TO RIGHT BOXES FOR ROW 2
        LRbox2 = wx.BoxSizer(wx.HORIZONTAL)
        LRbox2.AddSpacer(4)
        LRbox2.Add(self.GPSbox, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        LRbox2.AddSpacer(4)
        LRbox2.Add(self.TSPbox, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        LRbox2.AddSpacer(4)
        LRbox2.Add(self.DBSbox, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        LRbox2.AddSpacer(4)
        LRbox2.Add(self.EtDistbox, 0, flag=wx.ALIGN_LEFT | wx.TOP)

        # STACK ROWS OF BOXES
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.canvas, 1, flag=wx.ALIGN_LEFT | wx.TOP | wx.GROW) #plot
        vbox.Add(self.hbox0, 0, flag=wx.ALIGN_LEFT | wx.TOP)  # buttons
        vbox.Add(self.ELbox, 0, flag=wx.ALIGN_LEFT | wx.TOP)   # events log
        vbox.Add(LRbox, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        vbox.Add(LRbox2, 0, flag=wx.ALIGN_LEFT | wx.TOP)
#        vbox.Add(self.Infobox, 0, flag=wx.ALIGN_LEFT | wx.TOP)


        apanel.SetSizer(vbox)
        vbox.Fit(self)

# ***********************************************************
    def create_status_bar(self):    # as a function incase want to add any modifiers later
        return( self.CreateStatusBar())

# ###### END OF DISPLAY SET-UP ###############
        #############################################

    def set_plot_title(self):
        self.fig.suptitle(self.data.basename, fontsize=12)
        self.canvas.draw()

    def draw_plot(self):
        """ Redraws the plot
        """

        # when xmin is on auto, it "follows" xmax to produce a
        # sliding window effect. therefore, xmin is assigned after
        # xmax.
        #
#        if self.xmax_control.is_auto():
        self.set_plot_title()

# not used actually
        xmax = self.data.pdata["ET_BTM"][len(self.data.pdata["ET_BTM"])-1] if self.data.pdata["ET_BTM"][len(self.data.pdata["ET_BTM"])-1] > 1800 else 1800
#        else:
#            xmax = int(self.xmax_control.manual_value())

#        xmax = 400
        xmin = 0.0

        # for ymin and ymax, find the minimal and maximal values
        # in the data set and add a mininal margin.
        #
        # note that it's easy to change this scheme to the
        # minimal/maximal value in the current display, and not
        # the whole data set.

#        if self.ymin_control.is_auto():
#            ymin = round(min(self.data["Pres"]), 0)
#        else:
#            ymin = int(self.ymin_control.manual_value())



#        if self.tmin_control.is_auto():
#            tmin = round(min(self.data["Temp"]), 0)
#        else:
#            tmin = int(self.tmin_control.manual_value())

#        if self.tmax_control.is_auto():
#            tmax = round(max(self.data["Temp"]), 0)
#        else:
#            tmax = int(self.tmax_control.manual_value())



        # 60 is actually samples per minute from ctd, default is 1/sec but should be a var really
        # neg 60 is to handle depth negative
#        DEFAULT_RATE = 1.0
#        SlopeTime1 = (ymin / self.Dslope) * -60.0 / DEFAULT_RATE
#        SlopeTime2 = SlopeTime1 + (ymin / self.Uslope) * -60.0 / DEFAULT_RATE

#        self.SlopeLineX = np.array([0.0, SlopeTime1, SlopeTime2])
#        self.SlopeLineY = np.array([0.0, ymin, 0.0])

#        DPTM_D_min = 600.0

#        if DPTM_D_min > 0:  # we are working upside down
#            DPTM_D_min *= -1.0
#        DPTM_D_max = 0.0

#        TS_O_min = 1.0
#        TS_O_max = 8.0

#        TS_C_min = -1.0
#        TS_C_max = 11.0

#        DVTLAM_S_min = 10.0
#        DVTLAM_S_max = 80.0

#        CVTLAM_S_min = 5.0
#        CVTLAM_S_max = 30.0

#        VTG_SPD_min = 0.0
#        VTG_SPD_max = 5.0

#        self.host.set_xbound(lower=xmin, upper=xmax)
#        self.host.set_ybound(lower=DPTM_D_min - 10.0, upper=DPTM_D_max)

#       self.par1.set_xbound(lower=xmin, upper=xmax)
#       self.par1.set_ybound(lower=TS_O_min, upper=TS_O_max)

#        self.par4.set_xbound(lower=xmin, upper=xmax)
#        self.par4.set_ybound(lower=TS_C_min, upper=TS_C_max)

#        self.par2.set_xbound(lower=xmin, upper=xmax)
#        self.par2.set_ybound(lower=DVTLAM_S_min, upper=DVTLAM_S_max)

#        self.par3.set_xbound(lower=xmin, upper=xmax)
#        self.par3.set_ybound(lower=CVTLAM_S_min, upper=CVTLAM_S_max)

#        self.par5.set_xbound(lower=xmin, upper=xmax)
#        self.par5.set_ybound(lower=VTG_SPD_min, upper=VTG_SPD_max)

        # anecdote: axes.grid assumes b=True if any other flag is
        # given even if b is set to False.
        # so just passing the flag into the first statement won't
        # work.
        #
#        if self.cb_grid.IsChecked():
#            self.axes.grid(True, color='gray')
#        else:
#            self.axes.grid(False)
#        self.axes.grid(True, color='gray')

        # no need to redraw if we are idling the data input
#        if (self.GraphRun):
#        if (True):
            #            self.plot_Pres.set_xdata(np.arange(len(self.data["Pres"])))

# host axis is by default set to the net depth channel
# remeber we are working in negatives for depth
        ym = min(self.data.pdata[self.data.host_axis["CHANNEL"]])

        ymin = int(ym/10)*10 + 10

        ymax = ymin - 20
#        print (ym,ymin, ymax)
        self.host.set_ybound(lower=ymin, upper=ymax)
#        self.host.set_xbound(lower=ymin, upper=ymax)


        self.axis_plot[0].set_xdata(np.array(self.data.pdata[self.data.x_axis["CHANNEL"]]))
        self.axis_plot[0].set_ydata(np.array(self.data.pdata[self.data.host_axis["CHANNEL"]]))

        for i in range (1,6,1):

            self.axis_plot[i].set_xdata(np.array(self.data.pdata[self.data.x_axis["CHANNEL"]]))
            self.axis_plot[i].set_ydata(np.array(self.data.pdata[self.data.p_axis[i]["CHANNEL"]]))



            # if the ref line is changed
#        self.plot_Ref.set_xdata(self.SlopeLineX)
#        self.plot_Ref.set_ydata(self.SlopeLineY)

        # any scalling changes or change to the ref line will get updated on this call
        self.canvas.draw()

    # *** END of draw_plot ********************88
    def erase_plot(self):

        #            self.plot_Temp.set_xdata(np.arange(len(self.data["Temp"])))

        for i in range (0,6,1):
            self.axis_plot[i].set_xdata(np.array([0.0]))
            self.axis_plot[i].set_ydata(np.array([0.0]))

        self.canvas.draw()

    # Save plot image
    def on_save_plot(self, event):

            self.canvas.print_figure(self.data.PLOTFileName, dpi=self.dpi)
            self.flash_status_message("Image Saved to %s" % self.data.PLOTFileName)

    # ############################################
# ************* ACTION METHODS ***************
# ############################################

    # If we have no source, prompt to see of serial soruce desired (the normal)
    # Else do nothing; if user wants play back they can choose it from main menu
    def on_LoggerStart_button(self, event):

        if not self.LoggerStart_button.IsEnabled():
            return

        self.setup_new_tow()

        self.status.LoggerRun = True
        self.LoggerStart_button.Enable(False)
        self.BottomStart_button.Enable(True)
        self.Abort_button.Enable(True)
        self.screen_log.AppendText('\n' + self.data.mark_event("INWATER"))
        self.flash_status_message("LOGGER STARTED")

    def on_BottomStart_button(self, event):
        if not self.BottomStart_button.IsEnabled():
            return

        self.flash_status_message("BOTTOM TOW STARTED")
        self.status.OnBottom = True
        self.status.StartTime = 0
        self.BottomStart_button.Enable(False)
        self.Warp_button.Enable(True)
        self.BottomEnd_button.Enable(True)
        self.Warp_text.Enable(True)
        self.screen_log.AppendText('\n' +  self.data.mark_event("ONBOTTOM"))

    # if they use the warp button to enable the warp enter box
    def on_Warp_button(self, event):
        if not self.Warp_button.IsEnabled():
            return

        self.Warp_text.Enable(True)
        self.Warp_text.SetFocus()
        self.WarpOut = self.get_warp()
        self.flash_status_message("WARP ENTERED")

    # if they click in the warp enter box to enter value
    def OnWarpTyped(self, event):
        self.data.WarpOut = event.GetString()
        self.Warp_text.Enable(False)
        self.screen_log.AppendText('\n' + self.data.mark_event("WARPENTER"))

    def get_warp(self):
        return(self.Warp_text.GetValue())

    def on_BottomEnd_button(self, event):

        if not self.BottomEnd_button.IsEnabled():
            return

        self.status.OnBottom = False
        self.BottomEnd_button.Enable(False)
        self.LoggerEnd_button.Enable(True)

        self.screen_log.AppendText('\n' + self.data.mark_event("OFFBOTTOM"))
        self.flash_status_message("BOTTOM TOW ENDED")

    def on_LoggerEnd_button(self, event):

        if not self.LoggerEnd_button.IsEnabled():
            return
        self.on_save_plot(1)
        self.status.LoggerRun = False
        self.screen_log.AppendText('\n' + self.data.mark_event("OUTWATER"))
        self.Warp_text.Enable(False)
        self.Warp_button.Enable(False)

        self.clear_all_buttons()
        if self.status.RT_source:
            self.on_Increment_tow_button(-1)
        self.flash_status_message("TOW ENDED")


    def on_Abort_button(self, event):

            if not self.Abort_button.IsEnabled():
                self.flash_status_message("ABORT CANCELLED")
                return

            if self.Confirm_abort_dialogue(event):
                self.flash_status_message("ABORTTING....")
                self.status.OnBottom = False

                self.screen_log.AppendText('\n' + self.data.mark_event("ABORT"))

                self.abort_logging_file()
                self.clear_all_buttons()
                self.setup_new_tow()


    def on_Increment_tow_button(self, event):
        old = self.data.ShipTripSet["SET"]
        self.data.increment_tow()
        self.setup_new_tow()
        self.ShowMessage ("LOGGING FINISHED FOR SET # "+old+"\nREADY FOR NEXT SET# "+self.data.ShipTripSet["SET"], "Next Set Is..",-1)

    def on_start_arc(self,event):
        self.status.RT_source = False
        self.status.ARC_source = True
        self.Startup_Data_Source()
        self.LoggerStart_button.Enable(True)

    def on_stop_arc(self,event):
        self.status.RT_source = False
        self.status.ARC_source = False
        self.Shutdown_Data_Source()
        self.clear_all_buttons()

    def on_start_rt(self, event):
        self.status.RT_source = True
        self.status.ARC_source = False
        self.Startup_Data_Source()
        self.LoggerStart_button.Enable(True)

    def on_stop_rt(self, event):
        self.status.RT_source = False
        self.status.ARC_source = False
        self.Shutdown_Data_Source()
        self.clear_all_buttons()

#    def onF4(self, event):
#        print ("F4 hit",event)

# ########### -----------------------------------
    def display_values (self):

        for Sensor in self.data.disp_list :   #  dont display everything that might be feed
#            print ("sensor= ",Sensor)
            if Sensor in self.data.JDict:
                if Sensor == "LAT_DM":
                    lat= self.data.JDict[Sensor]["measurement_val"]
                    gps_lat_string = str(lat[:2] + "\xb0" + " " + '{:>6.6}'.format(lat[2:8]) + "\' " + lat[9:])
                    self.disp_text[Sensor].update_values(gps_lat_string, "X")
                elif Sensor == "LON_DM":
                    lon = self.data.JDict[Sensor]["measurement_val"]
                    gps_lon_string = str(lon[:3] + "\xb0" + " " + '{:>6.6}'.format(lon[3:8]) + "\' " + lon[9:])
                    self.disp_text[Sensor].update_values(gps_lon_string, "X")
                elif Sensor == "VTG_COG":
                    x= self.data.JDict[Sensor]["measurement_val"]
                    self.disp_text[Sensor].update_values(str(x) + "\xb0", "X")   # with ° symbol
                elif Sensor == "GPS_TIME":
                    self.disp_text[Sensor].update_values(self.data.JDict[Sensor]["measurement_val"],
                                                 self.data.JDict[Sensor]["STATUS"])
                else:
                    self.disp_text[Sensor].update_values(self.data.JDict[Sensor]["measurement_val"],
                                                 self.data.JDict[Sensor]["STATUS"])


################### ON_REDRAW_TIMER ##########################################################
# This method is repeatably called by the re-draw timer to get any new data
# what it does depends on the STATE variables
##############################################################################################

    def on_redraw_timer(self, event):

    # working variables with no persistence outside this routine or across calls to it
        Raw_String = OrderedDict()
#        dty =  time.strftime('%Y-%m-%d')
#        dtt= time.strftime('%H:%M:%S')
#        self.disp_text["TIMEDATE"].Data_text["DATE"].SetValue(str(dty))
#        self.disp_text["TIMEDATE"].Data_text["TIME"].SetValue(str(dtt))
        ET = 0

        # If a data source has not been defined do nothing on this pass
        if self.status.DataSource == None :
            return()

        if  not self.status.MonitorRun :
            # if we have a data source but are not monitoring
            # if source is live serial the data is just waste gated
            # if the source is a file the reader pauses
            self.status.DataSource.pause_data_feed()
            return()
        else :
            # process the available data to screen etc, so retrieve a block of input else return to try later
            if not self.BQueue.empty():
                tries = 0
                block = self.BQueue.get()
            else:   # Empty Queue - do nothing
                return()
# process the block of data
        if block["OK"]:
            for sentence_type in block:
                if sentence_type != "OK" and sentence_type != "REASON":  # skip these house keepers flag dict elements
                    self.smn_tools.dispatch_message(sentence_type, block[sentence_type], Raw_String,
                                                    self.data.JDict)
#                    print ("calling display "+self.data.JDict["LAT_DM"]["measurement_val"])
                else:
                    pass


            self.display_values()
        else:
            if block["REASON"] == "FINISHED":
                self.flash_status_message("DATA SOURCE SIGNALLED FINISHED")
                if self.status.ARC_source:
                    self.on_stop_arc(-1)
                else:
                    self.on_stop_rt(-1)
            return ()

    # This is the elapsed time since the start of monitoring the bottom section
        if self.status.OnBottom:
            if self.status.StartTime == 0:
#                self.status.StartTime = datetime.now()
                self.status.StartTime = datetime.strptime(self.data.JDict["GPS_TIME"]['measurement_val'],'%H:%M:%S')
                self.slat = float(self.data.JDict["LAT_deci"]['measurement_val'])   # for the distance calcualtion
                self.slon = float(self.data.JDict["LON_deci"]['measurement_val'])
                et = 0
                self.data.JDict["ET_BTM"]['measurement_val'] = 0.0
                self.data.dist  = 0.0
                self.data.elapsed = ""
            else:
                Et = datetime.strptime(self.data.JDict["GPS_TIME"]["measurement_val"],'%H:%M:%S') - self.status.StartTime
                self.data.elapsed = str(timedelta(seconds=Et.seconds))
                et = timedelta(seconds=Et.seconds).total_seconds()/60.0
#                self.data.JDict["ET"] = OrderedDict([("measurement_val", et), ("QF",'-'), ("STATUS",'-')])
                self.disp_text["ET_BTM"].update_values(str(timedelta(seconds=Et.seconds)),'X')
#                self.disp_text["ET_BTM"].update_values(str(et),'X')
                self.data.dist  = self.data.haversine (self.slon, self.slat, float(self.data.JDict["LON_deci"]['measurement_val']),
                                             float(self.data.JDict["LAT_deci"]['measurement_val']) )

#                self.data.JDict["DIST"] = OrderedDict([("measurement_val", '{:>7.3}'.format(self.data.dist)), ("QF", '-'), ("STATUS", '-')])
                self.disp_text["DIST"].update_values('{:>7.3}'.format(self.data.dist),'X')


# update the plot when on bottom (for now .. have an ET issue- need another ET for full tow)
            # bad data can cause issues here and break the plot ,, needs better error control and recovery
            try:
                self.data.pdata[self.data.x_axis["CHANNEL"]].append(et)
                self.data.pdata[self.data.host_axis["CHANNEL"]].append(-1. * float(self.data.JDict[self.data.host_axis["CHANNEL"]]["measurement_val"]))
                for i in range (1,6,1):
                    self.data.pdata[self.data.p_axis[i]["CHANNEL"]].append(float(self.data.JDict[self.data.p_axis[i]["CHANNEL"]]["measurement_val"]))

            except:
#                print ("plot exception")
                return

            self.draw_plot()


# update the logfile(s)
        if self.status.LoggerRun:
            if self.status.RT_source:  # only write files not in archive playback mode
                self.data.write_RawData(Raw_String)
                self.data.write_CSVdata(self.data.JDict)
        # end of if LoggerRun
        # end of for sentence in block...

######################## Menu things ########################

# #############################################################################
#  Note:  These Console messages seem to occur when FileDialog is used on a PC running ViewFinity
#    D_Lib: debug    printing    for files[. *] and level[100] is turned on
#    D_Lib: debug    printing    for files[. *] and level[200] is turned on
#    D_Lib: debug    printing    for files[. *] and level[300] is turned on
# ########################################################################

    ########################################################
    # dialog to verify abort

    def Confirm_abort_dialogue(self, event):
        dlg = wx.MessageDialog(self, "Want to Abort?", "Abort", wx.YES_NO | wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_YES:
            return (True)
        else:
            return (False)

    def Confirm_Increment_dialogue(self,event,new_set):
        dlg = wx.MessageDialog(self, "Increment set # to "+new_set+" for next tow?", "Newset",
                               wx.YES_NO | wx.ICON_QUESTION)

        if dlg.ShowModal() == wx.ID_YES:
            return (True)
        else:
            return (False)

    def Confirm_start_RT_dialogue(self, event):
        dlg = wx.MessageDialog(self, "Real-time data not Running.\nOpening feed from Scanmar"
                                     "When data seen on screen please retry IN WATER button", wx.OK | wx.ICON_QUESTION)

        if dlg.ShowModal() == wx.ID_OK:
            return (True)
        else:
            return (False)

    def abort_logging_file(self):
        pass

    def clear_all_buttons(self):
        if self.status.RT_source  == True  or self.status.ARC_source == True:
            self.LoggerStart_button.Enable(True)
        else:
            self.LoggerStart_button.Enable(False)
        self.BottomStart_button.Enable(False)
        self.BottomEnd_button.Enable(False)
        self.LoggerEnd_button.Enable(False)
        self.Abort_button.Enable(False)
        self.disp_text["ET_BTM"].update_values('00:00:00','X')
        self.disp_text["DIST"].update_values('0000.0','X')
        pass

    # Configure serial port, requires our serial instance, make sure port is closed before calling
    def on_ser_config(self,event):
        if self.ser.isOpen():
            self.ser.close()
        dialog_serial_cfg = wxSerialConfigDialog.SerialConfigDialog(None, -1, "",
                show=wxSerialConfigDialog.SHOW_BAUDRATE|wxSerialConfigDialog.SHOW_FORMAT|wxSerialConfigDialog.SHOW_FLOW,
                serial=self.ser
            )
        result = dialog_serial_cfg.ShowModal()
        dialog_serial_cfg.Destroy()
        self.data.save_cfg(self.ser)

# RT start button pressed on main menu RT pull down - note this is the default mode
    def Startup_Data_Source (self):

        menubar = self.menubar

        if self.status.RT_source :
            ID_START = ID_START_RT
            ID_STOP = ID_STOP_RT
            self.status.DataSource = DataGen_que(self, "SERIAL", self.ser, self.BQueue)
#            self.status.DataSource = DataGen_que(self, "SERIAL", self.ser)  # Create a data source instance
            menubar.EnableTop(2, False)  # lock out ARC playback while RealTime running
        else: # ARC_SOURCE
            FileName = self.data.get_file_dialog()  # get filename of logged file
            if FileName != None:

                Source = "ARCHIVE"
                self.data.basename = os.path.splitext(os.path.basename(FileName))[0]

                self.data.make_SYTS(self.data.basename)
                self.setup_new_tow()

                self.status.DataSource = DataGen_que(self, "ARCHIVE", FileName, self.BQueue)
#                self..status.DataSource = DataGen_que(self,"ARCHIVE", FileName)  # Create a data source instance
                menubar.EnableTop(1, False)  # lock out RT playback while Archived running
                ID_START = ID_START_ARC
                ID_STOP = ID_STOP_ARC
            else:
                self.status.ARC_source = False
                return()



        enabled = menubar.IsEnabled(ID_START)  # reverse the menu items
        menubar.Enable(ID_START,not enabled)
        enabled = menubar.IsEnabled(ID_STOP)
        menubar.Enable(ID_STOP,not enabled)

        menubar.Enable(ID_SER_CONF, False)  # lock out serial config while running

        self.settings = {}

        self.status.MonitorRun = True
        self.status.DataSource.start()
        self.status.DataSource.start_data_feed()

        if self.status.RT_source :
            self.screen_log.AppendText('Opening Data Port...' )
            self.ShowMessage ("Opening Data port\nPlease Wait for data to display\nbefore Starting Logging ", "PLease wait..",-1)


# *****************************************************************

    def Shutdown_Data_Source (self):

        if self.status.DataSource != None:
            self.status.DataSource.close_DataSource()
            self.status.DataSource = None
            self.status.StartTime = 0

        if self.status.RT_source :
            try:
              self.data.close_files("ALL")
              self.flash_status_message("CLOSING FILES...")
            except: pass
        
            self.status.RT_source = False
            self.status.ARC_source = False

        if self.status.RT_source :
            ID_START = ID_START_RT
            ID_STOP = ID_STOP_RT

        else:
            ID_START = ID_START_ARC
            ID_STOP = ID_STOP_ARC

        # reset the menu items to startup defaults
        menubar = self.GetMenuBar()
        menubar.EnableTop(1, True)  # turn back on menus
        menubar.EnableTop(2, True)

        menubar.Enable(ID_START_RT,True)
        menubar.Enable(ID_START_ARC,True)
        menubar.Enable(ID_STOP_RT,False)
        menubar.Enable(ID_STOP_ARC,False)

        menubar.Enable(ID_SER_CONF, True)

        self.status.MonitorRun = False
        self.status.OnBottom = False

    def setup_new_tow(self):
        if self.status.RT_source:
            self.data.save_cfg(self.ser)
            self.data.close_files("ALL")
            self.data.set_FileNames()
#            self.disp_BaseName.Data_text.SetValue(str(self.data.basename))
            self.set_plot_title()
        self.data.basename = self.data.make_base_name()
        self.data.WarpOut = '0'

        self.set_plot_title()
#        self.disp_BaseName.Data_text.SetValue(self.data.basename)
        self.disp_text["ET_BTM"].update_values('00:00:00','X')
        self.disp_text["DIST"].update_values('0000.0','X')
        self.Warp_text.SetValue('')
        self.erase_plot()
        self.data.initialize_pdata()


    def on_set_base_header(self,event):
        xx = ShipTrip_Dialog(self)

        xx.SetBase(self.data.ShipTripSet["SHIP"],self.data.ShipTripSet["YEAR"],self.data.ShipTripSet["TRIP"],self.data.ShipTripSet["SET"])
        res=xx.ShowModal()

        if res == wx.ID_OK:
            self.data.ShipTripSet["SHIP"] = xx.GetShip()
            self.data.ShipTripSet["YEAR"] = xx.GetYear()
            self.data.ShipTripSet["TRIP"] = xx.GetTrip()
            self.data.ShipTripSet["SET"] = xx.GetStn()
            self.data.basename = self.data.make_base_name()

            self.setup_new_tow()
            xx.Destroy()
            self.set_plot_title()

    def on_edit_head(self,event):
        if self.status.RT_source == True:
            self.on_stop_rt (1)
#        WINAQU_GUI_BONGO.main()

    def on_exit(self, event):
        self.flash_status_message("CLOSING SOURCE AND FILES...")
        self.Shutdown_Data_Source()
        self.redraw_timer.Stop()
        self.data.save_cfg(self.ser)
        self.data.close_files("ALL")

        self.Destroy()

    
    def flash_status_message(self, msg, flash_len_ms=2000):
        self.statusbar.SetStatusText(msg)
        self.timeroff = wx.Timer(self)
        self.Bind(
            wx.EVT_TIMER, 
            self.on_flash_status_off, 
            self.timeroff)
        self.timeroff.Start(flash_len_ms, oneShot=True)
    
    def on_flash_status_off(self, event):
        self.statusbar.SetStatusText('')

    def message_box (self,message):
        result= wx.MessageBox (message,style=wx.CENTER|wx.OK)

    def ShowMessage(self,msg,msg_title, event):
        dial = wx.MessageDialog(None, msg, msg_title,
        wx.OK | wx.ICON_INFORMATION)
        dial.ShowModal()  

    def OnAbout(self,event):
        """ Show About Dialog """
        try:
            info = wx.adv.AboutDialogInfo()
        except:
            info = wx.AboutDialogInfo()

        desc = ["\nScanMar_Logger\n",
                "Platform Info: (%s,%s)",
                "License: None - see code"]
        desc = "\n".join(desc)

        # Platform info
        py_version = [sys.platform,", python ",sys.version.split()[0]]
        platform = list(wx.PlatformInfo[1:])
        platform[0] += (" " + wx.VERSION_STRING)
        wx_info = ", ".join(platform)

        info.SetName(TITLE)
        info.SetVersion(VERSION)
        info.SetDevelopers (["D. Senciall ,  May 2018",
                             "\nScience Branch",
                             "\n NWAFC, NL region-DFO, Gov. of Canada"])
        info.SetCopyright ("Note: See Source for any 3rd party credits")
#        info.SetDescription (desc % (py_version, wx_info))
        try:
            wx.adv.AboutBox(info)
        except:
            wx.AboutBox(info)

#******** END of GraphFrame ************************************************************

##############################################################################################

class GraphApp(wx.App):
    def OnInit(self):
        title = TITLE + " " + VERSION
        self.frame = GraphFrame(None,title=title)
        self.frame.Show()
        return True
#####################################  MAIN ENTRY POINT ################################        
if __name__ == '__main__':

#    app = wx.App()
#    app.frame = GraphFrame()
#    app.frame.Show()
    app = GraphApp(False)
    app.MainLoop()
###################################### END OF CODE #####################################
