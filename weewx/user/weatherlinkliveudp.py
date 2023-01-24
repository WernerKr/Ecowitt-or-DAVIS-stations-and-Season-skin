#!/usr/bin/python
#
# Copyright 2020 Bastiaan Meelberg
# Modified 2021/2022 Werner Krenn (Leaf/Soil/...)
# Added Extra2..Extra4, Wind, Rain, ISS2
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.
#
# See http://www.gnu.org/licenses/
#
# Based on https://weatherlink.github.io/weatherlink-live-local-api/
#
# Bug Fixes September 2020
# added leaf/soil October 2021
# added extra Wind, extra Rain, extra2...4 December 2021
# added ISS2 - corrected Main Rain 1 Januar 2022
# added own log, more loop packets (dewpoint_1 ...)
# added did (MAC Adress from the Live) needed if more than one DAVIS stations reports on port 22222

"""

Weewx Driver for The WeatherLink Live (WLL).
It implements a HTTP interface for getting current weather data and can support continuous requests as often as every 10 seconds.
Also it collects a real-time 2.5 sec broadcast for wind speed and rain over UDP port 22222.

See Davis weatherlink-live-local-api

"""

from __future__ import with_statement

import socket
from socket import AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST
import time

import requests
import json

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

import weewx.drivers
import datetime
import weeutil.weeutil
import sys
import weewx.units

DRIVER_NAME = 'WeatherLinkLiveUDP'
DRIVER_VERSION = '0.5.1'

weewx.units.obs_group_dict['THW'] = 'group_temperature'
weewx.units.obs_group_dict['outWetbulb'] = 'group_temperature'
weewx.units.obs_group_dict['wetbulb1'] = 'group_temperature'
weewx.units.obs_group_dict['windSpeed1'] = 'group_speed2'
weewx.units.obs_group_dict['windDir1'] = 'group_direction'
#weewx.units.obs_group_dict['windSpeed10'] = 'group_speed2'
weewx.units.obs_group_dict['windDir10'] = 'group_direction'
weewx.units.obs_group_dict['windGustSpeed10'] = 'group_speed2'
weewx.units.obs_group_dict['windGustDir10'] = 'group_direction'
#weewx.units.obs_group_dict['rainfall_last_60_min'] = 'group_rain'
#weewx.units.obs_group_dict['rainfall_last_15_min'] = 'group_rain'
weewx.units.obs_group_dict['dewpoint_1'] = 'group_temperature'
weewx.units.obs_group_dict['dewpoint_2'] = 'group_temperature'
weewx.units.obs_group_dict['dewpoint_3'] = 'group_temperature'
weewx.units.obs_group_dict['dewpoint_4'] = 'group_temperature'
weewx.units.obs_group_dict['wetbulb_1'] = 'group_temperature'
weewx.units.obs_group_dict['wetbulb_2'] = 'group_temperature'
weewx.units.obs_group_dict['wetbulb_3'] = 'group_temperature'
weewx.units.obs_group_dict['wetbulb_4'] = 'group_temperature'
weewx.units.obs_group_dict['heatindex_1'] = 'group_temperature'
weewx.units.obs_group_dict['heatindex_2'] = 'group_temperature'
weewx.units.obs_group_dict['heatindex_3'] = 'group_temperature'
weewx.units.obs_group_dict['heatindex_4'] = 'group_temperature'
weewx.units.obs_group_dict['rain_rate_hi_last_15_min'] = 'group_rain'
#weewx.units.obs_group_dict['rainfall_last_24_hr'] = 'group_rain'
weewx.units.obs_group_dict['rain_storm_start_at'] = 'group_time'
weewx.units.obs_group_dict['rain_storm_last_start_at'] = 'group_time'
weewx.units.obs_group_dict['rain_storm_last_end_at'] = 'group_time'

weewx.units.obs_group_dict['windSpeed_2'] = 'group_speed2'
weewx.units.obs_group_dict['windDir_2'] = 'group_direction'
weewx.units.obs_group_dict['windGust_2'] = 'group_speed2'
weewx.units.obs_group_dict['windGustDir_2'] = 'group_direction'
weewx.units.obs_group_dict['windSpeed1_2'] = 'group_speed2'
weewx.units.obs_group_dict['windDir1_2'] = 'group_direction'
weewx.units.obs_group_dict['windSpeed10_2'] = 'group_speed2'
weewx.units.obs_group_dict['windDir10_2'] = 'group_direction'
weewx.units.obs_group_dict['windGustSpeed10_2'] = 'group_speed2'
weewx.units.obs_group_dict['windGustDir10_2'] = 'group_direction'
weewx.units.obs_group_dict['outTemp_2'] = 'group_temperature'
weewx.units.obs_group_dict['outHumidity_2'] =  'group_percent'
weewx.units.obs_group_dict['dewpoint2'] = 'group_temperature'
weewx.units.obs_group_dict['heatindex2'] = 'group_temperature'
weewx.units.obs_group_dict['windchill2'] = 'group_temperature'
weewx.units.obs_group_dict['THSW_2'] = 'group_temperature'
weewx.units.obs_group_dict['THW_2'] = 'group_temperature'
weewx.units.obs_group_dict['outWetbulb_2'] = 'group_temperature'
weewx.units.obs_group_dict['radiation_2'] = 'group_radiation'
weewx.units.obs_group_dict['UV_2'] = 'group_uv'
weewx.units.obs_group_dict['txBatteryStatus_2'] = 'group_count'
weewx.units.obs_group_dict['signal1_2'] = 'group_count'
weewx.units.obs_group_dict['rain_2'] = 'group_rain'
weewx.units.obs_group_dict['rainRate_2'] = 'group_rain'
weewx.units.obs_group_dict['stormRain_2'] = 'group_rain'
weewx.units.obs_group_dict['stormRainlast_2'] = 'group_rain'
weewx.units.obs_group_dict['rain15_2'] = 'group_rain'
weewx.units.obs_group_dict['rain60_2'] = 'group_rain'
weewx.units.obs_group_dict['rain24_2'] = 'group_rain'
weewx.units.obs_group_dict['dayRain_2'] = 'group_rain'
weewx.units.obs_group_dict['monthRain_2'] = 'group_rain'
weewx.units.obs_group_dict['yearRain_2'] = 'group_rain'
weewx.units.obs_group_dict['rain_rate_hi_last_15_min_2'] = 'group_rain'
weewx.units.obs_group_dict['rainfall_last_24_hr_2'] = 'group_rain'
weewx.units.obs_group_dict['rain_storm_start_at_2'] = 'group_time'
weewx.units.obs_group_dict['rain_storm_last_start_at_2'] = 'group_time'
weewx.units.obs_group_dict['rain_storm_last_end_at_2'] = 'group_time'

