
# Font note
# Point size	This is the standard way of referring to text size.
# Family	Supported families are: wx.DEFAULT, wx.DECORATIVE, wx.ROMAN, wx.SCRIPT, wx.SWISS, wx.MODERN. wx.MODERN is a fixed pitch font; the others are either fixed or variable pitch.
# Style	The value can be wx.NORMAL, wx.SLANT or wx.ITALIC.
# Weight	The value can be wx.NORMAL, wx.LIGHT or wx.BOLD.
# Underlining	The value can be True or False.
# Face name	An optional string specifying the actual typeface to be used. If None, a default typeface will chosen based on the family.
# Encoding	The font encoding (see wx.FONTENCODING_XXX constants and the Font Encodings for more details)


import wx
import string
#import wx.lib.colourdb as wb


class RollingDialBox_2d(wx.Panel):
    """ Displays the realtime data values, even when graph is paused. size = 50 for most
            self.dvtlam_text = RollingDialBox(self.panel, -1, "DVTLAM", '0',50)
    """
    def __init__(self, parent, ID, label, initval ,size,color, orient,afontsize):
        wx.Panel.__init__(self, parent, ID)

        self.value = initval

        style = wx.TE_MULTILINE | wx.TE_READONLY |wx.TE_RICH
#        style =  wx.TE_READONLY
        box = wx.StaticBox(self, -1, label)
        sizer = wx.StaticBoxSizer(box, orient)

#        x = 45
#        y=70
        self.Data_text = wx.TextCtrl( self, wx.ID_ANY, self.value, wx.DefaultPosition,wx.Size(size, -1)
                                      , style=style )
#        self.Data_text = wx.TextCtrl( self, wx.ID_ANY, self.value, wx.DefaultPosition,
#                                      wx.Size( size ,-1 ), wx.TE_READONLY)
        self.Data_text.SetForegroundColour(color)


        self.Data_text.SetFont( wx.Font( afontsize, wx.DEFAULT, wx.NORMAL, wx.BOLD, False, "Arial" ) )

        sizer.Add(self.Data_text, 0, wx.ALL, 0)

        self.SetSizer(sizer)
        sizer.Fit(self)
# #######################################################################
class RollingDialBox(wx.Panel):
    """ Displays the realtime data values, even when graph is paused. size = 50 for most
            self.dvtlam_text = RollingDialBox(self.panel, -1, "DVTLAM", '0',50)
    """
    def __init__(self, parent, ID, label, initval ,size,color, orient,afontsize):
        wx.Panel.__init__(self, parent, ID)

        self.value = initval

#        style = wx.TE_MULTILINE | wx.TE_READONLY |wx.TE_RICH
        style =  wx.TE_READONLY
        box = wx.StaticBox(self, -1, label)
        sizer = wx.StaticBoxSizer(box, orient)

#        x = 45
#        y=70
        self.Data_text = wx.TextCtrl( self, wx.ID_ANY, self.value, wx.DefaultPosition,wx.Size(size,-1)
                                      , style=style )
#        self.Data_text = wx.TextCtrl( self, wx.ID_ANY, self.value, wx.DefaultPosition,
#                                      wx.Size( size ,-1 ), wx.TE_READONLY)
        self.Data_text.SetForegroundColour(color)


        self.Data_text.SetFont( wx.Font( afontsize, wx.DEFAULT, wx.NORMAL, wx.BOLD, False, "Arial" ) )

        sizer.Add(self.Data_text, 0, wx.ALL, 0)

        self.SetSizer(sizer)
        sizer.Fit(self)
# #######################################################################
class RollingDialBox_multi(wx.Panel):
        """ Displays the realtime data values, even when graph is paused. size = 50 for most
                self.dvtlam_text = RollingDialBox(self.panel, -1, "DVTLAM", '0',50)
        """

        def __init__(self, parent, ID, label, DT, initval, size, color, orient,afontsize):
            wx.Panel.__init__(self, parent, ID)

            self.value = initval
            bordersize = 0
            logfont = wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD)
            self.DTT = DT
            self.Data_text = {}
            box = wx.StaticBox(self, -1, label)
            #        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)
            sizer = wx.StaticBoxSizer(box, orient)
            for x in self.DTT:
                #            print x,self.DTT[x]
                if self.DTT[x] == '':
                    style1 = wx.TE_READONLY | wx.BORDER_NONE | wx.TE_RICH2 | wx.TE_CENTRE
                else:
                    style1 = wx.TE_READONLY  #
                self.Data_text[x] = wx.TextCtrl(self, wx.ID_ANY, self.value, wx.DefaultPosition,
                                                wx.Size(size, -1), style=style1)
                self.Data_text[x].SetMaxLength(40)
                self.Data_text[x].SetFont(wx.Font(afontsize, 74, 90, 92, False, "Arial"))
