# -*- coding: utf-8 -*-
import pynmea2
import json
from collections import OrderedDict

DEGREE_SIGN = u'\N{DEGREE SIGN}'



class SCM(pynmea2.ProprietarySentence):
    sentence_types = {}
    """
        Generic ScanMar Message
    """

    def __new__(_cls, manufacturer, data):
        '''
            Return the correct sentence type based on the first field
        '''
        sentence_type = data[0] or data[1]
        name = manufacturer + sentence_type
        cls = _cls.sentence_types.get(name, _cls)
        return super(SCM, cls).__new__(cls)

    def __init__(self, manufacturer, data):
        self.sentence_type = data[0] or data[1]
        self.name = manufacturer + self.sentence_type
        super(SCM, self).__init__(manufacturer, data)


    """
    SCMGLL SCMVTG SCMZDA SCMDBS  are same as standard nmea sentences but have the proprietery prefix
    rather than the standard neam GP prefix these classes have been borrowed from pynmea2 talker defintions but
    but extend the SCM class instead of the TalkerSentence class used within pynmea2
    """

class SCMGLL(SCM, pynmea2.ValidStatusFix, pynmea2.LatLonFix):
    fields = (
        ('Telegram', 'tel'),
        ('Latitude', 'lat'),
        ('Latitude Direction', 'lat_dir'),
        ('Longitude', 'lon'),
        ('Longitude Direction', 'lon_dir'),
        ('Timestamp', 'timestamp', pynmea2.timestamp),
        ('Status', 'status'),  # contains the 'A' or 'V' flag
        ("FAA mode indicator", "faa_mode"),
    )


class SCMVTG(SCM):
    """
    Track Made Good and Ground Speed
    """
    fields = (
        ('Telegram', 'tel'),
        ("True Track made good", "true_track", float),
        ("True Track made good symbol", "true_track_sym"),
        ("Magnetic Track made good", "mag_track", pynmea2.Decimal),
        ("Magnetic Track symbol", "mag_track_sym"),
        ("Speed over ground knots", "spd_over_grnd_kts", pynmea2.Decimal),
        ("Speed over ground symbol", "spd_over_grnd_kts_sym"),
        ("Speed over ground kmph", "spd_over_grnd_kmph", float),
        ("Speed over ground kmph symbol", "spd_over_grnd_kmph_sym"),
        ("FAA mode indicator", "faa_mode"),
    )


class SCMZDA(SCM):
    fields = (
        ('Telegram', 'tel'),
        ("Timestamp", "timestamp", pynmea2.timestamp),  # hhmmss.ss = UTC
        ("Day", "day", int),  # 01 to 31
        ("Month", "month", int),  # 01 to 12
        ("Year", "year", int),  # Year = YYYY
        ("Local Zone Description", "local_zone", int),  # 00 to +/- 13 hours
        ("Local Zone Minutes Description", "local_zone_minutes", int),  # same sign as hours
    )


# DBS - Depth below surface
# Used by simrad devices (f.e. EK500)
# Deprecated and replaced by DPT
class SCMDBS(SCM):
    fields = (
        ('Telegram', 'tel'),
        ('Depth below surface, feet', 'depth_feet', pynmea2.Decimal),
        ('Feets', 'feets'),
        ('Depth below surface, meters', 'depth_meter', pynmea2.Decimal),
        ('Meters', 'meters'),
        ('Depth below surface, fathoms', 'depth_fathoms', pynmea2.Decimal),
        ('Fathoms', 'fathoms'),
    )


# DPT - water depth relative to the transducer and offset of the measuring
# transducer
# Used by simrad devices (f.e. EK500)
# class SCMDPT(TalkerSentence):
#    fields = (
#        ('Water depth, in meters', 'depth', pynmea2.Decimal),
#        ('Offset from the trasducer, in meters', 'offset', pynea2.Decimal),
#        ('Maximum range scale in use', 'range', pynmea2.Decimal),
#    )

######################################################################################################
# Proprietary Scanmar  NMEA sentence class definitions, all extend the base SCM class
# MEASUREMENTS from net sensors - the sensor field determines the meanings of following fields
# SAMPLE :
# <SCMSM2(tel='SM2', timestamp=datetime.time(13, 13, 23), status='V', sensor='DVTLAM', sensor_id='1',
#  measurement_id='B', measurement_val='6.2', qf='0')>
######################################################################################################

class SCMSM2(SCM):
    fields = (
        ('Telegram', 'tel'),
        ("Timestamp", "timestamp", pynmea2.timestamp),  # hhmmss.ss = UTC
        ('Status', 'status'),
        ('Sensor Type', 'sensor'),
        ('Sensor_ID', 'sensor_id'),
        ('Mesurement Id', 'measurement_id'),
        ('Measurement Value', 'measurement_val'),
        ('Quality Factor', 'qf'),
    )