MM2INCH = 1 / 25.4

# Open UDP Socket
comsocket = socket.socket(AF_INET, SOCK_DGRAM)
comsocket.bind(('', 22222))
comsocket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
comsocket.settimeout(5)

try:
    # Test for WeeWX v4 logging
    import weeutil.logger
    import logging

    log = logging.getLogger(__name__)


    def logdbg(msg):
        log.debug(msg)


    def loginf(msg):
        log.info(msg)


    def logerr(msg):
        log.error(msg)
except ImportError:
    # Old-style WeeWX logging
    import syslog


    def logmsg(level, msg):
        syslog.syslog(level, 'WLL UDP: %s' % msg)


    def logdbg(msg):
        logmsg(syslog.LOG_DEBUG, msg)


    def loginf(msg):
        logmsg(syslog.LOG_INFO, msg)


    def logerr(msg):
        logmsg(syslog.LOG_ERR, msg)


def loader(config_dict, engine):
    return WeatherLinkLiveUDPDriver(**config_dict[DRIVER_NAME])

class RainBarrel:
    def __init__(self):
        self.bucketsize = 0.0
        self.rain_previous_period2 = 0
        self.rain_previous_period = 0
        self.previous_day = None

        self.rain = 0

    # rain collector type/size **(0: Reserved, 1: 0.01", 2: 0.2 mm, 3:  0.1 mm, 4: 0.001")*
    def set_up_bucket_size(self, data):

        type = data['rain_size']
        if 1 <= type <= 4:

            if type == 1:
                self.bucketsize = 0.01
                logdbg('Bucketsize is set at 0.01 in')

            elif type == 2:
                self.bucketsize = 0.2 * MM2INCH
                logdbg('Bucketsize is set at 0.2 mm')

            elif type == 3:
                self.bucketsize = 0.1 * MM2INCH
                logdbg('Bucketsize is set at 0.1 mm')

            elif type == 4:
                self.bucketsize = 0.001
                logdbg('Bucketsize is set at 0.001 in')

    def set_rain_previous_period(self, data):
        self.rain_previous_period = data
        logdbg('({}) Previous rain is set at: {} buckets [{} mm / {} in]'
               .format(weeutil.weeutil.timestamp_to_string(time.time()),
                       (self.rain_previous_period),
                       round(self.rain_previous_period * self.bucketsize * 25.4, 1),
                       round(self.rain_previous_period * self.bucketsize, 2)))

    def empty_rain_barrel(self):
        self.rain = 0

    def set_rain_previous_date(self, data):
        # Setting the current date to Midnight for rain reset
        data += datetime.timedelta(days=1)
        data = data.replace(hour=0, minute=0, second=0, microsecond=0)
        self.previous_date_stamp = data
        logdbg('({}) Rain daily reset: {}'
               .format(weeutil.weeutil.timestamp_to_string(time.time()),
                       str(self.previous_date_stamp)))


class WllStation:
    def __init__(self):
        self.poll_interval = 10
        self.txid_iss = None
        self.extra1 = None
        self.extra2 = None
        self.extra3 = None
        self.extra4 = None
        self.soil = None
        self.leaf = None
        self.wind = None
        self.txid_rain = None
        self.did = None
        self.txid_iss2 = None
        self.leafsoil = None
        
        self.davis_date_stamp = None
        self.system_date_stamp = None

        self.real_rime_url = None
        self.current_conditions_url = None

        self.davis_packet = dict()
        self.davis_packet['rain'] = 0
        self.udp_countdown = 0

        self.log = 0
        #self.rainbarrel = 0

    rainbarrel = RainBarrel()


    def set_log(self, data):
        if data:
            self.log = int(data)
            loginf('log is %s' % self.log)

    def set_poll_interval(self, data):
        self.poll_interval = data
        if self.poll_interval < 10:
            logerr('Unable to set Poll Interval (minimal 10 s.)')
            self.poll_interval = 10
        loginf('HTTP polling interval is %s' % self.poll_interval)

    def set_txid(self, data):
        if data:
            self.txid_iss = int(data)
            loginf('txid of ISS/VUE is {}'.format(self.txid_iss))

    def set_extra1(self, data):
        if data:
            self.extra1 = int(data)
            loginf('Extra1 station is using txid: {}'.format(self.extra1))
    def set_extra2(self, data):
        if data:
            self.extra2 = int(data)
            loginf('Extra2 station is using txid: {}'.format(self.extra2))
    def set_extra3(self, data):
        if data:
            self.extra3 = int(data)
            loginf('Extra3 station is using txid: {}'.format(self.extra3))
    def set_extra4(self, data):
        if data:
            self.extra4 = int(data)
            loginf('Extra4 station is using txid: {}'.format(self.extra4))

    def set_wind(self, data):
        if data:
            self.wind = int(data)
            loginf('Wind station is using txid: {}'.format(self.wind))

    def set_rain(self, data):
        if data:
            self.txid_rain = int(data)
            loginf('Rain station is using txid: {}'.format(self.txid_rain))


    def set_leaf(self, data):
        if data:
            self.leaf = int(data)
            loginf('Leaf station is using txid: {}'.format(self.leaf))

    def set_soil(self, data):
        if data:
            self.soil = int(data)
            loginf('Soil station is using txid: {}'.format(self.soil))

    def set_txid2(self, data):
        if data:
            self.txid_iss2 = int(data)
            loginf('txid of 2. ISS/VUE is {}'.format(self.txid_iss2))


    def decode_data_wll(self, data):

        iss_data = None
        leaf_soil_data = None
        lss_bar_data = None
        lss_temp_hum_data = None
        iss_udp_data = None
        extra_data1 = None
        extra_data2 = None
        extra_data3 = None
        extra_data4 = None
        leaf_data = None
        soil_data = None
        wind_data = None
        rain_data = None
        iss2_data = None

        self.current_davis_data = data

        if self.log == 9:
          loginf("rec_data: %s" % data)

        timestamp = data['ts']
        self.davis_date_stamp = datetime.datetime.fromtimestamp(timestamp)
        self.system_date_stamp = datetime.datetime.now()

        packet = dict()

        packet['dateTime'] = timestamp
        packet['usUnits'] = weewx.US

        for condition in data['conditions']:
            # 1 = ISS Current Conditions record
            # 2 = Leaf/Soil Moisture Current Conditions record
            # 3 = LSS BAR Current Conditions record
            # 4 = LSS Temp/Hum Current Conditions record

            if condition.get('txid') == self.txid_iss and condition.get('data_structure_type') == 1:
                iss_data = condition

            #if condition.get('data_structure_type') == 2:
            #    if self.leaf and condition.get('txid') == self.leaf:    
            #       leaf_data = condition

            if condition.get('data_structure_type') == 2:
                if soil_data == None:
                   if self.soil and condition.get('txid') == self.soil:    
                      soil_data = condition
                if leaf_data == None:
                   if self.leaf and condition.get('txid') == self.leaf:    
                      leaf_data = condition
                if not self.leaf and not self.soil:
                  #if condition.get('data_structure_type') == 2:
                   leaf_soil_data = condition


            if condition.get('data_structure_type') == 3:
                lss_bar_data = condition

            if condition.get('data_structure_type') == 4:
                lss_temp_hum_data = condition

            if self.wind and condition.get('txid') == self.wind and condition.get('wind_speed_avg_last_10_min'):
                wind_data = condition

            if self.txid_rain and condition.get('txid') == self.txid_rain and condition.get('rainfall_last_15_min'):
                rain_data = condition