#                self.Data_text[x].SetFont(logfont)
                self.Data_text[x].SetValue(self.DTT[x])
                self.Data_text[x].SetForegroundColour(color)
                self.Data_text[x].SetBackgroundColour("#f9f9f9")
                sizer.Add(self.Data_text[x], 0, wx.ALL, bordersize)

#            self.Data_text[].SetBackgroundColour("#ffffff")
            self.SetSizerAndFit(sizer)
            sizer.Fit(self)


        def update_values(self,value,interp):
            for i in range(4,0,-1):
                self.Data_text[str(i)].SetValue(self.Data_text[str(i-1)].GetValue())
                self.Data_text[str(i)].SetForegroundColour(self.Data_text[str(i-1)].GetForegroundColour())
            self.Data_text["0"].SetValue(value)
            if interp == "A" :   # else a V for interpolated or eched
                self.Data_text["0"].SetForegroundColour(wx.RED)
            else:
                self.Data_text["0"].SetForegroundColour(wx.BLACK)



# *** END of RollingDial Box Class **************************

    # *** END of RollingDial Box Class **************************

class RollingDialBox_multi_static(wx.Panel):
        """ Displays the realtime data values, even when graph is paused. size = 50 for most
                self.dvtlam_text = RollingDialBox(self.panel, -1, "DVTLAM", '0',50)
        """

        def __init__(self, parent, ID, label, DT, initval, size, color,orient,afontsize):
            wx.Panel.__init__(self, parent, ID)

            self.value = initval
            bordersize=  0
            self.DTT = DT
            self.Data_text = {}
            box = wx.StaticBox(self, -1, label)
            sizer = wx.StaticBoxSizer(box, orient)
            for x in self.DTT:
#                print x, self.DTT[x]
                if self.DTT[x] == '':
                    style1 = wx.TE_READONLY | wx.BORDER_NONE | wx.TE_RICH2 | wx.TE_CENTRE
                else:
                    style1 = wx.TE_READONLY |wx.BORDER_NONE
                self.Data_text[x] = wx.StaticText(self, wx.ID_ANY, self.DTT[x], wx.DefaultPosition,
                                                wx.Size(size, -1), style=style1)
#                self.Data_text[x].SetMaxLength(40)  # point,family,Style,weight,Underline,facename,encoding
                self.Data_text[x].SetFont(wx.Font(afontsize, 74, 90, 92, False, "Arial"))
#                self.Data_text[x].SetValue(self.DTT[x])
                self.Data_text[x].SetForegroundColour(color)
                sizer.Add(self.Data_text[x], 0, wx.ALL, bordersize)
                sizer.AddSpacer(7)

            self.SetSizer(sizer)
            sizer.Fit(self)



# ##################### Multi line static text box for log output
class multiline_text_static(wx.Panel):

    def __init__(self, parent, ID):
        wx.Panel.__init__(self, parent, ID)

        style = wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL |wx.VSCROLL

        x= 600
        y=500
        self.log = wx.TextCtrl(self, wx.ID_ANY, size=(x,y), style=style)
#        self.log.SetDefaultStyle(wx.TextAttr(wx.NullColour,wx.LIGHT_GREY))
        self.SetBackgroundColour(wx.NamedColour("GREY25"))
#        self.log = wx.TextCtrl(self, wx.ID_ANY, style=style)

        # Add widgets to a sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.log, 1, wx.ALL | wx.EXPAND, 5)
        self.SetSizerAndFit(sizer)

         # redirect text here
#        sys.stdout = log

# *** END of RollingDial_multi Box Class **************************
class Vertical_lable_box_multi(wx.Panel):
    """
    """
    def __init__(self, parent, ID, label, initval ,size):
        wx.Panel.__init__(self, parent, ID)

        self.value = initval

        self.label_text = {"DVTLAM":'',"DVTLAS":'',"CVTLAS":'',"CVTLAM":''}
        box = wx.StaticBox(self, -1, '')
        sizer = wx.StaticBoxSizer(box, wx.HORIZONTAL)

        for x in self.label_text:
            self.label_text[x] = wx.TextCtrl( self, wx.ID_ANY, self.value, wx.DefaultPosition,
                                      wx.Size( size ,-1 ), wx.TE_READONLY )
            self.label_text[x].SetMaxLength( 10 )
            self.label_text[x].SetFont( wx.Font( 10, 74, 90, 92, False, "Arial" ) )
            self.label_text[x].SetValue(x)
            sizer.Add(self.label_text[x], 0, wx.ALL, 10)

        self.SetSizer(sizer)
        sizer.Fit(self)