###################################
# MEASUREMENTS from winch sensors -
###################################


# wirelength and speed PORT winch
class SCMWLP(SCM):
    fields = (
        ('Telegram', 'tel'),
        ("Timestamp", "timestamp", pynmea2.timestamp),  # hhmmss.ss = UTC
        ('WireOut', 'wireout'),
        ('Units', 'Wunits'),
        ('WireSpeed', 'wirespeed'),
        ('S-Units', 'Sunits'),
    )

# wirelength and speed STARBOARD winch
class SCMWLS(SCM):
    fields = (
        ('Telegram', 'tel'),
        ("Timestamp", "timestamp", pynmea2.timestamp),  # hhmmss.ss = UTC
        ('WireOut', 'wireout'),
        ('Units', 'Wunits'),
        ('WireSpeed', 'wirespeed'),
        ('S-Units', 'Sunits'),
    )

# wirelength and speed CENTRE or CENTRE.STARBOARD winch
class SCMWLC(SCM):
    fields = (
        ('Telegram', 'tel'),
        ("Timestamp", "timestamp", pynmea2.timestamp),  # hhmmss.ss = UTC
        ('WireOut', 'wireout'),
        ('Units', 'Wunits'),
        ('WireSpeed', 'wirespeed'),
        ('S-Units', 'Sunits'),
    )

# wirelength and speed PORT/CENTER winch
class SCMWLD(SCM):
    fields = (
        ('Telegram', 'tel'),
        ("Timestamp", "timestamp", pynmea2.timestamp),  # hhmmss.ss = UTC
        ('WireOut', 'wireout'),
        ('Units', 'Wunits'),
        ('WireSpeed', 'wirespeed'),
        ('S-Units', 'Sunits'),
    )

# wire tension STARBOARD winch
class SCMWTS(SCM):
    fields = (
        ('Telegram', 'tel'),
        ("Timestamp", "timestamp", pynmea2.timestamp),  # hhmmss.ss = UTC
        ('Wire Tension', 'wiretension'),
        ('Units', 'units'),
    )

# wire tension PORT winch
class SCMWTP(SCM):
    fields = (
        ('Telegram', 'tel'),
        ("Timestamp", "timestamp", pynmea2.timestamp),  # hhmmss.ss = UTC
        ('WireTension', 'wiretension'),
        ('Units', 'Tunits'),
    )

# wire tension CENTRE or STARBOARD winch
class SCMWTC(SCM):
    fields = (
        ('Telegram', 'tel'),
        ("Timestamp", "timestamp", pynmea2.timestamp),  # hhmmss.ss = UTC
        ('WireTension', 'wiretension'),
        ('Units', 'Tunits'),
    )

# wire tension PORT/CENTER winch
class SCMWTD(SCM):
    fields = (
        ('Telegram', 'tel'),
        ("Timestamp", "timestamp", pynmea2.timestamp),  # hhmmss.ss = UTC
        ('WireTension', 'wiretension'),
        ('Units', 'Tunits'),
    )

# water temperature
class SCMWST(SCM):
    fields = (
        ('Telegram', 'tel'),
        ("Timestamp", "timestamp", pynmea2.timestamp),  # hhmmss.ss = UTC
        ('Water Temperature', 'watertemp'),
        ('Units', 'units'),
    )
##############################
# Data processing functions class
##############################

#class SCAN_MSG():

##########
#    def serialize_instance(self,obj):
#        d = { '__classname__' : type(obj).__name__ }
#        d.update(vars(obj))
#        return d

#    def jsonDefault(self,object):
#        return object.__dict__

#    def unserialize_object(d):
#        clsname = d.pop('__classname__', None)
#        if clsname:
#            cls = classes[clsname]
#            obj = cls.__new__(cls)  # Make instance without calling __init__
#            for key, value in d.items():
#                setattr(obj, key, value)
#                return obj
#        else:
#            return d
##########



#    def process_dvtlam(self,msg):
#        print "hellohello dvtlam"
#        self.current[msg.sentence_type] = msg







    ###########################################################################
    #Process the messages based on thier sentence type
    ###########################################################################





    #########################################################################
    # the SM2 messages have to be sub processed to get the specific sensor data
    ##########################################################################