#            if self.wind and condition.get('txid') == self.wind and condition.get('data_structure_type') == 1 and wind_data is None: 
#                iss_udp_data = condition
#            elif self.wind == None and condition.get('txid') == self.txid_iss and condition.get(
#                    'data_structure_type') == 1 and not condition.get('temp'): #and condition.get('wind_speed_last'):
#                iss_udp_data = condition

            if condition.get('txid') == self.txid_iss and condition.get(
                    'data_structure_type') == 1 and not condition.get('temp'): #and condition.get('wind_speed_last'):
                iss_udp_data = condition

            # If extra sensor are requested, try to find them
            if self.extra1 and condition.get('txid') == self.extra1 and condition.get('temp'):
                extra_data1 = condition
            if self.extra2 and condition.get('txid') == self.extra2 and condition.get('temp'):
                extra_data2 = condition
            if self.extra3 and condition.get('txid') == self.extra3 and condition.get('temp'):
                extra_data3 = condition
            if self.extra4 and condition.get('txid') == self.extra4 and condition.get('temp'):
                extra_data4 = condition


            if self.txid_iss2 and condition.get('txid') == self.txid_iss2:
                iss2_data = condition


        # Get UDP data
        if iss_udp_data:
            if self.log == 8:
               loginf("iss_udp_data: %s" % iss_udp_data)

            # most recent valid wind speed **(mph)**
            packet['windSpeed'] = iss_udp_data['wind_speed_last']

            # most recent valid wind direction **(degree)**
            packet['windDir'] = iss_udp_data['wind_dir_last']

            # Rain
            ## Fix: Check for NoneType

            self.rainbarrel.rain = iss_udp_data['rainfall_daily']

            if iss_udp_data['rain_rate_last'] is None:
                logdbg("Error: UDP->rain_rate_last not defined")
            else:
                packet['rainRate'] = iss_udp_data['rain_rate_last'] * self.rainbarrel.bucketsize

            self.calculate_rain()
            if self.davis_packet['rain'] >= 0:
              packet['rain'] = self.davis_packet['rain']
            else:
              packet['rain'] = 0
            #packet['rain'] = self.davis_packet['rain']

            if packet['rain'] > 0:
                logdbg('UDP rain detect: {} buckets -> {} in'
                       .format(self.davis_packet['rain'] / self.rainbarrel.bucketsize,
                               self.davis_packet['rain']))

        # Get HTTP data
        if iss_data and iss_data.get('temp'):
            if self.log == 4:
               loginf("iss_data: %s" % iss_data)

            # most recent valid wind speed **(mph)**
            packet['windSpeed'] = iss_data['wind_speed_last']

            # most recent valid wind direction **(degree)**
            packet['windDir'] = iss_data['wind_dir_last']

            # maximum wind speed over last 2 min **(mph)**
            packet['windGust'] = iss_data['wind_speed_hi_last_2_min']

            # gust wind direction over last 2 min **(degree)**
            packet['windGustDir'] = iss_data["wind_dir_at_hi_speed_last_2_min"]

            # wind speed and direction average for the last 10 minutes
            # (not recorded in archive but used elsewhere)
            packet['windSpeed1'] = iss_data["wind_speed_avg_last_1_min"]
            packet['windDir1'] = iss_data["wind_dir_scalar_avg_last_1_min"]
            packet['windSpeed10'] = iss_data["wind_speed_avg_last_10_min"]
            packet['windDir10'] = iss_data["wind_dir_scalar_avg_last_10_min"]
            packet['windGustSpeed10'] = iss_data["wind_speed_hi_last_10_min"]
            packet['windGustDir10'] = iss_data["wind_dir_at_hi_speed_last_10_min"]

            #wind_speed_last=4.8
            #wind_dir_last=157
            #wind_speed=1.3
            #wind_dir=172
            #wind_gust=4.8
            #wind_gdir=124
            
            # most recent valid temperature **(F)**
            packet['outTemp'] = iss_data['temp']

            # most recent valid humidity **(%RH)**
            packet['outHumidity'] = iss_data['hum']

            # **(F)**
            packet['dewpoint'] = iss_data['dew_point']

            # **(F)**
            packet['heatindex'] = iss_data['heat_index']

            # **(F)**
            packet['windchill'] = iss_data['wind_chill']
            
            # **(F)**
            packet['THSW'] = iss_data['thsw_index']
            packet['THW'] = iss_data['thw_index']
            
            packet['outWetbulb'] = iss_data['wet_bulb']

            # most recent solar radiation **(W/m)**
            packet['radiation'] = iss_data['solar_rad']

            # most recent UV index **(Index)**
            packet['UV'] = iss_data['uv_index']

            # transmitter battery status flag **(no unit)**
            packet['txBatteryStatus'] = iss_data['trans_battery_flag']

            # configured radio receiver state **(no unit)**
            packet['signal1'] = iss_data['rx_state']

            #rain_rate_last=0
            #rain_rate_hi=0
            #rain_rate_hi_last_15_min=0
            #rain_storm_last=1.2
            
            if iss_data['rain_storm'] != None:
              packet['stormRain'] = iss_data['rain_storm'] * self.rainbarrel.bucketsize
            if iss_data['rain_storm_last'] != None:
              packet['stormRainlast'] = iss_data['rain_storm_last'] * self.rainbarrel.bucketsize
            if iss_data['rainfall_last_15_min'] != None:
              packet['rain15'] = iss_data['rainfall_last_15_min'] * self.rainbarrel.bucketsize
            if iss_data['rainfall_last_60_min'] != None:
              packet['rain60'] = iss_data['rainfall_last_60_min'] * self.rainbarrel.bucketsize
            if iss_data['rainfall_last_24_hr'] != None:
              packet['rain24'] = iss_data['rainfall_last_24_hr'] * self.rainbarrel.bucketsize
            if iss_data['rain_rate_hi_last_15_min'] != None:
              packet['rain_rate_hi_last_15_min'] = iss_data['rain_rate_hi_last_15_min'] * self.rainbarrel.bucketsize


            packet['rain_storm_start_at'] = iss_data['rain_storm_start_at']
            packet['rain_storm_last_start_at'] = iss_data['rain_storm_last_start_at']
            packet['rain_storm_last_end_at'] = iss_data['rain_storm_last_end_at']

            packet['dayRain'] = iss_data['rainfall_daily'] * self.rainbarrel.bucketsize
            packet['monthRain'] = iss_data['rainfall_monthly'] * self.rainbarrel.bucketsize
            packet['yearRain'] = iss_data['rainfall_year'] * self.rainbarrel.bucketsize

            self.rainbarrel.rain = iss_data['rainfall_daily']
            packet['rainRate'] = iss_data['rain_rate_last'] * self.rainbarrel.bucketsize

            self.calculate_rain()

            if self.davis_packet['rain'] >= 0:
              packet['rain'] = self.davis_packet['rain']
            else:
              packet['rain'] = 0
            if packet['rain'] > 0:
                logdbg('HTTP rain detect: {} buckets -> {} in'
                       .format(packet['rain'] / self.rainbarrel.bucketsize,
                               packet['rain']))

        if lss_bar_data:
            # most recent bar sensor reading with elevation adjustment **(inches)**
            packet['altimeter'] = lss_bar_data['bar_sea_level']
            packet['pressure'] = lss_bar_data['bar_absolute']
            packet['barometer'] = lss_bar_data['bar_sea_level']

        if lss_temp_hum_data:
            # most recent valid inside temp **(F)**
            packet['inTemp'] = lss_temp_hum_data['temp_in']
            # most recent valid inside humidity **(%RH)**
            packet['inHumidity'] = lss_temp_hum_data['hum_in']
            # **(F)**
            packet['inDewpoint'] = lss_temp_hum_data['dew_point_in']

        if leaf_data:
            # most recent valid leaf temp **(F)**
            packet['leafTemp1'] = leaf_data['temp_1']
            packet['leafTemp2'] = leaf_data['temp_2']
            # most recent valid leaf 
            packet['leafWet1'] = leaf_data['wet_leaf_1']
            packet['leafWet2'] = leaf_data['wet_leaf_2']
            packet['signal7'] = leaf_data['rx_state']
            packet['txBatteryStatus7'] = leaf_data['trans_battery_flag']
            #if leaf_data.get('trans_battery_flag'):
            packet['batteryStatus7'] = leaf_data['trans_battery_flag']

        if soil_data:
            # most recent valid soil temp **(F)**
            packet['soilTemp1'] = soil_data['temp_1']
            packet['soilTemp2'] = soil_data['temp_2']
            packet['soilTemp3'] = soil_data['temp_3']
            packet['soilTemp4'] = soil_data['temp_4']
            # most recent valid soilmoisture **(cb)**
            packet['soilMoist1'] = soil_data['moist_soil_1']
            packet['soilMoist2'] = soil_data['moist_soil_2']
            packet['soilMoist3'] = soil_data['moist_soil_3']
            packet['soilMoist4'] = soil_data['moist_soil_4']
            packet['signal8'] = soil_data['rx_state']
            #if soil_data.get('trans_battery_flag'):
            packet['batteryStatus8'] = soil_data['trans_battery_flag']

        if leaf_soil_data:
            # most recent valid soil temp **(F)**
            packet['soilTemp1'] = leaf_soil_data['temp_1']
            packet['soilTemp2'] = leaf_soil_data['temp_2']
            packet['soilTemp3'] = leaf_soil_data['temp_3']
            packet['soilTemp4'] = leaf_soil_data['temp_4']
            # most recent valid soilmoisture **(cb)**
            packet['soilMoist1'] = leaf_soil_data['moist_soil_1']
            packet['soilMoist2'] = leaf_soil_data['moist_soil_2']
            packet['soilMoist3'] = leaf_soil_data['moist_soil_3']
            packet['soilMoist4'] = leaf_soil_data['moist_soil_4']
            packet['leafWet1'] = leaf_soil_data['wet_leaf_1']
            packet['leafWet2'] = leaf_soil_data['wet_leaf_2']
            packet['signal6'] = leaf_soil_data['rx_state']
            #if leaf_soil_data.get('trans_battery_flag'):
            packet['batteryStatus6'] = leaf_soil_data['trans_battery_flag']

        if extra_data1:
            if self.log == 5:
               loginf("extra_data1: %s" % extra_data1)

            if extra_data1.get('temp'):
               packet['extraTemp1'] = extra_data1['temp']
            if extra_data1.get('hum'):
               packet['extraHumid1'] = extra_data1['hum']
            if extra_data1.get('dew_point'):
               packet['dewpoint_1'] = extra_data1['dew_point']
            if extra_data1.get('wet_bulb'):
               packet['wetbulb_1'] = extra_data1['wet_bulb']
            if extra_data1.get('heat_index'):
               packet['heatindex_1'] = extra_data1['heat_index']

            test = ''
            if extra_data1.get('rx_state') :
               packet['signal2'] = extra_data1['rx_state']
            else:
               test = extra_data1.get('rx_state', None) 
               if test != None:
                 packet['signal2'] = test
 
            test = ''
            if extra_data1.get('trans_battery_flag') :
               packet['batteryStatus2'] = extra_data1['trans_battery_flag']
            else:
               test = extra_data1.get('trans_battery_flag', None) 
               if test != None:
                 packet['batteryStatus2'] = test
                 #loginf("batteryStatus2: %s" % test)


        if extra_data2:
            if self.log == 5:
               loginf("extra_data2: %s" % extra_data2)

            if extra_data2.get('temp'):
               packet['extraTemp2'] = extra_data2['temp']
            if extra_data2.get('hum'):
               packet['extraHumid2'] = extra_data2['hum']
            if extra_data2.get('dew_point'):
               packet['dewpoint_2'] = extra_data2['dew_point']
            if extra_data2.get('wet_bulb'):
               packet['wetbulb_2'] = extra_data2['wet_bulb']
            if extra_data2.get('heat_index'):
               packet['heatindex_2'] = extra_data2['heat_index']

            test = ''            
            if extra_data2.get('rx_state'):
               packet['signal3'] = extra_data2['rx_state']
            else:
               test = extra_data2.get('rx_state', None) 
               if test != None:
                 packet['signal3'] = test

            test = '' 
            if extra_data2.get('trans_battery_flag'):
               packet['batteryStatus3'] = extra_data2['trans_battery_flag']
            else:
               test = extra_data2.get('trans_battery_flag', None) 
               if test != None:
                 packet['batteryStatus3'] = test


        if extra_data3:
            if self.log == 5:
               loginf("extra_data3: %s" % extra_data3)

            if extra_data3.get('temp'):
               packet['extraTemp3'] = extra_data3['temp']
            if extra_data3.get('hum'):
               packet['extraHumid3'] = extra_data3['hum']
            if extra_data3.get('dew_point'):
               packet['dewpoint_3'] = extra_data3['dew_point']
            if extra_data3.get('wet_bulb'):
               packet['wetbulb_3'] = extra_data3['wet_bulb']
            if extra_data3.get('heat_index'):
               packet['heatindex_3'] = extra_data3['heat_index']

            test = ''  
            if extra_data3.get('rx_state'):
               packet['signal4'] = extra_data3['rx_state']
            else:
               test = extra_data3.get('rx_state', None) 
               if test != None:
                 packet['signal4'] = test

            test = ''  
            if extra_data3.get('trans_battery_flag'):
             packet['batteryStatus4'] = extra_data3['trans_battery_flag']
            else:
               test = extra_data3.get('trans_battery_flag', None) 
               if test != None:
                 packet['batteryStatus4'] = test

        if extra_data4:
            if self.log == 5:
               loginf("extra_data4: %s" % extra_data4)

            if extra_data4.get('temp'):
               packet['extraTemp4'] = extra_data4['temp']
            if extra_data4.get('hum'):
               packet['extraHumid4'] = extra_data4['hum']
            if extra_data4.get('dew_point'):
               packet['dewpoint_4'] = extra_data4['dew_point']
            if extra_data4.get('wet_bulb'):
               packet['wetbulb_4'] = extra_data4['wet_bulb']
            if extra_data4.get('heat_index'):
               packet['heatindex_4'] = extra_data4['heat_index']

            test = ''  
            if extra_data4.get('rx_state'):
               packet['signal5'] = extra_data4['rx_state']
            else:
               test = extra_data4.get('rx_state', None) 
               if test != None:
                 packet['signal5'] = test

            test = ''  
            if extra_data4.get('trans_battery_flag'):
             packet['batteryStatus5'] = extra_data4['trans_battery_flag']
            else:
               test = extra_data4.get('trans_battery_flag', None) 
               if test != None:
                 packet['batteryStatus5'] = test

        if wind_data:
            if self.log == 6:
               loginf("wind_data: %s" % wind_data)
            if wind_data.get('wind_speed_last'):
              packet['windSpeed'] = wind_data['wind_speed_last']
            if wind_data.get('wind_dir_last'):
              packet['windDir'] = wind_data['wind_dir_last']
            if wind_data.get('wind_speed_hi_last_2_min'):
              packet['windGust'] = wind_data['wind_speed_hi_last_2_min']
            if wind_data.get('wind_dir_at_hi_speed_last_2_min'):
              packet['windGustDir'] = wind_data["wind_dir_at_hi_speed_last_2_min"]
            if wind_data.get('wind_speed_avg_last_1_min'):
              packet['windSpeed1'] = wind_data["wind_speed_avg_last_1_min"]
            if wind_data.get('wind_dir_scalar_avg_last_1_min'):
              packet['windDir1'] = wind_data["wind_dir_scalar_avg_last_1_min"]
            if wind_data.get('wind_speed_avg_last_10_min'):
              packet['windSpeed10'] = wind_data["wind_speed_avg_last_10_min"]
            if wind_data.get('wind_dir_scalar_avg_last_10_min'):
              packet['windDir10'] = wind_data["wind_dir_scalar_avg_last_10_min"]
            if wind_data.get('wind_speed_hi_last_10_min'):
              packet['windGustSpeed10'] = wind_data["wind_speed_hi_last_10_min"]
            if wind_data.get('wind_dir_at_hi_speed_last_10_min'):
              packet['windGustDir10'] = wind_data["wind_dir_at_hi_speed_last_10_min"]

            test = ''
            if wind_data.get('rx_state'):
               packet['signalw'] = wind_data['rx_state']
            else:
               test = wind_data.get('rx_state', None) 
               if test != None:
                 packet['signalw'] = test

            test = ''  
            if wind_data.get('trans_battery_flag'):
             packet['windBatteryStatus'] = wind_data['trans_battery_flag']
            else:
               test = wind_data.get('trans_battery_flag', None) 
               if test != None:
                 packet['windBatteryStatus'] = test


            #packet['windBatteryStatus'] = wind_data['trans_battery_flag']
            #if wind_data.get('rx_state'):
            #   packet['signalw'] = wind_data['rx_state']

        if rain_data:
            if self.log == 6:
               loginf("rain_data: %s" % rain_data)

            if rain_data['rain_storm'] != None:
              packet['stormRain'] = rain_data['rain_storm'] * self.rainbarrel.bucketsize
            if rain_data['rain_storm_last'] != None:
              packet['stormRainlast'] = rain_data['rain_storm_last'] * self.rainbarrel.bucketsize
            if rain_data['rainfall_last_15_min'] != None:
              packet['rain15'] = rain_data['rainfall_last_15_min'] * self.rainbarrel.bucketsize
            if rain_data['rainfall_last_60_min'] != None:
              packet['rain60'] = rain_data['rainfall_last_60_min'] * self.rainbarrel.bucketsize
            if rain_data['rainfall_last_24_hr'] != None:
              packet['rain24'] = rain_data['rainfall_last_24_hr'] * self.rainbarrel.bucketsize
            if rain_data['rain_rate_hi_last_15_min'] != None:
              packet['rain_rate_hi_last_15_min'] = rain_data['rain_rate_hi_last_15_min'] * self.rainbarrel.bucketsize

            if rain_data['rain_storm_start_at'] != None:
              packet['rain_storm_start_at'] = rain_data['rain_storm_start_at']
            if rain_data['rain_storm_last_start_at'] != None:
              packet['rain_storm_last_start_at'] = rain_data['rain_storm_last_start_at']
            if rain_data['rain_storm_last_end_at'] != None:
              packet['rain_storm_last_end_at'] = rain_data['rain_storm_last_end_at']

            if rain_data['rainfall_daily'] != None:
              packet['dayRain'] = rain_data['rainfall_daily'] * self.rainbarrel.bucketsize
            if rain_data['rainfall_monthly'] != None:
              packet['monthRain'] = rain_data['rainfall_monthly'] * self.rainbarrel.bucketsize
            if rain_data['rainfall_year'] != None:
              packet['yearRain'] = rain_data['rainfall_year'] * self.rainbarrel.bucketsize

            self.rainbarrel.rain = rain_data['rainfall_daily']
            if rain_data['rain_rate_last'] != None:
              packet['rainRate'] = rain_data['rain_rate_last'] * self.rainbarrel.bucketsize

            self.calculate_rain()
            if self.davis_packet['rain'] >= 0:
              packet['rain'] = self.davis_packet['rain']
            else:
              packet['rain'] = 0
            #packet['rain'] = self.davis_packet['rain']

            if packet['rain'] > 0:
                logdbg('HTTP rain detect: {} buckets -> {} in'
                       .format(packet['rain'] / self.rainbarrel.bucketsize,
                               packet['rain']))

            test = ''  
            if rain_data.get('rx_state'):
               packet['signalr'] = rain_data['rx_state']
            else:
               test = rain_data.get('rx_state', None) 
               if test != None:
                 packet['signalr'] = test

            test = ''  
            if rain_data.get('trans_battery_flag'):
             packet['rainBatteryStatus'] = rain_data['trans_battery_flag']
            else:
               test = rain_data.get('trans_battery_flag', None) 
               if test != None:
                 packet['rainBatteryStatus'] = test

            #packet['rainBatteryStatus'] = rain_data['trans_battery_flag']

            #if rain_data.get('rx_state'):
            #   packet['signalr'] = rain_data['rx_state']

        if iss2_data and iss2_data.get('temp'):
            if self.log == 7:
               loginf("iss2_data: %s" % iss2_data)

            packet['windSpeed_2'] = iss2_data['wind_speed_last']
            packet['windDir_2'] = iss2_data['wind_dir_last']
            packet['windGust_2'] = iss2_data['wind_speed_hi_last_2_min']
            packet['windGustDir_2'] = iss2_data["wind_dir_at_hi_speed_last_2_min"]
            packet['windSpeed1_2'] = iss2_data["wind_speed_avg_last_1_min"]
            packet['windDir1_2'] = iss2_data["wind_dir_scalar_avg_last_1_min"]
            packet['windSpeed10_2'] = iss2_data["wind_speed_avg_last_10_min"]
            packet['windDir10_2'] = iss2_data["wind_dir_scalar_avg_last_10_min"]
            packet['windGustSpeed10_2'] = iss2_data["wind_speed_hi_last_10_min"]
            packet['windGustDir10_2'] = iss2_data["wind_dir_at_hi_speed_last_10_min"]
            packet['outTemp_2'] = iss2_data['temp']
            packet['outHumidity_2'] = iss2_data['hum']
            packet['dewpoint2'] = iss2_data['dew_point']
            packet['heatindex2'] = iss2_data['heat_index']
            packet['windchill2'] = iss2_data['wind_chill']
            packet['THSW_2'] = iss2_data['thsw_index']
            packet['THW_2'] = iss2_data['thw_index']
            packet['outWetbulb_2'] = iss2_data['wet_bulb']
            packet['radiation_2'] = iss2_data['solar_rad']
            packet['UV_2'] = iss2_data['uv_index']
            packet['txBatteryStatus_2'] = iss2_data['trans_battery_flag']
            packet['signal1_2'] = iss2_data['rx_state']

            self.rainbarrel.bucketsize2 = 0.01
            type = iss2_data['rain_size']
            if 1 <= type <= 4:
               if type == 1:
                  self.rainbarrel.bucketsize2 = 0.01
               elif type == 2:
                  self.rainbarrel.bucketsize2 = 0.2 * MM2INCH
               elif type == 3:
                  self.rainbarrel.bucketsize2 = 0.1 * MM2INCH
               elif type == 4:
                  self.rainbarrel.bucketsize2 = 0.001

            if iss2_data['rain_storm'] != None:
              packet['stormRain_2'] = iss2_data['rain_storm'] * self.rainbarrel.bucketsize2
            if iss2_data['rain_storm_last'] != None:
              packet['stormRainlast_2'] = iss2_data['rain_storm_last'] * self.rainbarrel.bucketsize2
            if iss2_data['rainfall_last_15_min'] != None:
              packet['rain15_2'] = iss2_data['rainfall_last_15_min'] * self.rainbarrel.bucketsize2
            if iss2_data['rainfall_last_60_min'] != None:
              packet['rain60_2'] = iss2_data['rainfall_last_60_min'] * self.rainbarrel.bucketsize2
            if iss2_data['rainfall_last_24_hr'] != None:
              packet['rain24_2'] = iss2_data['rainfall_last_24_hr'] * self.rainbarrel.bucketsize2
            if iss2_data['rain_rate_hi_last_15_min'] != None:
              packet['rain_rate_hi_last_15_min_2'] = iss2_data['rain_rate_hi_last_15_min'] * self.rainbarrel.bucketsize2


            packet['rain_storm_start_at_2'] = iss2_data['rain_storm_start_at']
            packet['rain_storm_last_start_at_2'] = iss2_data['rain_storm_last_start_at']
            packet['rain_storm_last_end_at_2'] = iss2_data['rain_storm_last_end_at']

            packet['dayRain_2'] = iss2_data['rainfall_daily'] * self.rainbarrel.bucketsize2
            packet['monthRain_2'] = iss2_data['rainfall_monthly'] * self.rainbarrel.bucketsize2
            packet['yearRain_2'] = iss2_data['rainfall_year'] * self.rainbarrel.bucketsize2

            self.rainbarrel.rain2 = iss2_data['rainfall_daily']
            packet['rainRate_2'] = iss2_data['rain_rate_last'] * self.rainbarrel.bucketsize2

            rain_now = self.rainbarrel.rain2 - self.rainbarrel.rain_previous_period2
            if rain_now > 0:
               self.rainbarrel.rain_previous_period2 = self.rainbarrel.rain2
               # Empty Barrel
               #self.rainbarrel.empty_rain_barrel()
            self.rainbarrel.rain2 = 0
            rain_2v = rain_now * self.rainbarrel.bucketsize2

            if rain_2v >= 0:
              packet['rain_2'] = rain_2v
            else:
              packet['rain_2'] = 0



        return packet

    def calculate_rain(self):
      #if self.rainbarrel.previous_date_stamp.timestamp() != None: 
        if self.davis_date_stamp.timestamp() > self.rainbarrel.previous_date_stamp.timestamp():

            # Reset Previous rain at Midnight
            logdbg('Previous: {}'.format(self.rainbarrel.previous_date_stamp))
            logdbg('Davis:   {}'.format(self.davis_date_stamp))
            logdbg('System:   {}'.format(self.system_date_stamp))
            logdbg('daily rain Davis:     {}'.format(self.rainbarrel.rain))
            logdbg('prev. before reset:   {}'.format(self.rainbarrel.rain_previous_period))

            self.rainbarrel.set_rain_previous_date(self.davis_date_stamp)
            self.rainbarrel.set_rain_previous_period(0)

            logdbg('prev after reset:     {}'.format(self.rainbarrel.rain_previous_period))
            logdbg('({}) Daily rain reset - next reset midnight {}'
                   .format(weeutil.weeutil.timestamp_to_string(time.time()), str(self.rainbarrel.previous_date_stamp)))

        if self.rainbarrel.rain < self.rainbarrel.rain_previous_period:
            logdbg('({}) Negative Rain'.format(weeutil.weeutil.timestamp_to_string(time.time())))

        rain_now = self.rainbarrel.rain - self.rainbarrel.rain_previous_period
        if rain_now > 0:
            logdbg('({}) rainbarrel.rain: {} - rain_previous_period: {}.'
                   .format(weeutil.weeutil.timestamp_to_string(time.time()),
                           self.rainbarrel.rain,
                           self.rainbarrel.rain_previous_period))

            self.rainbarrel.rain_previous_period = self.rainbarrel.rain
            # Empty Barrel
            self.rainbarrel.empty_rain_barrel()

            logdbg('({}) Rain this period: +{} buckets.[{} mm / {} in]'
                   .format(weeutil.weeutil.timestamp_to_string(time.time()),
                           rain_now,
                           round(rain_now * self.rainbarrel.bucketsize * 25.4, 1),
                           round(rain_now * self.rainbarrel.bucketsize, 2)))
            logdbg('Set Previous period rain to: {} buckets.[{} mm / {} in]'
                   .format(self.rainbarrel.rain_previous_period,
                           round(self.rainbarrel.rain_previous_period * self.rainbarrel.bucketsize * 25.4, 1),
                           round(self.rainbarrel.rain_previous_period * self.rainbarrel.bucketsize, 2)))

        self.davis_packet['rain'] = rain_now * self.rainbarrel.bucketsize

    def check_udp_broascast(self):
        if (self.udp_countdown - 360) < time.time():
            response = make_request_using_socket(self.real_rime_url)
            if response is None:
                logerr('Unable to connect to Weather Link Live')
            elif response.get('data'):
                Req_data = response
                self.udp_countdown = time.time() + Req_data['data']['duration']
                if self.log == 1:
                  loginf('UDP check at: {}'.format(weeutil.weeutil.timestamp_to_string(self.udp_countdown)))
                logdbg('UDP check at: {}'.format(weeutil.weeutil.timestamp_to_string(self.udp_countdown)))