# *** END of RollingDial Box Class **************************
class BoundControlBox(wx.Panel):
    """ A static box with a couple of radio buttons and a text
        box. Allows to switch between an automatic mode and a
        manual mode with an associated value.
    """
    def __init__(self, parent, ID, label, initval ,start_val):
        wx.Panel.__init__(self, parent, ID)

        self.value = initval

        box = wx.StaticBox(self, -1, label)
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)

        if (start_val == 0) :
            self.radio_auto = wx.RadioButton(self, -1,
                                             label="Auto " +"(" + initval + ")", style=wx.RB_GROUP)
        else:
            self.radio_auto = wx.RadioButton(self, -1,
                                             label="Auto", style=wx.RB_GROUP)

        self.radio_manual = wx.RadioButton(self, -1,
                                           label="Manual")
        self.manual_text = wx.TextCtrl(self, -1,
                                       size=(35, -1),
                                       value=str(initval),
                                       style=wx.TE_PROCESS_ENTER)

        self.Bind(wx.EVT_UPDATE_UI, self.on_update_manual_text, self.manual_text)
        self.Bind(wx.EVT_TEXT_ENTER, self.on_text_enter, self.manual_text)

        manual_box = wx.BoxSizer(wx.HORIZONTAL)
        manual_box.Add(self.radio_manual, flag=wx.ALIGN_CENTER_VERTICAL)
        manual_box.Add(self.manual_text, flag=wx.ALIGN_CENTER_VERTICAL)

        sizer.Add(self.radio_auto, 0, wx.ALL, 10)
        sizer.Add(manual_box, 0, wx.ALL, 10)

        self.SetSizer(sizer)
        sizer.Fit(self)

        self.radio_manual.SetValue(start_val)  # 1 is manual enabled, 0 is auto enabled

    def on_update_manual_text(self, event):
        self.manual_text.Enable(self.radio_manual.GetValue())

    def on_text_enter(self, event):
        self.value = self.manual_text.GetValue()

    def is_auto(self):
        return self.radio_auto.GetValue()

    def manual_value(self):
        return self.value

# *** End of BOUND CONTROL BOX Class *************************************
class ShipTrip_Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, title=u"ShipYearTrpStn")
        #        super(ShipTrip_Dialog,self).__init__(parent)

        self.panel = EntryPanel(self)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.panel, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.SetInitialSize()

    def SetBase(self, ship, year, trip, stn):
        self.panel.SetBase(ship, year, trip, stn)

    def GetShip(self):
        return (self.panel.GetShip())

    def GetYear(self):
        return (self.panel.GetYear())

    def GetTrip(self):
        return (self.panel.GetTrip())

    def GetStn(self):
        return (self.panel.GetStn())

########################
class WarpOut(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, title=u"ShipTrpStn")
        #        super(ShipTrip_Dialog,self).__init__(parent)

        panel = wx.Panel(self, -1)
        self.SetBackgroundColour(wx.NamedColour("GREY25"))
        self.warp = wx.TextCtrl(self)
        self.warp.SetBackgroundColour("Yellow")
        #            self._ship = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 35,-1 ) )
        self.warp.SetMaxLength(4)
        self.warp.SetFont(wx.Font(12, 74, 90, 92, False, "Arial"))

        sizer = wx.FlexGridSizer(3, 2, 8, 8)
        sizer.Add(wx.StaticText(self, label="WARP OUT:"), 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.warp, 0, wx.EXPAND)

        msizer = wx.BoxSizer(wx.VERTICAL)
        msizer.Add(sizer, 1, wx.EXPAND | wx.ALL, 20)
        btnszr = wx.StdDialogButtonSizer()
        button = wx.Button(self, wx.ID_OK)
        button.SetDefault()
        btnszr.AddButton(button)
        msizer.Add(btnszr, 0, wx.ALIGN_CENTER | wx.ALL, 12)
        btnszr.Realize()

        self.SetSizer(msizer)


    def SetBase(self, warpout):
        self.warp.SetValue(warpout)

    def GetWarp(self):
        return (self.warp.GetValue())


########################

class EntryPanel(wx.Panel):
    def __init__(self, parent):
        super(EntryPanel, self).__init__(parent)
        #            wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, title = u"SET BASE HEADER", pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE )

        self.SetBackgroundColour(wx.Colour("GREY25"))