#class SMN_TOOLS:  # these are the values are valid to place on the screen
#    ScreenDict = {
#        'DVTLAM_1_P': "",
#        'DVTLAM_1_R': "",
#        'DVTLAS_1_P': "",
#        'DVTLAS_1_R': "",
#        'CVTLAM_1_S': "",
#        'TSP_1_X': "",
#        'TSP_1_Y': "",
#        'TS_5_H': "",
#        'TS_5_C': "",
#        'TS_5_O': "",
#        'TS_5_F': "",
#        'DP_1_H': "",
#    }

class SMN_TOOLS:  # these are the values are valid to place on the screen
    ScreenDict = {
        'DVTLAM_P': "",
        'DVTLAM_R': "",
        'DVTLAS_P': "",
        'DVTLAS_R': "",
		'DVTLAM_S': "",
        'CVTLAM_S': "",
        'TSP_X': "",
        'TSP_Y': "",
        'TLT_P': "",
        'TLT_R': "",
        'TS_H': "",
        'TS_C': "",
        'TS_O': "",
#        'TS_F': "",
        'DP_H': "",
        'DPTM_D': "",   #BIO use inplace of single d only nafc has DP see process_message_new
        'DPTM_T': "",   #BIO
        'DVTLAS_T': "", #BIO
        'DVTLAM_D': "", #BIO
    }
    def process_sm2(self,y,Raw_String,JDict):
        Sensor_Element = y.sensor +  '_' + y.measurement_id

#        print ("IN SM2 ",Sensor_Element,y.measurement_val,y.qf,y.status)
        JDict[Sensor_Element] = OrderedDict ([("measurement_val",y.measurement_val),("QF",y.qf),("STATUS",y.status) ])
        Raw_String[Sensor_Element] = y

    def process_gll(self,x,Raw_String,JDict):

        Raw_String["GLL"] = x

        lat = str(x.lat[:2] + ' ' + '{:>6.6}'.format(x.lat[2:]) + x.lat_dir)
        JDict["LAT_DM"] = OrderedDict ([("measurement_val",lat),("QF",'-'),("STATUS",'-') ])

        lon = str(x.lon[1:3] + ' ' + '{:>6.6}'.format(x.lon[3:]) + x.lon_dir)
        JDict["LON_DM"] = OrderedDict ([("measurement_val",lon),("QF",'-'),("STATUS",'-') ])

        JDict["GPS_TIME"] = OrderedDict ([("measurement_val",(str(x.timestamp))),("QF",'-'),("STATUS",'-') ])

        # latitude and longitude are methods within the object for GLL that return decimal values
        JDict["LAT_deci"]= OrderedDict ([("measurement_val",'{:>7.6}'.format(x.latitude)),("QF",'-'),("STATUS",'-')])

        JDict["LON_deci"] = OrderedDict ([("measurement_val", '{:>7.6}'.format(x.longitude)),("QF",'-'),("STATUS",'-')])


    def process_vtg(self,x,Raw_String,JDict):

        Raw_String["VTG"] = x
        JDict["VTG_SPD"] = OrderedDict ([("measurement_val",str(x.spd_over_grnd_kts)),("QF",'-'),("STATUS",'-') ])
        JDict["VTG_COG"] = OrderedDict ([("measurement_val",str(x.true_track)),("QF",'-'),("STATUS",'-') ])