class WeatherLinkLiveUDPDriver(weewx.drivers.AbstractDevice):
    """weewx driver that reads data from a WeatherLink Live
    """

    def __init__(self, **stn_dict):
        # Show Diver version
        loginf('WLL UDP driver version is %s' % DRIVER_VERSION)

        self.station = WllStation()

        self.station.set_poll_interval(float(stn_dict.get('poll_interval', 10)))

        self.station.set_log(stn_dict.get('log', 0))

        self.wll_ip = stn_dict.get('wll_ip', '192.168.0.121')
        self.station.did = stn_dict.get('did', None)


        if self.wll_ip is None:
            logerr("No Weatherlink Live IP provided")

        txid_iss = stn_dict.get('txid_iss', None)

        self.station.set_extra1(stn_dict.get('extra_id'))
        self.station.set_extra2(stn_dict.get('extra_id2'))
        self.station.set_extra3(stn_dict.get('extra_id3'))
        self.station.set_extra4(stn_dict.get('extra_id4'))
        self.station.set_soil(stn_dict.get('soil'))
        self.station.set_leaf(stn_dict.get('leaf'))
        self.station.set_wind(stn_dict.get('wind'))
        self.station.set_rain(stn_dict.get('txid_rain'))
        self.station.set_txid2(stn_dict.get('txid_iss2'))
        
        # Tells the WW to begin broadcasting UDP data and continue for 1 hour seconds
        self.station.real_rime_url = 'http://{}:80/v1/real_time?duration=3600'.format(self.wll_ip)
        self.station.current_conditions_url = 'http://{}:80/v1/current_conditions'.format(self.wll_ip)

        # Make First Contact with WLL
        response = make_request_using_socket(self.station.current_conditions_url)

        if response is None:
            logerr('Unable to connect to Weather Link Live')
        elif response.get('data'):

            data = response['data']
	
            if txid_iss is None:
               self.station.set_txid(data['conditions'][0]['txid'])
            else:
               self.station.set_txid(txid_iss) 

            if self.station.leaf == None and self.station.soil == None:
               for condition in data['conditions']:
                  if condition.get('data_structure_type') == 2:
                    self.station.leafsoil = condition.get('txid')
                    loginf('LeafSoil station is using txid: {}'.format(self.station.leafsoil))

            #main_condition = data['conditions'][0]
            if self.station.txid_iss is None and self.station.txid_rain is None:
               main_condition = data['conditions'][0]
            else:
               for condition in data['conditions']:
                  if self.station.txid_rain != None and condition.get('txid') == self.station.txid_rain:
                     main_condition = condition
                  elif self.station.txid_rain is None and condition.get('txid') == self.station.txid_iss: 
                     main_condition = condition

            # Set Bucket Size
            self.station.rainbarrel.set_up_bucket_size(main_condition)

            # Check current rain for the day and set it
            self.station.rainbarrel.set_rain_previous_period(main_condition['rainfall_daily'])

            # Set date for previous rain
            self.station.rainbarrel.set_rain_previous_date(datetime.datetime.fromtimestamp(data['ts']))

    @property
    def hardware_name(self):
        return "WeatherLinkLiveUDP"

    def test_midnight(self):
        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M:%S")
        start = '00:00:00'
        end = '00:00:05'
        if start < current_time < end:
            logdbg('Midnight nap')
            logdbg(current_time)
            return True
        else:
            return False

    def genLoopPackets(self):

        # Start Loop
        while True:
            # Sleep for 5 seconds at midnight
            if self.test_midnight():
                logdbg("Midnight, no HTTP packet.")
            else:
                # Get Current Conditions
                current_conditions = make_request_using_socket(self.station.current_conditions_url)
                if current_conditions is None:
                    logerr('No current conditions from wll. Check ip address.')
                elif current_conditions.get('data'):
                    packet = self.station.decode_data_wll(current_conditions['data'])
                    if packet == "":
                       logerr('No current conditions from wll')
                    if self.station.log == 2 or self.station.log == 3:
                       loginf("packet: %s" % packet)
                    yield packet
                    #time.sleep(3)

            # Check if UDP is still on
            self.station.check_udp_broascast()

            # Set timer to listen to UDP
            self.timeout = time.time() + self.station.poll_interval

            # Listen for UDP Broadcast for the duration of the poll interval
            while time.time() < self.timeout:
                try:
                    data, wherefrom = comsocket.recvfrom(2048)
                    UDP_data = json.loads(data.decode("utf-8"))
                    if UDP_data["conditions"] is None:
                        logdbg(UDP_data["error"])
                    else:
                        if self.test_midnight():
                            logdbg("Midnight, no UDP packet.")
                        elif self.station.did == None or (UDP_data["did"] and UDP_data["did"] == self.station.did):
                            packet = self.station.decode_data_wll(UDP_data)
                            if self.station.log == 3:
                               loginf("udp-packet: %s" % packet)
                            # Yield UDP
                            yield packet
                # Catch json decoder faults
                except json.JSONDecodeError:
                    logging.info(
                        "Message was ignored because it was not valid JSON.",
                    )

                except socket.timeout:
                    logerr('UDP Socket Time Out')
                    # Reset Countdown to Switch UDP back on.
                    self.station.udp_countdown = 0
                    self.station.check_udp_broascast()