#        self.ship = wx.TextCtrl(self)
#        self.ship.SetBackgroundColour("Yellow")
        self._ship = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 35,-1),validator=CharValidator('no-digit') )
        self._ship.SetMaxLength(3)
        self._ship.SetFont(wx.Font(12, 74, 90, 92, False, "Arial"))
        self._year = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 35,-1),validator=CharValidator('no-alpha') )
        self._year.SetMaxLength(4)
        self._year.SetFont(wx.Font(12, 74, 90, 92, False, "Arial"))
        self._trip = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(57, -1),validator=CharValidator('no-alpha'))
        self._trip.SetMaxLength(3)
        self._trip.SetFont(wx.Font(12, 74, 90, 92, False, "Arial"))
        self._stn = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(57, -1),validator=CharValidator('no-alpha'))
        self._stn.SetMaxLength(3)
        self._stn.SetFont(wx.Font(12, 74, 90, 92, False, "Arial"))

        #                SHPTRPSTN_GRID.Add( self.TRIP, 0, wx.ALL, 5 )


        #            self._ship = wx.TextCtrl(self)
        #            self._trip = wx.TextCtrl(self)
        #            self._stn = wx.TextCtrl(self)

        sizer = wx.FlexGridSizer(4, 2, 8, 8)
        sizer.Add(wx.StaticText(self, label="SHIP:"), 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self._ship, 0, wx.EXPAND)
        sizer.Add(wx.StaticText(self, label="YEAR:"), 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self._year, 0, wx.EXPAND)
        sizer.Add(wx.StaticText(self, label="TRIP:"), 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self._trip, 0, wx.EXPAND)
        sizer.Add(wx.StaticText(self, label="STN:"), 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self._stn, 0, wx.EXPAND)

        msizer = wx.BoxSizer(wx.VERTICAL)
        msizer.Add(sizer, 1, wx.EXPAND | wx.ALL, 20)
        btnszr = wx.StdDialogButtonSizer()
        button = wx.Button(self, wx.ID_OK)
        button.SetDefault()
        btnszr.AddButton(button)
        msizer.Add(btnszr, 0, wx.ALIGN_CENTER | wx.ALL, 12)
        btnszr.Realize()

        self.SetSizer(msizer)

        self._ship.SetValue("000")
        self._year.SetValue("0000")
        self._trip.SetValue("000")
        self._stn.SetValue("000")

    def SetBase(self, ship,year, trip, stn):
        self._ship.SetValue(ship)
        self._year.SetValue(year)
        self._trip.SetValue(trip)
        self._stn.SetValue(stn)

    def GetBase(self):
        return( '{0:0{width}}'.format((self._ship.GetValue()), width=3),
                '{0:0{width}}'.format(int(self._year.GetValue()), width=4),
            '{0:0{width}}'.format(int(self._trip.GetValue()), width=3),
            '{0:0{width}}'.format(int(self._stn.GetValue()), width=3) )

    def GetShip(self):
        val = (self._ship.GetValue()).upper()
        return val

    def GetYear(self):
        val = '{0:0{width}}'.format(int(self._year.GetValue()), width=4)
        return val

    def GetTrip(self):
        val = '{0:0{width}}'.format(int(self._trip.GetValue()), width=3)
        return val


    def GetStn(self):
        val = '{0:0{width}}'.format(int(self._stn.GetValue()), width=3)
        return val



# from wxpytohn demo library
class CharValidator(wx.Validator):
    ''' Validates data as it is entered into the text controls. '''

    #----------------------------------------------------------------------
    def __init__(self, flag):
        wx.Validator.__init__(self)
        self.flag = flag
        self.Bind(wx.EVT_CHAR, self.OnChar)

    #----------------------------------------------------------------------
    def Clone(self):
        '''Required Validator method'''
        return CharValidator(self.flag)

    #----------------------------------------------------------------------
    def Validate(self, win):
        return True

    #----------------------------------------------------------------------
    def TransferToWindow(self):
        return True

    #----------------------------------------------------------------------
    def TransferFromWindow(self):
        return True

    #----------------------------------------------------------------------
    def OnChar(self, event):
        keycode = int(event.GetKeyCode())
        if keycode < 256:
            #print keycode
            key = chr(keycode)
            #print key
            if self.flag == 'alpha-digit' and not (key in string.ascii_letters or key in string.digits):
                return
            if self.flag == 'no-alpha' and key in string.ascii_letters:
                return
            if self.flag == 'no-digit' and key in string.digits:
                return
        event.Skip()