# not that the ZDA has been re-written by scanmar with what seems to be the units time-date stamp vs true GPS feed time
# unfortunately the GLL which seems to have a true GPS time, does not have a date, so we have to use this data, which
# is a bit tricky at mid night if we use the GLL time so really we should use the zda time date pair and hope that the
# scanmar units clock is reasonably close to true gmt.

    def process_zda(self,x,Raw_String,JDict):

        Raw_String["ZDA"] = x
        # just the scanmar time stamp
        JDict["ZDA_TS"] = OrderedDict ([("measurement_val",str(x.timestamp)),("QF",'-'),("STATUS",'-')])
        # full date time with zone info
        dt = str(x.year).zfill(4) + '-' + str(x.month).zfill(2) + '-' + str(x.day).zfill(2) + 'T' + \
                str(x.timestamp)+'-' + str(x.local_zone)+":"+str(x.local_zone_minutes)

        JDict["ZDA_DATETIME"] = OrderedDict([("measurement_val", dt), ("QF", '-'), ("STATUS", '-')])

    def process_dbs(self,x,Raw_String,JDict):
        Raw_String["DBS"] = x
        JDict["DBS"] = OrderedDict([("measurement_val",str(x.depth_meter) ), ("QF", '-'), ("STATUS", '-')])

    def process_wtp(self, x, Raw_String, JDict):
        Raw_String["WTP"] = x
        JDict["WTP"] = OrderedDict([("measurement_val",str(x.wiretension) ), ("QF", '-'), ("STATUS", '-')])

    def process_wlp(self, x, Raw_String, JDict):
        Raw_String["WLP"] = x
        JDict["WLPS"] = OrderedDict([("measurement_val",str(x.wirespeed) ), ("QF", '-'), ("STATUS", '-')])
        JDict["WLPO"] = OrderedDict([("measurement_val",str(x.wireout) ), ("QF", '-'), ("STATUS", '-')])

    def process_wls(self, x, Raw_String, JDict):
        Raw_String["WLS"] = x
        JDict["WLSS"] = OrderedDict([("measurement_val",str(x.wirespeed)), ("QF", '-'), ("STATUS", '-')])
        JDict["WLSO"] = OrderedDict([("measurement_val",str(x.wireout) ), ("QF", '-'), ("STATUS", '-')])

    def process_wts(self, x, Raw_String, JDict):
        Raw_String["WTS"] = x
        JDict["WTS"] = OrderedDict([("measurement_val",str(x.wiretension) ), ("QF", '-'), ("STATUS", '-')])

    def process_wst(self, x, Raw_String, JDict):
        Raw_String["WST"] = x
        JDict["WST"] = str(x.watertemp)
        JDict["WST"] = OrderedDict([("measurement_val",str(x.watertemp) ), ("QF", '-'), ("STATUS", '-')])
    #################################################################################
    # Dictionaries to allow translation of sensor into the correct procedure to call
    # GroupDict are the highest level ones that come from the pymea2 Sentence_type ;
    #
    #  call it like this :
    # GroupDict[msg.sensor](msg)    ex. GroupDict["GLL](msg)
    # would call the process_gll function and pass it the msg data
    #################################################################################
    GroupDict = {
        'SM2': process_sm2,
        'GLL': process_gll,
        'VTG': process_vtg,
        'ZDA': process_zda,
        'DBS': process_dbs,
# these could be precessed more like an SM2 since they are same format
        'WLP': process_wlp,
        'WLS': process_wls,
        'WTP': process_wtp,
        'WTS': process_wtp,
        'WST': process_wst
       }

# called from scanmarlogger3
    def dispatch_message(self,sentence_type, line_x ,Raw_String,JDict):
            if sentence_type in self.GroupDict:

                if sentence_type == "SM2":
                    # process sm2 messages since they are in a nested dictionary withing the block
                    for z in line_x:
                        y = line_x[z]
                        self.GroupDict[sentence_type](self,y,Raw_String,JDict) # this is a function call
                else:
                    self.GroupDict[sentence_type](self,line_x,Raw_String,JDict)

#                current['OK'] = True
            else:
                print ("missing key, not in GroupDict=", sentence_type)
#                current['OK'] = False

# called from nextblock in scanmar serial tools ; to fix some channel coding issues wrt legacy sensors
    def process_message_new(self, msg):
        self.current = dict()
        if isinstance(msg, SCM):
            if msg.sentence_type in self.GroupDict:
                if msg.sentence_type == "SM2":

                    if (msg.sensor == 'DVTLAM' or msg.sensor == 'CVTLAM') and msg.measurement_id == '':  # issue with CVTLAM having no id value in test data
                        msg.measurement_id = 'S'
                    elif msg.sensor == "DP":  # DP does not have an id field ; also map it to the DPTM sensors field
                        msg.sensor = "DPTM"
                        msg.measurement_id = "D"
                    elif msg.sensor == "TEY":  # MAP Trawl Eye to Trawler sounder field ; has same elements
                        msg.sensor = "TS"
                    elif msg.sensor == "DST":  # DST legacy on chan 3(wing) or 4(door) does not have an id field; map to cvtlam dvtlam
                        if msg.sensor_id == '3':
                            msg.sensor = "CVTLAM"
                        elif msg.sensor_id == '4':
                            msg.sensor = "DVTLAM"
                        msg.measurement_id = 'S'


                    m = msg.sensor  + '_' + msg.measurement_id
#                    m = msg.sensor + '_' + msg.sensor_id + '_' + msg.measurement_id
                    self.current[msg.sentence_type] = msg  # DVTLAS
                    self.current["SENSOR"] = msg.sentence_type  # DVTLAS_1_A
                    self.current["SENSOR_ELEMENT"] = m  # DVTLAS_1_A
                else:
                    self.current["SENSOR"] = msg.sentence_type
                    self.current[msg.sentence_type] = msg
                self.current['OK'] = True
            else:
                print ("missing key, not in GroupDict=", msg.sentence_type)
                self.current['OK'] = False
#            print ("in SCM instance",msg,"!!")
        else:
            print ("NOT SCM instance",msg,"!!")