def make_request_using_socket(url):
    try:
        retry_strategy = Retry(total=3, backoff_factor=1)

        adapter = HTTPAdapter(max_retries=retry_strategy)
        http = requests.Session()
        http.mount("http://", adapter)

        resp = http.get(url, timeout=10)

        json_data = json.loads(resp.text)
        if json_data["data"] is None:
            logerr(json_data["error"])
        else:
            return json_data
    except requests.Timeout as err:
        logerr({"message": err})
    except requests.RequestException as err:
        # Max retries exceeded
        logerr('Request Exception: {}'.format(err))


# To test this driver, run it directly as follows:
#   PYTHONPATH=/home/weewx/bin python /home/weewx/bin/user/weatherlinkliveudp.py
#   for RasPi:  PYTHONPATH=/usr/share/weewx python3 /usr/share/weewx/user/weatherlinkliveudp.py
#
if __name__ == "__main__":
    import optparse

    import weeutil.logger
    import weewx

    weewx.debug = 1
    weeutil.logger.setup('WeatherLinkLiveUDP', {})
    usage = """Usage:%prog --wll_ip= [options] [--help] [--version]"""

    parser = optparse.OptionParser(usage=usage)
    parser.add_option('--version', dest='version', action='store_true',
                      help='Display driver version')
    #
    parser.add_option('--wll_ip', dest='wll_ip', metavar='wll_ip',
                      help='ip address from Weather Link Live')

    (options, args) = parser.parse_args()

    if options.version:
        print("Weatherlink Liver version %s" % DRIVER_VERSION)
        exit(0)

    driver = WeatherLinkLiveUDPDriver()
    for packet in driver.genLoopPackets():
        print(weeutil.weeutil.timestamp_to_string(packet['dateTime']), packet)
