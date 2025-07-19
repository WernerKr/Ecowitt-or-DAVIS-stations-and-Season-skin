#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ecowitt_http.py

A WeeWX driver for devices using Ecowitt local HTTP API.

Copyright (C) 2024-25 Gary Roderick                     gjroderick<at>gmail.com

Modified Werner Krenn July 2025


This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program.  If not, see https://www.gnu.org/licenses/.

Version: 0.1.6                                  Date: 19 July 2025

Revision History
    3 July 2025            v0.1.0x
        - WH45/WH46 = co2 missed - added
        - changed some keys that are the same as my ecowittcustom driver
        - add some keys
        - completed all data from the SDcard GW3000
        - completed all data from the device 
    4 July 2025            v0.1.0x
        - corrected radiation
        - corrected co2_Temp
        - corrected wh51 - forget to add sensors wh51 at sensors
        - corrected signal to None if signal id is "FFFFFFFE" or "FFFFFFFF"
        - add some unit-settings
        - corrected rain, piezo_rain, lightning_count for loop packets
    5 July 2025            v0.1.0x
        - add missed wh40_sig
        - changed daymaxwind to maxdailygust (because customecowitt driver)
        - hail, hailrate is Piezo Rain too
        - add wh40_batt, wh80_batt, wh85_batt, wh95_bat
        - now is 'hailBatteryStatus': 'piezoRain.0x13.voltage',
        - add correction for rain, piezo_rain, lightning_count with data from sdcard
    6 July 2025            v0.1.0x
        - added more values (soilmoist9..soilmoist16, ...) to history data
          added debug option "archive"
    7 July 2025 
        - added voltage from leaf sensors
        - increased the default url_timeout to 10 - but seems do be better with 20 
        - corrected history - mapping from ecowitt.net
    8 July 2025
        - added ws85_ver, ws90_ver, radiationcompensation, upgrade, newVersion,
                rain_source, rain_priority, rain_day_reset, rain_week_reset, rain_annual_reset,
                piezo, raingain, gain0, gain1, gain2, gain3, gain4
                to the supported fields, because compatible with Ecowitt Custom Driver and the GW1000 Driver


    10 July 2025            v0.1.0
        - initial release
    11 July 2025		v0.1.1
        -lightning 
    12 July 2025		v0.1.2
        - piezo, leak_Batt3, rain, piezo rain wasn't set to new value
    13 July 2025		v0.1.3
        - calc vpd if data from Ecowitt.net - because this value is not provided.
        - changed lighting_distance to lighting_dist 
    14 July 2025		v0.1.4         
        - 'ch_lds1', 'ch_lds2', 'ch_lds3', 'ch_lds4' from Ecowitt.net added
        - wh68_batt, wh69_batt
    15 July 2025		v0.1.5     
        - p_rain is back      
    19 July 2025		v0.1.6     
        - new rssi, rain voltage, winddir_avg10m, last24hrainin, last24hrain_piezo, LDS total_heat, wn20 (Mini rain)      


    Driver not working as service!


This driver is based on the Ecowitt local HTTP API. At the time of release the
following sensors are supported:

WN31        temperature, humidity, signal level, battery state. channels 1-8
            inclusive
WN32P       temperature, humidity, pressure, signal level, battery state.
            single device only
WN32        (non-WH32P models) temperature, humidity, signal level, battery
            state. single device only
WN34        temperature, signal level, battery state. channels 1-8 inclusive
WN35        leaf wetness, signal level, battery state. channels 1-8 inclusive
WH41/43:    PM2.5, 24-hour average PM2.5, signal level, battery state.
            Channels 1-4 inclusive
WH45        CO2, PM2.5, PM10, signal level, battery state. single device only
WH46        CO2, PM2.5, PM10, PM1, PM4, signal level, battery state. single device only	
WH54        LDS Sensor	
WH55        Leak Sensor	
WH57        Lightning, signal level, battery state. single device only
WH68        signal level, battery state
WH69        signal level, battery state
WS80        temperature, humidity, wind speed, wind direction, illuminance,
            UV index, signal level, battery state. single device only
WS85        piezo rain, wind speed, wind direction, signal level, battery
            state. single device only
WS90        temperature, humidity, piezo rain, wind speed, wind direction,
            illuminance, UV index, signal level, battery state. single device
            only

The Ecowitt local HTTP API is poorly documented with the documentation largely
consisting of a dated (circa April 2022) example get_livedata_info API command
response. Other API commands have been published informally on wxforum.net but
no documentation for the use of the commands or the interpretation of the
device responses exists.

The following deviations have been made from the known 'documentation':

-   common list field 3. The example 'get_livedata_info' includes a common_list
    field with id '3' that is a temperature, but give no explanation as to what
    this field is. When using the WS View+ app this field appears to populate
    the 'Feels Like' display. Therefore the Ecowitt HTTP driver assumes
    common_list field '3' is the feels like temperature.

-   HTTP API command get_ws_services response does not populate the 'mqtt_name'
    field. In WS View+ the MQTT 'Client Name' and 'Username' fields mirror each
    other (ie populating one populates the other with the same data); however,
    the get_ws_services response 'mqtt_name' field is always an empty string.

-   Ecowitt continues to chop and change sensor model numbers; eg WH31 is
    referred to as both WH31 and WN31 on shop.ecowitt.com and the sensor manual
    and is referred to as WH31 in Ecowitt HTTP API responses. Similarly for
    WH32. WN34 and WN35 sensors are referred to as WN34 and WN35 on
    shop.ecowitt.com and the sensor manual, but the HTTP API responses refer
    to WH34 and WH35. Like for LDS01 and WH54. To provide consistency this
    driver uses the following sensor model numbers throughout:
    -   WN31 in lieu of WH31
    -   WN32 in lieu of WH32
    -   WN34 in lieu of WH34
    -   WN35 in lieu of WH35
    -   WN36 in lieu of WH36
    -   WS80 in lieu of WH80
    -   WS85 in lieu of WH85
    -   WS90 in lieu of WH90
    Note: Where Ecowitt HTTP API commands contain a legacy model number,
          eg 'get_cli_wh34' the use of the legacy model is retained.
"""

# Python imports
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import calendar
import collections
import csv
import datetime
import io
import json
import logging
import operator
import queue
import re
import socket
import struct
import sys
import textwrap
import threading
import datetime
import time
import math
import urllib.error
import urllib.parse
import urllib.request

from collections.abc import MutableMapping
from operator import itemgetter

import configobj

# WeeWX imports
import weecfg
import weeutil.weeutil
import weeutil.logger
import weewx.defaults
import weewx.drivers
import weewx.engine
import weewx.units
import weewx.wxformulas
from weeutil.weeutil import bcolors, timestamp_to_string

log = logging.getLogger(__name__)


DRIVER_NAME = 'EcowittHttp'
DRIVER_VERSION = '0.1.0'

# device models that are supported by the driver
SUPPORTED_DEVICES = ('GW1100', 'GW1200', 'GW2000',
                     'GW3000', 'WH2650', 'WH2680',
                     'WN1900', 'WN1980',
                     'WS3800', 'WS3810', 'WS3900', 'WS3910')
# device models that are not supported by the driver
UNSUPPORTED_DEVICES = ('GW1000',)
# device models that we know about
KNOWN_DEVICES = SUPPORTED_DEVICES + UNSUPPORTED_DEVICES
# sensors we know about
KNOWN_SENSORS = ('wn20', 'wh25', 'wh26', 'wn31', 'wn34', 'wn35',
                 'wh40', 'wh41', 'wh45',
                 'wh51', 'wh54', 'wh55', 'wh57',
                 'wh65', 'wh68', 'ws69', 'ws80', 'ws85', 'ws90')
# default max number of attempts to obtain data from the device
DEFAULT_MAX_TRIES = 3
# default wait time between retries when attempting to obtain data from the
# device
DEFAULT_RETRY_WAIT = 2
# default timeout when fetching data from a URL
DEFAULT_URL_TIMEOUT = 10
# default grace period after last_good_ts/start_ts after which we accept
# catchup records
DEFAULT_CATCHUP_GRACE = 0
# default max tries when downloading a catchup file
DEFAULT_CATCHUP_RETRIES = 3
# When run as a service the default age in seconds after which API data is
# considered stale and will not be used to augment loop packets
DEFAULT_MAX_AGE = 60
# default device poll interval
DEFAULT_POLL_INTERVAL = 20
# default discovery port
DEFAULT_DISCOVERY_PORT = 59387
# default discovery listening period
DEFAULT_DISCOVERY_PERIOD = 5
# default discovery timeout period
DEFAULT_DISCOVERY_TIMEOUT = 5
# default period between lost contact log entries during an extended period of
# lost contact when run as a Service
DEFAULT_LOST_CONTACT_LOG_PERIOD = 21600
# default loop packet unit system emitted by the driver
DEFAULT_UNIT_SYSTEM = weewx.METRICWX
# default battery state filtering (whether to only display battery state data
# for connected sensors)
DEFAULT_FILTER_BATTERY = False

# default firmware update check interval
DEFAULT_FW_CHECK_INTERVAL = 86400
# The HTTP API will return some sensor data (usually meta data) for sensors
# that are 'unregistered' or 'learning' as well as 'registered' sensors. The
# default is to only accept data from registered sensors (True).
#  DEFAULT_ONLY_REGISTERED_SENSORS = True
DEFAULT_ONLY_REGISTERED_SENSORS = False

weewx.units.obs_group_dict['leafWet1'] = 'group_percent'
weewx.units.obs_group_dict['leafWet2'] = 'group_percent'
weewx.units.obs_group_dict['leafWet3'] = 'group_percent'
weewx.units.obs_group_dict['leafWet4'] = 'group_percent'
weewx.units.obs_group_dict['leafWet5'] = 'group_percent'
weewx.units.obs_group_dict['leafWet6'] = 'group_percent'
weewx.units.obs_group_dict['leafWet7'] = 'group_percent'
weewx.units.obs_group_dict['leafWet8'] = 'group_percent'
weewx.units.obs_group_dict['soilMoist1'] = 'group_percent'
weewx.units.obs_group_dict['soilMoist2'] = 'group_percent'
weewx.units.obs_group_dict['soilMoist3'] = 'group_percent'
weewx.units.obs_group_dict['soilMoist4'] = 'group_percent'
weewx.units.obs_group_dict['soilMoist5'] = 'group_percent'
weewx.units.obs_group_dict['soilMoist6'] = 'group_percent'
weewx.units.obs_group_dict['soilMoist7'] = 'group_percent'
weewx.units.obs_group_dict['soilMoist8'] = 'group_percent'
weewx.units.obs_group_dict['soilMoist9'] = 'group_percent'
weewx.units.obs_group_dict['soilMoist10'] = 'group_percent'
weewx.units.obs_group_dict['soilMoist11'] = 'group_percent'
weewx.units.obs_group_dict['soilMoist12'] = 'group_percent'
weewx.units.obs_group_dict['soilMoist13'] = 'group_percent'
weewx.units.obs_group_dict['soilMoist14'] = 'group_percent'
weewx.units.obs_group_dict['soilMoist15'] = 'group_percent'
weewx.units.obs_group_dict['soilMoist16'] = 'group_percent'

weewx.units.obs_group_dict['pm1_24h_co2'] = 'group_concentration'
weewx.units.obs_group_dict['pm4_24h_co2'] = 'group_concentration'
weewx.units.obs_group_dict['pm25_24h_co2'] = 'group_concentration'
weewx.units.obs_group_dict['pm10_24h_co2'] = 'group_concentration'
weewx.units.obs_group_dict['pm25_avg_24h_ch1'] = 'group_concentration'
weewx.units.obs_group_dict['pm25_avg_24h_ch2'] = 'group_concentration'
weewx.units.obs_group_dict['pm25_avg_24h_ch3'] = 'group_concentration'
weewx.units.obs_group_dict['pm25_avg_24h_ch4'] = 'group_concentration'

weewx.units.obs_group_dict['rainrate'] = 'group_rainrate'
weewx.units.obs_group_dict['eventRain'] = 'group_rain'
weewx.units.obs_group_dict['weekRain'] = 'group_rain'
weewx.units.obs_group_dict['raintotal'] = 'group_rain'

weewx.units.obs_group_dict['rrain_piezo'] = 'group_rainrate'
weewx.units.obs_group_dict['erain_piezo'] = 'group_rain'
weewx.units.obs_group_dict['hrain_piezo'] = 'group_rain'
weewx.units.obs_group_dict['drain_piezo'] = 'group_rain'
weewx.units.obs_group_dict['wrain_piezo'] = 'group_rain'
weewx.units.obs_group_dict['mrain_piezo'] = 'group_rain'
weewx.units.obs_group_dict['yrain_piezo'] = 'group_rain'
weewx.units.obs_group_dict['rain_piezo'] = 'group_rain'
weewx.units.obs_group_dict['rain24_piezo'] = 'group_rain'
weewx.units.obs_group_dict['p_rain'] = 'group_rain'
weewx.units.obs_group_dict['p_rainrate'] = 'group_rainrate'
#weewx.units.obs_group_dict['hail'] = 'group_rain'
#weewx.units.obs_group_dict['hailRate'] = 'group_rainrate'
weewx.units.obs_group_dict['t_rainyear'] = 'group_rain'
weewx.units.obs_group_dict['p_rainyear'] = 'group_rain'
weewx.units.obs_group_dict['rain24_piezo'] = 'group_rain'

weewx.units.obs_group_dict['rainBatteryStatus'] = 'group_volt'
weewx.units.obs_group_dict['hailBatteryStatus'] = 'group_volt'
weewx.units.obs_group_dict['windBatteryStatus'] = 'group_volt'
weewx.units.obs_group_dict['ws80_batt'] = 'group_volt'
weewx.units.obs_group_dict['ws85_batt'] = 'group_volt'
weewx.units.obs_group_dict['ws90_batt'] = 'group_volt'

weewx.units.obs_group_dict['ws1900batt'] = 'group_volt'
weewx.units.obs_group_dict['console_batt'] = 'group_volt'
weewx.units.obs_group_dict['wh68_batt'] = 'group_count'
weewx.units.obs_group_dict['wh69_batt'] = 'group_count'
weewx.units.obs_group_dict['wh80_batt'] = 'group_count'
weewx.units.obs_group_dict['wh85_batt'] = 'group_count'
weewx.units.obs_group_dict['wh90_batt'] = 'group_count'

weewx.units.obs_group_dict['maxdailygust'] = 'group_speed2'

weewx.units.obs_group_dict['ws90cap_volt'] = 'group_volt'
weewx.units.obs_group_dict['ws85cap_volt'] = 'group_volt'
weewx.units.obs_group_dict['ws90_ver'] = 'group_count'
weewx.units.obs_group_dict['ws85_ver'] = 'group_count'
weewx.units.obs_group_dict['rain_annual_reset'] = 'group_count'
weewx.units.obs_group_dict['rain_day_reset'] = 'group_count'
weewx.units.obs_group_dict['rain_week_reset'] = 'group_count'
weewx.units.obs_group_dict['rain_source'] = 'group_count'
weewx.units.obs_group_dict['piezo'] = 'group_count'

weewx.units.obs_group_dict['lightning_dist'] = 'group_count'
weewx.units.obs_group_dict['lightning_distance'] = 'group_count'
weewx.units.obs_group_dict['lightning_disturber_count'] = 'group_time'
weewx.units.obs_group_dict['lightning_strike_count'] = 'group_count'
weewx.units.obs_group_dict['lightning_noise_count'] = 'group_count'

weewx.units.obs_group_dict['runtime'] = 'group_deltatime'
weewx.units.obs_group_dict['heap'] = 'group_data'
weewx.units.obs_group_dict['pb'] = 'group_data'
weewx.units.obs_group_dict['srain_piezo'] = 'group_count'

weewx.units.obs_group_dict['ldsbatt1'] = 'group_volt'
weewx.units.obs_group_dict['ldsbatt2'] = 'group_volt'
weewx.units.obs_group_dict['ldsbatt3'] = 'group_volt'
weewx.units.obs_group_dict['ldsbatt4'] = 'group_volt'
weewx.units.obs_group_dict['ldsheat_ch1'] = 'group_count'
weewx.units.obs_group_dict['ldsheat_ch2'] = 'group_count'
weewx.units.obs_group_dict['ldsheat_ch3'] = 'group_count'
weewx.units.obs_group_dict['ldsheat_ch4'] = 'group_count'

weewx.units.obs_group_dict['windDir10'] = 'group_direction'

#weewx.units.obs_group_dict['wh25_rssi'] = "group_db" 

# define the WeeWX unit group used by each device field
DEFAULT_GROUPS = {
    'datetime': 'group_time',
    'common_list.0x02.val': 'group_temperature',
    'common_list.0x02.battery': 'group_count',
    'common_list.0x02.voltage': 'group_volt',
    'common_list.0x03.val': 'group_temperature',
    'common_list.0x03.battery': 'group_count',
    'common_list.0x03.voltage': 'group_volt',
    'common_list.3.val': 'group_temperature',
    'common_list.3.battery': 'group_count',
    'common_list.3.voltage': 'group_volt',
    'common_list.0x04.val': 'group_temperature',
    'common_list.0x04.battery': 'group_count',
    'common_list.0x04.voltage': 'group_volt',
    'common_list.4.val': 'group_temperature',
    'common_list.4.battery': 'group_count',
    'common_list.4.voltage': 'group_volt',
    'common_list.0x05.val': 'group_temperature',
    'common_list.0x05.battery': 'group_count',
    'common_list.0x05.voltage': 'group_volt',
    'common_list.5.val': 'group_pressurevpd',
    'common_list.5.battery': 'group_count',
    'common_list.5.voltage': 'group_volt',
    'common_list.0x07.val': 'group_percent',
    'common_list.0x07.battery': 'group_count',
    'common_list.0x07.voltage': 'group_volt',
    'common_list.0x0A.val': 'group_direction',
    'common_list.0x0A.battery': 'group_count',
    'common_list.0x0A.voltage': 'group_volt',
    'common_list.0x0B.val': 'group_speed',
    'common_list.0x0B.battery': 'group_count',
    'common_list.0x0B.voltage': 'group_volt',
    'common_list.0x0C.val': 'group_speed',
    'common_list.0x0C.battery': 'group_count',
    'common_list.0x0C.voltage': 'group_volt',
    'common_list.0x0F.val': 'group_speed',
    'common_list.0x0F.battery': 'group_count',
    'common_list.0x0F.voltage': 'group_volt',
    'common_list.0x14.val': 'group_speed',
    'common_list.0x14.battery': 'group_count',
    'common_list.0x14.voltage': 'group_volt',
    'common_list.0x15.val': 'group_radiation',
    'common_list.0x15.battery': 'group_count',
    'common_list.0x15.voltage': 'group_volt',
    'common_list.0x16.val': 'group_radiation',
    'common_list.0x16.battery': 'group_count',
    'common_list.0x16.voltage': 'group_volt',
    'common_list.0x17.val': 'group_uv',
    'common_list.0x17.battery': 'group_count',
    'common_list.0x17.voltage': 'group_volt',
    'common_list.0x19.val': 'group_speed',
    'common_list.0x19.battery': 'group_count',
    'common_list.0x19.voltage': 'group_volt',
    'rain.0x0D.val': 'group_rain',
    'rain.0x0D.battery': 'group_count',
    'rain.0x0D.voltage': 'group_volt',
    'rain.0x0E.val': 'group_rainrate',
    'rain.0x0E.battery': 'group_count',
    'rain.0x0E.voltage': 'group_volt',
    'rain.0x0F.val': 'group_rain',
    'rain.0x10.val': 'group_rain',
    'rain.0x10.battery': 'group_count',
    'rain.0x10.voltage': 'group_volt',
    'rain.0x11.val': 'group_rain',
    'rain.0x11.battery': 'group_count',
    'rain.0x11.voltage': 'group_volt',
    'rain.0x12.val': 'group_rain',
    'rain.0x12.battery': 'group_count',
    'rain.0x12.voltage': 'group_volt',
    'rain.0x13.val': 'group_rain',
    'rain.0x13.voltage': 'group_volt',
    't_rain': 'group_rain',
    't_rainyear': 'group_rain',
    #    'rain.0x13.battery': 'group_count',
    'rain.0x13.voltage': 'group_volt',
    'piezoRain.srain_piezo.val': 'group_boolean',
    'piezoRain.0x0D.val': 'group_rain',
    'piezoRain.0x0D.battery': 'group_count',
    'piezoRain.0x0D.voltage': 'group_volt',
    'piezoRain.0x0E.val': 'group_rainrate',
    'piezoRain.0x0E.battery': 'group_count',
    'piezoRain.0x0E.voltage': 'group_volt',
    'piezoRain.0x0F.val': 'group_rain',
    'piezoRain.0x10.val': 'group_rain',
    'piezoRain.0x10.battery': 'group_count',
    'piezoRain.0x10.voltage': 'group_volt',
    'piezoRain.0x11.val': 'group_rain',
    'piezoRain.0x11.battery': 'group_count',
    'piezoRain.0x11.voltage': 'group_volt',
    'piezoRain.0x12.val': 'group_rain',
    'piezoRain.0x12.battery': 'group_count',
    'piezoRain.0x12.voltage': 'group_volt',
    'piezoRain.0x13.val': 'group_rain',
    'piezoRain.0x13.voltage': 'group_volt',
    'piezoRain.srain_piezo': 'group_boolean',
    'p_rain': 'group_rain',
    'p_rainyear': 'group_rain',
    'wh25.intemp': 'group_temperature',
    'wh25.inhumi': 'group_percent',
    'wh25.abs': 'group_pressure',
    'wh25.rel': 'group_pressure',
    'wh25.CO2': 'group_fraction',
    'wh25.CO2_24H': 'group_fraction',
    'lightning.distance': 'group_distance',
    'lightning.timestamp': 'group_time',
    'lightning.count': 'group_count',
    'lightning.num': 'group_count',
    'co2.temperature': 'group_temperature',
    'co2.temp': 'group_temperature',
    'co2.humidity': 'group_percent',
    'co2.PM25': 'group_concentration',
    'co2.PM25_RealAQI': 'group_count',
    'co2.PM25_24HAQI': 'group_count',
    'co2.PM10': 'group_concentration',
    'co2.PM10_RealAQI': 'group_count',
    'co2.PM10_24HAQI': 'group_count',
    'co2.PM1': 'group_concentration',
    'co2.PM1_RealAQI': 'group_count',
    'co2.PM1_24HAQI': 'group_count',
    'co2.PM4': 'group_concentration',
    'co2.PM4_RealAQI': 'group_count',
    'co2.PM4_24HAQI': 'group_count',
    'co2.CO2': 'group_fraction',
    'co2.CO2_24H': 'group_fraction',
    'co2.battery': 'group_count',
    'ch_pm25.1.PM25': 'group_concentration',
    'ch_pm25.1.PM25_24H': 'group_concentration',
    'ch_pm25.1.PM25_RealAQI': 'group_count',
    'ch_pm25.1.PM25_24HAQI': 'group_count',
    'ch_pm25.2.PM25': 'group_concentration',
    'ch_pm25.2.PM25_24H': 'group_concentration',
    'ch_pm25.2.PM25_RealAQI': 'group_count',
    'ch_pm25.2.PM25_24HAQI': 'group_count',
    'ch_pm25.3.PM25': 'group_concentration',
    'ch_pm25.3.PM25_24H': 'group_concentration',
    'ch_pm25.3.PM25_RealAQI': 'group_count',
    'ch_pm25.3.PM25_24HAQI': 'group_count',
    'ch_pm25.4.PM25': 'group_concentration',
    'ch_pm25.4.PM25_24H': 'group_concentration',
    'ch_pm25.4.PM25_RealAQI': 'group_count',
    'ch_pm25.4.PM25_24HAQI': 'group_count',
    'ch_leak.1.status': 'group_count',
    'ch_leak.2.status': 'group_count',
    'ch_leak.3.status': 'group_count',
    'ch_leak.4.status': 'group_count',
    'ch_aisle.1.temp': 'group_temperature',
    'ch_aisle.1.humidity': 'group_percent',
    'ch_aisle.2.temp': 'group_temperature',
    'ch_aisle.2.humidity': 'group_percent',
    'ch_aisle.3.temp': 'group_temperature',
    'ch_aisle.3.humidity': 'group_percent',
    'ch_aisle.4.temp': 'group_temperature',
    'ch_aisle.4.humidity': 'group_percent',
    'ch_aisle.5.temp': 'group_temperature',
    'ch_aisle.5.humidity': 'group_percent',
    'ch_aisle.6.temp': 'group_temperature',
    'ch_aisle.6.humidity': 'group_percent',
    'ch_aisle.7.temp': 'group_temperature',
    'ch_aisle.7.humidity': 'group_percent',
    'ch_aisle.8.temp': 'group_temperature',
    'ch_aisle.8.humidity': 'group_percent',
    'ch_soil.1.humidity': 'group_percent',
    'ch_soil.1.voltage': 'group_volt',
    'ch_soil.2.humidity': 'group_percent',
    'ch_soil.2.voltage': 'group_volt',
    'ch_soil.3.humidity': 'group_percent',
    'ch_soil.3.voltage': 'group_volt',
    'ch_soil.4.humidity': 'group_percent',
    'ch_soil.4.voltage': 'group_volt',
    'ch_soil.5.humidity': 'group_percent',
    'ch_soil.5.voltage': 'group_volt',
    'ch_soil.6.humidity': 'group_percent',
    'ch_soil.6.voltage': 'group_volt',
    'ch_soil.7.humidity': 'group_percent',
    'ch_soil.7.voltage': 'group_volt',
    'ch_soil.8.humidity': 'group_percent',
    'ch_soil.8.voltage': 'group_volt',
    'ch_soil.9.humidity': 'group_percent',
    'ch_soil.9.voltage': 'group_volt',
    'ch_soil.10.humidity': 'group_percent',
    'ch_soil.10.voltage': 'group_volt',
    'ch_soil.11.humidity': 'group_percent',
    'ch_soil.11.voltage': 'group_volt',
    'ch_soil.12.humidity': 'group_percent',
    'ch_soil.12.voltage': 'group_volt',
    'ch_soil.13.humidity': 'group_percent',
    'ch_soil.13.voltage': 'group_volt',
    'ch_soil.14.humidity': 'group_percent',
    'ch_soil.14.voltage': 'group_volt',
    'ch_soil.15.humidity': 'group_percent',
    'ch_soil.15.voltage': 'group_volt',
    'ch_soil.16.humidity': 'group_percent',
    'ch_soil.16.voltage': 'group_volt',
    'ch_temp.1.temp': 'group_temperature',
    'ch_temp.1.voltage': 'group_volt',
    'ch_temp.2.temp': 'group_temperature',
    'ch_temp.2.voltage': 'group_volt',
    'ch_temp.3.temp': 'group_temperature',
    'ch_temp.3.voltage': 'group_volt',
    'ch_temp.4.temp': 'group_temperature',
    'ch_temp.4.voltage': 'group_volt',
    'ch_temp.5.temp': 'group_temperature',
    'ch_temp.5.voltage': 'group_volt',
    'ch_temp.6.temp': 'group_temperature',
    'ch_temp.6.voltage': 'group_volt',
    'ch_temp.7.temp': 'group_temperature',
    'ch_temp.7.voltage': 'group_volt',
    'ch_temp.8.temp': 'group_temperature',
    'ch_temp.8.voltage': 'group_volt',
    'ch_leaf.1.humidity': 'group_percent',
    'ch_leaf.2.humidity': 'group_percent',
    'ch_leaf.3.humidity': 'group_percent',
    'ch_leaf.4.humidity': 'group_percent',
    'ch_leaf.5.humidity': 'group_percent',
    'ch_leaf.6.humidity': 'group_percent',
    'ch_leaf.7.humidity': 'group_percent',
    'ch_leaf.8.humidity': 'group_percent',
    'ch_leaf.1.voltage': 'group_volt',
    'ch_leaf.2.voltage': 'group_volt',
    'ch_leaf.3.voltage': 'group_volt',
    'ch_leaf.4.voltage': 'group_volt',
    'ch_leaf.5.voltage': 'group_volt',
    'ch_leaf.6.voltage': 'group_volt',
    'ch_leaf.7.voltage': 'group_volt',
    'ch_leaf.8.voltage': 'group_volt',
    'ch_lds.1.air': 'group_depth',
    'ch_lds.1.depth': 'group_depth',
    'ch_lds.1.total_height': 'group_depth',
    'ch_lds.1.total_heat': 'group_count',
    'ch_lds.1.voltage': 'group_volt',
    'ch_lds.2.air': 'group_depth',
    'ch_lds.2.depth': 'group_depth',
    'ch_lds.2.total_height': 'group_depth',
    'ch_lds.2.total_heat': 'group_count',
    'ch_lds.2.voltage': 'group_volt',
    'ch_lds.3.air': 'group_depth',
    'ch_lds.3.depth': 'group_depth',
    'ch_lds.3.total_height': 'group_depth',
    'ch_lds.3.total_heat': 'group_count',
    'ch_lds.3.voltage': 'group_volt',
    'ch_lds.4.air': 'group_depth',
    'ch_lds.4.depth': 'group_depth',
    'ch_lds.4.total_heat': 'group_count',
    'ch_lds.4.total_height': 'group_depth',
    'ch_lds.4.voltage': 'group_volt',
    'debug.heap': 'group_data',
    'debug.runtime': 'group_deltatime',
    'debug.usr_interval': 'group_deltatime',
    'debug.is_cnip': 'group_boolean',
    'wn20.battery': 'group_count',
    'wh26.battery': 'group_count',
    'wh25.battery': 'group_count',
    'wh24.battery': 'group_count',
    'wh65.battery': 'group_count',
    'wn32.battery': 'group_count',
    'wn32p.battery': 'group_count',
    'wn31.ch1.battery': 'group_count',
    'wn31.ch2.battery': 'group_count',
    'wn31.ch3.battery': 'group_count',
    'wn31.ch4.battery': 'group_count',
    'wn31.ch5.battery': 'group_count',
    'wn31.ch6.battery': 'group_count',
    'wn31.ch7.battery': 'group_count',
    'wn31.ch8.battery': 'group_count',
    'wn34.ch1.battery': 'group_count',
    'wn34.ch2.battery': 'group_count',
    'wn34.ch3.battery': 'group_count',
    'wn34.ch4.battery': 'group_count',
    'wn34.ch5.battery': 'group_count',
    'wn34.ch6.battery': 'group_count',
    'wn34.ch7.battery': 'group_count',
    'wn34.ch8.battery': 'group_count',
    'wn35.ch1.battery': 'group_count',
    'wn35.ch2.battery': 'group_count',
    'wn35.ch3.battery': 'group_count',
    'wn35.ch4.battery': 'group_count',
    'wn35.ch5.battery': 'group_count',
    'wn35.ch6.battery': 'group_count',
    'wn35.ch7.battery': 'group_count',
    'wn35.ch8.battery': 'group_count',
    'wh40.battery': 'group_count',
    'wh41.ch1.battery': 'group_count',
    'wh41.ch2.battery': 'group_count',
    'wh41.ch3.battery': 'group_count',
    'wh41.ch4.battery': 'group_count',
    'wh45.battery': 'group_count',
    'wh51.ch1.battery': 'group_count',
    'wh51.ch2.battery': 'group_count',
    'wh51.ch3.battery': 'group_count',
    'wh51.ch4.battery': 'group_count',
    'wh51.ch5.battery': 'group_count',
    'wh51.ch6.battery': 'group_count',
    'wh51.ch7.battery': 'group_count',
    'wh51.ch8.battery': 'group_count',
    'wh51.ch9.battery': 'group_count',
    'wh51.ch10.battery': 'group_count',
    'wh51.ch11.battery': 'group_count',
    'wh51.ch12.battery': 'group_count',
    'wh51.ch13.battery': 'group_count',
    'wh51.ch14.battery': 'group_count',
    'wh51.ch15.battery': 'group_count',
    'wh51.ch16.battery': 'group_count',
    'wh54.ch1.battery': 'group_count',
    'wh54.ch2.battery': 'group_count',
    'wh54.ch3.battery': 'group_count',
    'wh54.ch4.battery': 'group_count',
    'wh55.ch1.battery': 'group_count',
    'wh55.ch2.battery': 'group_count',
    'wh55.ch3.battery': 'group_count',
    'wh55.ch4.battery': 'group_count',
    'wh57.battery': 'group_count',
    'wh68.battery': 'group_count',
    'wh69.battery': 'group_count',
    'ws80.battery': 'group_count',
    'ws85.battery': 'group_count',
    'ws90.battery': 'group_count',
    'wh51.ch1.voltage': 'group_volt',
    'wh51.ch2.voltage': 'group_volt',
    'wh51.ch3.voltage': 'group_volt',
    'wh51.ch4.voltage': 'group_volt',
    'wh51.ch5.voltage': 'group_volt',
    'wh51.ch6.voltage': 'group_volt',
    'wh51.ch7.voltage': 'group_volt',
    'wh51.ch8.voltage': 'group_volt',
    'wh51.ch9.voltage': 'group_volt',
    'wh51.ch10.voltage': 'group_volt',
    'wh51.ch11.voltage': 'group_volt',
    'wh51.ch12.voltage': 'group_volt',
    'wh51.ch13.voltage': 'group_volt',
    'wh51.ch14.voltage': 'group_volt',
    'wh51.ch15.voltage': 'group_volt',
    'wh51.ch16.voltage': 'group_volt',
    'wn20.signal': 'group_count',
    'wh24.signal': 'group_count',
    'wh25.signal': 'group_count',
    'wh26.signal': 'group_count',
    'wn32.signal': 'group_count',
    'wn32p.signal': 'group_count',
    'wn31.ch1.signal': 'group_count',
    'wn31.ch2.signal': 'group_count',
    'wn31.ch3.signal': 'group_count',
    'wn31.ch4.signal': 'group_count',
    'wn31.ch5.signal': 'group_count',
    'wn31.ch6.signal': 'group_count',
    'wn31.ch7.signal': 'group_count',
    'wn31.ch8.signal': 'group_count',
    'wn34.ch1.signal': 'group_count',
    'wn34.ch2.signal': 'group_count',
    'wn34.ch3.signal': 'group_count',
    'wn34.ch4.signal': 'group_count',
    'wn34.ch5.signal': 'group_count',
    'wn34.ch6.signal': 'group_count',
    'wn34.ch7.signal': 'group_count',
    'wn34.ch8.signal': 'group_count',
    'wn35.ch1.signal': 'group_count',
    'wn35.ch2.signal': 'group_count',
    'wn35.ch3.signal': 'group_count',
    'wn35.ch4.signal': 'group_count',
    'wn35.ch5.signal': 'group_count',
    'wn35.ch6.signal': 'group_count',
    'wn35.ch7.signal': 'group_count',
    'wn35.ch8.signal': 'group_count',
    'wh40.signal': 'group_count',
    'wh41.ch1.signal': 'group_count',
    'wh41.ch2.signal': 'group_count',
    'wh41.ch3.signal': 'group_count',
    'wh41.ch4.signal': 'group_count',
    'wh45.signal': 'group_count',
    'wh51.ch1.signal': 'group_count',
    'wh51.ch2.signal': 'group_count',
    'wh51.ch3.signal': 'group_count',
    'wh51.ch4.signal': 'group_count',
    'wh51.ch5.signal': 'group_count',
    'wh51.ch6.signal': 'group_count',
    'wh51.ch7.signal': 'group_count',
    'wh51.ch8.signal': 'group_count',
    'wh51.ch9.signal': 'group_count',
    'wh51.ch10.signal': 'group_count',
    'wh51.ch11.signal': 'group_count',
    'wh51.ch12.signal': 'group_count',
    'wh51.ch13.signal': 'group_count',
    'wh51.ch14.signal': 'group_count',
    'wh51.ch15.signal': 'group_count',
    'wh51.ch16.signal': 'group_count',
    'wh54.ch1.signal': 'group_count',
    'wh54.ch2.signal': 'group_count',
    'wh54.ch3.signal': 'group_count',
    'wh54.ch4.signal': 'group_count',
    'wh55.ch1.signal': 'group_count',
    'wh55.ch2.signal': 'group_count',
    'wh55.ch3.signal': 'group_count',
    'wh55.ch4.signal': 'group_count',
    'wh57.signal': 'group_count',
    'wh65.signal': 'group_count',
    'wh68.signal': 'group_count',
    'wh69.signal': 'group_count',
    'ws80.signal': 'group_count',
    'ws85.signal': 'group_count',
    'ws90.signal': 'group_count',
    'ws85.version': 'group_count',
    'ws90.version': 'group_count',
    'radcompensation': 'group_count',
    'upgrade': 'group_count',
    'newVersion': 'group_count',
    'wn20.rssi': 'group_db',
    'wh24.rssi': 'group_db',
    'wh25.rssi': 'group_db',
    'wh26.rssi': 'group_db',
    'wn32.rssi': 'group_db',
    'wn32p.rssi': 'group_db',
    'wn31.ch1.rssi': 'group_db',
    'wn31.ch2.rssi': 'group_db',
    'wn31.ch3.rssi': 'group_db',
    'wn31.ch4.rssi': 'group_db',
    'wn31.ch5.rssi': 'group_db',
    'wn31.ch6.rssi': 'group_db',
    'wn31.ch7.rssi': 'group_db',
    'wn31.ch8.rssi': 'group_db',
    'wn34.ch1.rssi': 'group_db',
    'wn34.ch2.rssi': 'group_db',
    'wn34.ch3.rssi': 'group_db',
    'wn34.ch4.rssi': 'group_db',
    'wn34.ch5.rssi': 'group_db',
    'wn34.ch6.rssi': 'group_db',
    'wn34.ch7.rssi': 'group_db',
    'wn34.ch8.rssi': 'group_db',
    'wn35.ch1.rssi': 'group_db',
    'wn35.ch2.rssi': 'group_db',
    'wn35.ch3.rssi': 'group_db',
    'wn35.ch4.rssi': 'group_db',
    'wn35.ch5.rssi': 'group_db',
    'wn35.ch6.rssi': 'group_db',
    'wn35.ch7.rssi': 'group_db',
    'wn35.ch8.rssi': 'group_db',
    'wh40.rssi': 'group_db',
    'wh41.ch1.rssi': 'group_db',
    'wh41.ch2.rssi': 'group_db',
    'wh41.ch3.rssi': 'group_db',
    'wh41.ch4.rssi': 'group_db',
    'wh45.rssi': 'group_db',
    'wh51.ch1.rssi': 'group_db',
    'wh51.ch2.rssi': 'group_db',
    'wh51.ch3.rssi': 'group_db',
    'wh51.ch4.rssi': 'group_db',
    'wh51.ch5.rssi': 'group_db',
    'wh51.ch6.rssi': 'group_db',
    'wh51.ch7.rssi': 'group_db',
    'wh51.ch8.rssi': 'group_db',
    'wh51.ch9.rssi': 'group_db',
    'wh51.ch10.rssi': 'group_db',
    'wh51.ch11.rssi': 'group_db',
    'wh51.ch12.rssi': 'group_db',
    'wh51.ch13.rssi': 'group_db',
    'wh51.ch14.rssi': 'group_db',
    'wh51.ch15.rssi': 'group_db',
    'wh51.ch16.rssi': 'group_db',
    'wh54.ch1.rssi': 'group_db',
    'wh54.ch2.rssi': 'group_db',
    'wh54.ch3.rssi': 'group_db',
    'wh54.ch4.rssi': 'group_db',
    'wh55.ch1.rssi': 'group_db',
    'wh55.ch2.rssi': 'group_db',
    'wh55.ch3.rssi': 'group_db',
    'wh55.ch4.rssi': 'group_db',
    'wh57.rssi': 'group_db',
    'wh65.rssi': 'group_db',
    'wh68.rssi': 'group_db',
    'wh69.rssi': 'group_db',
    'ws80.rssi': 'group_db',
    'ws85.rssi': 'group_db',
    'ws90.rssi': 'group_db',
}


# ============================================================================
#                            InvertibleMap classes
#
# Based on the implementation of an invertible (bijective) map at
# https://stackoverflow.com/a/34460187
# ============================================================================

class InvertibleSetError(Exception):
    """Must set a unique value in a InvertibleMap."""

    def __init__(self, value):
        self.value = value
        msg = 'The value "{}" is already in the mapping.'
        super().__init__(msg.format(value))


class InvertibleMap(dict):
    """Class implementing a basic invertible map.

    An invertible map operates as per a normal python dictionary. However,
    unlike a dictionary an InvertibleMap object can look up a dictionary key
    given the value for that key. This 'reverse lookup' is achieved by using
    the InvertibleMap objects 'inverse' property and the value concerned.

    For example, if inv_map is created from the dictionary my_dict as follows:

    my_dict = {'a': 1, 'b': 2, 'c': 3}
    inv_map = InvertibleMap(my_dict)

    then the following expressions return the values indicated:

    inv_map['a']
    1
    inv_map['b']
    2
    inv_map.inverse[2]
    b
    inv_map.inverse[3]
    c

    This means that an InvertibleDict object must have not only unique keys,
    but must have unique values as well. An InvertibleMap object supports all
    standard dictionary methods and properties.
    """

    def __init__(self, *args, inverse=None, **kwargs):
        super().__init__(*args, **kwargs)
        if inverse is None:
            _inv = dict()
            for key, value in self.items():
                _inv[value] = key
            inverse = self.__class__(_inv, inverse=self, **kwargs)
        self.inverse = inverse

    def __setitem__(self, key, value):
        if value in self.inverse:
            raise InvertibleSetError(value)

        self.inverse._set_item(value, key)
        self._set_item(key, value)

    def __delitem__(self, key):
        self.inverse._del_item(self[key])
        self._del_item(key)

    def _del_item(self, key):
        super().__delitem__(key)

    def _set_item(self, key, value):
        super().__setitem__(key, value)

    def pop(self, key):
        self.inverse._del_item(self[key])
        return super().pop(key)


# ============================================================================
#                 Ecowitt Local HTTP API driver error classes
# ============================================================================

class ServiceInitializationError(Exception):
    """Exception raised during initialization of an EcowittHttpService object."""

class UnknownApiCommand(Exception):
    """Exception raised when an unknown API command was selected."""


class DeviceIOError(Exception):
    """Exception raised when an input/output error with the device is
    encountered."""


class ParseError(Exception):
    """Exception raised when an error occurs parsing an Ecowitt HTTP API
    response."""


class ProcessorError(Exception):
    """Exception raised when an error occurs processing an Ecowitt HTTP API
    response."""


class UnitError(Exception):
    """Exception raised when an error occurs determining the unit used by an
    observation."""


class CatchupObjectError(Exception):
    """Exception raised when an Ecowitt catchup object cannot be obtained."""


class InvalidApiResponseError(Exception):
    """Exception raised when an invalid API response is received."""


class ApiResponseError(Exception):
    """Exception raised when an API response error code is received."""


# ============================================================================
#                             class DebugOptions
# ============================================================================

class DebugOptions:
    """Class to simplify use and handling of device debug options."""

    debug_groups = ('rain', 'wind', 'lightning', 'loop', 'sensors', 'parser',
                    'catchup', 'collector', 'archive')

    def __init__(self, **config):
        # get any specific debug settings
        # first get the list of debug options from the config
        debug_list = weeutil.weeutil.option_as_list(config.get('debug',
                                                               list()))
        try:
            lower_debug_list = [d.lower() for d in debug_list]
        except AttributeError:
            lower_debug_list = list()
        # rain
        self._debug_rain = 'rain' in lower_debug_list
        # wind
        self._debug_wind = 'wind' in lower_debug_list
        # lightning
        self._debug_lightning = 'lightning' in lower_debug_list
        # loop data
        self._debug_loop = 'loop' in lower_debug_list
        # sensors
        self._debug_sensors = 'sensors' in lower_debug_list
        # parser
        self._debug_parser = 'parser' in lower_debug_list
        # catchup
        self._debug_catchup = 'catchup' in lower_debug_list
        # collector
        self._debug_collector = 'collector' in lower_debug_list
        # archive
        self._debug_archive = 'archive' in lower_debug_list

    @property
    def rain(self):
        """Are we debugging rain data processing."""

        return self._debug_rain

    @property
    def wind(self):
        """Are we debugging wind data processing."""

        return self._debug_wind

    @property
    def lightning(self):
        """Are we debugging lightning data processing."""

        return self._debug_lightning

    @property
    def loop(self):
        """Are we debugging loop data processing."""

        return self._debug_loop

    @property
    def sensors(self):
        """Are we debugging sensor processing."""

        return self._debug_sensors

    @property
    def parser(self):
        """Are we debugging the parser."""

        return self._debug_parser

    @property
    def catchup(self):
        """Are we debugging the catchup."""

        return self._debug_catchup

    @property
    def collector(self):
        """Are we debugging the collector."""

        return self._debug_collector

    @property
    def archive(self):
        """Are we debugging the archive."""

        return self._debug_archive


    @property
    def any(self):
        """Are we performing any debugging."""

        for debug_group in self.debug_groups:
            if getattr(self, debug_group):
                return True
        return False


# ============================================================================
#                              class FieldMapper
# ============================================================================

class FieldMapper:
    """Base class for mapping of dictionary data to new fields.

    Mapping of dictionary data is required to, for example, translate API field
    names to WeeWX archive field names. Field maps are defined in a config
    stanza as follows:

    [field_map]
        destination field = source field

    where:

        source field is the source field, if the source field data exists in a
        record the source field must be a key in the source data dict

        destination field is the destination field, if corresponding valid
        source field data exists the destination field will be a key in the
        mapped data dict

    The field map definition is contained in the field_map key in the config
    dict passed to the FieldMapper initialisation.

    A FieldMapper object also supports extensions to a field map. Field map
    extensions are identical to map definitions; however, field map extensions
    are used to extend/change an existing field map rather than define a new
    field map. Field map extensions are defined in a config stanza as follows:

    [field_map_extensions]
        destination field = source field

    where:

        source field is the source field, if the source field data exists in a
        record the source field must be a key in the source data dict

        destination field is the destination field, if corresponding valid
        source field data exists the destination field will be a key in the
        mapped data dict

    Field map extensions are not additive, that is, field map extensions
    definitions will change the mapping for a given source field rather than
    adding an additional mapping for that source field. In other words, a
    source field can only be mapped to a single destination field.

    Parameters:

        default_map: optional dict containing the default field map to be used
                     if no field map is provided
        debug: optional DebugOptions object containing debug options
        mapper_config: optional dict containing, among others, the field map and
                       field map extensions definitions
    """

    def __init__(self, driver_debug=None, default_map=None, **mapper_config):
        """Initialise a FieldMapper object."""

        # save our driver debug options
        self.driver_debug = driver_debug
        # Depending on the model a WN32 TH sensor can override/provide indoor
        # and/or outdoor TH data and outdoor pressure data to the device. The
        # use of WN32 data by the device is transparent to the driver does not
        # need to know what type of sensor (WN32 or something else) is
        # providing this data. However, in terms of battery state the driver
        # needs to know the sensor type so that sensor battery and signal state
        # data can be reported against the correct sensor type.
        self.wn32_indoor = weeutil.weeutil.tobool(mapper_config.get('wn32_indoor', False))
        self.wn32_outdoor = weeutil.weeutil.tobool(mapper_config.get('wn32_outdoor', False))
        # obtain the default map we are to use
        def_map = default_map if default_map is not None else dict()
        # construct my field map
        self.field_map = self.construct_field_map(def_map=def_map,
                                                  **mapper_config)

    def construct_field_map(self, def_map, **config):
        """Construct a field map given a default field map and field map config.

        Returns a field map as defined by the field map definition and then
        modified by the field map extensions definition. If no field map
        definition exists the default map modified by the field map extensions
        definition is returned. If no field map or field map extensions
        definitions exist the default map is returned.

        Returns an InvertibleMap object.

    default_sensor_state_map = {
        'wh25_batt': 'wh25.battery',
        'wh25_sig': 'wh25.signal',
        'wh26_batt': 'wh26.battery',
        'wh26_sig': 'wh26.signal',
        'wn31_ch1_batt': 'wn31.ch1.battery',
        'wn31_ch1_sig': 'wn31.ch1.signal',



        """

        # Update the default map given the wn32 indoor/outdoor config. First
        # make sure the default map is an InvertibleMap object.
        default_map = InvertibleMap(def_map)
        # do we have an indoor WN32, if so update any WH25 battery and signal
        # mappings to reflect the WN32
        if self.wn32_indoor:
            # we have a WN32 indoor, iterate over the source fields for which
            # we need to change the mapped dest field
            for source in ('wh25.battery', 'wh25.signal'):
                # is the source field in the default map
                if source in default_map.values():
                    # the source field is in the default map, obtain the
                    # current dest field
                    dest_field = default_map.inverse[source]
                    # remove the current source field mapping
                    _ = default_map.pop(dest_field)
                    # construct the new dest field name, it is a simple
                    # substitution in the old dest field name
                    new_dest_field = dest_field.replace('wh25', 'wn32')
                    # add the new mapping using the new dest field
                    default_map[new_dest_field] = source
        # do we have an outdoor WN32 (a WN32P), if so update any WH26 battery
        # and signal mappings to reflect the WN32P
        if self.wn32_outdoor:
            # we have a WN32P outdoor, iterate over the source fields for which
            # we need to change the mapped dest field
            for source in ('wh26.battery', 'wh26.signal'):
                # is the source field in the default map
                if source in default_map.values():
                    # the source field is in the default map, obtain the
                    # current dest field
                    dest_field = default_map.inverse[source]
                    # remove the current source field mapping
                    _ = default_map.pop(dest_field)
                    # construct the new dest field name, it is a simple
                    # substitution in the old dest field name
                    new_dest_field = dest_field.replace('wh26', 'wn32p')
                    # add the new mapping using the new dest field
                    default_map[new_dest_field] = source
        # obtain the map from our config
        field_map = config.get('field_map')
        # if no map was provided use the default
        if field_map is None:
            field_map = dict(default_map)

        # If a user wishes to map a device field differently to that in the
        # default map they can include an entry in field_map_extensions, but if
        # we just update the field map dict with the field map extensions that
        # will leave two entries for that device field in the field map; the
        # original field map entry as well as the entry from the extended map.
        # So if we have field_map_extensions we need to first go through the
        # field map and delete any entries that map device fields that are
        # included in the field_map_extensions.

        # obtain any field map extensions from our config
        extensions = config.get('field_map_extensions', {})
        # we only need process the field_map_extensions if we have any
        if len(extensions) > 0:
            # first make a copy of the field map because we will be iterating
            # over it and likely changing it
            field_map_copy = dict(field_map)
            # iterate over each key, value pair in the copy of the field map
            for k, v in field_map_copy.items():
                # if the 'value' (ie the device field) is in the field map
                # extensions we will be mapping that device field elsewhere so
                # pop that field map entry out of the field map so we don't end
                # up with multiple mappings for a device field
                if v in extensions.values():
                    # pop the field map entry
                    _dummy = field_map.pop(k)
            # now we can update the field map with the extensions
            field_map.update(extensions)
        # we now have our final field map, ensuring it is an InvertibleMap
        return InvertibleMap(field_map)

    def map_data(self, rec, unit_system=None):
        """Map a dict of data according to the field map.

        Use the field map to map a packet of data. Typically used to produce a
        WeeWX loop packet.

        rec:         dict of source data to be mapped
        unit_system: optional unit system value to be included in the mapped
                     data 'usUnits' field. Note will override any source
                     data/field mapping that would result in source data being
                     mapped to the 'usUnits' field.
        """

        if self.field_map is not None and len(self.field_map) > 0:
            # we have a field map

            # initialise a empty dict to hold the mapped data
            mapped_data = {}
            # iterate over each of the key, value pairs in the field map
            for dest_field, source_field in self.field_map.items():
                # if the field to be mapped exists in the data obtain its
                # value and map it to the packet
                if source_field in rec:
                    mapped_data[dest_field] = rec.get(source_field)
            # now add the unit_system value to field 'usUnits' if it was provided
            if unit_system is not None:
                mapped_data['usUnits'] = unit_system
            # return the mapped data
            return mapped_data
        else:
            # we have no useful field map so just return the data as is
            return rec


# ============================================================================
#                              class HttpMapper
# ============================================================================

class HttpMapper(FieldMapper):
    """Class for mapping data obtained from a device using the HTTP API.

    The HttpMapper uses a dictionary based map to map 'dotted' HTTP API fields
    to loop packet fields emitted by the Ecowitt HTTP driver/service. The map
    is produced as follows:

    - the base map is obtained from the 'default_map' initialisation parameter
      if non-None, otherwise the HttpMapper.default_map map is used as the base
      map
    - if the initialisation dict contains a 'field_map' entry the base map is
      replaced with the initialisation dict 'field_map'
    - if the initialisation dict contains a 'field_map_extensions' entry the
      base map is extended by updating it with the initialisation dict
      'field_map_extensions'

    Construction of the field map is handled by my super class initialisation.

    The resulting map must contain the map entry 'dateTime': 'datetime'. If
    this entry is missing, or the field names altered in the final map, the
    entry is removed (if applicable) and the map entry 'dateTime': 'datetime'
    inserted.

    The default field map (HttpMapper.default_map) is constructed from a number
    of modular maps to facilitate easier debug logging. The default map is used
    as the base map for mapping of HTTP API sensor data to WeeWX loop packet
    fields. Field names in the WeeWX wview_extended schema are used where there
    is a direct correlation to the WeeWX wview_extended schema or
    weewx.units.obs_group_dict (eg outTemp). If there is a related but
    different field in the wview_extended schema then a WeeWX field name with a
    similar format is used (eg extraTemp9). Otherwise, a suitable unique name
    is used.

    Field map format is:

        WeeWX field name: Device field name
    """

    # modular observation map
    default_obs_map = {
        'inTemp': 'wh25.intemp',
        'inHumidity': 'wh25.inhumi',
        'pressure': 'wh25.abs',
        'barometer': 'wh25.rel',
        'outTemp': 'common_list.0x02.val',
        'dewpoint': 'common_list.0x03.val',
        'feelslike': 'common_list.3.val',
        'appTemp': 'common_list.4.val',
        'vpd': 'common_list.5.val',
        'outHumidity': 'common_list.0x07.val',
        'radiation': 'common_list.0x15.val',
        'uvradiation': 'common_list.0x16.val',
        'UV': 'common_list.0x17.val',
        'lightning_dist': 'lightning.distance',
        'lightning_disturber_count': 'lightning.timestamp',
        'lightning_num': 'lightning.num',
        'lightningcount': 'lightning.count',
        'lightning_strike_count': 'lightning.count',
        'extraTemp1': 'ch_aisle.1.temp',
        'extraTemp2': 'ch_aisle.2.temp',
        'extraTemp3': 'ch_aisle.3.temp',
        'extraTemp4': 'ch_aisle.4.temp',
        'extraTemp5': 'ch_aisle.5.temp',
        'extraTemp6': 'ch_aisle.6.temp',
        'extraTemp7': 'ch_aisle.7.temp',
        'extraTemp8': 'ch_aisle.8.temp',
        'extraHumid1': 'ch_aisle.1.humidity',
        'extraHumid2': 'ch_aisle.2.humidity',
        'extraHumid3': 'ch_aisle.3.humidity',
        'extraHumid4': 'ch_aisle.4.humidity',
        'extraHumid5': 'ch_aisle.5.humidity',
        'extraHumid6': 'ch_aisle.6.humidity',
        'extraHumid7': 'ch_aisle.7.humidity',
        'extraHumid8': 'ch_aisle.8.humidity',
        'soilTemp1': 'ch_temp.1.temp',
        'soilTemp2': 'ch_temp.2.temp',
        'soilTemp3': 'ch_temp.3.temp',
        'soilTemp4': 'ch_temp.4.temp',
        'soilTemp5': 'ch_temp.5.temp',
        'soilTemp6': 'ch_temp.6.temp',
        'soilTemp7': 'ch_temp.7.temp',
        'soilTemp8': 'ch_temp.8.temp',
        'co2in': 'wh25.CO2',
        'co2in_24h': 'wh25.CO2_24H',
        'co2': 'co2.CO2',
        'co2_24h': 'co2.CO2_24H',
        'co2_Temp': 'co2.temp',
        'co2_Hum': 'co2.humidity',
        'pm2_5': 'co2.PM25',
        'pm25_24h_co2': 'co2.PM25_24H',
        'pm25_RealAQI_co2': 'co2.PM25_RealAQI',
        'pm25_24hAQI_co2': 'co2.PM25_24HAQI',
        'pm10_0': 'co2.PM10',
        'pm10_24h_co2': 'co2.PM10_24H',
        'pm10_RealAQI_co2': 'co2.PM10_RealAQI',
        'pm10_24hAQI_co2': 'co2.PM10_24HAQI',
        'pm1_0': 'co2.PM1',
        'pm1_24h_co2': 'co2.PM1_24H',
        'pm1_RealAQI_co2': 'co2.PM1_RealAQI',
        'pm1_24hAQI_co2': 'co2.PM1_24HAQI',
        'pm4_0': 'co2.PM4',
        'pm4_24h_co2': 'co2.PM4_24H',
        'pm4_RealAQI_co2': 'co2.PM4_RealAQI',
        'pm4_24hAQI_co2': 'co2.PM4_24HAQI',
        'pm25_1': 'ch_pm25.1.PM25',
        'pm25_avg_24h_ch1': 'ch_pm25.1.PM25_24H',
        'pm25_RealAQI_ch1': 'ch_pm25.1.PM25_RealAQI',
        'pm25_AQI_24h_ch1': 'ch_pm25.1.PM25_24HAQI',
        'pm25_2': 'ch_pm25.2.PM25',
        'pm25_avg_24h_ch2': 'ch_pm25.2.PM25_24H',
        'pm25_RealAQI_ch2': 'ch_pm25.2.PM25_RealAQI',
        'pm25_AQI_24h_ch2': 'ch_pm25.2.PM25_24HAQI',
        'pm25_3': 'ch_pm25.3.PM25',
        'pm25_avg_24h_ch3': 'ch_pm25.3.PM25_24H',
        'pm25_RealAQI_ch3': 'ch_pm25.3.PM25_RealAQI',
        'pm25_AQI_24h_ch3': 'ch_pm25.3.PM25_24HAQI',
        'pm25_4': 'ch_pm25.4.PM25',
        'pm25_avg_24h_ch4': 'ch_pm25.4.PM25_24H',
        'pm25_RealAQI_ch4': 'ch_pm25.4.PM25_RealAQI',
        'pm25_AQI_24h_ch4': 'ch_pm25.4.PM25_24HAQI',
        'soilMoist1': 'ch_soil.1.humidity',
        'soilMoist2': 'ch_soil.2.humidity',
        'soilMoist3': 'ch_soil.3.humidity',
        'soilMoist4': 'ch_soil.4.humidity',
        'soilMoist5': 'ch_soil.5.humidity',
        'soilMoist6': 'ch_soil.6.humidity',
        'soilMoist7': 'ch_soil.7.humidity',
        'soilMoist8': 'ch_soil.8.humidity',
        'soilMoist9': 'ch_soil.9.humidity',
        'soilMoist10': 'ch_soil.10.humidity',
        'soilMoist11': 'ch_soil.11.humidity',
        'soilMoist12': 'ch_soil.12.humidity',
        'soilMoist13': 'ch_soil.13.humidity',
        'soilMoist14': 'ch_soil.14.humidity',
        'soilMoist15': 'ch_soil.15.humidity',
        'soilMoist16': 'ch_soil.16.humidity',
        'leafWet1': 'ch_leaf.1.humidity',
        'leafWet2': 'ch_leaf.2.humidity',
        'leafWet3': 'ch_leaf.3.humidity',
        'leafWet4': 'ch_leaf.4.humidity',
        'leafWet5': 'ch_leaf.5.humidity',
        'leafWet6': 'ch_leaf.6.humidity',
        'leafWet7': 'ch_leaf.7.humidity',
        'leafWet8': 'ch_leaf.8.humidity',
        'leak_1': 'ch_leak.1.status',
        'leak_2': 'ch_leak.2.status',
        'leak_3': 'ch_leak.3.status',
        'leak_4': 'ch_leak.4.status',
        'thi_ch1': 'ch_lds.1.air',
        'thi_ch2': 'ch_lds.2.air',
        'thi_ch3': 'ch_lds.3.air',
        'thi_ch4': 'ch_lds.4.air',
        'depth_ch1': 'ch_lds.1.depth',
        'depth_ch2': 'ch_lds.2.depth',
        'depth_ch3': 'ch_lds.3.depth',
        'depth_ch4': 'ch_lds.4.depth',
        'ldsheat_ch1': 'ch_lds.1.total_heat',
        'ldsheat_ch2': 'ch_lds.2.total_heat',
        'ldsheat_ch3': 'ch_lds.3.total_heat',
        'ldsheat_ch4': 'ch_lds.4.total_heat',
        'height_ch1': 'ch_lds.1.total_height',
        'height_ch2': 'ch_lds.2.total_height',
        'height_ch3': 'ch_lds.3.total_height',
        'height_ch4': 'ch_lds.4.total_height',
        'heap': 'debug.heap',
        'runtime': 'debug.runtime',
        'ws_interval': 'debug.usr_interval',

        'radcompensation': 'radcompensation',
        'upgrade': 'upgrade',
        'newVersion': 'newVersion',

        'rain_source': 'rain_priority',
        'rain_day_reset': 'rain_reset_day',
        'rain_week_reset': 'rain_reset_week',
        'rain_annual_reset': 'rain_reset_year',
        'piezo': 'rain_piezo',
        'raingain': 'rain_gain',
        'gain0': 'gain1',
        'gain1': 'gain2',
        'gain2': 'gain3',
        'gain3': 'gain4',
        'gain4': 'gain5',

        'soilad1': 'cli_soilad_ch1.nowAd',
        'soilad2': 'cli_soilad_ch2.nowAd',
        'soilad3': 'cli_soilad_ch3.nowAd',
        'soilad4': 'cli_soilad_ch4.nowAd',
        'soilad5': 'cli_soilad_ch5.nowAd',
        'soilad6': 'cli_soilad_ch6.nowAd',
        'soilad7': 'cli_soilad_ch7.nowAd',
        'soilad8': 'cli_soilad_ch8.nowAd',
        'soilad9': 'cli_soilad_ch9.nowAd',
        'soilad10': 'cli_soilad_ch10.nowAd',
        'soilad11': 'cli_soilad_ch11.nowAd',
        'soilad12': 'cli_soilad_ch12.nowAd',
        'soilad13': 'cli_soilad_ch13.nowAd',
        'soilad14': 'cli_soilad_ch14.nowAd',
        'soilad15': 'cli_soilad_ch15.nowAd',
        'soilad16': 'cli_soilad_ch16.nowAd',

    }
    # modular rain map
    default_rain_map = {
        #'t_rainevent': 'rain.0x0D.val',
        #'t_rainRate': 'rain.0x0E.val',
        #'t_rainhour': 't_rainhour',
        #'t_rainday': 'rain.0x10.val',
        #'t_rainweek': 'rain.0x11.val',
        #'t_rainmonth': 'rain.0x12.val',
        't_rain': 'rain.0x0D.val',
        't_rainRate': 'rain.0x0E.val',
        't_rainyear': 'rain.0x13.val',
        'eventRain': 'rain.0x0D.val',
        'rainRate': 'rain.0x0E.val',
        'hourRain': 'rain.0x0F.val',
        'dayRain': 'rain.0x10.val',
        'weekRain': 'rain.0x11.val',
        'monthRain': 'rain.0x12.val',
        'yearRain': 'rain.0x13.val',
        't_rainyear': 'rain.0x13.val',
        'rain24': 'rain.0x7C.val',
        #'p_rainevent': 'piezoRain.0x0D.val',
        #'p_rainrate': 'piezoRain.0x0E.val',
        #'p_rainhour': 'p_rainhour',
        #'p_rainday': 'piezoRain.0x10.val',
        #'p_rainweek': 'piezoRain.0x11.val',
        #'p_rainmonth': 'piezoRain.0x12.val',
        'srain_piezo': 'piezoRain.srain_piezo.val',
        #'p_rain': 'piezoRain.0x0D.val',
        'p_rainrate': 'piezoRain.0x0E.val',
        'p_rainyear': 'piezoRain.0x13.val',
        'erain_piezo': 'piezoRain.0x0D.val',
        'rrain_piezo': 'piezoRain.0x0E.val',
        'hailRate': 'piezoRain.0x0E.val',
        'hrain_piezo': 'piezoRain.0x1F.val',
        'drain_piezo': 'piezoRain.0x10.val',
        'wrain_piezo': 'piezoRain.0x11.val',
        'mrain_piezo': 'piezoRain.0x12.val',
        'yrain_piezo': 'piezoRain.0x13.val',
        'rain24_piezo': 'piezoRain.0x7C.val',
    }
    # modular wind map
    default_wind_map = {
        'windDir': 'common_list.0x0A.val',
        'windDir10': 'common_list.0x6D.val',
        'windSpeed': 'common_list.0x0B.val',
        'windGust': 'common_list.0x0C.val',
        'maxdailygust': 'common_list.0x19.val',
    }
    # modular sensor state map
    default_sensor_state_map = {
        'inTempBatteryStatus': 'wh25.battery',
        'outTempBatteryStatus': 'wh65.battery',
        'wn20_batt': 'wn20.battery',
        'wh25_batt': 'wh25.battery',
        'wh26_batt': 'wh26.battery',
        'batteryStatus1': 'wn31.ch1.battery',
        'batteryStatus2': 'wn31.ch2.battery',
        'batteryStatus3': 'wn31.ch3.battery',
        'batteryStatus4': 'wn31.ch4.battery',
        'batteryStatus5': 'wn31.ch5.battery',
        'batteryStatus6': 'wn31.ch6.battery',
        'batteryStatus7': 'wn31.ch7.battery',
        'batteryStatus8': 'wn31.ch8.battery',
        'soilTempBatt1s': 'wn34.ch1.battery',
        'soilTempBatt2s': 'wn34.ch2.battery',
        'soilTempBatt3s': 'wn34.ch3.battery',
        'soilTempBatt4s': 'wn34.ch4.battery',
        'soilTempBatt5s': 'wn34.ch5.battery',
        'soilTempBatt6s': 'wn34.ch6.battery',
        'soilTempBatt7s': 'wn34.ch7.battery',
        'soilTempBatt8s': 'wn34.ch8.battery',
        'pm25_Batt1': 'wh41.ch1.battery',
        'pm25_Batt2': 'wh41.ch2.battery',
        'pm25_Batt3': 'wh41.ch3.battery',
        'pm25_Batt4': 'wh41.ch4.battery',
        'soilMoistBatt1s': 'wh51.ch1.battery',
        'soilMoistBatt2s': 'wh51.ch2.battery',
        'soilMoistBatt3s': 'wh51.ch3.battery',
        'soilMoistBatt4s': 'wh51.ch4.battery',
        'soilMoistBatt5s': 'wh51.ch5.battery',
        'soilMoistBatt6s': 'wh51.ch6.battery',
        'soilMoistBatt7s': 'wh51.ch7.battery',
        'soilMoistBatt8s': 'wh51.ch8.battery',
        'soilMoistBatt9s': 'wh51.ch9.battery',
        'soilMoistBatt10s': 'wh51.ch10.battery',
        'soilMoistBatt11s': 'wh51.ch11.battery',
        'soilMoistBatt12s': 'wh51.ch12.battery',
        'soilMoistBatt13s': 'wh51.ch13.battery',
        'soilMoistBatt14s': 'wh51.ch14.battery',
        'soilMoistBatt15s': 'wh51.ch15.battery',
        'soilMoistBatt16s': 'wh51.ch16.battery',
        'co2_Batt': 'co2.battery',
        'wh40_batt': 'wh40.battery',
        'wn20_batt': 'wn20.battery',

        'leak_Batt1': 'wh55.ch1.battery',
        'leak_Batt2': 'wh55.ch2.battery',
        'leak_Batt3': 'wh55.ch3.battery',
        'leak_Batt4': 'wh55.ch4.battery',
        'lightning_Batt': 'wh57.battery',

        'soilTempBatt1': 'ch_temp.1.voltage',
        'soilTempBatt2': 'ch_temp.2.voltage',
        'soilTempBatt3': 'ch_temp.3.voltage',
        'soilTempBatt4': 'ch_temp.4.voltage',
        'soilTempBatt5': 'ch_temp.5.voltage',
        'soilTempBatt6': 'ch_temp.6.voltage',
        'soilTempBatt7': 'ch_temp.7.voltage',
        'soilTempBatt8': 'ch_temp.8.voltage',
        'soilMoistBatt1': 'ch_soil.1.voltage',
        'soilMoistBatt2': 'ch_soil.2.voltage',
        'soilMoistBatt3': 'ch_soil.3.voltage',
        'soilMoistBatt4': 'ch_soil.4.voltage',
        'soilMoistBatt5': 'ch_soil.5.voltage',
        'soilMoistBatt6': 'ch_soil.6.voltage',
        'soilMoistBatt7': 'ch_soil.7.voltage',
        'soilMoistBatt8': 'ch_soil.8.voltage',
        'soilMoistBatt9': 'ch_soil.9.voltage',
        'soilMoistBatt10': 'ch_soil.10.voltage',
        'soilMoistBatt11': 'ch_soil.11.voltage',
        'soilMoistBatt12': 'ch_soil.12.voltage',
        'soilMoistBatt13': 'ch_soil.13.voltage',
        'soilMoistBatt14': 'ch_soil.14.voltage',
        'soilMoistBatt15': 'ch_soil.15.voltage',
        'soilMoistBatt16': 'ch_soil.16.voltage',
        'leafWetBatt1': 'ch_leaf.1.voltage',
        'leafWetBatt2': 'ch_leaf.2.voltage',
        'leafWetBatt3': 'ch_leaf.3.voltage',
        'leafWetBatt4': 'ch_leaf.4.voltage',
        'leafWetBatt5': 'ch_leaf.5.voltage',
        'leafWetBatt6': 'ch_leaf.6.voltage',
        'leafWetBatt7': 'ch_leaf.7.voltage',
        'leafWetBatt8': 'ch_leaf.8.voltage',
        'ldsbatt1': 'ch_lds.1.voltage',
        'ldsbatt2': 'ch_lds.2.voltage',
        'ldsbatt3': 'ch_lds.3.voltage',
        'ldsbatt4': 'ch_lds.4.voltage',
        'wh68_batt': 'wh68.battery',
        'wh69_batt': 'wh69.battery',
        'wh80_batt': 'ws80.battery',
        'wh85_batt': 'ws85.battery',
        'wh90_batt': 'ws90.battery',

        'ws85cap_volt': 'ws85.capvoltage',
        'ws90cap_volt': 'ws90.capvoltage',

        'ws80_batt': 'ws80.voltage',
        'ws85_batt': 'ws85.voltage',
        'ws90_batt': 'piezoRain.0x13.voltage',
        'rainBatteryStatus': 'rain.0x13.voltage',
        'hailBatteryStatus': 'piezoRain.0x13.voltage',
        'windBatteryStatus': 'ws80.voltage',

        'consBatteryVoltage': 'wh25.console_batt',
        'ws1900batt': 'wh25.ws1900_batt',
        'ws1800batt': 'wh25.ws1800_batt',
        'ws6006batt': 'wh25.ws6006_batt',

        'ws85_ver': 'ws85.version',
        'ws90_ver': 'ws90.version',

        'wn20_sig': 'wn20.signal',
        'wh25_sig': 'wh25.signal',
        'wh26_sig': 'wh26.signal',
        'wn31_ch1_sig': 'wn31.ch1.signal',
        'wn31_ch2_sig': 'wn31.ch2.signal',
        'wn31_ch3_sig': 'wn31.ch3.signal',
        'wn31_ch4_sig': 'wn31.ch4.signal',
        'wn31_ch5_sig': 'wn31.ch5.signal',
        'wn31_ch6_sig': 'wn31.ch6.signal',
        'wn31_ch7_sig': 'wn31.ch7.signal',
        'wn31_ch8_sig': 'wn31.ch8.signal',
        'wn34_ch1_sig': 'wn34.ch1.signal',
        'wn34_ch2_sig': 'wn34.ch2.signal',
        'wn34_ch3_sig': 'wn34.ch3.signal',
        'wn34_ch4_sig': 'wn34.ch4.signal',
        'wn34_ch5_sig': 'wn34.ch5.signal',
        'wn34_ch6_sig': 'wn34.ch6.signal',
        'wn34_ch7_sig': 'wn34.ch7.signal',
        'wn34_ch8_sig': 'wn34.ch8.signal',
        'wn35_ch1_sig': 'wn35.ch1.signal',
        'wn35_ch2_sig': 'wn35.ch2.signal',
        'wn35_ch3_sig': 'wn35.ch3.signal',
        'wn35_ch4_sig': 'wn35.ch4.signal',
        'wn35_ch5_sig': 'wn35.ch5.signal',
        'wn35_ch6_sig': 'wn35.ch6.signal',
        'wn35_ch7_sig': 'wn35.ch7.signal',
        'wn35_ch8_sig': 'wn35.ch8.signal',
        'wh40_sig': 'wh40.signal',
        'wh41_ch1_sig': 'wh41.ch1.signal',
        'wh41_ch2_sig': 'wh41.ch2.signal',
        'wh41_ch3_sig': 'wh41.ch3.signal',
        'wh41_ch4_sig': 'wh41.ch4.signal',
        'wh45_sig': 'co2.signal',
        'wh51_ch1_sig': 'wh51.ch1.signal',
        'wh51_ch2_sig': 'wh51.ch2.signal',
        'wh51_ch3_sig': 'wh51.ch3.signal',
        'wh51_ch4_sig': 'wh51.ch4.signal',
        'wh51_ch5_sig': 'wh51.ch5.signal',
        'wh51_ch6_sig': 'wh51.ch6.signal',
        'wh51_ch7_sig': 'wh51.ch7.signal',
        'wh51_ch8_sig': 'wh51.ch8.signal',
        'wh51_ch9_sig': 'wh51.ch9.signal',
        'wh51_ch10_sig': 'wh51.ch10.signal',
        'wh51_ch11_sig': 'wh51.ch11.signal',
        'wh51_ch12_sig': 'wh51.ch12.signal',
        'wh51_ch13_sig': 'wh51.ch13.signal',
        'wh51_ch14_sig': 'wh51.ch14.signal',
        'wh51_ch15_sig': 'wh51.ch15.signal',
        'wh51_ch16_sig': 'wh51.ch16.signal',
        'wh54_ch1_sig': 'wh54.ch1.signal',
        'wh54_ch2_sig': 'wh54.ch2.signal',
        'wh54_ch3_sig': 'wh54.ch3.signal',
        'wh54_ch4_sig': 'wh54.ch4.signal',
        'wh55_ch1_sig': 'wh55.ch1.signal',
        'wh55_ch2_sig': 'wh55.ch2.signal',
        'wh55_ch3_sig': 'wh55.ch3.signal',
        'wh55_ch4_sig': 'wh55.ch4.signal',

        'wh57_sig': 'wh57.signal',
        'wh68_sig': 'wh68.signal',
        'wh69_sig': 'wh69.signal',
        'ws80_sig': 'ws80.signal',
        'ws85_sig': 'ws85.signal',
        'ws90_sig': 'ws90.signal',

        'wn20_rssi': 'wn20.rssi',
        'wh25_rssi': 'wh25.rssi',
        'wh26_rssi': 'wh26.rssi',
        'wn31_ch1_rssi': 'wn31.ch1.rssi',
        'wn31_ch2_rssi': 'wn31.ch2.rssi',
        'wn31_ch3_rssi': 'wn31.ch3.rssi',
        'wn31_ch4_rssi': 'wn31.ch4.rssi',
        'wn31_ch5_rssi': 'wn31.ch5.rssi',
        'wn31_ch6_rssi': 'wn31.ch6.rssi',
        'wn31_ch7_rssi': 'wn31.ch7.rssi',
        'wn31_ch8_rssi': 'wn31.ch8.rssi',
        'wn34_ch1_rssi': 'wn34.ch1.rssi',
        'wn34_ch2_rssi': 'wn34.ch2.rssi',
        'wn34_ch3_rssi': 'wn34.ch3.rssi',
        'wn34_ch4_rssi': 'wn34.ch4.rssi',
        'wn34_ch5_rssi': 'wn34.ch5.rssi',
        'wn34_ch6_rssi': 'wn34.ch6.rssi',
        'wn34_ch7_rssi': 'wn34.ch7.rssi',
        'wn34_ch8_rssi': 'wn34.ch8.rssi',
        'wn35_ch1_rssi': 'wn35.ch1.rssi',
        'wn35_ch2_rssi': 'wn35.ch2.rssi',
        'wn35_ch3_rssi': 'wn35.ch3.rssi',
        'wn35_ch4_rssi': 'wn35.ch4.rssi',
        'wn35_ch5_rssi': 'wn35.ch5.rssi',
        'wn35_ch6_rssi': 'wn35.ch6.rssi',
        'wn35_ch7_rssi': 'wn35.ch7.rssi',
        'wn35_ch8_rssi': 'wn35.ch8.rssi',
        'wh40_rssi': 'wh40.rssi',
        'wh41_ch1_rssi': 'wh41.ch1.rssi',
        'wh41_ch2_rssi': 'wh41.ch2.rssi',
        'wh41_ch3_rssi': 'wh41.ch3.rssi',
        'wh41_ch4_rssi': 'wh41.ch4.rssi',
        'wh45_rssi': 'co2.rssi',
        'wh51_ch1_rssi': 'wh51.ch1.rssi',
        'wh51_ch2_rssi': 'wh51.ch2.rssi',
        'wh51_ch3_rssi': 'wh51.ch3.rssi',
        'wh51_ch4_rssi': 'wh51.ch4.rssi',
        'wh51_ch5_rssi': 'wh51.ch5.rssi',
        'wh51_ch6_rssi': 'wh51.ch6.rssi',
        'wh51_ch7_rssi': 'wh51.ch7.rssi',
        'wh51_ch8_rssi': 'wh51.ch8.rssi',
        'wh51_ch9_rssi': 'wh51.ch9.rssi',
        'wh51_ch10_rssi': 'wh51.ch10.rssi',
        'wh51_ch11_rssi': 'wh51.ch11.rssi',
        'wh51_ch12_rssi': 'wh51.ch12.rssi',
        'wh51_ch13_rssi': 'wh51.ch13.rssi',
        'wh51_ch14_rssi': 'wh51.ch14.rssi',
        'wh51_ch15_rssi': 'wh51.ch15.rssi',
        'wh51_ch16_rssi': 'wh51.ch16.rssi',
        'wh54_ch1_rssi': 'wh54.ch1.rssi',
        'wh54_ch2_rssi': 'wh54.ch2.rssi',
        'wh54_ch3_rssi': 'wh54.ch3.rssi',
        'wh54_ch4_rssi': 'wh54.ch4.rssi',
        'wh55_ch1_rssi': 'wh55.ch1.rssi',
        'wh55_ch2_rssi': 'wh55.ch2.rssi',
        'wh55_ch3_rssi': 'wh55.ch3.rssi',
        'wh55_ch4_rssi': 'wh55.ch4.rssi',

        'wh57_rssi': 'wh57.rssi',
        'wh68_rssi': 'wh68.rssi',
        'wh69_rssi': 'wh69.rssi',
        'ws80_rssi': 'ws80.rssi',
        'ws85_rssi': 'ws85.rssi',
        'ws90_rssi': 'ws90.rssi',

    }
    # construct the default map based on the modular maps
    default_map = (dict(default_obs_map))
    default_map.update(default_rain_map)
    default_map.update(default_wind_map)
    default_map.update(default_sensor_state_map)
    
    #DEFAULT_SENSOR_MAP = default_map

    def __init__(self, driver_debug=None, default_map=None, **mapper_config):
        """Initialise an HttpMapper object."""

        # obtain my base map, if we were passed a default map use it,
        # otherwise fall back to our default_map
        def_map = default_map if default_map is not None else HttpMapper.default_map
        # initialise my parent
        super().__init__(driver_debug=driver_debug,
                         default_map=def_map,
                         **mapper_config)
        # We must have a mapping from device field 'datetime' to the WeeWX
        # packet field 'dateTime', too many parts of the driver depend on this.
        # So check to ensure this mapping is in place as the user could have
        # removed or altered it. If the mapping is not there add it in.
        # initialise the key that maps 'datetime'
        datetime_key = None
        # iterate over the field map entries
        for k, v in self.field_map.items():
            # if the mapping is for 'datetime' save the key and break
            if v == 'datetime':
                datetime_key = k
                break
        # if we have a mapping for 'datetime' delete that field map entry
        if datetime_key:
            _ = self.field_map.pop(datetime_key)
        # add the required mapping
        self.field_map['dateTime'] = 'datetime'
        # construct the in-use rain_map
        self.rain_map = {d: s for d,s in self.field_map.items() if s in self.default_rain_map.values()}
        # construct the in-use wind_map
        self.wind_map = {d: s for d,s in self.field_map.items() if s in self.default_wind_map.values()}
        # ensure all destination (WeeWX) fields are assigned a unit group
        self.assign_unit_groups()
        # log our field map if required
        if getattr(driver_debug, 'any', False) or getattr(driver_debug, 'debug', 0) >= 1 or weewx.debug > 0:
            # The field map. Field map dict output will be in unsorted key order.
            # It is easier to read if sorted alphanumerically, but we have keys
            # such as xxxxx16 that do not sort well. Use a custom natural sort of
            # the keys in a manually produced formatted dict representation.
            log.info('     field map is %s' % natural_sort_dict(self.field_map))

    def assign_unit_groups(self):
        """Assign destination fields to a WeeWX unit group.

        To allow destination fields to be formatted and converted using the
        WeeWX machinery each obs needs to be assigned to a unit group. This is
        already the case for obs in the WeeWX schemas, however, any obs
        'created' by the driver will need to be assigned a unit group. Obs are
        assigned to a unit group by adding an entry to
        weewx.units.obs_group.dict.
        """

        # iterate over the destination (WeeWX) obs and source (Ecowitt) field
        # pairs in our map
        for w_field, e_field in self.field_map.items():
            # is there an existing entry for the WeeWX field in the
            # obs_group_dict
            if w_field not in weewx.units.obs_group_dict.keys():
                # the WeeWX field is not in the obs_group_dict so add an entry
                # for the WeeWX field using the group previously assigned to
                # the source Ecowitt field
                try:
                  weewx.units.obs_group_dict[w_field] = DEFAULT_GROUPS[e_field]
                except KeyError:
                  # there is a missing key , do nothing
                  pass


# ============================================================================
#                               class SdMapper
# ============================================================================

class SdMapper(FieldMapper):
    """Class to map SD card history file records.

    The SdMapper uses a dictionary based map to map SD card history file fields
    to 'dotted' HTTP API fields used by the Ecowitt HTTP driver/service. This
    means that two mappings must be applied to map SD card history data fields
    to WeeWX loop packet/archive record fields; however, this approach removes
    the need for any user defined/changed field mapping to be applied to
    SD card history file field mapping.

    The SD card history file field names used are a modified version of the
    actual SD card history file field names that have had any applicable
    bracketed unit information removed, eg: 'Dew Point' is used in lieu of
    'Dew Point(°C)' (or 'Dew Point(°F)')

    Field map format is:

        HTTP driver 'dotted' field name: SD card history file field name
    """

    # default map to map SD card history file fields to 'dotted' fields used by
    # the Ecowitt local HTTP API driver
    default_map = {
        #'datetime' : 'Time', 
        'wh25.intemp': 'Indoor Temperature',
        'wh25.inhumi': 'Indoor Humidity',
        'common_list.0x02.val': 'Outdoor Temperature',
        'common_list.0x07.val': 'Outdoor Humidity',
        'common_list.0x03.val': 'Dew Point',
        'feelslike': 'Feels Like',
        'common_list.5.val': 'VPD',
        'common_list.0x0B.val': 'Wind',
        'common_list.0x0C.val': 'Gust',
        'common_list.0x0A.val': 'Wind Direction',
        'wh25.abs': 'ABS Pressure',
        'wh25.rel': 'REL Pressure',
        'common_list.0x15.val': 'Solar Rad',
        'common_list.0x17.val': 'UV-Index',
        'rain.0x0E.val': 'Rain Rate',
        'rain.0x0F.val': 'Hourly Rain',
        'rain.0x0D.val': 'Event Rain',
        'rain.0x10.val': 'Daily Rain',
        'rain.0x11.val': 'Weekly Rain',
        'rain.0x12.val': 'Monthly Rain',
        'rain.0x13.val': 'Yearly Rain',
        'piezoRain.0x0E.val': 'Piezo Rate',
        'piezoRain.0x0F.val': 'Piezo Hourly Rain',
        'piezoRain.0x0D.val': 'Piezo Event Rain',
        'piezoRain.0x10.val': 'Piezo Daily Rain',
        'piezoRain.0x11.val': 'Piezo Weekly Rain',
        'piezoRain.0x12.val': 'Piezo Monthly Rain',
        'piezoRain.0x13.val': 'Piezo Yearly Rain',
        'ch_aisle.1.temp': 'CH1 Temperature',
        'dewpoint1': 'CH1 Dew point',
        'heatindex1': 'CH1 HeatIndex',
        'ch_aisle.1.humidity': 'CH1 Humidity',
        'ch_aisle.2.temp': 'CH2 Temperature',
        'dewpoint2': 'CH2 Dew point',
        'heatindex2': 'CH2 HeatIndex',
        'ch_aisle.2.humidity': 'CH2 Humidity',
        'ch_aisle.3.temp': 'CH3 Temperature',
        'dewpoint3': 'CH3 Dew point',
        'heatindex3': 'CH3 HeatIndex',
        'ch_aisle.3.humidity': 'CH3 Humidity',
        'ch_aisle.4.temp': 'CH4 Temperature',
        'dewpoint4': 'CH4 Dew point',
        'heatindex4': 'CH4 HeatIndex',
        'ch_aisle.4.humidity': 'CH4 Humidity',
        'ch_aisle.5.temp': 'CH5 Temperature',
        'dewpoint5': 'CH5 Dew point',
        'heatindex5': 'CH5 HeatIndex',
        'ch_aisle.5.humidity': 'CH5 Humidity',
        'ch_aisle.6.temp': 'CH6 Temperature',
        'dewpoint6': 'CH6 Dew point',
        'heatindex6': 'CH6 HeatIndex',
        'ch_aisle.6.humidity': 'CH6 Humidity',
        'ch_aisle.7.temp': 'CH7 Temperature',
        'dewpoint7': 'CH7 Dew point',
        'heatindex7': 'CH7 HeatIndex',
        'ch_aisle.7.humidity': 'CH7 Humidity',
        'ch_aisle.8.temp': 'CH8 Temperature',
        'dewpoint8': 'CH8 Dew point',
        'heatindex8': 'CH8 HeatIndex',
        'ch_aisle.8.humidity': 'CH8 Humidity',
        'ch_leaf.1.humidity': 'WH35 CH1hum',
        'ch_leaf.2.humidity': 'WH35 CH2hum',
        'ch_leaf.3.humidity': 'WH35 CH3hum',
        'ch_leaf.4.humidity': 'WH35 CH4hum',
        'ch_leaf.5.humidity': 'WH35 CH5hum',
        'ch_leaf.6.humidity': 'WH35 CH6hum',
        'ch_leaf.7.humidity': 'WH35 CH7hum',
        'ch_leaf.8.humidity': 'WH35 CH8hum',
        'lightning.timestamp': 'Thunder time',
        'lightning.count': 'Thunder count',
        'lightning.distance': 'Thunder distance',
        'co2.temp': 'AQIN Temperature',
        'co2.humidity': 'AQIN Humidity',
        'co2.CO2': 'AQIN CO2',
        'co2.PM25': 'AQIN PM2.5',
        'co2.PM10': 'AQIN PM10',
        'co2.PM1': 'AQIN PM1.0',
        'co2.PM4': 'AQIN PM4.0',
        'ch_soil.1.humidity': 'SoilMoisture CH1',
        'ch_soil.2.humidity': 'SoilMoisture CH2',
        'ch_soil.3.humidity': 'SoilMoisture CH3',
        'ch_soil.4.humidity': 'SoilMoisture CH4',
        'ch_soil.5.humidity': 'SoilMoisture CH5',
        'ch_soil.6.humidity': 'SoilMoisture CH6',
        'ch_soil.7.humidity': 'SoilMoisture CH7',
        'ch_soil.8.humidity': 'SoilMoisture CH8',
        'ch_soil.9.humidity': 'SoilMoisture CH9',
        'ch_soil.10.humidity': 'SoilMoisture CH10',
        'ch_soil.11.humidity': 'SoilMoisture CH11',
        'ch_soil.12.humidity': 'SoilMoisture CH12',
        'ch_soil.13.humidity': 'SoilMoisture CH13',
        'ch_soil.14.humidity': 'SoilMoisture CH14',
        'ch_soil.15.humidity': 'SoilMoisture CH15',
        'ch_soil.16.humidity': 'SoilMoisture CH16',
        'ch_leak.1.status': 'Water CH1',
        'ch_leak.2.status': 'Water CH2',
        'ch_leak.3.status': 'Water CH3',
        'ch_leak.4.status': 'Water CH4',
        'ch_pm25.1.PM25': 'PM2.5 CH1',
        'ch_pm25.2.PM25': 'PM2.5 CH2',
        'ch_pm25.3.PM25': 'PM2.5 CH3',
        'ch_pm25.4.PM25': 'PM2.5 CH4',
        'ch_temp.1.temp': 'WN34 CH1',
        'ch_temp.2.temp': 'WN34 CH2',
        'ch_temp.3.temp': 'WN34 CH3',
        'ch_temp.4.temp': 'WN34 CH4',
        'ch_temp.5.temp': 'WN34 CH5',
        'ch_temp.6.temp': 'WN34 CH6',
        'ch_temp.7.temp': 'WN34 CH7',
        'ch_temp.8.temp': 'WN34 CH8',
        'ch_lds.1.air': 'LDS_Air CH1',
        'ch_lds.1.depth': 'LDS_Depth CH1',
        'ch_lds.1.total_heat': 'LDS_Heat CH1',
        'ch_lds.2.air': 'LDS_Air CH2',
        'ch_lds.2.depth': 'LDS_Depth CH2',
        'ch_lds.2.total_heat': 'LDS_Heat CH2',
        'ch_lds.3.air': 'LDS_Air CH3',
        'ch_lds.3.depth': 'LDS_Depth CH3',
        'ch_lds.3.total_heat': 'LDS_Heat CH3',
        'ch_lds.4.air': 'LDS_Air CH4',
        'ch_lds.4.depth': 'LDS_Depth CH4',
        'ch_lds.4.total_heat': 'LDS_Heat CH4'
    }

    def __init__(self, driver_debug=None, default_map=None, **mapper_config):

        # obtain the default map to be used
        def_map = default_map if default_map is not None else SdMapper.default_map
        # initialise my super class
        super().__init__(driver_debug=driver_debug,
                         default_map=def_map,
                         **mapper_config)

    def map_data(self, rec, unit_system=None):
        """Map a packet of data according to the field map.

        The normal mapping approach is to iterate over the source fields in the
        field map and if the source field exists in the source data that field
        is mapped to the destination field in the mapped data. This approach
        will not work with SD card history data as the source data fields
        contain unit information which must be stripped before mapping may be
        applied.

        For SD card history data we iterate over the source data fields then
        strip the extraneous unit information before mapping the source data if
        required. To better facilitate this process a modified dict structure
        that allows reversible lookups is used to hold the field map. The
        process is slower but this is less of an issue as this process only
        occurs during startup; not during the main packet loop.

        Parameters:

        rec:         dict of source data to be mapped
        unit_system: optional unit system value to be included in the mapped
                     data 'usUnits' field. Note will override any source
                     data/field mapping that would result in source data being
                     mapped to the 'usUnits' field.
        """

        # we can only map data if we have a field map
        if self.field_map is not None and len(self.field_map) > 0:
            # we have a field map
            # initialise an empty dict to hold the mapped data
            mapped_rec = {}
            # iterate over the source data keys
            for field in rec.keys():
                # strip the units information from the key
                clean_key = re.sub(r"\(.*?\)","", field)
                #clean_key = re.sub("\(.*?\)","", field)
                # now try to map the source data using the sanitised key, but
                # be prepared to catch any one of a number of exceptions
                try:
                    if 'Time' in clean_key or clean_key == '':
                       if self.driver_debug.catchup:
                          log.info("Problem with key %s", clean_key)                        
                       continue
                    dest_field = self.field_map.inverse[clean_key]

                    if clean_key == 'Thunder time':
                       datetime_obj = datetime.datetime.strptime(rec[field], "%Y-%m-%d %H:%M") 
                       mapped_rec[dest_field] = datetime_obj.timestamp()
                       continue 
                    elif rec[field] == '--' or rec[field] == '':
                       if self.driver_debug.catchup:
                          log.info("no Data field %s", clean_key)                        
                       continue
                    elif 'Water' in clean_key:
                       if rec[field] == 'Normal':
                          mapped_rec[dest_field] = 0
                       if rec[field] == 'Leaking':
                          mapped_rec[dest_field] = 1
                       if rec[field] == 'Offline':
                          mapped_rec[dest_field] = 2
                       continue
                    else:  
                      mapped_rec[dest_field] = float(rec[field])
                except (KeyError, TypeError, ValueError) as e:
                    # KeyError indicates no mapping exists for this source
                    # field, TypeError and ValueError indicate the source data
                    # could not be converted to a float. In either case log it,
                    # ignore this field and continue.
                    if self.driver_debug.catchup:
                        log.info("Error mapping field '%s': %s", field, e)
                    continue
            # return the mapped data
            return mapped_rec
        else:
            # we have no useful field map so just return the data as is
            return rec


# ============================================================================
#                            class EcowittCommon
# ============================================================================

class EcowittCommon:
    """Base class for common Ecowitt driver and service properties/methods.

    There are a number of common properties and methods (eg IP address, field
    map, rain calculation etc) between a WeeWX driver and service when
    operating with an Ecowitt device. This class captures those common
    features.
    """

    def __init__(self, unit_system=None, **ec_config):
        """Initialise an EcowittCommon object."""

        # get driver/service specific debug settings
        self.driver_debug = DebugOptions(**ec_config)

        # obtain a HttpMapper object to do our field mapping
        self.mapper = HttpMapper(driver_debug=self.driver_debug, **ec_config)

        # obtain and save the socket timeout to be used
        max_tries = weeutil.weeutil.to_int(ec_config.get('max_tries',
                                                         DEFAULT_MAX_TRIES))
        # obtain and save the retry wait time to be used
        retry_wait = weeutil.weeutil.to_int(ec_config.get('retry_wait',
                                                          DEFAULT_RETRY_WAIT))
        # obtain and save the socket timeout to be used
        self.url_timeout = weeutil.weeutil.to_int(ec_config.get('url_timeout',
                                                                DEFAULT_URL_TIMEOUT))
        # obtain and save the device IP address
        self.ip_address = ec_config.get('ip_address')
        # how often (in seconds) we should poll the API, default is
        # DEFAULT_POLL_INTERVAL
        self.poll_interval = int(ec_config.get('poll_interval',
                                               DEFAULT_POLL_INTERVAL))
        # do we show all battery state data including nonsense data or do we
        # filter those sensors with signal state == 0
        show_battery = weeutil.weeutil.tobool(ec_config.get('show_all_batt',
                                                            DEFAULT_FILTER_BATTERY))
        # whether to log unknown API fields, unknown fields are normally logged
        # at the debug level, this will log them at the info level. Default to
        # False (log at debug level).
        log_unknown_fields = weeutil.weeutil.tobool(ec_config.get('log_unknown_fields',
                                                                  False))
        # how often (in seconds) to check for a device firmware update, default
        # is DEFAULT_FW_CHECK_INTERVAL
        fw_update_check_interval = int(ec_config.get('firmware_update_check_interval',
                                                     DEFAULT_FW_CHECK_INTERVAL))
        self.api_key = ec_config.get('api_key')
        self.app_key = ec_config.get('app_key')
        self.mac = ec_config.get('mac')
        #self.mac_address = ec_config.get('mac_address')

        # define custom unit settings used by the driver
        define_units()

        # log our config/settings that are not being pushed further down before
        # we obtain an EcowittHttpCollector object. Obtaining an
        # EcowittHttpCollector object may fail due to connectivity issues, this
        # way we at least log our config which may aid debugging.

        log.info('     device IP address is %s' % self.ip_address)
        log.info('     poll interval is %d seconds' % self.poll_interval)
        if self.driver_debug.any or weewx.debug > 0:
            log.info('     Max tries is %d URL retry wait is %d seconds', max_tries, retry_wait)
            log.info('     URL timeout is %d seconds', self.url_timeout)

        if self.driver_debug.any:
            log.info('      any debug is set')

        # log specific debug output but only if set
        #debug_list = []
        if self.driver_debug.rain:
            #debug_list.append(f"rain debug is {self.driver_debug.rain}")
            log.info('     rain debug is set')
        else:
            log.info('     rain debug is not set')

        if self.driver_debug.wind:
            #debug_list.append(f"wind debug is {self.driver_debug.wind}")
            log.info('     wind debug is set')
        else:
            log.info('     wind debug is not set')

        if self.driver_debug.lightning:
            log.info('lightning debug is set')
        else:
            log.info('lightning debug is not set')

        if self.driver_debug.loop:
            #debug_list.append(f"loop debug is {self.driver_debug.loop}")
            log.info('     loop debug is set')
        else:
            log.info('     loop debug is not set')

        #if len(debug_list) > 0:
        #    log.info(' '.join(debug_list))
        #debug_list = []
        if self.driver_debug.sensors:
            #debug_list.append(f"sensors debug is {self.driver_debug.sensors}")
            log.info('  sensors debug is set')
        else:
            log.info('  sensors debug is not set')

        if self.driver_debug.catchup:
            #debug_list.append(f"catchup debug is {self.driver_debug.catchup}")
            log.info('  catchup debug is set')
        else:
            log.info('  catchup debug is not set')

        if self.driver_debug.parser:
            #debug_list.append(f"parser debug is {self.driver_debug.parser}")
            log.info('   parser debug is set')
        else:
            log.info('   parser debug is not set')

        if self.driver_debug.collector:
            log.info('collector debug is set')
        else:
            log.info('collector debug is not set')

        if self.driver_debug.archive:
            log.info('  archive debug is set')
        else:
            log.info('  archive debug is not set')

        #if len(debug_list) > 0:
        #    log.info(' '.join(debug_list))
        if self.mapper.wn32_indoor:
            log.info("   wn32_indoor: sensor ID decoding will use indoor 'WN32'")
        else:
            log.info("   wn32_indoor: sensor ID decoding will use 'WH26'")
        if self.mapper.wn32_outdoor:
            log.info("  wn32_outdoor: sensor ID decoding will use outdoor 'WN32P'")
        else:
            log.info("  wn32_outdoor: sensor ID decoding will use 'WH26'")

        # create a EcowittHttpCollector object to interact with the device API,
        # if there is a problem our parent will handle any exceptions
        self.collector = EcowittHttpCollector(ip_address=self.ip_address,
                                              poll_interval=self.poll_interval,
                                              max_tries=max_tries,
                                              retry_wait=retry_wait,
                                              url_timeout=self.url_timeout,
                                              unit_system=unit_system,
                                              show_battery=show_battery,
                                              log_unknown_fields=log_unknown_fields,
                                              fw_update_check_interval=fw_update_check_interval,
                                              debug=self.driver_debug)
        self.last_lightning = None
        self.lightning_mapping_confirmed = False
        self.last_lightningcount = None
        #self.last_lightningtime = None

        self.last_rain = None
        self.rain_mapping_confirmed = False
        self.rain_total_field = None
        self.last_rainnew = None

        self.piezo_last_rain = None
        self.piezo_rain_mapping_confirmed = False
        self.piezo_rain_total_field = None
        self.piezo_last_rainnew = None

        self.last_lightning_a = None
        self.lightning_mapping_confirmed_a = False
        self.last_lightningcount_a = None
        #self.last_lightningtime_a = None

        self.last_rain_a = None
        self.rain_mapping_confirmed_a = False
        self.rain_total_field_a = None
        self.last_rainnew_a = None

        self.piezo_last_rain_a = None
        self.piezo_rain_mapping_confirmed_a = False
        self.piezo_rain_total_field_a = None
        self.piezo_last_rainnew_a = None

    def log_rain_data(self, data, preamble=None):
        """Log rain related data from the collector.

        General routine to obtain and log rain related data from a packet. The
        packet could be unmapped device data using 'device' field names, or it
        may be mapped data or a WeeWX loop packet that uses 'WeeWX' field
        names. In addition, the user may have specified a custom field map so
        any rain-related WeeWX fields may be different to those in the default
        map. So create a list of the values ('device' field names) in the rain
        map and the corresponding key ('WeeWX' field name). This combined list
        will consist of all 'device' and 'WeeWX' rain related fields

        This combined field list is then used to log any rain related fields.
        """

        msg_list = []
        # iterate over our rain_map keys (the 'WeeWX' fields) and values (the
        # 'device' fields) we are interested in
        for weewx_field, gw_field in self.mapper.rain_map.items():
            # do we have a 'WeeWX' field of interest
            if weewx_field in data:
                # we do so add some formatted output to our list
                msg_list.append(f"{weewx_field}={data[weewx_field]}")
            # do we have a 'device' field of interest
            if gw_field in data and weewx_field != gw_field:
                # we do so add some formatted output to our list
                msg_list.append(f"{gw_field}={data[gw_field]}")
        # pre-format the log line label
        label = f'{preamble}: ' if preamble is not None else ''
        # if we have some entries log them otherwise provide suitable text
        if len(msg_list) > 0:
            log.info('%s%s' % (label, ' '.join(msg_list)))
        else:
            log.info('%sno rain data found' % (label,))

    def log_wind_data(self, data, preamble=None):
        """Log wind related data from the collector.

        General routine to obtain and log wind related data from a packet. The
        packet could be unmapped device data using 'device' field names, or it
        may be mapped data or a WeeWX loop packet that uses 'WeeWX' field
        names. So we iterate over the keys ('WeeWX' field names) and values
        ('device' field names) of the rain field map.
        """

        msg_list = []
        # iterate over our wind_map keys (the 'WeeWX' fields) and values
        # (the 'device' fields) we are interested in
        for weewx_field, gw_field in self.mapper.wind_map.items():
            # do we have a 'WeeWX' field of interest
            if weewx_field in data:
                # we do so add some formatted output to our list
                msg_list.append(f"{weewx_field}={data[weewx_field]}")
            # do we have a 'device' field of interest
            if gw_field in data:
                # we do so add some formatted output to our list
                msg_list.append(f"{gw_field}={data[gw_field]}")
        # pre-format the log line label
        label = f"{preamble}: " if preamble is not None else ""
        # if we have some entries log them otherwise provide suitable text
        if len(msg_list) > 0:
            log.info('%s%s' % (label, ' '.join(msg_list)))
        else:
            log.info('%sno wind data found' % (label,))

# == Neu ! Krenn Werner =======================================================

    def get_cumulative_rain_field(self, data):
        """Determine the cumulative rain field used to derive field 'rain'.

        Ecowitt gateway devices emit various rain totals but WeeWX needs a per
        period value for field rain. Try the 'big' (four byte) counters
        starting at the longest period and working our way down. This should
        only need be done once.

        This is further complicated by the introduction of 'piezo' rain with
        the WS90. Do a second round of checks on the piezo rain equivalents and
        create piezo equivalent properties.

        data: dic of parsed device API data
        """

        # Do we have a confirmed field to use for calculating rain? If we do we
        # can skip this otherwise we need to look for one.
        if not self.rain_mapping_confirmed:
            # We have no field for calculating rain so look for one, if device
            # field 't_rainyear' is present used that as our first choice.
            # Otherwise, work down the list in order of descending period.
            if 'rain.0x13.val' in data:
                self.rain_total_field = 'rain.0x13.val'
                self.rain_mapping_confirmed = True
            # rain.0x13.val is not present so now try rainmonth
            elif 'rain.0x12.val' in data:
                self.rain_total_field = 'rain.0x12.val'
                self.rain_mapping_confirmed = True
            # do nothing, we can try again next packet
            else:
                self.rain_total_field = None
            # if we found a field log what we are using
            if self.rain_mapping_confirmed:
                log.info("Using '%s' for rain total" % self.rain_total_field)
            elif self.driver_debug.rain:
                # if debug_rain is set log that we had nothing
                log.info("No suitable field found for rain")

        # now do the same for piezo rain

        # Do we have a confirmed field to use for calculating piezo rain? If we
        # do we can skip this otherwise we need to look for one.
        if not self.piezo_rain_mapping_confirmed:
            # We have no field for calculating piezo rain so look for one, if
            # device field 'p_rainyear' is present used that as our first
            # choice. Otherwise, work down the list in order of descending
            # period.
            if 'piezoRain.0x13.val' in data:
                self.piezo_rain_total_field = 'piezoRain.0x13.val'
                self.piezo_rain_mapping_confirmed = True
            # rainyear is not present so now try rainmonth
            elif 'piezoRain.0x12.val' in data:
                self.piezo_rain_total_field = 'piezoRain.0x12.val'
                self.piezo_rain_mapping_confirmed = True
            # do nothing, we can try again next packet
            else:
                self.piezo_rain_total_field = None
            # if we found a field log what we are using
            if self.piezo_rain_mapping_confirmed:
                log.info("Using '%s' for piezo rain total" % self.piezo_rain_total_field)
            elif self.driver_debug.rain:
                # if debug_rain is set log that we had nothing
                log.info("No suitable field found for piezo rain")

    def calculate_rain(self, data):
        """Calculate total rainfall for a period.

        'rain' is calculated as the change in a user designated cumulative rain
        field between successive periods. 'rain' is only calculated if the
        field to be used has been selected and the designated field exists.

        This is further complicated by the introduction of 'piezo' rain with
        the WS90. Do a second round of calculations on the piezo rain
        equivalents and calculate the piezo rain field.

        data: dict of parsed device API data
        """

        # have we decided on a field to use and is the field present
        if self.rain_mapping_confirmed and self.rain_total_field in data:
            # yes on both counts, so get the new total
            new_total = data[self.rain_total_field]
            # now calculate field rain as the difference between the new and
            # old totals
            self.last_rainnew = self.delta_rain(new_total, self.last_rain)
            # if debug_rain is set log some pertinent values
            if self.driver_debug.rain:
                log.info("calculate_rain: last_rain=%s new_total=%s calculated rain=%s" % (self.last_rain,
                                                                                         new_total,
                                                                                         self.last_rainnew))
            # save the new total as the old total for next time
            self.last_rain = new_total

        # now do the same for piezo rain

        # have we decided on a field to use for piezo rain and is the field
        # present
        if self.piezo_rain_mapping_confirmed and self.piezo_rain_total_field in data:
            # yes on both counts, so get the new total
            piezo_new_total = data[self.piezo_rain_total_field]
            # now calculate field p_rain as the difference between the new and
            # old totals
            self.piezo_last_rainnew = self.delta_rain(piezo_new_total,
                                             self.piezo_last_rain,
                                             descriptor='piezo rain')
            # if debug_rain is set log some pertinent values
            if self.driver_debug.rain:
                log.info("calculate_rain: piezo_last_rain=%s piezo_new_total=%s "
                       "calculated p_rain=%s" % (self.piezo_last_rain,
                                                 piezo_new_total,
                                                 self.piezo_last_rainnew))
            # save the new total as the old total for next time
            self.piezo_last_rain = piezo_new_total

    def calculate_lightning_count(self, data):
        """Calculate total lightning strike count for a period.

        'lightning_strike_count' is calculated as the change in field
        'lightning.count' between successive periods. 'lightning_strike_count'
        is only calculated if 'lightning.count' exists.

        data: dict of parsed device API data
        """

        # is the lightningcount field present
        if self.lightning_mapping_confirmed and 'lightning.count' in data:
 
            # yes, so get the new total
            new_total = data['lightning.count']
            #log.info('lightning.count %s', new_total)
            # now calculate field lightning_strike_count as the difference
            # between the new and old totals
            data['lightning.count'] = self.delta_lightning(new_total,
                                                                  self.last_lightning)
            if self.driver_debug.lightning:
                log.info("calculate_lightning: last_lightning_count=%s new_total=%s "
                       "calculated lightning_count=%s" % (self.last_lightning,
                                                 new_total,
                                                 data['lightning.count']))

            # save the new total as the old total for next time
            self.last_lightning = new_total

    @staticmethod
    def delta_rain(rain, last_rain, descriptor='rain'):
        """Calculate rainfall from successive cumulative values.

        Rainfall is calculated as the difference between two cumulative values.
        If either value is None the value None is returned. If the previous
        value is greater than the latest value a counter wrap around is assumed
        and the latest value is returned.

        rain:       current cumulative rain value
        last_rain:  last cumulative rain value
        descriptor: string to indicate what rain data we are working with
        """

        # do we have a last rain value
        if last_rain is None:
            # no, log it and return None
            log.info("skipping %s measurement of %s: no last rain" % (descriptor, rain))
            return None
        # do we have a non-None current rain value
        if rain is None:
            # no, log it and return None
            log.info("skipping %s measurement: no current rain data" % descriptor)
            return None
        # is the last rain value greater than the current rain value
        if rain < last_rain:
            # it is, assume a counter wrap around/reset, log it and return the
            # latest rain value
            log.info("%s counter wraparound detected: new=%s last=%s" % (descriptor, rain, last_rain))
            #if (rain) > 2:										#KW
            #   log.info("%s too high rain detected: new=%s last=%s" % (descriptor, rain, last_rain))
            #   return 0
            return rain
        # return the difference between the counts
        return rain - last_rain

    @staticmethod
    def delta_lightning(count, last_count):
        """Calculate lightning strike count from successive cumulative values.

        Lightning strike count is calculated as the difference between two
        cumulative values. If either value is None the value None is returned.
        If the previous value is greater than the latest value a counter wrap
        around is assumed and the latest value is returned.

        count:      current cumulative lightning count
        last_count: last cumulative lightning count
        """

        # do we have a last count
        if last_count is None:
            # no, log it and return None
            log.info("Skipping lightning count of %s: no last count" % count)
            return None
        # do we have a non-None current count
        if count is None:
            # no, log it and return None
            log.info("Skipping lightning count: no current count")
            return None
        # is the last count greater than the current count
        if count < last_count:
            # it is, assume a counter wrap around/reset, log it and return the
            # latest count
            log.info("Lightning counter wraparound detected: new=%s last=%s" % (count, last_count))
            return count
        # otherwise return the difference between the counts
        return count - last_count


# ============================================================================
#                          class EcowittHttpService
# ============================================================================

class EcowittHttpService(weewx.engine.StdService, EcowittCommon):
    """Ecowitt HTTP API device service class.

    A WeeWX service to augment loop packets with observational data obtained
    from a device via the Ecowitt local HTTP API. The EcowittHttpService is
    useful when data is required from more than one source; for example, WeeWX
    is using another driver and the EcowittHttpDriver cannot be used.

    Data is obtained via the Ecowitt local HTTP API. The data is parsed and
    mapped to WeeWX fields and if the device data is not stale the loop packet
    is augmented with the mapped device data.

    Class EcowittHttpCollector collects and parses data from the API. The
    EcowittHttpCollector runs in a separate thread so it does not block the
    main WeeWX processing loop. The EcowittHttpCollector is turn uses child
    class EcowittDevice to interact with the Ecowitt device and obtain and
    parse data from the API.
    """

    def __init__(self, engine, config_dict):
        """Initialise an EcowittHttpService object."""

        # first extract the service config dictionary, try looking for
        # [EcowittHttpService]
        if 'EcowittHttpService' in config_dict:
            # we have a [EcowittHttpService] config stanza so use it
            gw_config_dict = config_dict['EcowittHttpService']
        else:
            # we don't have a [EcowittHttpService] stanza so use [EcowittHttp] if it
            # exists otherwise use an empty config
            gw_config_dict = config_dict.get('EcowittHttp', {})

        # Log our driver version first. Normally we would call our superclass
        # initialisation method first; however, that involves establishing a
        # network connection to the device and it may fail. Doing our logging
        # first will aid in remote debugging.

        # log our version number
        log.info('EcowittHttpService: version is %s' % DRIVER_VERSION)
        # set the unit system we will emit
        self.unit_system = DEFAULT_UNIT_SYSTEM
        # initialize my superclasses, we need to do this manually due to
        # differing signatures
        try:
            EcowittCommon.__init__(self, unit_system=self.unit_system, **gw_config_dict)
        except weewx.ViolatedPrecondition as e:
            # we encountered an error during initialization and we cannot
            # continue, raise a ServiceInitializationError
            raise ServiceInitializationError from e
        weewx.engine.StdService.__init__(self, engine, config_dict)

        # age (in seconds) before API data is considered too old to use, use a
        # default
        self.max_age = int(gw_config_dict.get('max_age', DEFAULT_MAX_AGE))
        # minimum period in seconds between 'lost contact' log entries during
        # an extended lost contact period
        self.lost_contact_log_period = int(gw_config_dict.get('lost_contact_log_period',
                                                              DEFAULT_LOST_CONTACT_LOG_PERIOD))
        if self.driver_debug.any or weewx.debug > 0:
            log.info('     max age of API data to be used is %d seconds' % self.max_age)
            log.info('     lost contact will be logged every '
                     '%d seconds' % self.lost_contact_log_period)

        # set failure logging on
        self.log_failures = True
        # reset the lost contact timestamp
        self.lost_con_ts = None
        # create a placeholder for our most recent, non-stale queued device
        # sensor data packet
        self.latest_sensor_data = None
        # start the Gw1000Collector in its own thread
        self.collector.startup()
        # bind our self to the relevant WeeWX events
        self.bind(weewx.NEW_LOOP_PACKET, self.new_loop_packet)

    def new_loop_packet(self, event):
        """Augment a loop packet with device data.

        When a new loop packet arrives process the queue looking for any device
        sensor data packets. If there are sensor data packets keep the most
        recent, non-stale packet and use it to augment the loop packet. If
        there are no sensor data packets, or they are all stale, then the loop
        packet is not augmented.

        The queue may also contain other control data, eg exception reporting
        from the EcowittHttpCollector thread. This control data needs to be
        processed as well.
        """

        # log the loop packet received if necessary, there are several debug
        # settings that may require this
        if self.driver_debug.loop or self.driver_debug.rain or self.driver_debug.wind:
            log.info('EcowittHttpService: Processing loop packet: %s %s' % (timestamp_to_string(event.packet['dateTime']),
                                                                            natural_sort_dict(event.packet)))
        # we are about to process the queue so reset our latest sensor data
        # packet property
        self.latest_sensor_data = None
        # now process the queue until it is empty
        while True:
            # Get the next item from the queue. Wrap in a try to catch any
            # instances where the queue is empty as that is our signal to break
            # out of the while loop.
            try:
                # get the next item from the collector queue, but don't dwell
                # very long
                queue_data = self.collector.queue.get(True, 0.5)
            except queue.Empty:
                # the queue is now empty, but that may be because we have
                # already processed any queued data, log if necessary and break
                # out of the while loop
                if self.latest_sensor_data is None and (self.driver_debug.loop or self.driver_debug.rain or self.driver_debug.wind):
                    log.info('EcowittHttpService: No queued items to process')
                if self.lost_con_ts is not None and time.time() > self.lost_con_ts + self.lost_contact_log_period:
                    self.lost_con_ts = time.time()
                    self.set_failure_logging(True)
                # now break out of the while loop
                break
            else:
                # We received something in the queue, it will be one of three
                # things:
                # 1. a dict containing sensor data
                # 2. an exception
                # 3. the value None signalling a serious error that means the
                #    Collector needs to shut down

                # if the data has a 'keys' attribute it is a dict so must be
                # data
                if hasattr(queue_data, 'keys'):
                    # we have a dict so assume it is data
                    self.lost_con_ts = None
                    self.set_failure_logging(True)
                    # log the received data if necessary, there are several
                    # debug settings that may require this, start from the
                    # highest (most encompassing) and work to the lowest (least
                    # encompassing)
                    if self.driver_debug.loop:
                        if 'datetime' in queue_data:
                            # if we have a 'datetime' field it is almost
                            # certainly a sensor data packet
                            log.info('EcowittHttpService: newLoop Received queued sensor '
                                     'data: %s %s' % (timestamp_to_string(queue_data['datetime']),
                                                      natural_sort_dict(queue_data)))
                        else:
                            # There is no 'datetime' field, this should not
                            # happen. Log it in any case.
                            log.info('EcowittHttpService: newLoop Received queued data: %s' % (natural_sort_dict(queue_data),))
                    else:
                        # perhaps we have individual debugs such as rain or wind
                        if self.driver_debug.rain:
                            # debug_rain is set so log the 'rain' field in the
                            # mapped data, if it does not exist say so
                            self.log_rain_data(queue_data,
                                               f'EcowittHttpService: newLoop Received {self.collector.device.model} data')
                        if self.driver_debug.wind:
                            # debug_wind is set so log the 'wind' fields in the
                            # received data, if they do not exist say so
                            self.log_wind_data(queue_data,
                                               f'EcowittHttpService: newLoop Received {self.collector.device.model} data')
                    # now process the just received sensor data packet
                    self.process_queued_sensor_data(queue_data, event.packet['dateTime'])

                # if it's a tuple then it's a tuple with an exception and
                # exception text
                elif isinstance(queue_data, BaseException):
                    # We have an exception. The collector did not deem it
                    # serious enough to want to shut down, or it would have
                    # sent None instead. The action we take depends on the type
                    # of exception it is. If it's a DeviceIOError we can ignore
                    # it as appropriate action will have been taken by the
                    # EcowittHttpCollector. If it is anything else we log it.
                    # process the exception
                    self.process_queued_exception(queue_data)

                # if it's None then it's a signal the Collector needs to shut down
                elif queue_data is None:
                    # if debug_loop log what we received
                    if self.driver_debug.loop:
                        log.info('EcowittHttpService: Received collector shutdown signal')
                    # we received the signal that the EcowittHttpCollector
                    # needs to shut down, that means we cannot continue so call
                    # our shutdown method which will also shut down the
                    # EcowittHttpCollector thread
                    self.shutDown()
                    # the EcowittHttpCollector has been shut down, so we will
                    # not see anything more in the queue. We are still bound to
                    # NEW_LOOP_PACKET but since the queue is always empty we
                    # will just wait for the empty queue timeout before exiting

                # if it's none of the above (which it should never be) we don't
                # know what to do with it so pass and wait for the next item in
                # the queue
                else:
                    pass

        # we have now finished processing the queue, do we have a sensor data
        # packet to add to the loop packet
        if self.latest_sensor_data is not None:
            # we have a sensor data packet

            # map the raw data to WeeWX loop packet fields
            mapped_data = self.mapper.map_data(self.latest_sensor_data)
            # add 'usUnits' to the packet
            mapped_data['usUnits'] = self.unit_system
            # log the mapped data if necessary
            if self.driver_debug.loop:
                log.info('EcowittHttpService: newLoop Mapped %s data: %s' % (self.collector.device.model,
                                                                     natural_sort_dict(mapped_data)))
            else:
                # perhaps we have individual debugs such as rain or wind
                if self.driver_debug.rain:
                    # debug_rain is set so log the 'rain' field in the
                    # mapped data, if it does not exist say so
                    self.log_rain_data(mapped_data,
                                       f'EcowittHttpService: newLoop Mapped {self.collector.device.model} data')
                if self.driver_debug.wind:
                    # debug_wind is set so log the 'wind' fields in the
                    # mapped data, if they do not exist say so
                    self.log_wind_data(mapped_data,
                                       f'EcowittHttpService: newLoop Mapped {self.collector.device.model} data')
            # and finally augment the loop packet with the mapped data
            self.augment_packet(event.packet, mapped_data)
            # log the augmented packet if necessary, there are several debug
            # settings that may require this, start from the highest (most
            # encompassing) and work to the lowest (least encompassing)
            if self.driver_debug.loop or weewx.debug >= 2:
                log.info('EcowittHttpService: newLoop Augmented packet: %s %s' % (timestamp_to_string(event.packet['dateTime']),
                                                                          natural_sort_dict(event.packet)))
            else:
                # perhaps we have individual debugs such as rain or wind
                if self.driver_debug.rain:
                    # debug_rain is set so log the 'rain' field in the
                    # augmented loop packet, if it does not exist say
                    # so
                    self.log_rain_data(event.packet, 'EcowittHttpService: newLoop Augmented packet')
                if self.driver_debug.wind:
                    # debug_wind is set so log the 'wind' fields in the
                    # loop packet being emitted, if they do not exist
                    # say so
                    self.log_wind_data(event.packet, 'EcowittHttpService: newLoop Augmented packet')

    def process_queued_sensor_data(self, sensor_data, date_time):
        """Process a sensor data packet received in the collector queue.

        When the queue is processed there may be multiple sensor data packets
        in the queue, but we only want the most recent, non-stale packet. Check
        the received sensor packet is timestamped and not stale, if it is not
        stale and is newer than the previously saved sensor data packet then
        replace the saved packet with this packet.

        Non-timestamped sensor data packets are discarded.

        sensor_data: the sensor data packet obtained from the queue
        date_time:   the timestamp of the current loop packet
        """

        # first up check we have a field 'datetime' and that it is not None
        if 'datetime' in sensor_data and sensor_data['datetime'] is not None:
            # now check it is not stale
            if sensor_data['datetime'] > date_time - self.max_age:
                # the sensor data is not stale, but is it more recent than our
                # current saved packet
                if self.latest_sensor_data is None or sensor_data['datetime'] > self.latest_sensor_data['datetime']:
                    # this packet is newer, so keep it
                    self.latest_sensor_data = dict(sensor_data)
            elif self.driver_debug.loop or weewx.debug >= 2:
                # the sensor data is stale and we have debug settings that
                # dictate we log the discard
                log.info('EcowittHttpService: Discarded packet with '
                         'timestamp %s' % timestamp_to_string(sensor_data['datetime']))
        elif self.driver_debug.loop or weewx.debug >= 2:
            # the sensor data is not timestamped so it will be discarded and we
            # have debug settings that dictate we log the discard
            log.info('EcowittHttpService: Discarded non-timestamped packet')

    def process_queued_exception(self, e):
        """Process an exception received in the collector queue."""

        # is it a DeviceIOError
        if isinstance(e, DeviceIOError):
            # set our failure logging appropriately
            if self.lost_con_ts is None:
                # we have previously been in contact with the device so set our
                # lost contact timestamp
                self.lost_con_ts = time.time()
                # any failure logging for this failure will already have
                # occurred in our EcowittHttpCollector object and its
                # EcowittDevice object, so turn off failure logging
                self.set_failure_logging(False)
            elif self.log_failures:
                # we are already in a lost contact state, but failure logging
                # may have been turned on for a 'once in a while' log entry so
                # we need to turn it off again
                self.set_failure_logging(False)
        else:
            # it's not so log it
            log.error('EcowittHttpService: Caught unexpected exception %s: %s' % (e.__class__.__name__,
                                                                                  e))

    def augment_packet(self, packet, data):
        """Augment a loop packet with data from another packet.

        The data to be used for augmentation (the new data) may not be in the
        same unit system as the loop data being augmented so the new data is
        converted to the same unit system as used in the loop packet before
        augmentation occurs. Only fields that exist in the new data but not in
        the loop packet are added to the loop packet.

        packet: dict containing the loop packet
        data:   dict containing the data to be used to augment the loop packet
        """

        if self.driver_debug.loop:
            log.info('EcowittHttpService: Mapped data will be used to augment loop packet(%s)',
                     timestamp_to_string(packet['dateTime']))
        # But the mapped data must be converted to the same unit system as
        # the packet being augmented. First get a converter.
        converter = weewx.units.StdUnitConverters[packet['usUnits']]
        # convert the mapped data to the same unit system as the packet to
        # be augmented
        converted_data = converter.convertDict(data)
        # if required log the converted data
        if self.driver_debug.loop:
            log.info('EcowittHttpService: Converted %s data: %s',
                     self.collector.device.model,
                     natural_sort_dict(converted_data))
        # now we can freely augment the packet with any of our mapped obs
        for field, field_data in converted_data.items():
            # Any existing packet fields, whether they contain data or are
            # None, are respected and left alone. Only fields from the
            # converted data that do not already exist in the packet are
            # used to augment the packet.
            if field not in packet:
                packet[field] = field_data

    # TODO. Why have this, isn't failure_logging passed through each instantiation
    def set_failure_logging(self, log_failures):
        """Turn failure logging on or off.

        When operating as a service lost contact or other non-fatal errors
        should only be logged every so often so as not to flood the logs.
        Failure logging occurs at three levels:
        1. in myself (the service)
        2. in the EcowittHttpCollector object
        3. in the EcowittHttpCollector object's Station object

        Failure logging is turned on or off by setting the log_failures
        property True or False for each of the above 3 objects.
        """

        self.log_failures = log_failures
        self.collector.log_failures = log_failures
        self.collector.device.log_failures = log_failures

    def shutDown(self):
        """Shut down the service."""

        # the collector will likely be running in a thread so call its
        # shutdown() method so that any thread shut down/tidy up can occur
        self.collector.shutdown()


# ============================================================================
#           Ecowitt HTTP driver Loader/Configurator/Editor methods
# ============================================================================

def loader(config_dict, engine):
    return EcowittHttpDriver(**config_dict[DRIVER_NAME])


def configurator_loader(config_dict):  # @UnusedVariable

    return EcowittHttpDriverConfigurator()


def confeditor_loader():
    return EcowittHttpDriverConfEditor()


# ============================================================================
#                     class EcowittHttpDriverConfEditor
# ============================================================================

class EcowittHttpDriverConfEditor(weewx.drivers.AbstractConfEditor):
    """Config editor class for the Ecowitt local HTTP driver."""

    # define our config as a multiline string so we can preserve comments
    accum_config_str = """
    [Accumulator]
        # GW1000, Ecowittcustom, Ecowitt local HTTP API driver extractors
    [[model]]
        accumulator = firstlast
        extractor = last
    [[stationtype]]
        accumulator = firstlast
        extractor = last
    
    [[gain0]]
        extractor = last
    [[gain1]]
        extractor = last
    [[gain2]]
        extractor = last
    [[gain3]]
        extractor = last
    [[gain4]]
        extractor = last
    [[gain5]]
        extractor = last
    
    [[lightning_distance]]
        extractor = last
    [[lightning_strike_count]]
        extractor = sum
    [[lightning_last_det_time]]
        extractor = last
    [[lightningcount]]
        extractor = last
    [[lightning_noise_count]]
        extractor = sum

    [[maxdailygust]]
        extractor = last
    [[daymaxwind]]
        extractor = last
    [[windspdmph_avg10m]]
        extractor = last
    [[winddir_avg10m]]
        extractor = last
    
    [[rainRate]]
        extractor = max
    [[stormRain]]
        extractor = last
    [[hourRain]]
        extractor = last
    [[dayRain]]
        extractor = last
    [[weekRain]]
        extractor = last
    [[monthRain]]
        extractor = last
    [[yearRain]]
        extractor = last
    [[totalRain]]
        extractor = last
    
    [[rrain_piezo]]
        extractor = max
    [[erain_piezo]]
        extractor = last
    [[hrain_piezo]]
        extractor = last
    [[drain_piezo]]
        extractor = last
    [[wrain_piezo]]
        extractor = last
    [[mrain_piezo]]
        extractor = last
    [[yrain_piezo]]
        extractor = last
    
    [[p_rainrate]]
        extractor = max
    [[p_eventrain]]
        extractor = last
    [[p_hourrain]]
        extractor = last
    [[p_dayrain]]
        extractor = last
    [[p_weekrain]]
        extractor = last
    [[p_monthrain]]
        extractor = last
    [[p_yearrain]]
        extractor = last
    
    [[dayHail]]
        extractor = last
    [[hail]]
        extractor = sum
    
    [[vpd]]
        extractor = last
    [[depth_ch1]]
        extractor = last
    [[depth_ch2]]
        extractor = last
    [[depth_ch3]]
        extractor = last
    [[depth_ch4]]
        extractor = last
   
    [[pm2_51_24hav]]
        extractor = last
    [[pm2_52_24hav]]
        extractor = last
    [[pm2_53_24hav]]
        extractor = last
    [[pm2_54_24hav]]
        extractor = last
    [[24havpm255]]
        extractor = last
    
    [[pm2_51_24h_avg]]
        extractor = last
    [[pm2_52_24h_avg]]
        extractor = last
    [[pm2_53_24h_avg]]
        extractor = last
    [[pm2_54_24h_avg]]
        extractor = last
    [[pm2_55_24h_avg]]
        extractor = last
    [[pm10_24h_avg]]
        extractor = last
    [[co2_24h_avg]]
        extractor = last
    
    [[wh25_batt]]
        extractor = last
    [[wh26_batt]]
        extractor = last
    [[wh31_ch1_batt]]
        extractor = last
    [[wh31_ch2_batt]]
        extractor = last
    [[wh31_ch3_batt]]
        extractor = last
    [[wh31_ch4_batt]]
        extractor = last
    [[wh31_ch5_batt]]
        extractor = last
    [[wh31_ch6_batt]]
        extractor = last
    [[wh31_ch7_batt]]
        extractor = last
    [[wh31_ch8_batt]]
        extractor = last
    [[wn35_ch1_batt]]
        extractor = last
    [[wn35_ch2_batt]]
        extractor = last
    [[wn35_ch3_batt]]
        extractor = last
    [[wn35_ch4_batt]]
        extractor = last
    [[wn35_ch5_batt]]
        extractor = last
    [[wn35_ch6_batt]]
        extractor = last
    [[wn35_ch7_batt]]
        extractor = last
    [[wn35_ch8_batt]]
        extractor = last
    [[wh40_batt]]
        extractor = last
    [[wn20_batt]]
        extractor = last
    [[wh41_ch1_batt]]
        extractor = last
    [[wh41_ch2_batt]]
        extractor = last
    [[wh41_ch3_batt]]
        extractor = last
    [[wh41_ch4_batt]]
        extractor = last
    [[wh45_batt]]
        extractor = last
    [[wh51_ch1_batt]]
        extractor = last
    [[wh51_ch2_batt]]
        extractor = last
    [[wh51_ch3_batt]]
        extractor = last
    [[wh51_ch4_batt]]
        extractor = last
    [[wh51_ch5_batt]]
        extractor = last
    [[wh51_ch6_batt]]
        extractor = last
    [[wh51_ch7_batt]]
        extractor = last
    [[wh51_ch8_batt]]
        extractor = last
    [[wh51_ch9_batt]]
        extractor = last
    [[wh51_ch10_batt]]
        extractor = last
    [[wh51_ch11_batt]]
        extractor = last
    [[wh51_ch12_batt]]
        extractor = last
    [[wh51_ch13_batt]]
        extractor = last
    [[wh51_ch14_batt]]
        extractor = last
    [[wh51_ch15_batt]]
        extractor = last
    [[wh51_ch16_batt]]
        extractor = last
    [[wh55_ch1_batt]]
        extractor = last
    [[wh55_ch2_batt]]
        extractor = last
    [[wh55_ch3_batt]]
        extractor = last
    [[wh55_ch4_batt]]
        extractor = last
    [[wh57_batt]]
        extractor = last
    [[wh65_batt]]
        extractor = last
    [[wh68_batt]]
        extractor = last
    [[wh69_batt]]
        extractor = last
    [[ws80_batt]]
        extractor = last
    [[ws85_batt]]
        extractor = last
    [[ws90_batt]]
        extractor = last
    [[ws85cap_volt]]
        extractor = last
    [[ws90cap_volt]]
        extractor = last
    [[ws1900batt]]
        extractor = last
    [[console_batt]]
        extractor = last

        # End Ecowitt local HTTP API driver extractors
    """
    # Ecowitt cumulative rain fields, in order of preference, used to calculate
    # a WeeWX 'rain' field for a traditional type rainfall gauge
    t_src_fields = ('rain.0x13.val', 'rain.0x12.val', 'rain.0x11.val', 'rain.0x10.val')
    # Ecowitt cumulative rain fields, in order of preference, used to calculate
    # a WeeWX 'rain' field for a piezo type rainfall gauge
    p_src_fields = ('piezoRain.0x13.val', 'piezoRain.0x12.val', 'piezoRain.0x11.val', 'piezoRain.0x10.val')

    @property
    def default_stanza(self):
        return f"""
    [EcowittHttp]
        # This section is for the Ecowitt local HTTP API driver.

        # the driver to use
        driver = user.ecowitt_http

        # how often to poll the device
        poll_interval = {int(DEFAULT_POLL_INTERVAL):d}
        # how many attempts to contact the device before giving up
        max_tries = {int(DEFAULT_MAX_TRIES):d}
        # wait time in seconds between retries to contact the device
        retry_wait = {int(DEFAULT_RETRY_WAIT):d}
        # max wait for device to respond to a HTTP request
        url_timeout = {int(DEFAULT_URL_TIMEOUT):d}
        
        # whether to show all battery state data including nonsense data and 
        # sensors that are disabled sensors and connecting
        show_all_batt = False

        # whether to always log unknown API fields, unknown fields are always 
        # logged at the debug level, this will log them at the info level
        log_unknown_fields = False
        
        # How often to check for device firmware updates, 0 disables firmware 
        # update checks. Available firmware updates are logged.
        firmware_update_check_interval = 86400
        
    """

    # def get_conf(self, orig_stanza=None):
    #     """Given a configuration stanza, return a possibly modified copy
    #     that will work with the current version of the device driver.
    #
    #     The default behavior is to return the original stanza, unmodified.
    #
    #     Derived classes should override this if they need to modify previous
    #     configuration options or warn about deprecated or harmful options.
    #
    #     The return value should be a long string. See default_stanza above
    #     for an example string stanza.
    #     """
    #
    #     return self.default_stanza if orig_stanza is None else orig_stanza
    #
    def prompt_for_settings(self):
        """Prompt for settings required for proper operation of this driver.

        Returns a dict of setting, value key pairs for settings to be included
        in the driver stanza. The _prompt() method may be used to prompt the
        user for input with a default.
        """

        # obtain IP address
        print()
        prompt = 'Specify the device IP address, for example: 192.168.1.100.'
        default = self.existing_options.get('ip_address')
        ip_address = weecfg.prompt_with_options(prompt, default)

        # obtain poll interval
        print()
        prompt = 'Specify how often to poll the device in seconds.'
        default = self.existing_options.get('poll_interval',
                                            DEFAULT_POLL_INTERVAL)
        poll_interval = int(weecfg.prompt_with_options(prompt, default))
        # return our results
        return {'ip_address': ip_address,
                'poll_interval': poll_interval
                }

    def modify_config(self, config_dict):
        """Make Ecowitt local HTTP API driver specific changes to WeeWX config."""

        import weecfg

        # set loop_on_init
        self.do_loop_on_init(config_dict)
        # configure rain calculations
        self.do_rain(config_dict)
        # configure lightning calculations
        #           self.do_lightning(config_dict)
        # configure archive record generation
        self.do_archive_record_generation(config_dict)
        # configure extractors
        self.do_extractors(config_dict)
        # we don't need weecfg anymore so remove it from memory
        del weecfg

    @staticmethod
    def do_loop_on_init(config_dict):
        """Configure loop_on_init."""

        print()
        # obtain the current loop_on_init setting if it exists, default
        # to 1 (enabled)
        default = config_dict.get('loop_on_init', '1')
        # construct the prompt text
        prompt = """The Ecowitt HTTP driver requires a network connection to the device.
Consequently, the absence of a network connection when WeeWX starts will cause
WeeWX to exit. The WeeWX 'loop_on_init' setting can be used to mitigate such
problems by having WeeWX retry startup indefinitely. Set to '0' to attempt
startup once only or '1' to attempt startup indefinitely."""
        # obtain the user loop_on_init setting, coerce to an integer
        loop_on_init = int(weecfg.prompt_with_options(prompt, default, ['0', '1']))
        # define the loop_on_init template string
        loop_on_init_config_str = f'loop_on_init = {loop_on_init:d}'
        # convert the loop_on_init config to a ConfigObj
        loop_on_init_dict = configobj.ConfigObj(io.StringIO(loop_on_init_config_str))
        # merge the loop_on_init config into our overall config
        config_dict.merge(loop_on_init_dict)
        # if we don't have any loop_on_init comments add a brief explanatory
        # comment
        if len(config_dict.comments['loop_on_init']) == 0:
            config_dict.comments['loop_on_init'] = ['',
                                                    '# Whether to try indefinitely to load the driver']

    @staticmethod
    def do_rain(config_dict):
        """Configure rain calculations.

        Configure [StdWXCalculate] and [EcowittHttp] config stanzas to populate
        rain rate and per-period rain fields as per user requirements. A default
        install populates WeeWX fields t_rain and p_rain with per-period tipping
        and piezo rain respectively via the StdWXCalculate service. WeeWX
        fields t_rainrate and p_rainrate are populated with tipping and piezo
        rain rate data respectively via the driver field map.

        Consequently, setting the rain calculations is complex, possibly
        involving changes to StdWXCalculate and the driver config.
        """

        # first get the driver config stanza (if it exists) from the WeeWX
        # config dict, we will refer to this a few times
        driver_config_dict = config_dict.get('EcowittHttp', {})
        # Get a HttpMapper object so we can access the field map being used. We
        # need the field map so we can 'talk' WeeWX field names with the
        # user - the user does not necessarily know the 'dotted' Ecowitt field
        # names.
        mapper = HttpMapper(driver_config_dict)
        # Determine the rain gauge type(s) paired with the device. To do this
        # we obtain an EcowittDevice and inspect the paired_rain_gauges
        # property.
        # first get the device IP address
        ip_address = driver_config_dict.get('ip_address')
        # now get an EcowittDevice object
        try:
            device = EcowittDevice(ip_address=ip_address)
        except weewx.ViolatedPrecondition:
            raise
        else:
            # and finally get the paired_rain_gauges property
            paired = device.paired_rain_gauges
            paired_str = 'none'
            if paired is not None:
                paired_str = 'both' if len(paired) == 2 else paired[0]
        # construct the prompt text
        _prompt = """Ecowitt gateways/consoles can simultaneously support both tipping and 
piezoelectric (piezo) rain gauges. Select the gauge type(s) paired with this device. Set
to 'none' if no gauges are paired, 'tipping' if only a tipping gauge is paired, 
'piezo' if only a piezo gauge is paired or 'both' if both a tipping gauge and a 
piezo gauge are paired."""
        # format the prompt string to a 80 character wide multiline string
        prompt = '\n'.join([i for i in textwrap.wrap(_prompt, 80, break_long_words=False)])
        print()
        # obtain the user rain gauge type(s) paired with the device
        paired_gauges = weecfg.prompt_with_options(prompt,
                                                   paired_str,
                                                   ['none', 'tipping', 'piezo', 'both']).lower()
#        if len(paired) > 0:
        if paired_gauges in ('tipping', 'piezo', 'both'):
            # we have a least one paired gauge

            # obtain the current [StdWXCalculate] [[Delta]] config if it exists
            _deltas_config_dict = config_dict['StdWXCalculate'].get('Delta', {})
            # get the WeeWX field used as the 'cumulative' key used to calculate
            # 'rain', if there isn't one then use None
            curr_rain_w_src = _deltas_config_dict['rain'].get('input') if 'rain' in _deltas_config_dict else None
            # get the Ecowitt field used to derive the 'cumulative' key used to
            # calculate 'rain', if there isn't such a WeeWX field then use None
            curr_rain_e_src = mapper.field_map.get(curr_rain_w_src) if curr_rain_w_src is not None else None
            # Determine the rain gauge type used to calculate 'rain', it will
            # be either 'tipping' or 'piezo'. If we can't determine the type
            # then use the string 'none'.
            curr_gauge_type = 'none'
            if curr_rain_w_src is not None:
                if curr_rain_e_src in EcowittHttpDriverConfEditor.t_src_fields:
                    curr_gauge_type = 'tipping'
                elif curr_rain_e_src in EcowittHttpDriverConfEditor.p_src_fields:
                    curr_gauge_type = 'piezo'
            # Now determine the preferred WeeWX field name for tipping and
            # piezo gauges. The preferred field is the available cumulative
            # rain field with the longest reset interval. If no field is
            # available (unlikely) then use None.
            # tipping, set our preferred tipping field name to None until we
            # find a field
            pref_t_field = None
            # iterate over the possible Ecowitt tipping source fields
            for _field in EcowittHttpDriverConfEditor.t_src_fields:
                # does that field appear in the field map, it is of no use if it
                # does not
                if _field in mapper.field_map.values():
                    # we have a field we can use, now do an inverse lookup to find
                    # the WeeWX field it is mapped to
                    pref_t_field = mapper.field_map.inverse[_field]
                    # no need to search further, break out of the loop
                    break
            # piezo, set our preferred tipping field name to None until we find
            # a field
            pref_p_field = None
            # iterate over the possible Ecowitt piezo source fields
            for _field in EcowittHttpDriverConfEditor.p_src_fields:
                # does that field appear in the field map, it is of no use if it
                # does not
                if _field in mapper.field_map.values():
                    # we have a field we can use, now do an inverse lookup to find
                    # the WeeWX field it is mapped to
                    pref_p_field = mapper.field_map.inverse[_field]
                    # no need to search further, break out of the loop
                    break
            # initialise a variable to hold the Ecowitt field being used to
            # populate the WeeWX rainRate field
            rate_field = None
            # initialise a variable to hold the WeeWX field name (t_rain or p_rain)
            # to be added back to StdWXCalculate if the user changes from 'tipping'
            # to 'none' or 'piezo' to 'none'
            add_back = None
            # construct the prompt text, the prompt text will vary depending on
            # what gauges are paired
            if paired_gauges == 'both':
                # both tipping and piezo are paired
                select_1 = "'tipping' to populate the WeeWX rain fields from a paired tipping gauge"
                select_2 = "'piezo' to populate the WeeWX rain fields from a paired piezo gauge"
                select_3 = "'none' to not populate the WeeWX rain fields"
                punc = ", "
                conj = " or "
                possible = ['tipping', 'piezo', 'none']
            elif paired_gauges == 'tipping':
                # we have a paired tipping gauge
                select_1 = "'tipping' to populate the WeeWX rain fields from a paired tipping gauge"
                select_2 = ""
                select_3 = "'none' to not populate the WeeWX rain fields"
                punc = ""
                conj = " or "
                possible = ['tipping', 'none']
            else:
                # there must be a paired piezo gauge
                select_1 = ""
                select_2 = "'piezo' to populate the WeeWX rain fields from a paired piezo gauge"
                select_3 = "'none' to not populate the WeeWX rain fields"
                punc = ""
                conj = " or "
                possible = ['piezo', 'none']
            selection_str = f"Set to {select_1}{punc}{select_2}{conj}{select_3}."
            # now construct the overall prompt string
            _prompt = f"""By default, per-period rainfall values and rain rates will appear in
fields 'rain'/'rainRate' and 'p_rain'/'p_rainrate for paired tipping and 
piezo rain gauges respectively. WeeWX can populate the default WeeWX rain observations 
('rain' and 'rainRate') from either a paired tipping or piezo rain gauge. {selection_str}"""
            # format the prompt string to a 80 character wide multiline string
            prompt = '\n'.join([i for i in textwrap.wrap(_prompt, 80, break_long_words=False)])
            print()
            # obtain the user rain gauge type being used
            user_gauge_type = weecfg.prompt_with_options(prompt,
                                                         curr_gauge_type,
                                                         possible).lower()
            # given the rain gauge type selected, obtain the source field to be
            # used to calculate WeeWX field 'rain'
            if user_gauge_type in ('tipping', 'piezo'):
                if user_gauge_type == 'tipping':
                    # a tipping rainfall gauge was chosen

                    # Get the default WeeWX source field, it is the WeeWX field
                    # currently used to derive the WeeWX 'rain' field if we are
                    # currently using a tipping gauge. If the WeeWX field does
                    # not exist or we are currently using a piezo gauge use the
                    # preferred tipping field from earlier.
                    if curr_gauge_type == 'tipping':
                        # the default WeeWX source field is the field we are
                        # currently using or if that does not exist the preferred
                        # tipping source field
                        default_source = curr_rain_w_src if curr_rain_w_src is not None else pref_t_field
                    else:
                        # 'piezo' had been previously selected so choose the
                        # preferred tipping source field from earlier
                        default_source = pref_t_field
                        # the user has chosen 'tipping' and the current gauge type
                        # is 'piezo' so we will need to add 'p_rain' back to
                        # StdWXCalculate
                        add_back = 'p_rain'
                    # construct a string listing the available WeeWX tipping
                    # cumulative rain fields, the available fields consist of those
                    # fields in our tipping source field list that exist in the
                    # field map
                    _fields = [mapper.field_map.inverse[f] for f in EcowittHttpDriverConfEditor.t_src_fields
                               if f in mapper.field_map.values()]
                    # set the WeeWX field that will be replaced by 'rain', we will
                    # need to remove this field from StdWXCalculate before we are
                    # done
                    rain_field = 'rain'
                    # set the Ecowitt field to be used to map to WeeWX field
                    # rainRate
                    rate_field = 'rain.0x0E.val'
                else:
                    # a piezo rainfall gauge was chosen

                    # Get the default WeeWX source field, it is the WeeWX field
                    # currently used to derive the WeeWX 'rain' field if we are
                    # currently using a piezo gauge. If one does not exist or we are
                    # currently using a tipping gauge use the preferred piezo field
                    # from earlier.
                    if curr_gauge_type == 'piezo':
                        default_source = curr_rain_w_src if curr_rain_w_src is not None else pref_p_field
                    else:
                        default_source = pref_p_field
                        add_back = 'rain'
                    # construct a string listing the available WeeWX piezo cumulative
                    # rain fields
                    _fields = [mapper.field_map.inverse[f] for f in EcowittHttpDriverConfEditor.p_src_fields
                               if f in mapper.field_map.values()]
                    # set the WeeWX field that will be replaced by 'rain', we will
                    # need to remove this field from StdWXCalculate before we are
                    # done
                    rain_field = 'p_rain'
                    # set the Ecowitt field to be used to map to WeeWX field
                    # rainRate
                    rate_field = 'piezoRain.0x0E.val'
                # Construct a string consisting of a comma separated list of
                # available cumulative WeeWX fields. This needs a bit of
                # finessing to get the grammar correct.
                if len(_fields) == 1:
                    # we have just one field so this is simple
                    options = f" Possible observations are '{_fields[0]}'"
                elif len(_fields) == 2:
                    # we have two fields so separate them with 'or'
                    _options = ' or '.join(_fields)
                    options = f" Possible observations are '{_options}'"
                elif len(_fields) > 2:
                    # we have more than two fields so comma separate the first
                    # n-1 and 'or' the last one
                    _first = ', '.join(_fields[:-1])
                    options = f" Possible observations are {' or '.join([_first, _fields[-1]])}"
                else:
                    # this should not happen, but set options just in case
                    options = ''
                # construct the prompt text to use, it includes a list of the
                # available possible fields
                _prompt = f"""Select the WeeWX observation to be used to derive 
WeeWX observation 'rain'. Possible observations are {options}."""
                # format the prompt string to a 80 character wide multiline string
                prompt = '\n'.join([i for i in textwrap.wrap(_prompt, 80, break_long_words=False)])
                print()
                # obtain the user rain source field selection
                rain_source_field = weecfg.prompt_with_options(prompt,
                                                               default_source,
                                                               options)
                # Construct the rain config dict, it will comprise the user rain
                # selections, the rain rate field map extension and any default
                # rain fields that may need to be added back to StdWXCalculate.
                # Once we have everything we can do one merge to the config dict.
                # first construct a config string that reflect the user selected
                # rain calculations
                _rain_config_str = f"""
                    [StdWXCalculate]
                        [[Calculations]]
                            rain = prefer_hardware"""
                # convert the rain config string to a ConfigObj
                _rain_config_dict = configobj.ConfigObj(io.StringIO(_rain_config_str))
                # now add any rain rate field map extension changes
                # mapping
                if rate_field is not None:
                    # we have a rain rate field, construct an appropriate config
                    # string
                    _rate_config_str = f"""
                        [EcowittHttp]
                            [[field_map_extensions]]
                                rainRate = {rate_field}"""
                    # merge the rain rate config into our rain config
                    _rain_config_dict.merge(configobj.ConfigObj(io.StringIO(_rate_config_str)))
                # if we have had a change from 'tipping' to 'piezo' or vice-versa
                # we need to add back the old 'rain' or 'p_rain' calculation,
                # but only if we have 'both' gauges
                if add_back is not None and paired_gauges == 'both':
                    # we have had a change of source, construct a suitable config
                    # string
                    _change_config_str = f"""
                        [StdWXCalculate]
                            [[Calculations]]
                                {add_back} = prefer_hardware"""
                    # merge the 'add back' config into our rain config
                    _rain_config_dict.merge(configobj.ConfigObj(io.StringIO(_change_config_str)))
                # We now have the complete rain config so merge into our overall
                # config dict
                config_dict.merge(_rain_config_dict)
                # finally we need to remove any [StdWXCalculate] entries for
                # default rain field ('t_rain' or 'p_rain') that has now been
                # replaced with WeeWX field 'rain'
                # first remove any [[Delta]] entry that exists
                if rain_field in config_dict['StdWXCalculate'].get('Delta', {}):
                    # we have a [[[]]] stanza for our field, we need to delete it
                    _ = config_dict['StdWXCalculate']['Delta'].pop(rain_field)
                # now check to see if there is a corresponding [[Calculations]]
                # entry, if there is remove it
                if rain_field in config_dict['StdWXCalculate'].get('Calculations', {}):
                    # we have such a config entry, delete it
                    _ = config_dict['StdWXCalculate']['Calculations'].pop(rain_field)
            else:
                # no rainfall gauge was selected, all we need do is remove any
                # (now) unused [StdWXCalculate] config stanzas/options

                # do we have a [[Delta]] [[[rain]]], if so remove it
                if 'rain' in config_dict['StdWXCalculate'].get('Delta', {}) and \
                        config_dict['StdWXCalculate']['Delta']['rain'] in mapper.field_map.values():
                    # we have a [[[rain]]] stanza, we can safely delete it
                    _ = config_dict['StdWXCalculate']['Delta'].pop('rain')
                # if we went from a gauge to no gauge we need to restore the
                # default WeeWX per-period rain and rain rate fields
                if curr_gauge_type in ('tipping', 'piezo'):
                    # we went from a gauge to no gauge, construct a suitable config
                    # string to restore the default WeeWX per-period rain field
                    _rain_config_str = f"""
                        [StdWXCalculate]
                            [[Calculations]]
                                {curr_gauge_type[0]}_rain = prefer_hardware
                            [[Delta]]
                                [[[{curr_gauge_type[0]}_rain]]]
                                    input = {curr_gauge_type[0]}_rainyear"""
                    # convert the rain config string to a ConfigObj
                    _rain_config_dict = configobj.ConfigObj(io.StringIO(_rain_config_str))
                    # merge the rain config into our overall config
                    config_dict.merge(_rain_config_dict)
                # remove any rainRate field map extensions, this will restore the
                # original/default rain rate fields
                if 'field_map_extensions' in config_dict['EcowittHttp']:
                    # is there a rainRate field map extension, if so delete it
                    if 'rainRate' in config_dict['EcowittHttp']['field_map_extensions']:
                        # we have a rainRate entry, delete it
                        _ = config_dict['EcowittHttp']['field_map_extensions'].pop('rainRate')
                    # if there are no other field map extension entries remove the
                    # [[field_map_extensions]] stanza
                    if len(config_dict['EcowittHttp']['field_map_extensions']) == 0:
                        _ = config_dict['EcowittHttp'].pop('field_map_extensions')
            # finally, if we have ended up with no [StdWXCalculate] [[Delta]]
            # entries we can safely delete the entire [[Delta]] stanza
        else:
            # we have no paired gauges
            # our config is straightforward, we should leave [Calculations]
            # 'rain' as is, remove any 'rainRate' field map extensions, remove
            # any 'rain' or ''p_rain' deltas, remove any 'rain' deltas if
            # they use an Ecowitt HTTP driver sourced field
            if 'field_map_extensions' in config_dict['EcowittHttp'].keys():
                _ = config_dict['EcowittHttp']['field_map_extensions'].pop('rainRate', None)
                # finally, if we have ended up with no [EcowittHttp] [[field_map_extensions]]
                # entries we can safely delete the entire [[field_map_extensions]] stanza
                if len(config_dict['EcowittHttp']['field_map_extensions']) == 0:
                    _ = config_dict['EcowittHttp'].pop('field_map_extensions')
            if 'Delta' in config_dict['StdWXCalculate'].keys():
                # do we have a 'rain' delta and if so is it sourced from an
                # Ecowitt HTTP driver field
                if 'rain' in config_dict['StdWXCalculate']['Delta'] and \
                        config_dict['StdWXCalculate']['Delta']['rain'].get('input') in mapper.field_map.values():
                    # we an Ecowitt HTTP driver rain delta, remove it
                    _ = config_dict['StdWXCalculate']['Delta'].pop('rain', None)
                # remove any other Ecowitt sourced deltas
                _ = config_dict['StdWXCalculate']['Delta'].pop('rain', None)
                _ = config_dict['StdWXCalculate']['Delta'].pop('p_rain', None)
                # finally, if we have ended up with no [StdWXCalculate] [[Delta]]
                # entries we can safely delete the entire [[Delta]] stanza
                if len(config_dict['StdWXCalculate']['Delta']) == 0:
                    _ = config_dict['StdWXCalculate'].pop('Delta')

    @staticmethod
    def do_archive_record_generation(config_dict):
        """Configure archive record generation.

        Create [StdArchive] config entry to force software record generation.
        """

        print()
        # there is no user input for this, but inform the user what we are
        # doing
        print("""Setting record_generation to software.""")
        # update the record_generation setting directly
        config_dict['StdArchive']['record_generation'] = 'software'

    @staticmethod
    def do_extractors(config_dict):
        """Configure extractors.

        Create [Accumulator] config entries to set extractor functions for
        driver unique WeeWX fields requiring non-default (average) extractors.
        """

        print()
        # there is no user input for this, but inform the user what we are
        # doing
        print("""Setting accumulator extractor functions.""")
        # construct our default accumulator config dict
        accum_config_dict = configobj.ConfigObj(io.StringIO(EcowittHttpDriverConfEditor.accum_config_str))
        # merge the existing config dict into our default accumulator config
        # dict before merging tje updated accumulator config dict into our
        # config dict, doing the merge in this manner is wasteful but preserves
        # any existing accumulator config settings originally in config_dict
        accum_config_dict.merge(config_dict)
        # now merge the updated accumulator config into the config dict
        config_dict.merge(accum_config_dict)


# ============================================================================
#                        class EcowittHttpDriverConfigurator
# ============================================================================

class EcowittHttpDriverConfigurator(weewx.drivers.AbstractConfigurator):
    """Configures the Ecowitt device.

    This class is used by wee_device when interrogating a supported Ecowitt
    device.

    The Ecowitt local HTTP API supports both reading and setting various device
    parameters; however, at this time the Ecowitt local HTTP API driver only
    supports the reading these parameters. The Ecowitt local HTTP API driver
    does not support setting these parameters, rather this should be done via
    the Ecowitt WSView Plus or the Ecowitt device web page.

    When used with wee_device this configurator allows station hardware
    parameters to be displayed. The Ecowitt local HTTP API driver may also be
    run directly to test the Ecowitt local HTTP API driver operation as well as
    display various driver configuration options (as distinct from device
    hardware parameters).
    """

    @property
    def description(self):
        """Description displayed as part of weectl device help information."""

        return "Read data and configuration from an Ecowitt device."

    @property
    def usage(self):
        """weectl device usage information."""
        return f"""{bcolors.BOLD}%prog --help
       %prog --live-data
            [CONFIG_FILE|--config=CONFIG_FILE]
            [--units=us|metric|metricwx]
            [--ip-address=IP_ADDRESS]
            [--show-all-batt]
            [--debug=0|1|2|3]
       %prog --sensors
            [CONFIG_FILE|--config=CONFIG_FILE]
            [--ip-address=IP_ADDRESS]
            [--show-all-batt]
            [--debug=0|1|2|3]
       %prog --firmware|--mac-address|--system-params|
            --get-rain-data|--get-all-rain_data
            [CONFIG_FILE|--config=CONFIG_FILE]
            [--ip-address=IP_ADDRESS]
            [--debug=0|1|2|3]
       %prog --get-calibration|--get-mulch-th-cal|
            --get-mulch-soil-cal|--get-pm25-cal|
            --get-co2-cal|--get-lds-cal|
            [CONFIG_FILE|--config=CONFIG_FILE]
            [--ip-address=IP_ADDRESS]
            [--debug=0|1|2|3]
       %prog --get-services
            [CONFIG_FILE|--config=CONFIG_FILE]
            [--ip-address=IP_ADDRESS]
            [--unmask] [--debug=0|1|2|3]{bcolors.ENDC}"""

    @property
    def epilog(self):
        """Epilog displayed as part of wee_device help information."""

        return ""
        # return "Mutating actions will request confirmation before proceeding.\n"

    def add_options(self, parser):
        """Define wee_device option parser options."""

        parser.add_option('--live-data', dest='live', action='store_true',
                          help='display device live sensor data')
        parser.add_option('--sensors', dest='sensors', action='store_true',
                          help='display device sensor information')
        parser.add_option('--firmware', dest='firmware',
                          action='store_true',
                          help='display device firmware information')
        parser.add_option('--mac-address', dest='mac', action='store_true',
                          help='display device station MAC address')
        parser.add_option('--system-params', dest='sys_params', action='store_true',
                          help='display device system parameters')
        parser.add_option('--get-rain-data', dest='get_rain', action='store_true',
                          help='display device traditional rain data only')
        parser.add_option('--get-all-rain-data', dest='get_rain_totals', action='store_true',
                          help='display device traditional, piezo and rain reset '
                               'time data')
        parser.add_option('--get-calibration', dest='calibration',
                          action='store_true',
                          help='display device calibration data')
        parser.add_option('--get-mulch-th-cal', dest='mulch_offset',
                          action='store_true',
                          help='display device multi-channel temperature and '
                               'humidity calibration data')
        parser.add_option('--get-mulch-soil-cal', dest='soil_calibration',
                          action='store_true',
                          help='display device soil moisture calibration data')
        parser.add_option('--get-mulch-t-cal', dest='get_temp_calibration',
                          action='store_true',
                          help='display device temperature (WN34) calibration data')
        parser.add_option('--get-pm25-cal', dest='pm25_offset',
                          action='store_true',
                          help='display device PM2.5 calibration data')
        parser.add_option('--get-co2-cal', dest='co2_offset',
                          action='store_true',
                          help='display device CO2 (WH45) calibration data')
        parser.add_option('--get-lds-cal', dest='lds_offset',
                          action='store_true',
                          help='display device LDS (WH54) calibration data')
        parser.add_option('--get-services', dest='services',
                          action='store_true',
                          help='display device weather services configuration data')
        parser.add_option('--ip-address', dest='ip_address',
                          help='device IP address to use')
        parser.add_option('--max-tries', dest='max_tries', type=int,
                          help='max number of attempts to contact the device')
        parser.add_option('--retry-wait', dest='retry_wait', type=int,
                          help='how long to wait between attempts to contact '
                               'the device')
        parser.add_option('--timeout', dest='timeout', type=int,
                          help='how long to wait for a device to respond to a '
                               'HTTP request')
        parser.add_option('--show-all-batt', dest='show_battery',
                          action='store_true',
                          help='show all available battery state data regardless of '
                               'sensor state')
        parser.add_option('--unmask', dest='unmask', action='store_true',
                          help='unmask sensitive settings')
        parser.add_option('--units', dest='units', metavar='UNITS', default='metric',
                          help='unit system to use when displaying live data')
        parser.add_option('--config', dest='config_path', metavar='CONFIG_FILE',
                          help="use configuration file CONFIG_FILE.")
        parser.add_option('--debug', dest='debug', type=int,
                          help='how much status to display, 0-3')
        parser.add_option('--yes', '-y', dest="noprompt", action="store_true",
                          help="answer yes to every prompt")

    def do_options(self, options, parser, config_dict, prompt):
        """Process weectl device option parser options."""

        # get station config dict to use
        stn_dict = config_dict.get('EcowittHttp', {})

        # set weewx.debug as necessary
        if options.driver_debug is not None:
            _debug = weeutil.weeutil.to_int(options.driver_debug)
        else:
            _debug = weeutil.weeutil.to_int(config_dict.get('debug', 0))
        weewx.debug = _debug
        # inform the user if the debug level is 'higher' than 0
        if _debug > 0:
            print(f"debug level is '{int(_debug):d}'")

        # Now we can set up the user customized logging
        weeutil.logger.setup('weewx', config_dict)

        # define custom unit settings used by the driver
        define_units()

        # get a DirectEcowittDevice object
        direct_http_gw = DirectEcowittDevice(options, parser, stn_dict)
        # now let the DirectEcowittDevice object process the options
        direct_http_gw.process_options()


# ============================================================================
#                               class Catchup
# ============================================================================

class Catchup:
    """Base class for an object that performs a catchup on WeeWX startup."""

    def __init__(self):
        """Initialize the object."""

        pass

    @property
    def name(self):
        """Return the name of the Catchup object."""

        return 'Not implemented'

    @property
    def source(self):
        """The source used by the Catchup object."""

        return 'Not implemented'

    def do_debug_logging(self):
        """Do any debug logging that is relevant to my source."""

        pass

# ============================================================================
#                          class EcowittNetCatchup
# ============================================================================

class EcowittNetCatchup(Catchup):
    """Class that implements catchup via Ecowitt.net API.

    Ecowitt devices do not include a hardware logger per se, though some
    devices do have the ability to record observational data to on board
    non-volatile memory (eg SD card). Those devices that do not have this
    capability do have the ability to independently upload observation data to
    Ecowitt.net at various integer (1-5) minute intervals provided the device
    has an active internet connection. Ecowitt provides an API to access this
    history data at Ecowitt.net. The Ecowitt.net history data provides a means
    for obtaining historical archive data, the data will likely differ slightly
    in values and times to the device generated archive data, but it may
    provide an effective 'virtual' logger capability to support catchup on
    startup.

    Ecowitt.net uses an age-based approach for aggregating data as follows:
    - station data from the past 90 days is stored using a five-minute interval
    - station data older than 90 days but from the past 365 days is stored
      using a 30-minute interval
    - station data older than 365 days but from the past 730 days is stored
      using a four-hour interval
    - station data older than 760 days but from the past 1460 days is stored
      using a 30-minute interval
    """

    # Ecowitt.net API endpoint
    endpoint = 'https://api.ecowitt.net/api/v3/device'
    # available Ecowitt.net API commands
    commands = ('real_time', 'history', 'list', 'info')
    # Ecowitt.net API result codes
    api_result_codes = {
        -1: 'System is busy',
        0: 'success result',
        40000: 'Illegal parameter',
        40010: 'Illegal Application_Key Parameter',
        40011: 'Illegal Api_Key Parameter',
        40012: 'Illegal MAC/IMEI Parameter',
        40013: 'Illegal start_date Parameter',
        40014: 'Illegal end_date Parameter',
        40015: 'Illegal cycle_type Parameter',
        40016: 'Illegal call_back Parameter',
        40017: 'Missing Application_Key Parameter',
        40018: 'Missing Api_Key Parameter',
        40019: 'Missing MAC Parameter',
        40020: 'Missing start_date Parameter',
        40021: 'Missing end_date Parameter',
        40022: 'Illegal Voucher type',
        43001: 'Needs other service support',
        44001: 'Media file or data packet is null',
        45001: 'Over the limit or other error',
        46001: 'No existing request',
        47001: 'Parse JSON/XML contents error',
        48001: 'Privilege Problem'
    }
    # default history call back
    default_call_back = ('outdoor', 'indoor', 'solar_and_uvi', 'rainfall',
                         'rainfall_piezo', 'wind', 'pressure', 'lightning',
                         'indoor_co2', 'co2_aqi_combo', 'pm25_aqi_combo',
                         'pm25_ch1', 'pm25_ch2', 'pm25_ch3',  'pm25_ch4', 
                         'pm10_aqi_combo', 'pm1_aqi_combo', 'pm4_aqi_combo',
                         't_rh_aqi_combo',
                         'temp_and_humidity_ch1', 'temp_and_humidity_ch2',
                         'temp_and_humidity_ch3', 'temp_and_humidity_ch4',
                         'temp_and_humidity_ch5', 'temp_and_humidity_ch6',
                         'temp_and_humidity_ch7', 'temp_and_humidity_ch8',
                         'soil_ch1', 'soil_ch2', 'soil_ch3', 'soil_ch4',
                         'soil_ch5', 'soil_ch6', 'soil_ch7', 'soil_ch8',
                         'soil_ch9', 'soil_ch10', 'soil_ch11', 'soil_ch12',
                         'soil_ch13', 'soil_ch14', 'soil_ch15', 'soil_ch16',
                         'temp_ch1', 'temp_ch2', 'temp_ch3', 'temp_ch4',
                         'temp_ch5', 'temp_ch6', 'temp_ch7', 'temp_ch8',
                         'leaf_ch1', 'leaf_ch2', 'leaf_ch3', 'leaf_ch4',
                         'leaf_ch5', 'leaf_ch6', 'leaf_ch7', 'leaf_ch8',
                         'battery',
                         'ch_lds1', 'ch_lds2', 'ch_lds3', 'ch_lds4')
    # Map from Ecowitt.net history fields to internal driver fields. Map is
    # keyed by Ecowitt.net history 'data set'. Individual key: value pairs are
    # Ecowitt.net field:driver field.
    net_to_driver_map = {
        'outdoor': {
            'temperature': 'common_list.0x02.val',
            'humidity': 'common_list.0x07.val'
        },
        'indoor': {
            'temperature': 'wh25.intemp',
            'humidity': 'wh25.inhumi'
        },
        'solar_and_uvi': {
            'solar': 'common_list.0x15.val',
            'uvi': 'common_list.0x17.val'
        },
        'rainfall': {
            'rain_rate': 'rain.0x0E.val',
            'event': 'rain.0x0D.val',
            'hourly': 't_rainhour',
            'daily': 'rain.0x10.val',
            'weekly': 'rain.0x11.val',
            'monthly': 'ain.0x12.val',
            'yearly': 'rain.0x13.val',
        },
        'rainfall_piezo': {
            'rain_rate': 'piezoRain.0x0E.val',
            'event': 'piezoRain.0x0D.val',
            'hourly': 'hrain_piezo',
            'daily': 'piezoRain.0x10.val',
            'weekly': 'piezoRain.0x11.val',
            'monthly': 'piezoRain.0x12.val',
            'yearly': 'piezoRain.0x13.val',
        },
        'wind': {
            'wind_speed': 'common_list.0x0B.val',
            'wind_gust': 'common_list.0x0C.val',
            'wind_direction': 'common_list.0x0A.val'
        },
        'pressure': {
            'absolute': 'wh25.abs',
            'relative': 'wh25.rel'
        },
        'lightning': {
            'distance': 'lightning.distance',
            'count': 'lightning.count'
        },
        'indoor_co2': {
            'co2': 'wh25.CO2',
            '24_hours_average': 'wh25.CO2_24H'
        },
        'pm25_ch1': {
            'pm25': 'ch_pm25.1.PM25'
        },
        'pm25_ch2': {
            'pm25': 'ch_pm25.2.PM25'
        },
        'pm25_ch3': {
            'pm25': 'ch_pm25.3.PM25'
        },
        'pm25_ch4': {
            'pm25': 'ch_pm25.4.PM25'
        },
        'co2_aqi_combo': {
            'co2': 'co2.CO2',
            '24_hours_average': 'co2.CO2_24H'
        },
        'pm25_aqi_combo': {
            'pm25': 'co2.PM25',
            'real_time_aqi': 'co2.PM25_RealAQI',
            '24_hours_aqi': 'co2.PM25_24HAQI'
        },
        'pm10_aqi_combo': {
            'pm10': 'co2.PM10',
            'real_time_aqi': 'co2.PM10_RealAQI',
            '24_hours_aqi': 'co2.PM10_24HAQI'
        },
        'pm1_aqi_combo': {
            'pm1': 'co2.PM1',
            'real_time_aqi': 'co2.PM1_RealAQI',
            '24_hours_aqi': 'co2.PM1_24HAQI'
        },
        'pm4_aqi_combo': {
            'pm4': 'co2.PM4',
            'real_time_aqi': 'co2.PM4_RealAQI',
            '24_hours_aqi': 'co2.PM4_24HAQI'
        },
        't_rh_aqi_combo': {
            'temperature': 'co2.temp',
            'humidity': 'co2.humidity'
        },
        'temp_and_humidity_ch1': {
            'temperature': 'ch_aisle.1.temp',
            'humidity': 'ch_aisle.1.humidity'
        },
        'temp_and_humidity_ch2': {
            'temperature': 'ch_aisle.2.temp',
            'humidity': 'ch_aisle.2.humidity'
        },
        'temp_and_humidity_ch3': {
            'temperature': 'ch_aisle.3.temp',
            'humidity': 'ch_aisle.3.humidity'
        },
        'temp_and_humidity_ch4': {
            'temperature': 'ch_aisle.4.temp',
            'humidity': 'ch_aisle.4.humidity'
        },
        'temp_and_humidity_ch5': {
            'temperature': 'ch_aisle.5.temp',
            'humidity': 'ch_aisle.5.humidity'
        },
        'temp_and_humidity_ch6': {
            'temperature': 'ch_aisle.6.temp',
            'humidity': 'ch_aisle.6.humidity'
        },
        'temp_and_humidity_ch7': {
            'temperature': 'ch_aisle.7.temp',
            'humidity': 'ch_aisle.7.humidity'
        },
        'temp_and_humidity_ch8': {
            'temperature': 'ch_aisle.8.temp',
            'humidity': 'ch_aisle.8.humidity'
        },
        'soil_ch1': {
            'soilmoisture': 'ch_soil.1.humidity'
        },
        'soil_ch2': {
            'soilmoisture': 'ch_soil.2.humidity'
        },
        'soil_ch3': {
            'soilmoisture': 'ch_soil.3.humidity'
        },
        'soil_ch4': {
            'soilmoisture': 'ch_soil.4.humidity'
        },
        'soil_ch5': {
            'soilmoisture': 'ch_soil.5.humidity'
        },
        'soil_ch6': {
            'soilmoisture': 'ch_soil.6.humidity'
        },
        'soil_ch7': {
            'soilmoisture': 'ch_soil.7.humidity'
        },
        'soil_ch8': {
            'soilmoisture': 'ch_soil.8.humidity'
        },
        'soil_ch9': {
            'soilmoisture': 'ch_soil.9.humidity'
        },
        'soil_ch10': {
            'soilmoisture': 'ch_soil.10.humidity'
        },
        'soil_ch11': {
            'soilmoisture': 'ch_soil.11.humidity'
        },
        'soil_ch12': {
            'soilmoisture': 'ch_soil.12.humidity'
        },
        'soil_ch13': {
            'soilmoisture': 'ch_soil.13.humidity'
        },
        'soil_ch14': {
            'soilmoisture': 'ch_soil.14.humidity'
        },
        'soil_ch15': {
            'soilmoisture': 'ch_soil.15.humidity'
        },
        'soil_ch16': {
            'soilmoisture': 'ch_soil.16.humidity'
        },

        'temp_ch1': {
            'temperature': 'ch_temp.1.temp'
        },
        'temp_ch2': {
            'temperature': 'ch_temp.2.temp'
        },
        'temp_ch3': {
            'temperature': 'ch_temp.3.temp'
        },
        'temp_ch4': {
            'temperature': 'ch_temp.4.temp'
        },
        'temp_ch5': {
            'temperature': 'ch_temp.5.temp'
        },
        'temp_ch6': {
            'temperature': 'ch_temp.6.temp'
        },
        'temp_ch7': {
            'temperature': 'ch_temp.7.temp'
        },
        'temp_ch8': {
            'temperature': 'ch_temp.8.temp'
        },
        'leaf_ch1': {
            'leaf_wetness': 'ch_leaf.1.humidity'
        },
        'leaf_ch2': {
            'leaf_wetness': 'ch_leaf.2.humidity'
        },
        'leaf_ch3': {
            'leaf_wetness': 'ch_leaf.3.humidity'
        },
        'leaf_ch4': {
            'leaf_wetness': 'ch_leaf.4.humidity'
        },
        'leaf_ch5': {
            'leaf_wetness': 'ch_leaf.5.humidity'
        },
        'leaf_ch6': {
            'leaf_wetness': 'ch_leaf.6.humidity'
        },
        'leaf_ch7': {
            'leaf_wetness': 'ch_leaf.7.humidity'
        },
        'leaf_ch8': {
            'leaf_wetness': 'ch_leaf.8.humidity'
        },
        'ch_lds1': {
            'air_ch1': 'ch_lds.1.air',
            'depth_ch1': 'ch_lds.1.depth',
            'lds_heat_ch1': 'ch_lds.1.total_heat'
        },
        'ch_lds2': {
            'air_ch2': 'ch_lds.2.air',
            'depth_ch2': 'ch_lds.2.depth',
            'lds_heat_ch2': 'ch_lds.2.total_heat'
        },
        'ch_lds3': {
            'air_ch3': 'ch_lds.3.air',
            'depth_ch3': 'ch_lds.3.depth',
            'lds_heat_ch3': 'ch_lds.3.total_heat'
        },
        'ch_lds4': {
            'air_ch4': 'ch_lds.4.air',
            'depth_ch4': 'ch_lds.4.depth',
            'lds_heat_ch4': 'ch_lds.4.total_heat'
        },
        'battery': {
            'ws1900_console': 'wh25.ws1900_batt',
            'ws1800_console': 'wh25.ws1800_batt',
            'ws6006_console': 'wh25.ws6006_batt',
            'console': 'wh25.console_batt',
            'wind_sensor': 'ws80.voltage',
            'haptic_array_battery': 'piezoRain.0x13.voltage',
            'haptic_array_capacitor': 'ws90cap_volt',
            'sonic_array': 'ws80.battery',
            'rainfall_sensor': 'wh40.voltage',
            #'rainfall_sensor': 'wn20.voltage',
            'soilmoisture_sensor_ch1': 'ch_soil.1.voltage',
            'soilmoisture_sensor_ch2': 'ch_soil.2.voltage',
            'soilmoisture_sensor_ch3': 'ch_soil.3.voltage',
            'soilmoisture_sensor_ch4': 'ch_soil.4.voltage',
            'soilmoisture_sensor_ch5': 'ch_soil.5.voltage',
            'soilmoisture_sensor_ch6': 'ch_soil.6.voltage',
            'soilmoisture_sensor_ch7': 'ch_soil.7.voltage',
            'soilmoisture_sensor_ch8': 'ch_soil.8.voltage',
            'soilmoisture_sensor_ch9': 'ch_soil.9.voltage',
            'soilmoisture_sensor_ch10': 'ch_soil.10.voltage',
            'soilmoisture_sensor_ch11': 'ch_soil.11.voltage',
            'soilmoisture_sensor_ch12': 'ch_soil.12.voltage',
            'soilmoisture_sensor_ch13': 'ch_soil.13.voltage',
            'soilmoisture_sensor_ch14': 'ch_soil.14.voltage',
            'soilmoisture_sensor_ch15': 'ch_soil.15.voltage',
            'soilmoisture_sensor_ch16': 'ch_soil.16.voltage',
            'temperature_sensor_ch1': 'ch_temp.1.voltage',
            'temperature_sensor_ch2': 'ch_temp.2.voltage',
            'temperature_sensor_ch3': 'ch_temp.3.voltage',
            'temperature_sensor_ch4': 'ch_temp.4.voltage',
            'temperature_sensor_ch5': 'ch_temp.5.voltage',
            'temperature_sensor_ch6': 'ch_temp.6.voltage',
            'temperature_sensor_ch7': 'ch_temp.7.voltage',
            'temperature_sensor_ch8': 'ch_temp.8.voltage',
            'leaf_wetness_sensor_ch1': 'ch_leaf.1.voltage',
            'leaf_wetness_sensor_ch2': 'ch_leaf.2.voltage',
            'leaf_wetness_sensor_ch3': 'ch_leaf.3.voltage',
            'leaf_wetness_sensor_ch4': 'ch_leaf.4.voltage',
            'leaf_wetness_sensor_ch5': 'ch_leaf.5.voltage',
            'leaf_wetness_sensor_ch6': 'ch_leaf.6.voltage',
            'leaf_wetness_sensor_ch7': 'ch_leaf.7.voltage',
            'leaf_wetness_sensor_ch8': 'ch_leaf.8.voltage',
            'ldsbatt_1': 'ch_lds.1.voltage',
            'ldsbatt_2': 'ch_lds.2.voltage',
            'ldsbatt_3': 'ch_lds.3.voltage',
            'ldsbatt_4': 'ch_lds.4.voltage',
        }
    }

    def __init__(self, **options):
        """Initialise an EcowittNetCatchup object."""

        # initialise my parent
        super().__init__()
        try:
            # save the user Ecowitt.net API key
            self.api_key = options['api_key']
        except KeyError:
            # pre-requisite api_key is missing, raise a CatchupObjectError with
            # a suitable error message
            # raise CatchupObjectError("API key not specified")
            self.api_key = None
            log.info("API key not specified")
        try:
            # save the user Ecowitt.net application key
            self.app_key = options['app_key']
        except KeyError:
            # pre-requisite app_key is missing, raise a CatchupObjectError with
            # a suitable error message
            # raise CatchupObjectError("Application key not specified")
            self.app_key = None
            log.info("Application key not specified")
        try:
            # save the device MAC address
            self.mac = options['mac']
            log.info("EcowittNetCatchup using MAC: %s", self.mac) 
        except KeyError:
            # could not obtain the device MAC address, raise a
            # CatchupObjectError with a suitable error message
            # raise CatchupObjectError('Device MAC address not found')
            self.mac = None
            log.info("Device MAC address not set")
        if self.api_key == None or self.app_key == None or self.mac == None:
           log.info("Missing Data for Ecowitt.net - so do not try to get data")

    @property
    def name(self):
        """The name of the Catchup object."""

        return 'Ecowitt.net Catchup'

    @property
    def source(self):
        """The source used by the Catchup object."""

        return 'Ecowitt.net'

    def do_debug_logging(self):
        """Do any debug logging that is relevant to my source."""

        log.info('EcowittNetCatchup: API key: %s '
                 'Application key: %s' % (obfuscate(self.api_key),
                                          obfuscate(self.app_key)))


    def gen_history_records(self, start_ts=None, stop_ts=None, **kwargs):
        """Generate archive-like records from Ecowitt.net API history data.

        Generator function that uses the Ecowitt.net API to obtain history data
        from Ecowitt.net and generate archive-like records suitable for catchup
        by the WeeWX Ecowitt local HTTP API driver. Generated records are
        timestamped from start_ts (earliest ts) to stop_ts (most recent ts)
        inclusive. If stop_ts is not specified records are generated up to and
        including the current system time.

        start_ts: Earliest timestamp for which archive-like records are to be
                  emitted. If earlier than midnight 90 days ago midnight 90
                  days ago is used. If not specified or specified as None
                  midnight at the start of the day 90 days earlier than the
                  system time is used. Optional, integer or None.
        stop_ts:  Latest timestamp for which archive-like records are to be
                  emitted. If not specified or specified as None the current
                  system time is used instead. Optional, integer or None.

        Keyword Arguments. Supported keyword arguments include:
        call_back: Tuple containing the Ecowitt.net history data set names to
                   be sought in the API request. If not specified the default
                   call back data sets (EcowittNetCatchup.default_call_back)
                   are used. Optional, tuple of strings.
        """

        # get the timestamp for midnight at the start of the day 90 days ago,
        # this is the earliest date-time for which Ecowitt.net can provide five
        # minute interval records

        start_90_dt = datetime.datetime.now() - datetime.timedelta(days=90)
        start_90_dt = start_90_dt.replace(minute=0, hour=0, second=0, microsecond=0)
        start_90_ts = time.mktime(start_90_dt.timetuple())
        # Check if we have a start timestamp and if so is it is earlier than
        # the timestamp for midnight at the start of the day 90 days ago.If we
        # do set the start timestamp to the timestamp for midnight at the start
        # of the day 90 days ago
        if start_ts is None or start_ts < start_90_ts:
            start_ts = start_90_ts
        # use the current system time if stop_ts was not specified
        adj_stop_ts = int(time.time()) if stop_ts is None else stop_ts
        # construct the call_back, this specifies the data sets to be included
        # in the API history request
        # first check if we were given a call_back to use, if not use the
        # default

        _call_back = kwargs.get('call_back') if 'call_back' in kwargs else self.default_call_back
        # construct the call_back string; the call_back is specified in a tuple
        # but the API requires a comma separated string
        call_back = ','.join(_call_back)
        # we can only obtain a max of one days data at a time from Ecowitt.net
        # so split our interval into a series of 'day' spans
        if not self.api_key == None and not self.app_key == None and not self.mac == None:
          for t_span in weeutil.weeutil.genDaySpans(start_ts, adj_stop_ts):
            # construct a dict containing the data elements to be included in
            # the API request

            #'temp_unitid': 1, = °C
            #'pressure_unitid': 3, = hPa
            #'wind_speed_unitid': 6, = m\/s
            #'rainfall_unitid': 12, = mm
            #'solar_irradiance_unitid': 16 = W\/m²
            #'distance = km
             
            data = {
                'application_key': self.app_key,
                'api_key': self.api_key,
                'mac': self.mac,
                # weeutil.weeutil.genDaySpans returns a 'midnight to midnight'
                # timespan. If we use the generated day span start and stop
                # timestamps when querying the Ecowitt.net API, the first
                # record in each query will actually belong to the previous
                # day. Plus we will have the last midnight record of a given
                # day appearing as the first record in the next days API query
                # causing a unique constraint warnings when saving archive
                # records to database. To avoid this add one second to the day
                # span start timestamp.
                'start_date': datetime.datetime.fromtimestamp(t_span.start + 1).strftime('%Y-%m-%d %H:%M:%S'),
                'end_date': datetime.datetime.fromtimestamp(t_span.stop).strftime('%Y-%m-%d %H:%M:%S'),
                'call_back': call_back,
                'cycle_type': '5min',
                'temp_unitid': 1,
                'pressure_unitid': 3,
                'wind_speed_unitid': 6,
                'rainfall_unitid': 12,
                'solar_irradiance_unitid': 16
            }
            # Obtain a day of history data via the Ecowitt.net API. We will
            # either receive data or encounter an exception if the request
            # failed or the data invalid. So wrap in a try .. except to catch
            # and handle any exceptions.
            try:
                day_data = self.request(command_str='history', data=data, headers=None)
            except (socket.timeout, urllib.error.URLError, InvalidApiResponseError) as e:
                # A technical comms error was encountered or the response
                # received contains invalid data, either way we cannot
                # continue. Any logging has already occurred so just raise the
                # exception.
                raise
            else:
                # parse the raw day data, this will give us an iterable we can
                # traverse to construct archive-like records for the day
                parsed_day_data = self.parse_history(day_data.get('data', dict()))
                # traverse the timestamped data for the day and construct and
                # yield records, we need the timestamps in ascending order
                for ts in sorted(parsed_day_data.keys()):
                    # ensure we are only yielding timestamps within our span of
                    # interest
                    if start_ts <= ts <= adj_stop_ts:
                        # Construct an outline record, the timestamp is the
                        # current timestamp in our parsed data. We don't (yet)
                        # need a usUnits field nor an interval field
                        rec = {'datetime': ts,
                               'interval': 5}
                        # add the rest of the parsed day data for this timestamp
                        rec.update(parsed_day_data[ts])
                        
                        # yield the archive-like record
                        yield rec

    def request(self, command_str, data=None, headers=None, max_tries=3):
        """Send a HTTP request to the Ecowitt.net API and return the response.

        Create a HTTP request with optional data and headers. Send the HTTP
        request to the device as a GET request and obtain the response. If an
        exception occurs the exception is logged and the request attempted
        again up to a total of max_tries attempts. The deserialized JSON
        response is returned. If after max_tries attempts a valid response has
        been received but cannot be deserialized, or is otherwise invalid, a
        InvalidApiResponseError exception is raised.

        command_str: a string containing the command to be sent,
                     eg: 'get_livedata_info'
        data: a dict containing key:value pairs representing the data to be
              sent
        headers: a dict containing headers to be included in the HTTP request
        max_tries: the maximum number of attempts to send the request

        Returns a deserialized JSON object or raises an exception
        """

        # ensure we have dicts for data and headers
        data_dict = {} if data is None else data
        headers_dict = {} if headers is None else headers
        # check if we have a command that we know about
        if command_str in EcowittNetCatchup.commands:
            # first convert any data to a percent-encoded ASCII text string
            data_enc = urllib.parse.urlencode(data_dict)
            # construct the endpoint and 'path' of the URL
            endpoint_path = '/'.join([EcowittNetCatchup.endpoint, command_str])
            # Finally add the encoded data. We need to add the data in this manner
            # rather than using the Request object's 'data' parameter so that the
            # request is sent as a GET request rather than a POST request.
            url = '?'.join([endpoint_path, data_enc])
            # create a Request object
            if weewx.debug >= 2:
                log.info("url: %s", url)
            req = urllib.request.Request(url=url, headers=headers_dict)
            # attempt to obtain a valid response max_tries times
            for attempt in range(max_tries):
                # wrap the request in a try..except in case we encounter and
                # error
                try:
                    # submit the request and obtain the raw response
                    with urllib.request.urlopen(req) as w:
                        # get charset used so we can decode the stream correctly
                        char_set = w.headers.get_content_charset()
                        # Now get the response and decode it using the headers
                        # character set. Be prepared for charset==None.
                        if char_set is not None:
                            response = w.read().decode(char_set)
                        else:
                            response = w.read().decode()
                except (socket.timeout, urllib.error.URLError) as e:
                    # Log the error. If this was the last attempt raise the
                    # exception, otherwise continue with the next attempt.
                    log.error('Failed to obtain data from Ecowitt.net on attempt %d' % (attempt + 1))
                    log.error('   **** %s' % e)
                    if attempt < max_tries - 1:
                        continue
                    else:
                        raise
                # we have a response, but first check it for validity
                try:
                    return self.check_response(response)
                except (InvalidApiResponseError, ApiResponseError) as e:
                    # The response is invalid or an explicit response error was
                    # returned or some other unexpected error occurred. Log the
                    # error. If this was the last attempt raise an
                    # InvalidApiResponseError exception, otherwise continue with
                    # the next attempt.
                    log.error('Invalid Ecowitt.net API response on attempt %d' % (attempt + 1))
                    log.error('   **** %s' % e)
                    if attempt < max_tries - 1:
                        continue
                    else:
                        raise InvalidApiResponseError(e) from e

    def check_response(self, response):
        """Check the validity of an API response.

        Checks the validity of an API response. Three checks are performed:

        1.  the response has a length > 0
        2.  the response is valid JSON
        3.  the response contains a field 'code' with the value 0

        If any check fails an appropriate exception is raised, if all checks
        pass the decoded JSON response is returned.

        response: Raw, character set decoded response from a HTTP request the
        Ecowitt.net API.

        Returns a deserialized JSON object or raises an exception.
        """

        # do we have a response
        if response is not None and len(response) > 0:
            # we have some sort of response, but is it JSON and is the response
            # code 0
            try:
                # attempt to decode the response as JSON
                json_resp = json.loads(response)
            except json.JSONDecodeError as e:
                # the response could not be decoded as JSON, raise an
                # InvalidApiResponseError exception
                raise InvalidApiResponseError(e)
            # we have JSON format response, but does the response contain
            # 'code' == 0
            if json_resp.get('code') == 0:
                # we have valid JSON and a (sic) 'success result', return the
                # JSON format response
                return json_resp
            else:
                # we have a non-zero 'code', raise an ApiResponseError
                # exception with a suitable error message
                code = json_resp.get('code', 'no code')
                raise ApiResponseError(f"Received API response error code "
                                       f"'{code}': {self.api_result_codes.get(code)}")
        else:
            # response is None or zero length, raise an InvalidApiResponseError
            # exception
            raise InvalidApiResponseError(f"Invalid API response received")

    def parse_history(self, history_data):
        """Parse Ecowitt.net history data"""

        #        history_data = json.loads(self.d).get('data', dict())
        # initialise a dict to hold the parsed data
        result = dict()
        # iterate over each set of data in history_data
        for set_name, set_data in history_data.items():
            # obtain the parsed set data
            parsed_set_data = self.parse_data_set(set_name, set_data)
            # the parsed set data is a dict of data keyed by timestamp, iterate
            # over each timestamp: data pair and add the data to the
            # corresponding timestamp in the parsed data accumulated so far
            for ts, ts_data in parsed_set_data.items():
                # if we have not previously seen this timestamp add an entry to
                # the parsed data results
                if ts not in result:
                    result[ts] = dict()
                # update the accumulated parsed data with the current parsed
                # data
                result[ts].update(ts_data)
        # return the accumulated parsed data
        return result

    def parse_data_set(self, set_name, data):
        """Parse a data set containing one or more observation types."""

        # initialise a dict to hold our accumulated results
        result = dict()
        # iterate over each observation type and its data in the data set
        for obs, obs_data in data.items():
            # obtain the field name to use, this is an internal
            field_name = self.get_field_name(set_name, obs)
            # if the field name is not None then add the current obs type data
            # to our results, if the field name is None then skip this obs type
            if field_name is not None:
                # obtain the parsed obs type data
                parsed_data = self.parse_float(obs_data)
                # iterate over the timestamp: data pairs and add them to our
                # accumulated results
                for ts, value in parsed_data.items():
                    # if we have not previously seen this timestamp add an
                    # entry to the parsed data results
                    if ts not in result:
                        result[ts] = dict()
                    # update the accumulated parsed data with the current
                    # parsed data
                    result[ts][field_name] = value
        # return the accumulated results
        return result

    @staticmethod
    def parse_float(data):
        """Parse an observation type consisting of floating point data.

        Each data set (eg 'outdoor', 'indoor', 'pressure' etc) equates to a
        JSON object (eg "outdoor", "indoor", "pressure" etc) and consists of
        one or more observation types (eg 'temperature', 'feels_like' etc)
        which also equate to JSON objects (eg "temperature", "feels_like" etc)
        containing timestamped observation values. Currently, this timestamped
        data exists in the JSON object "list" as a sequence of timestamp:value
        pairs where timestamp is a unix epoch timestamp enclosed in quotes and
        value is a numeric observation value again enclosed in quotes.

        The JSON "list" object is processed with each timestamp converted to an
        integer and the corresponding value converted to a floating point
        number. A dict of converted numeric timestamp:value pair is returned.
        The return dict may be in ascending timestamp order, but this is not
        guaranteed. If a timestamp string cannot be converted to an integer the
        timestamp:value pair is ignored. If a value cannot be converted to a
        floating point number the value is set to None.

        Example JSON data extract showing the 'outdoor' data set including the
        'temperature' and 'feels_like' observation types:

        ....
        "data": {
            "outdoor": {
                "temperature": {
                    "unit": "℃",
                    "list": {
                        "1722764400": "16.8",
                        "1722764700": "16.8",
                        "1722765000": "16.7",
                        "1722765300": "16.7"
                    }
                },
                "feels_like": {
                    "unit": "℃",
                    "list": {
                        "1722764400": "16.8",
                        "1722764700": "16.8",
                        "1722765000": "16.7",
                        "1722765300": "16.7"
                    }
                },
                ....
            },
            ....
        },
        ....
        """

        # initialise a dict to hold the result
        result = dict()
        # iterate over each ts, value pair in the 'list' entry in the source
        # data
        for ts_string, value_str in data['list'].items():
            # the ts is a string, try to convert to an int, if we cannot
            # skip the ts
            try:
                ts = int(ts_string)
            except ValueError:
                continue
            # Convert the value to a float and save to our result dict, if we
            # cannot convert to a float then save the value None
            try:
                result[ts] = float(value_str)
            except ValueError:
                result[ts] = None
        # return the result
        return result

    def get_field_name(self, set_name, obs):
        """Determine the destination field name to be used.

        The field names used in an Ecowitt.net API history response are
        different to those field names used internally within the Ecowitt local
        HTTP API driver. To allow Ecowitt.net API history obs data to be used
        by the Ecowitt local HTTP API driver each Ecowitt.net API obs data
        field must be mapped to an Ecowitt local HTTP API driver internal
        field.

        Some Ecowitt.net API history fields are not used by the Ecowitt local
        HTTP API driver and can be ignored. In these cases the value None is
        returned.

        Given an Ecowitt.net history set name and obs type a lookup table can
        be used to determine the applicable Ecowitt local HTTP API driver
        internal field.
        """

        # wrap in a try .. except so we can catch those API fields we will
        # ignore (ie not in the lookup table)
        try:
            # Obtain the driver field name from the lookup table. If the
            # Ecowitt.net history field is to be ignored there will be no
            # lookup table entry resulting in a KeyError.
            return self.net_to_driver_map[set_name][obs]
        except KeyError:
            # we can ignore this API field so return None
            return None


# ============================================================================
#                         class EcowittDeviceCatchup
# ============================================================================

class EcowittDeviceCatchup:
    """Class that implements catchup via local device history files.

    Some Ecowitt devices store history data files locally in non-volatile
    memory such as SD card. These history files record selected sensor data at
    regular user specified intervals. This history data can be used as a source
    for historical archive records used by WeeWX during the WeeWX catchup that
    is attempted during WeeWX startup.

    Class EcowittDeviceCatchup supports such a catchup from selected Ecowitt
    devices though:

    -   identifying and selecting history data files for use during catchup
    -   processing, parsing and mapping of history data records to produce
        archive like historical records suitable for use by the driver
        genArchiveRecords method
    """

    # history data file fields by WeeWX unit group that may require unit
    # conversion
    unit_groups_by_field = {
        'group_temperature': ('wh25.intemp', 'common_list.0x02.val', 'common_list.0x03.val', 'feelslike',
                              'ch_aisle.1.temp', 'ch_aisle.2.temp', 'ch_aisle.3.temp', 'ch_aisle.4.temp',
                              'ch_aisle.5.temp', 'ch_aisle.6.temp', 'ch_aisle.7.temp', 'ch_aisle.8.temp',
                              'dewpoint1', 'dewpoint2', 'dewpoint3', 'dewpoint4',
                              'dewpoint5', 'dewpoint6', 'dewpoint7', 'dewpoint8',
                              'heatindex1', 'heatindex2', 'heatindex3', 'heatindex4',
                              'heatindex5', 'heatindex6', 'heatindex7', 'heatindex8',
                              'ch_temp.1.temp', 'ch_temp.2.temp', 'ch_temp.3.temp', 'ch_temp.4.temp',
                              'ch_temp.5.temp', 'ch_temp.6.temp', 'ch_temp.7.temp', 'ch_temp.8.temp',
                              'co2.temperature', 'co2.temp'),
        'group_speed' : ('common_list.0x0B.val', 'common_list.0x0C.val'),
        'group_pressure': ('wh25.abs', 'wh25.rel', 'common_list.5.val'),
        'group_pressurevpd': ('common_list.5.val'),
        'group_rain': ('rain.0x0D.val', 'rain.0x10.val', 'rain.0x11.val', 'rain.0x12.val',
                       'rain.0x13.val', 'rain.0x0F.val', 'piezoRain.0x0D.val', 'piezoRain.0x10.val',
                       'piezoRain.0x11.val', 'piezoRain.0x12.val', 'piezoRain.0x13.val', 'piezoRain.0x0F.val'),
        'group_rainrate': ('rain.0x0E.val', 'piezoRain.0x0E.val'),
        'group_radiation': ('common_list.0x15.val', ),
        'group_distance': ('lightning.distance', ),
        'group_depth': ('ch_lds.1.air', 'ch_lds.2.air', 'ch_lds.3.air', 'ch_lds.4.air',
                        'ch_lds.1.depth', 'ch_lds.2.depth', 'ch_lds.3.depth', 'ch_lds.4.depth'
                        'ch_lds.1.total_height', 'ch_lds.2.total_height', 'ch_lds.3.total_height', 'ch_lds.4.total_height')
    }

    def __init__(self, **options):
        """Initialise an EcowittDeviceCatchup object."""

        # save the device IP address, wrap in a try..except so we can catch an
        # exception if an IP address is not provided
        try:
            self.ip_address = options['ip_address']
        except KeyError:
            # A device IP address was not provided, that means we cannot go
            # on. Raise a CatchupObjectError exception with an error message.
            raise CatchupObjectError('Device IP address not found.')
        # save the URL download timeout
        self.url_timeout = weeutil.weeutil.to_int(options.get('url_timeout',
                                                              DEFAULT_URL_TIMEOUT))
        # obtain an EcowittDevice object, we will use this object for
        # interacting with the device
        self.device = EcowittDevice(ip_address=self.ip_address,
                                    url_timeout=self.url_timeout)
        # save the device unit system to be used, if not specified use the default
        self.unit_system = weeutil.weeutil.to_int(options.get('unit_system',
                                                              DEFAULT_UNIT_SYSTEM))
        # save the grace time we will add to last_good_ts/start_ts to determine
        # which catchup records we accept
        self.catchup_grace = weeutil.weeutil.to_int(options.get('catchup_grace',
                                                                DEFAULT_CATCHUP_GRACE))
        # save the max number of retries when attempting to access a device
        # file
        # TODO. Look at making parameter, property and default names match better
        self.max_catchup_retries = weeutil.weeutil.to_int(options.get('max_retries',
                                                                      DEFAULT_CATCHUP_RETRIES))
        # Attempt to get the SD card info, this serves as a check whether the
        # devices support catchup via locally stored history data files. Wrap
        # in a try..except so an exception can be raised should the device not
        # support locally stored history data files.
        try:
            _ = self.device.get_sdmmc_info_data()
        except (DeviceIOError, ParseError):
            raise CatchupObjectError(f"{self.device.model} at '{self.ip_address}' does "
                                     f"not appear to support HTTP API based catchup")
        # save our driver debug settings
        self.driver_debug = options.get('driver_debug', DebugOptions())
        # obtain a suitable Mapper object to map the SD card history data, the
        # default map is what we want so pass an empty config
        self.mapper = SdMapper(driver_debug=self.driver_debug,
                               mapper_config={})

    def gen_history_records(self, start_ts=None):
        """Generator to yield archive like records from device history files.

        Obtain details of available device history data files then selects the
        files to be processed based on start_ts. Iterate over the history files
        to be processed in ascending date order, downloading each file,
        processing, mapping and unit converting any applicable records and
        finally yielding records in ascending date-time order.

        History file record fields are mapped to 'dotted' field names
        compatible with the local device HTTP API and unit converted as per the
        unit system in use.

        Generated records are archive like dicts that are timestamped and unit
        converted.
        """

        # first get details of available history files from the device, be
        # prepared to catch exceptions if a response could not be obtained from
        # the device or the response could not be parsed
        try:
            sdmmc_info = self.device.get_sdmmc_info_data()
        except (DeviceIOError, ParseError) as e:
            raise CatchupObjectError(f"{self.device.model} at '{self.ip_address}' does "
                                     f"not appear to support HTTP API based catchup")
        # extract a dict of lists of available, relevant history data files
        files = self.get_file_list(sdmmc_info, start_ts)
        # obtain the interval value, this is in minutes
        try:
            interval = int(sdmmc_info['info']['Interval'])
        except (KeyError, ValueError, TypeError) as e:
            # we could not find the 'Interval' key value or could not coalesce
            # an integer from the key value, either way we cannot continue,
            # raise a CatchupObjectError
            raise CatchupObjectError(f"Unable to determine history file record interval: {e}")
        # iterate over the dict of lists in oldest to newest year-month index
        # order
        for ym in sorted(files.keys()):
            # initialise a list to hold lists of records for each file for this
            # year-month
            month_lists_of_recs = []
            # iterate over each file for this year-month
            for file in files[ym]:
                if weewx.debug >= 2 or self.driver_debug.catchup:
                    log.info("Processing history file '%s' from %s at %s",
                             file, self.device.model, self.ip_address)
                # Obtain the records from all files belonging to this
                # year-month. The end result is a list of dicts keyed by the
                # record date-time.

                # first attempt to obtain the history file from the device, if
                # it cannot be obtained log it and continue
                try:
                    response = self.get_file(file)
                except DeviceIOError as e:
                    log.error("Unable to download history file '%s' from %s at %s",
                              file, self.device.model, self.ip_address)
                    continue
                # now try to decode the file contents, if the file cannot be
                # decoded log it and continue
                try:
                    # decode the
                    lines = [l.decode('utf-8') for l in response.readlines()]
                except UnicodeDecodeError as e:
                    log.error("Unable to decode file '%s' from %s at %s",
                              file, self.device.model, self.ip_address)
                    continue
                # Whilst the file contents have been downloaded and decoded
                # there might still be various control or special characters
                # (eg null characters, blank lines) that will cause the
                # DictReader to fail. Strip these problem characters/sequences
                # from the raw data.
                clean_lines = self.clean_data(lines)
                # finally, obtain a DictReader object so we can convert our
                # data to a sequence of dicts
                try:
                    csv_reader = csv.DictReader(clean_lines)
                except csv.Error as e:
                    log.error("Unable to parse CSV file '%s' from %s at %s",
                              file, self.device.model, self.ip_address)
                    continue
                # Process the raw csv data and obtain a list of records. Append
                # these records to our month list.
                month_lists_of_recs.append(self.process_raw_csv_data(csv_reader,
                                                                     start_ts,
                                                                     interval))
            # We now have all data for a given month. However, the data for a
            # given timestamp is potentially split across (possibly multiple)
            # lists of dicts. We need to coalesce the month data into a format
            # where all data for a given timestamp is in a single dict
            # ie record. We can do this efficiently using a defaultdict with
            # the result being a dict keyed by timestamp where each
            # corresponding value contains the amalgamated data for that
            # timestamp.

            # create a defaultdict using dict as the factory
            d = collections.defaultdict(dict)
            # iterate over the lists of 'list of dicts', ie the data from each
            # file
            for file_list in month_lists_of_recs:
                # iterate over the dicts in the list, ie the records from each
                # file
                for file_rec in file_list:
                    # 'update' the relevant defaultdict key (ie timestamp)
                    # value with corresponding data from the current file
                    d[file_rec['datetime']].update(file_rec)
            # the combined data will likely not be in date-time order, so sort
            # the data by ascending timestamp
            sorted_recs = sorted(list(d.values()), key=operator.itemgetter('datetime'))
            # now we can yield the records for the current year-month
            for rec in sorted_recs:
                yield rec

    def clean_data(self, raw_data):
        """Clean raw data to remove detritus that will upset a CSV dict reader."""

        # just in case the data has been sourced from the web we will remove
        # any HTML tags and blank lines that may exist
        clean_data = []
        for row in raw_data:
            # check for and remove any null bytes
            clean_row = row
            if "\x00" in row:
                clean_row = clean_row.replace("\x00", "")
                if weewx.debug >= 2 or self.driver_debug.catchup:
                    log.info('One or more null bytes found in and removed')
            if clean_row != "\n":
                # save anything that is not a blank line
                clean_data.append(clean_row)
        return clean_data

    def process_raw_csv_data(self, data_reader, start_ts, interval):
        """Process raw CSV data into archive like records.

        Process a csv reader object and return a list of archive like records.
        Each record will contain the key 'datetime' which holds the timestamp
        of the record and key 'interval' which holds the history file interval
        value. Other keys are present depending on available data.

        Returns a list of dicts (records).
        """

        # initialise a list to hold our result
        result = []
        # initialise a dict to hold details of units used in the history file
        units = {}
        # iterate over the record in our reader
        for row in data_reader:
            # obtain the record 'Time' field as an epoch timestamp, if the
            # 'Time' field cannot be parsed ignore the record and continue to
            # the next record
            try:
                ts = datetime.datetime.strptime(row['Time'], '%Y-%m-%d %H:%M').timestamp()
            except ValueError:
                # the 'Time' field could not be parsed, so ignore it and
                # continue with the next record
                continue
            # continue processing the record if the timestamp is within our
            # span of interest, otherwise skip the record
            if start_ts is None or ts > start_ts + self.catchup_grace:
                # if we have not already done so obtain the units in use
                if len(units) == 0:
                    units = self.get_units(row.keys())
                # map the record
                mapped_rec = self.mapper.map_data(rec=row)
                # Whilst the history record has now been mapped to a standard
                # set of field names, the units being used will be whatever
                # units the user has specified through the WS View+ app. We
                # need to convert as necessary so the record uses one of the
                # three WeeWX unit systems.
                converted_rec = self.convert_history_rec(mapped_rec, units)
                converted_rec['datetime'] = ts
                converted_rec['interval'] = interval
                # append the mapped data to our accumulated list of mapped
                # records
                result.append(converted_rec)
        # return our list of records, our list of recs may or may not be in
        # timestamp order, but it does not matter as the records are sorted
        # later once the month records are coalesced
        return result

    @staticmethod
    def get_units(keys):
        """Extract the history file units from the history file field names.

        Examines the field names for a history file (keys for a dictreader row)
        and determine the WeeWX unit name to be used for each WeeWX unit group.

        Returns a dict of WeeWX unit names keyed by WeeWX unit group.
        """

        # Create a dict for our result, pre-populate with those unit
        # groups/names for groups that only have a single unit (ie groups for
        # which Ecowitt only allows one possible unit, eg group_percent -
        # percent). Include groups/units not used by Ecowitt where WeeWX only
        # uses one unit for the group.
        units = {
            "group_altitude"    : "meter",
            "group_amp"         : "amp",
            "group_angle"       : "degree_angle",
            "group_boolean"     : "boolean",
            "group_concentration": "microgram_per_meter_cubed",
            "group_count"       : "count",
            "group_data"        : "byte",
            "group_db"          : "dB",
            # TODO. Should this group/unit be included?
            "group_degree_day"  : "degree_C_day",
            "group_deltatime"   : "second",
            "group_direction"   : "degree_compass",
            "group_elapsed"     : "second",
            "group_energy"      : "watt_hour",
            "group_energy2"     : "watt_second",
            "group_fraction"    : "ppm",
            "group_frequency"   : "hertz",
            "group_interval"    : "minute",
            "group_length"      : "cm",
            "group_moisture"    : "centibar",
            "group_percent"     : "percent",
            "group_power"       : "watt",
            "group_pressurerate": "mbar_per_hour",
            "group_time"        : "unix_epoch",
            "group_uv"          : "uv_index",
            "group_volt"        : "volt",
            "group_volume"      : "liter"
        }
        required_groups = {'group_temperature', 'group_speed', 'group_speed2',
                           'group_pressure', 'group_pressurevpd','group_rain', 'group_rainrate',
                           'group_radiation', 'group_distance', 'group_depth'
                           }
        found_groups = set()
        # iterate over the keys in the record
        for _key in keys:
            # do all our unit label comparisons in lower case to guard against
            # firmware changes that might (inadvertently or deliberately)
            # change the case of unit labels in SD card files
            key = _key.lower()
            # For temperature we check for keys containing 'Temperature'. Is
            # the key a 'temperature' and have we already set group_temperature
            # units.
            if 'temperature' in key and 'group_temperature' not in units:
                # we have a 'temperature' for the first time
                if 'c)' in key or chr(8451) in key:
                    # we have temperature in C (chr(8451) is a legacy unit
                    # symbol used by Ecowitt)
                    units['group_temperature'] = 'degree_C'
                    # update the found groups list
                    found_groups.add('group_temperature')
                elif 'f)' in key or chr(8457) in key:
                    # we have temperature in F (chr(8457) is a legacy unit
                    # symbol used by Ecowitt)
                    units['group_temperature'] = 'degree_F'
                    # update the found groups list
                    found_groups.add('group_temperature')
                continue
            # For pressure we check for keys containing 'Pressure'. Is the key
            # a 'pressure' and have we already set group_pressure units.
            if 'pressure' in key and 'group_pressure' not in units:
                # we have a 'pressure' for the first time
                if '(hpa)' in key:
                    # we have speed in hPa
                    units['group_pressure'] = 'hPa'
                    # update the found groups list
                    found_groups.add('group_pressure')
                elif '(inhg)' in key:
                    # we have pressure in inHg
                    units['group_pressure'] = 'inHg'
                    # update the found groups list
                    found_groups.add('group_pressure')
                elif '(mmhg)' in key:
                    # we have pressure in mmHg
                    units['group_pressure'] = 'mmHg'
                    # update the found groups list
                    found_groups.add('group_pressure')
                continue
            # For speed we check for keys containing 'Gust'. Is the key a
            # 'speed' and have we already set group_speed units.
            if 'gust' in key and 'group_speed' not in units:
                # we have a 'speed' for the first time
                if '(km/h)' in key:
                    # we have speed in km/h
                    units['group_speed'] = 'km_per_hour'
                    # it's likely not required but for consistency set the units
                    # for group_speed2 to the same as for group_speed
                    units['group_speed2'] = units['group_speed']
                    # update the found groups list
                    found_groups.add('group_speed')
                    found_groups.add('group_speed2')
                elif '(mph)' in key:
                    # we have speed in mph
                    units['group_speed'] = 'mile_per_hour'
                    # it's likely not required but for consistency set the units
                    # for group_speed2 to the same as for group_speed
                    units['group_speed2'] = units['group_speed']
                    # update the found groups list
                    found_groups.add('group_speed')
                    found_groups.add('group_speed2')
                elif '(m/s)' in key:
                    # we have speed in m/s
                    units['group_speed'] = 'meter_per_second'
                    # it's likely not required but for consistency set the units
                    # for group_speed2 to the same as for group_speed
                    units['group_speed2'] = units['group_speed']
                    # update the found groups list
                    found_groups.add('group_speed')
                    found_groups.add('group_speed2')
                elif '(knots)' in key:
                    # we have speed in knots
                    units['group_speed'] = 'knot'
                    # it's likely not required but for consistency set the units
                    # for group_speed2 to the same as for group_speed
                    units['group_speed2'] = units['group_speed']
                    # update the found groups list
                    found_groups.add('group_speed')
                    found_groups.add('group_speed2')
                elif '(nhg)' in key:
                    # we have speed in knots
                    units['group_speed'] = 'knot'
                    # it's likely not required but for consistency set the units
                    # for group_speed2 to the same as for group_speed
                    units['group_speed2'] = units['group_speed']
                    # update the found groups list
                    found_groups.add('group_speed')
                    found_groups.add('group_speed2')
                continue
            # For rain we check for keys containing 'Rain'. Is the key a 'rain'
            # and have we already set group_rain units.
            if 'rain' in key and 'group_rain' not in units:
                # we have a 'rain' for the first time
                if '(mm)' in key:
                    # we have rain in mm
                    units['group_rain'] = 'mm'
                    units['group_rainrate'] = 'mm_per_hour'
                    # update the found groups list
                    found_groups.add('group_rain')
                    found_groups.add('group_rainrate')
                elif '(in)' in key:
                    # we have rain in inches
                    units['group_rain'] = 'inch'
                    units['group_rainrate'] = 'inch_per_hour'
                    # update the found groups list
                    found_groups.add('group_rain')
                    found_groups.add('group_rainrate')
                continue
            # TODO. Operation of this section needs to be confirmed
            # Illuminance is a special case. Ecowitt sensors/suites do not
            # contain pyranometers, rather they contain a light sensor that
            # measures illuminance and then optionally uses this value to
            # approximate solar irradiance (or WeeWX field 'radiation') and
            # group_illuminance. Consequently, for 'illuminance=radiation!' we need to
            # look for a Solar Radiation field. Is the key a 'Solar Radiation'
            # and have we already set group_illuminance units.
            if 'solar rad' in key and 'group_radiation' not in units:
                # we have a 'Solar Radiation' for the first time
                if '(w/m2)' in key:
                    # we have ?? in W/m2
                    units['group_radiation'] = 'watt_per_meter_squared'
                    # update the found groups list
                    found_groups.add('group_radiation')
                elif '(klux)' in key:
                    # we have speed in kLux
                    units['group_illuminance'] = 'kilolux'
                    # update the found groups list
                    found_groups.add('group_illuminance')
                elif '(kfc)' in key:
                    # we have speed in KFC
                    units['group_illuminance'] = 'kfc'
                    # update the found groups list
                    found_groups.add('group_illuminance')
                continue
            # For distance we check for keys containing 'distance'. Is the key
            # a 'distance' and have we already set group_distance units.
            if 'distance' in key and 'group_distance' not in units:
                # we have a 'distance' for the first time
                if '(km)' in key:
                    # we have distance in km
                    units['group_distance'] = 'km'
                    # update the found groups list
                    found_groups.add('group_distance')
                elif '(mi)' in key:
                    # we have distance in miles
                    units['group_distance'] = 'mile'
                    # update the found groups list
                    found_groups.add('group_distance')
                elif '(nmi)' in key:
                    # we have distance in miles
                    units['group_distance'] = 'nautical_mile'
                    # update the found groups list
                    found_groups.add('group_distance')
                continue
            # For depth we check for keys containing 'LDS'. Is the key a
            # 'depth' and have we already set group_depth units.
            if 'lds' in key and 'group_depth' not in units:
                # we have a 'depth' for the first time
                if '(mm)' in key:
                    # we have depth in mm
                    units['group_depth'] = 'mm2'
                    # update the found groups list
                    found_groups.add('group_depth')
                elif 'cm)' in key:
                    # we have depth in cm
                    units['group_depth'] = 'cm2'
                    # update the found groups list
                    found_groups.add('group_depth')
                elif 'in)' in key:
                    # we have depth in inches
                    units['group_depth'] = 'inch2'
                    # update the found groups list
                    found_groups.add('group_depth')
                elif '(ft)' in key:
                    # we have depth in feet
                    units['group_depth'] = 'foot2'
                    # update the found groups list
                    found_groups.add('group_depth')
                continue
            # do we have entries for all required groups, if so we can finish
            # iterating
            if required_groups == found_groups:
                break
        # return our result
        return units

    def convert_history_rec(self, rec, units):
        """Convert a history record to a given unit system."""

        # make a copy of the source record as we may be altering it
        converted = dict(rec)
        # iterate over the unit groups that may require conversion
        for unit_group in self.unit_groups_by_field.keys():
            # iterate over each field belonging to the current unit group
            for field in self.unit_groups_by_field[unit_group]:
                if field in rec:
                    # obtain a ValueTuple representing the current field so we
                    # can use the WeeWX unit conversion machinery
                    try:
                        # Ecowitt have decided that when pressure units are set
                        # to 'hPa' VPD (common_list.5.val) will be returned in
                        # kPa. This will occur when the 'group_pressure' unit
                        # setting is hPa. Unfortunately, WeeWX can only use one
                        # pressure unit at a time so check if we have VPD and
                        # 'group_pressure' is set to hPa (this means VPD is in
                        # kPa) and if so do a pre-convert of the VPD kPa value
                        # to hPa.

                        if field == 'common_list.5.val' and units.get(unit_group) == 'hPa':
                            # we have VPD and it is in kPa, so convert the
                            # value to hPa
                            _val = rec[field] * 10
                        else:
                            # no need to do any pre-conversion
                            _val = rec[field]
                        # now we can express our value as a ValueTuple
                        _vt = weewx.units.ValueTuple(_val,
                                                     units.get(unit_group),
                                                     unit_group)
                    except (KeyError, TypeError, ValueError) as e:
                        # an error occurred creating a ValueTuple, log it and
                        # skip this field
                        if weewx.debug >= 3 or self.driver_debug.catchup:
                            log.info("Could not create ValueTuple for field '%s' "
                                     "with unit group '%s': %s",
                                     field, unit_group, e)
                        continue
                    # convert the ValueTuple to the unit system in use and save
                    # the converted value in our 'converted' record
                    try:
                        converted[field] = weewx.units.convertStd(_vt,
                                                                  self.unit_system).value
                    except Exception as e:
                        # an error occurred converting this field, log it and
                        # skip this field
                        if weewx.debug >= 3 or self.driver_debug.catchup:
                            log.info("Could not convert field '%s' "
                                     "with unit group '%s' to '%s': %s",
                                     field,
                                     unit_group,
                                     weewx.units.unit_nicknames[self.unit_system],
                                     e)
                        continue
        # return the converted record
        return converted

    def get_file(self, file_name):
        """Attempt to obtain a file from a device with retries.

        Used to obtain history data files from devices that support local
        storage of history data files. Returns the file contents or raises a
        DeviceIOError if the file cannot be opened.
        """

        url = ''.join(['http://', self.ip_address, ':81/', file_name])
        for attempt in range(self.max_catchup_retries):
            try:
                response = urllib.request.urlopen(url, timeout=self.url_timeout)
            except urllib.error.URLError as e:
                if attempt < self.max_catchup_retries - 1:
                    log.debug("Failed to obtain file '%s' after %d attempts: %s",
                              file_name, attempt + 1, e)
                    time.sleep(1)
                    continue
                else:
                    # we've used all our tries, log it and raise an exception
                    _msg = f"Failed to obtain file '{file_name}' after {attempt + 1} attempts: {e}"
                    log.error(_msg)
                    raise DeviceIOError(_msg)
            else:
                return response

    @staticmethod
    def get_file_list(sd_info, start_ts=None):
        """Extract a dict of history files from a get_sdmmc_info response.

        Extracts a dict of available history files from a get_sdmmc_info
        response. If start_ts is provided only names of files that may
        contain data on or after start_ts are returned. If start_ts is omitted
        or None then all available file names are returned.

        History file names are of the format 'YYYYMMxxxxxxxxZ.csv' where:

        YYYY    is the four digit year the file refers to
        MM      is the two digit (zero padded) month number the file refers to
        xxxxx   is an optional string which may be zero length or some other
                string (at present Ecowitt uses a zero length string or
                'Allsensors_' for xxxxx)
        Z       is an upper case alphabetical character to indicate changes to
                units, sensor names etc during a month. At the start of each
                month the character 'A' is used, then if there is a change to
                units or sensor name the character 'B' is used, then 'C' etc
                to 'Z'

        The resulting dict is keyed by an arbitrary calculated year-month
        index. Such an index facilitates easier discrimination and sorting of
        relevant history files. The index is a positive integer calculated
        using the following formula:

            YYYY * 100 + MM

            where YYYY is year number and MM is month number (1-12)

        The file list is then sorted by this index from low to high. A similar
        index is also calculated for start_ts and if start_ts is non-None only
        files whose index is >= the start_ts index are included in the
        response.

        Returns a dict keyed by year-month index with each entry containing a
        list of files for the year-month.
        """

        # obtain the history file data, it is contained in the file_list field
        # of the JSON data
        file_list = sd_info['file_list']
        # now extract a list of file names but only include those whose type
        # is 'file'
        files = [f['name'] for f in file_list if f['type'] == 'file']
        # Calculate an 'index' for start_ts based on the start_ts year and
        # month. The earlier the month and year the lower the index. This makes
        # it easier to sort files by date and exclude files that are too old.
        # If start_ts was not specified or is None we want all files so set the
        # index to zero.
        if start_ts is not None:
            # get the index for our ts
            # first get start_ts as a DateTime object
            ts_dt = datetime.datetime.fromtimestamp(start_ts)
            # now convert to a TimeTuple
            ts_tt = ts_dt.timetuple()
            # and finally calculate the index
            ts_index = ts_tt.tm_year * 100 + ts_tt.tm_mon
        else:
            # start_ts is None so we want all files, set the index to zero
            ts_index = 0
        # initialise a dict to hold the files names of interest
        indexed_files = {}
        # iterate over the list of files
        for file in files:
            # calculate an index for the file using the same method as for the
            # earlier start_ts index
            index = int(file[0:4]) * 100 + int(file[4:6])
            # compare the file and start_ts indices to determine if the file
            # might contain required data
            if index >= ts_index:
                # this file might contain required data
                if index not in indexed_files.keys():
                    # we have not seen a file from this year and month before
                    # so add an empty entry for the current file year-month
                    # index to our dict
                    indexed_files[index] = []
                # add the file to the list for the current year-month
                indexed_files[index].append(file)
        return indexed_files


# ============================================================================
#                          class EcowittHttpDriver
# ============================================================================

class EcowittHttpDriver(weewx.drivers.AbstractDevice, EcowittCommon):
    """Driver class for an Ecowitt device using the local HTTP API.

    A WeeWX driver to emit loop packets based on data obtained from an Ecowitt
    device using the local HTTP API. The EcowittHttpDriver should be used when
    the device is the sole WeeWX data source or where data from other sources
    is ingested by WeeWX via one or more WeeWX services.

    Data is obtained from the device via the device local HTTP API. The data is
    parsed and mapped to WeeWX fields and emitted as a WeeWX loop packet.

    The EcowittHttpCollector runs in a separate thread ensuring it does not
    block the main WeeWX processing loop. The EcowittHttpCollector uses child
    classes to interact directly with the HTTP API and parse the API responses
    respectively.
    """

    def __init__(self, **stn_dict):
        """Initialise an EcowittHttpDriver object."""

        # Log our driver version first. Normally we would call our superclass
        # initialisation method first; however, that involves establishing a
        # network connection to the device and it may fail. Doing some basic
        # logging first will aid in debugging.

        # log our version number
        log.info('EcowittHttpDriver: version is %s' % DRIVER_VERSION)
        # set the unit system we will emit
        self.unit_system = DEFAULT_UNIT_SYSTEM
        log.info("unit_system: %s" , (self.unit_system))
        # now initialize my superclasses
        try:
            EcowittCommon.__init__(self, unit_system=self.unit_system, **stn_dict)
        except weewx.ViolatedPrecondition as e:
            # we encountered an error during initialization and we cannot
            # continue, raise a ServiceInitializationError
            raise weewx.engine.InitializationError from e
        # save the catchup settings
        catchup_dict = stn_dict.get('catchup', dict())
        # the source
        self.catchup_source = catchup_dict.get('source')
        #self.catchup_source = device
        log.info("catchup source: %s" , (self.catchup_source))

        # the grace period applied to any catchup record timestamps
        self.catchup_grace = weeutil.weeutil.to_int(catchup_dict.get('grace',
                                                                     DEFAULT_CATCHUP_GRACE))
        # the number of retries to use for catchup file downloads
        self.catchup_retries = catchup_dict.get('retries', DEFAULT_CATCHUP_RETRIES)
        # start the EcowittHttpCollector in its own thread
        self.collector.startup()

    def genLoopPackets(self):
        """Generator function that returns loop packets.

        Run a continuous loop checking the collector queue for data. Queue data
        will be either obs data, and exception or None. When obs data arrives
        map the raw data to a WeeWX loop packet and yield the packet. If an
        exception arrives hande any further logging and re-raising. None is the
        signal we need to close.
        """

        # attempt to generate loop packets forever
        while True:
            # wrap in a try..except to catch any instances where the queue is
            # empty
            try:
                # get any data from the collector queue
                queue_data = self.collector.queue.get(True, 10)
            except queue.Empty:
                # there was nothing in the queue so continue
                pass
            else:
                # We received something in the queue, it will be one of three
                # things:
                # 1. a dict containing sensor data
                # 2. a tuple containing an exception and it's text
                # 3. the value None signalling a serious error that means the
                #    collector needs to shut down

                # if the data has a 'keys' attribute it is a dict so must be
                # data
                if hasattr(queue_data, 'keys'):
                    # we have a dict so assume it is data
                    # log the received data if necessary
                    if self.driver_debug.loop:
                        if 'datetime' in queue_data:
                            log.info('EcowittHttpDriver: Loop Received %s data: %s %s' % (self.collector.device.model,
                                                                                     timestamp_to_string(queue_data['datetime']),
                                                                                     natural_sort_dict(queue_data)))
                        else:
                            log.info('EcowittHttpDriver: Loop Received %s data: %s' % (self.collector.device.model,
                                                                                  natural_sort_dict(queue_data)))
                    else:
                        # perhaps we have individual debugs such as rain or
                        # wind
                        if self.driver_debug.rain:
                            # debug.rain is set so log the 'rain' field in the
                            # received data
                            self.log_rain_data(queue_data,
                                               f'EcowittHttpDriver: Loop Received {self.collector.device.model} data')
                        if self.driver_debug.wind:
                            # debug.wind is set so log the 'wind' fields in the
                            # received data
                            self.log_wind_data(queue_data,
                                               f'EcowittHttpDriver: Loop Received {self.collector.device.model} data')
                    # Now start creating a loop packet. A loop packet must
                    # have a timestamp, if we have one (key 'datetime') in the
                    # received data use it, otherwise allocate one based on the
                    # current system time.
                    if 'datetime' in queue_data:
                        packet = {'dateTime': queue_data['datetime']}
                    else:
                        # we don't have a timestamp so create one
                        packet = {'dateTime': int(time.time() + 0.5)}
                    # add 'usUnits' to the packet
                    packet['usUnits'] = self.unit_system
                    # use our mapper to map the raw data to WeeWX loop packet
                    # fields

                    # Krenn Werner - hier korrigieren Regen und Blitz

                    ## if not already determined, determine which cumulative rain
                    ## field will be used to determine the per period rain field
                    if not self.rain_mapping_confirmed or not self.piezo_rain_mapping_confirmed:
                        self.get_cumulative_rain_field(queue_data)
                    ## get the rainfall this period from total
                    self.calculate_rain(queue_data)
                    ## get the lightning strike count this period from total
                    #log.info('queue_data %s' , queue_data)
                    if not self.lightning_mapping_confirmed:
                       if 'lightning.count' in queue_data:
                          self.lightning_mapping_confirmed = True

                    if 'lightning.count' in queue_data: 
                       packet['lightning_num'] = queue_data['lightning.count']
                    self.calculate_lightning_count(queue_data)

                    #if 'common_list.5.val' in queue_data:
                    #  log.info("loop VPD: %s ", queue_data['common_list.5.val'])

                    packet['rain'] = self.last_rainnew
                    packet['hail'] = self.piezo_last_rainnew
                    packet['p_rain'] = self.piezo_last_rainnew

                    ## map the raw data to WeeWX loop packet fields
                    mapped_data = self.mapper.map_data(queue_data)

                    # log the mapped data if necessary
                    if self.driver_debug.loop:
                        if 'datetime' in mapped_data:
                            log.info('EcowittHttpDriver: Loop Mapped %s data: %s %s' % (self.collector.device.model,
                                                                                   timestamp_to_string(mapped_data['dateTime']),
                                                                                   natural_sort_dict(mapped_data)))
                        else:
                            log.info('EcowittHttpDriver: Loop Mapped %s data: %s' % (self.collector.device.model,
                                                                                natural_sort_dict(mapped_data)))
                    else:
                        # perhaps we have individual debugs such as rain or wind
                        if self.driver_debug.rain:
                            # debug.rain is set so log the 'rain' field in the
                            # mapped data, if it does not exist say so
                            self.log_rain_data(mapped_data,
                                               f'EcowittHttpDriver: Loop Mapped {self.collector.device.model} data')
                        if self.driver_debug.wind:
                            # debug.wind is set so log the 'wind' fields in the
                            # mapped data, if they do not exist say so
                            self.log_wind_data(mapped_data,
                                               f'EcowittHttpDriver: Loop Mapped {self.collector.device.model} data')
                    # add the mapped data to the empty packet
                    packet.update(mapped_data)
                    # log the packet if necessary, there are several debug
                    # settings that may require this, start from the highest
                    # (most encompassing) and work to the lowest (least
                    # encompassing)
                    if self.driver_debug.loop or weewx.debug >= 2:
                        log.info('EcowittHttpDriver: Loop Packet %s: %s' % (timestamp_to_string(packet["dateTime"]),
                                                                       natural_sort_dict(packet)))
                    else:
                        # perhaps we have individual debugs such as rain or wind
                        if self.driver_debug.rain:
                            # debug.rain is set so log the 'rain' field in the
                            # loop packet being emitted, if it does not exist
                            # say so
                            self.log_rain_data(mapped_data,
                                               f'EcowittHttpDriver: Loop Packet {timestamp_to_string(packet["dateTime"])}')
                        if self.driver_debug.wind:
                            # debug.wind is set so log the 'wind' fields in the
                            # loop packet being emitted, if they do not exist
                            # say so
                            self.log_wind_data(mapped_data,
                                               f'EcowittHttpDriver: Loop Packets {timestamp_to_string(packet["dateTime"])}')
                    # we are done, so yield the loop packet
                    yield packet
                # if it's a tuple then it's an exception with the tuple
                # containing an exception and exception text
                elif isinstance(queue_data, BaseException):
                    # We have an exception. The collector did not deem it
                    # serious enough to want to shut down otherwise it would
                    # have sent None instead. The action we take depends on
                    # the type of exception it is. If it's a DeviceIOError we
                    # need to force the WeeWX engine to restart by raising a
                    # WeewxIOError. If it is anything else we log it and then
                    # raise it.

                    # first extract our exception
                    e = queue_data
                    # and process it if we have something
                    if e:
                        # is it a DeviceIOError
                        if isinstance(e, DeviceIOError):
                            # it is, so we raise a WeewxIOError
                            raise weewx.WeeWxIOError from e
                        # it's not so log it
                        log.error('EcowittHttpDriver: Loop Caught unexpected exception %s: %s' % (e.__class__.__name__,
                                                                                             e))
                        # then raise it, WeeWX will decide what to do
                        raise e
                # if it's None then it's a signal the Collector needs to shut
                # down
                elif queue_data is None:
                    # if debug.loop log what we received
                    if self.driver_debug.loop:
                        log.info('EcowittHttpDriver: Received shutdown signal from the Collector')
                    # we received the signal to shut down, so call closePort()
                    self.closePort()
                    # and raise an exception to cause the engine to shut down
                    raise DeviceIOError("EcowittHttpCollector needs to shutdown")
                # if it's none of the above (which it should never be) we don't
                # know what to do with it, so pass and wait for the next item in
                # the queue
                else:
                    pass

    def genStartupRecords(self, last_ts):
        """Generator to return archive records on WeeWX startup.

        genStartupRecords() is called on WeeWX startup to allow catchup of any
        missing records since WeeWX last stopped/restarted.

        last_ts is the timestamp of the last good archive record at time of
        startup/restart; last_ts will be None if the WeeWX archive is empty.
        The default driver genStartupRecords() action is to call
        genArchiveRecords(). In the case of the Ecowitt HTTP driver
        genStartupRecords() is overridden to cater for some additional debug
        output before genArchiveRecords() is called.

        last_ts: the timestamp after which startup archive records are to be
                 generated, may be None

        Returns a generator function yielding archive records timestamped after
        last_ts.
        """

        return self.genArchiveRecords(last_ts)

    def genArchiveRecords(self, lastgood_ts):
        """Generator to return archive records timestamped after a given time.

        Ecowitt now provides the ability to obtain archive-like records from
        either the local device or Ecowitt.net. Note that at the time of
        release the GW3000 is the only device that supports external access to
        stored archive-like records. Note also that Ecowitt.net uses a sliding
        scale of data aggregation such that data from the past 90 days is
        aggregated using a five-minute interval, but data older than 90 days is
        aggregated using a 30 minute, four hour or 24-hour aggregation period
        depending on age.

        genArchiveRecords() is called by genStartupRecords() on WeeWX startup
        to allow catchup of any missing archive records since WeeWX last
        stopped/restarted. The Ecowitt HTTP driver support catchup from the
        local device (if supported) or from Ecowitt.net. The default driver
        action is to first attempt local device catchup and if unsuccessful
        catchup from Ecowitt.net is attempted. If this is unsuccessful catchup
        is abandoned. This behaviour can be tailored by use of the driver
        catchup_source config option.

        lastgood_ts is the timestamp of the last good archive record at time of
        startup/restart; lastgood_ts will be None if the WeeWX archive is
        empty. At this time the Ecowitt.net catchup limits itself archive-like
        records within the last 90 days to ensure catchup records have a
        five-minute interval. The default driver genStartupRecords() action is to call
        genArchiveRecords().

        lastgood_ts: the timestamp after which historical archive records are
                     to be generated, may be None

        Returns a generator function yielding archive records timestamped after
        lastgood_ts.
        """

        # if necessary log the MAC address being used
        if self.driver_debug.catchup:
            log.info('genArchiveRecords: Using MAC address: %s' % self.mac_address)
        try:
            for rec in self.gen_ecowitt_archive_records(since_ts=lastgood_ts):
                # if necessary log the timestamp of the record being yielded
                if self.driver_debug.catchup:
                    log.info('genArchiveRecords: Yielding archive '
                             'record %s' % timestamp_to_string(rec['dateTime']))
                yield rec
        except DeviceIOError as e:
            # we encountered a serious problem accessing the device, log it,
            # and we exit genArchiveRecords
            log.error('genArchiveRecords: History access error: %s', e)

    def gen_ecowitt_archive_records(self, since_ts):
        """Generator to return Ecowitt archive records.

        Uses a factory method to create a suitable 'catchup' object to obtain
        archive-like records from either the local device (if supported) or
        Ecowitt.net. Archive-like records timestamped after since_ts are then
        mapped and formatted into WeeWX archive records. These archive records
        are then yielded in ascending timestamp order.

        since_ts: the timestamp after which historical archive records are to
                  be generated, may be None

        Returns a generator function yielding archive records timestamped after
        since_ts.
        """

        # first try to obtain a suitable 'catchup source' object, be prepared
        # to catch the exception raised if catchup is not available
        try:
            catchup_obj = self.catchup_factory()
        except CatchupObjectError as e:
            # we could not obtain a catchup source object so catchup is not available
            pass
        else:
            # we have a 'catchup source' object, iterate over the history
            # records obtained from the catchup source
            for rec in catchup_obj.gen_history_records(start_ts=since_ts):
                # initialise a dict to hold our history archive record, its
                # timestamp will be in the 'datetime' field and the unit system
                # will be our as per my unit_system property
                record = {'dateTime': rec['datetime'],
                          'usUnits': self.unit_system,
                          'interval': rec['interval']}
                # map the history data to WeeWX archive record/loop packet fields

                # Krenn Werner - korrigieren Regen und Blitz for archive

                if not self.rain_mapping_confirmed_a:
                   if 'rain.0x13.val' in rec:
                       self.rain_total_field = 'rain.0x13.val'
                       self.rain_mapping_confirmed_a = True
                   elif 'rain.0x12.val' in rec:
                       self.rain_total_field = 'rain.0x12.val'
                       self.rain_mapping_confirmed_a = True
                   else:
                       self.rain_total_field = None
                   if self.rain_mapping_confirmed_a:
                       log.info("Archive: using '%s' for rain total" % self.rain_total_field)
                   elif self.driver_debug.rain:
                       log.info("Archive: no suitable field found for rain")

                if not self.piezo_rain_mapping_confirmed_a:
                   if 'piezoRain.0x13.val' in rec:
                       self.piezo_rain_total_field = 'piezoRain.0x13.val'
                       self.piezo_rain_mapping_confirmed_a = True
                   elif 'piezoRain.0x12.val' in rec:
                       self.piezo_rain_total_field = 'piezoRain.0x12.val'
                       self.piezo_rain_mapping_confirmed_a = True
                   else:
                       self.piezo_rain_total_field = None
                   if self.piezo_rain_mapping_confirmed_a:
                       log.info("Archive: using '%s' for piezo rain total" % self.piezo_rain_total_field)
                   elif self.driver_debug.rain:
                       log.info("Archive: no suitable field found for piezo rain")

                if self.rain_mapping_confirmed_a and self.rain_total_field_a in rec:
                    new_total = rec[self.rain_total_field]
                    self.last_rainnew_a = self.delta_rain(new_total, self.last_rain_a)
                    # if debug_rain is set log some pertinent values
                    if self.driver_debug.rain:
                        log.info("Archive: calculate_rain: last_rain=%s new_total=%s calculated rain=%s" % (self.last_rain_a,
                                                                                         new_total,
                                                                                         self.last_rainnew_a))
                    self.last_rain_a = new_total

                if self.piezo_rain_mapping_confirmed_a and self.piezo_rain_total_field_a in rec:
                    piezo_new_total = rec[self.piezo_rain_total_field]
                    self.piezo_last_rainnew_a = self.delta_rain(piezo_new_total,
                                             self.piezo_last_rain_a,
                                             descriptor='piezo rain')
                    if self.driver_debug.rain:
                        log.info("Archive: calculate_rain: piezo_last_rain=%s piezo_new_total=%s "
                               "calculated p_rain=%s" % (self.piezo_last_rain_a,
                                                 piezo_new_total,
                                                 self.piezo_last_rainnew_a))
                    self.piezo_last_rain_a = piezo_new_total

                # self.last_lightning = None
                # self.lightning_mapping_confirmed = False
                # self.last_lightningcount = None
                # self.last_lightningtime = None

                #if 'lightning.count' and 'lightning.timestamp'in rec:
                #    if not self.lightning_mapping_confirmed:                        
                #       self.last_lightningcount = rec['lightning.count']
                #       self.last_lightningtime = rec['lightning.timestamp']
                #       self.lightning_mapping_confirmed = True
                #    newtot = rec['lightning.count']
                #    newtime = rec['lightning.timestamp']
                #    rec['lightning_strike_count'] = self._delta_lightning_num(newtot, self.last_lightningcount, newtime, self.last_lightningtime)
                #    self.last_lightningcount = newtot
                #    self.last_lightningtime = newtime

                if not self.lightning_mapping_confirmed_a:
                   if 'lightning.count' in rec:
                       self.lightning_mapping_confirmed_a = True

                if self.lightning_mapping_confirmed_a and 'lightning.count' in rec:
                   new_total = rec['lightning.count']
                   rec['lightning.count'] = self.delta_lightning(new_total,
                                                                  self.last_lightning_a)
                   if self.driver_debug.lightning:
                      log.info("calculate_lightning: last_lightning_count=%s new_total=%s "
                               "calculated lightning_count=%s" % (self.last_lightning,
                                                           new_total,
                                                           data['lightning.count']))

                   self.last_lightning_a = new_total

                # is vpd missed?
                if 'common_list.5.val' not in rec:
                   #'outTemp': 'common_list.0x02.val',
                   #'vpd': 'common_list.5.val',
                   #'outHumidity': 'common_list.0x07.val',

                   try:
                     # tempc = (float(rec['common_list.0x02.val'])-32)*5/9
                     tempc = float(rec['common_list.0x02.val'])
                     humidity = float(rec['common_list.0x07.val'])
                     vpdtest = round(0.61094 * math.exp((17.625 * tempc) / (tempc + 243.04)) * (1 - humidity/100),2) * 10
                     #vpdtest = round(vpdtest/3.386,3) 
                   except:
                     vpdtest = None
                   #log.info("calc VPD: %s ", vpdtest)
                   if not vpdtest == None:
                      rec['common_list.5.val'] = vpdtest
 
 
                rec['rain'] = self.last_rainnew_a
                rec['hail'] = self.piezo_last_rainnew_a
                rec['p_rain'] = self.piezo_last_rainnew_a

                if self.driver_debug.archive: 
                   log.info('Archive rec data %s' , rec)

                mapped_data = self.mapper.map_data(rec)
                # add the mapped data to the empty record
                record.update(mapped_data)
                # yield the record
                yield record

    def catchup_factory(self):
        """Factory method to return a 'catchup source' object.

        Return a 'catchup source' object depending on our catchup_source
        property. If a 'catchup source' object cannot be created raise a
        CatchupObjectError.
        """
        # self.catchup_source = 'device'

        if self.catchup_source is None or self.catchup_source.lower() in ('either', 'both'):
            # no catchup source was specified, so first try to obtain a device
            # 'catchup' object
            try:
                return EcowittDeviceCatchup(ip_address=self.ip_address,
                                            unit_system=self.unit_system,
                                            catchup_grace=self.catchup_grace,
                                            catchup_retries=self.catchup_retries,
                                            url_timeout=self.url_timeout,
                                            driver_debug=self.driver_debug)
            except weewx.ViolatedPrecondition as e:
                # most likely our IP address is None, we cannot continue, raise
                # a CatchupObjectError from our exception
                raise CatchupObjectError from e
            except CatchupObjectError:
                pass
            # cannot obtain a local device 'catchup source' object so try
            # Ecowitt.net
            try:
                return EcowittNetCatchup(api_key=self.api_key,
                                         app_key=self.app_key,
                                         mac=self.mac_address,
                                         driver_debug=self.driver_debug)
            except CatchupObjectError:
                # we cannot obtain a 'catchup source' object of any type so
                # raise the CatchupObjectError
                raise
        elif self.catchup_source.lower() == 'net':
            # try to obtain an Ecowitt.net 'catchup source' object only
            try:
                return EcowittNetCatchup(api_key=self.api_key,
                                         app_key=self.app_key,
                                         mac=self.mac_address,
                                         driver_debug=self.driver_debug)
            except CatchupObjectError:
                # could not obtain an Ecowitt.net 'catchup source' object so
                # raise the CatchupObjectError
                raise
        elif self.catchup_source.lower() == 'device':
            # try to obtain a local device 'catchup' object only
            try:
                return EcowittDeviceCatchup(ip_address=self.ip_address,
                                            unit_system=self.unit_system,
                                            catchup_retries=self.catchup_retries,
                                            url_timeout=self.url_timeout,
                                            driver_debug=self.driver_debug)
            except CatchupObjectError:
                # could not obtain a local device 'catchup' object so raise the
                # CatchupObjectError
                raise
        else:
            # we cannot make sense of the catchup_source property so raise a
            # CatchupObjectError
            raise CatchupObjectError



# == Neu Archive ! Krenn Werner =======================================================

    @staticmethod
    def delta_rain(rain, last_rain_a, descriptor='rain'):
        """Calculate rainfall from successive cumulative values.

        rain:       current cumulative rain value
        last_rain:  last cumulative rain value
        descriptor: string to indicate what rain data we are working with
        """

        # do we have a last rain value
        if last_rain_a is None:
            # no, log it and return None
            log.info("Archive: skipping %s measurement of %s: no last rain" % (descriptor, rain))
            return None
        # do we have a non-None current rain value
        if rain is None:
            # no, log it and return None
            log.info("Archive: skipping %s measurement: no current rain data" % descriptor)
            return None
        # is the last rain value greater than the current rain value
        if rain < last_rain_a:
            # it is, assume a counter wrap around/reset, log it and return the
            # latest rain value
            log.info("Archive: %s counter wraparound detected: new=%s last=%s" % (descriptor, rain, last_rain_a))
            return rain
        # return the difference between the counts
        return rain - last_rain_a

    @staticmethod
    def delta_lightning(count, last_count_a):
        """Calculate lightning strike count from successive cumulative values.

        count:      current cumulative lightning count
        last_count_a: last cumulative lightning count
        """

        # do we have a last count
        if last_count_a is None:
            # no, log it and return None
            log.info("Archive: Skipping lightning count of %s: no last count" % count)
            return None
        # do we have a non-None current count
        if count is None:
            # no, log it and return None
            log.info("Archive: Skipping lightning count: no current count")
            return None
        # is the last count greater than the current count
        if count < last_count_a:
            # it is, assume a counter wrap around/reset, log it and return the
            # latest count
            log.info("Archive: Lightning counter wraparound detected: new=%s last=%s" % (count, last_count_a))
            return count
        # otherwise return the difference between the counts
        return count - last_count_a



    @property
    def hardware_name(self):
        """Return the device hardware name.

        Use the device model from our Collector's EcowittDevice object, but if
        this is None use the driver name.
        """

        if self.collector.device.model is not None:
            return self.collector.device.model
        return DRIVER_NAME

    @property
    def mac_address(self):
        """Return the device MAC address."""

        return self.collector.device.mac_address

    def closePort(self):
        """Close down the driver port."""

        # in this case there is no port to close, just shutdown the collector
        self.collector.shutdown()


# ============================================================================
#                              class Collector
# ============================================================================

class Collector:
    """Base class for a threaded client to pass data to a parent via a queue."""

    def __init__(self):
        # create a Queue object for passing data to a parent process
        self.queue = queue.Queue()

    def startup(self):
        pass

    def shutdown(self):
        pass


# ============================================================================
#                         class EcowittHttpCollector
# ============================================================================

class EcowittHttpCollector(Collector):
    """Class to collect and pass Ecowitt device data to a WeeWX service/driver.

    An EcowittHttpCollector object is responsible for collecting, parsing and
    dispatching data to a WeeWX driver/service. Specifically, an
    EcowittHttpCollector object:

    1. obtains data from an Ecowitt device via the local HTTP API,
    2. parses the data obtained from an Ecowitt device, and
    3. passes relevant parsed data to the parent driver/service.

    An EcowittHttpCollector object uses subordinate classes to obtain and parse
    data from the device. An EcowittHttpCollector object can also be used to
    obtain device data when the driver is operated in direct mode.
    """

    def __init__(self, ip_address,
                 poll_interval=DEFAULT_POLL_INTERVAL,
                 max_tries=DEFAULT_MAX_TRIES,
                 retry_wait=DEFAULT_RETRY_WAIT,
                 url_timeout=DEFAULT_URL_TIMEOUT,
                 unit_system=DEFAULT_UNIT_SYSTEM,
                 show_battery=DEFAULT_FILTER_BATTERY,
                 log_unknown_fields=False,
                 fw_update_check_interval=DEFAULT_FW_CHECK_INTERVAL,
                 debug = DebugOptions()):
        """Initialise a EcowittHttpCollector object."""

        # initialize my base class
        super().__init__()

        # interval between polls of the API, defaults to DEFAULT_POLL_INTERVAL
        self.poll_interval = poll_interval
        # save our debug options
        self.debug = debug
        # how often to check for a firmware update, defaults to
        # DEFAULT_FW_CHECK_INTERVAL
        self.fw_update_check_interval = fw_update_check_interval
        # log our config options before obtaining an EcowittDevice object, this
        # will help in remote debugging should the device be uncontactable
        if self.fw_update_check_interval > 0:
            log.info('     device firmware update checks will occur every %d '
                      'seconds' % self.fw_update_check_interval)
            log.info('     available device firmware updates will be logged')
        else:
            log.info('     device firmware update checks will not occur')
        if show_battery:
            log.info('     battery state will be reported for all sensors')
        else:
            log.info('     battery state will not be reported for sensors with no signal data')
        if log_unknown_fields:
            log.info('     unknown fields will be reported')
        else:
            log.info('     unknown fields will be ignored')

        # obtain an EcowittDevice object to handle interaction with the device
        self.device = EcowittDevice(ip_address=ip_address,
                                    unit_system=unit_system,
                                    max_tries=max_tries,
                                    retry_wait=retry_wait,
                                    url_timeout=url_timeout,
                                    show_battery=show_battery,
                                    log_unknown_fields=log_unknown_fields,
                                    debug=debug)

        # start by assuming we are logging failures
        self.log_failures = True
        # create a thread property
        self.thread = None
        # we start off not collecting data, it will be turned on later when we
        # are threaded
        self.collect_data = False

    def collect(self):
        """Collect and queue sensor data.

        Loop forever waking periodically to see if it is time to quit or
        collect more data. A dictionary of data is placed in the queue on each
        successful poll of the device. If an exception is raised when
        interacting with the device the exception is placed in the queue as a
        signal to our parent there is a problem.
        """

        # initialise ts of last time API was polled
        last_poll = 0
        # initialise ts of last firmware check
        last_fw_check = 0
        # collect data continuously while we are told to collect data
        while self.collect_data:
            # store the current time
            now = time.time()
            # is it time to poll?
            if now - last_poll > self.poll_interval:
                if self.debug.collector:
                    log.info("Polling the device, time '%d' "
                             "last poll '%d' elapsed '%d'", (int(now), int(last_poll), int(now - last_poll)))
                # it is time to poll, wrap in a try..except in case we get a
                # DeviceIOError exception
                try:
                    queue_data = self.get_current_data()
                except DeviceIOError as e:
                    # a DeviceIOError occurred, most likely because the
                    # EcowittDevice object could not contact the device
                    # first up log the event, but only if we are logging
                    # failures
                    if self.log_failures:
                        log.error('Unable to obtain live sensor data')
                    # assign the DeviceIOError exception to queue_data so it
                    # will be sent in the queue to our controlling object
                    queue_data = e

                if self.debug.collector:
                    log.info('Collected data: %s', queue_data)
                # put the queue data in the queue
                self.queue.put(queue_data)

                # debug log when we will next poll the API
                if weewx.debug: #or self.debug.collector:
                    log.info('Next update in %d seconds', self.poll_interval)
                # reset the last poll ts
                last_poll = now
                if self.debug.collector and (int(now - last_fw_check) >=300):
                    log.info("Firmware update check,  time '%d' "
                             "last check '%d' elapsed '%d'", int(now), int(last_fw_check), int(now - last_fw_check))
                # do a firmware update check if required
                if 0 < self.fw_update_check_interval < now - last_fw_check:
                    if self.debug.collector:
                        log.info('Performing firmware update check')
                    if self.device.firmware_update_avail:
                        _msg = f"A firmware update is available, current {self.device.model} "\
                               f"firmware version is {self.device.firmware_version}"
                        log.info(_msg)
                        _msg = f"    update at http://{self.device.ip_address} or via "\
                               f"the WSView Plus app"
                        log.info(_msg)
                        curr_msg = self.device.firmware_update_message
                        if curr_msg is not None:
                            log.info("    firmware update message: '%s'", curr_msg)
                        else:
                            log.info('    no firmware update message found')
                    last_fw_check = now
                    if self.debug.collector:
                        log.info('Firmware update check complete')
            # sleep for a second and then see if it's time to poll again
            time.sleep(1)

    def get_current_data(self):
        """Get all current sensor data.

        Return current sensor data, battery state data and signal state data
        for each sensor. The current sensor data consists of sensor data
        available through multiple API api_commands. Each API command response is
        parsed and the results accumulated in a dictionary. Battery and signal
        state for each sensor is added to this dictionary. The dictionary is
        timestamped and the timestamped accumulated data is returned. If the
        API does not return any data a suitable exception will have been
        raised.
        """

        # get a timestamp to use in case our data does not come with one
        _timestamp = int(time.time())
        # Now obtain the current data via the API. If the data cannot be
        # obtained we will see a DeviceIOError exception which we just let
        # bubble up. Otherwise, we are returned the parsed current live data.
        curr_data = self.device.get_live_data()

        curr_data.update(self.device.get_rain_totalspart())
        curr_data.update(self.device.get_piezo_rain_datapart())
        curr_data.update(self.device.get_device_info_datapart())
        ##curr_data.update(self.device.get_soil_calibration_data())

        # add the timestamp to the data dict
        curr_data['datetime'] = _timestamp
        # The current live data contains sensor battery state data, but no
        # signal level data. So obtain the sensor info and add it to the
        # current live data. We will end up with battery data for each sensor
        # appearing twice under two different fields, but later field mapping
        # will take care of this.
        curr_data.update(self.device.get_sensors_data())

        # log the combined current data but only if debug>=3
        #log.info('Current data: %s' % curr_data)
        if weewx.debug >= 3:
            log.debug('Current data: %s' % curr_data)
        return curr_data


    def startup(self):
        """Start a thread that collects data from the API."""

        try:
            self.thread = EcowittHttpCollector.CollectorThread(self)
            log.info('EcowittHttpCollector startup')
            self.collect_data = True
            self.thread.daemon = True
            self.thread.name = 'EcowittHttpCollectorThread'
            self.thread.start()
        except threading.ThreadError:
            log.error('Unable to launch EcowittHttpCollector thread')
            self.thread = None

    def shutdown(self):
        """Shut down the thread that collects data from the API.

        Tell the thread to stop, then wait for it to finish.
        """

        # we only need do something if a thread exists
        if self.thread:
            # tell the thread to stop collecting data
            self.collect_data = False
            # terminate the thread
            self.thread.join(10.0)
            # log the outcome
            if self.thread.is_alive():
                log.error('Unable to shut down EcowittHttpCollector thread')
            else:
                log.info('EcowittHttpCollector thread has been terminated')
        self.thread = None

    class CollectorThread(threading.Thread):
        """Class using a thread to collect data via the local HTTP API."""

        def __init__(self, client):
            # initialise our parent
            threading.Thread.__init__(self)
            # keep reference to the client we are supporting
            self.client = client
            self.name = 'ecowitt_http-collector'

        def run(self):
            # rather than letting the thread silently fail if an exception
            # occurs within the thread, wrap in a try..except so the exception
            # can be caught and available exception information displayed
            try:
                # kick the collection off
                self.client.collect()
            except Exception as e:
                # we have an exception so log what we can
                weeutil.logger.log_traceback(log.critical, '    ****  ')


# ============================================================================
#                            class EcowittHttpApi
# ============================================================================

class EcowittHttpApi:
    """Class to interact with an Ecowitt device via the local HTTP API."""

    # HTTP request commands
    commands = ['get_version', 'get_livedata_info', 'get_ws_settings',
                'get_calibration_data', 'get_rain_totals', 'get_device_info',
                'get_sensors_info', 'get_network_info', 'get_units_info',
                'get_cli_soilad', 'get_cli_multiCh', 'get_cli_pm25',
                'get_cli_co2', 'get_piezo_rain', 'get_cli_wh34', 'get_cli_lds',
                'get_sdmmc_info']
    # Ecowitt continues to refer to some sensors by multiple model numbers.
    # Create a map to map such sensor models to a common model number in any
    # API responses.
    sensor_rename_map = {
        'wh30': 'wn30',
        'wh31': 'wn31',
        'wh32': 'wn32',
        'wh34': 'wn34',
        'wh35': 'wn35',
        'wh36': 'wn36',
        #'wh68': 'ws68',
        #'wh69': 'ws69',
        'wh80': 'ws80',
        'wh85': 'ws85',
        'wh90': 'ws90'
    }


    def __init__(self, ip_address,
                 max_tries=DEFAULT_MAX_TRIES,
                 retry_wait=DEFAULT_RETRY_WAIT,
                 timeout=DEFAULT_URL_TIMEOUT):
        """Initialise an EcowittHttpApi object."""

        # the IP address to be used (stored as a string)
        self.ip_address = ip_address
        # max number of attempts to obtain data from the device
        self.max_tries = max_tries
        # wait time in seconds between attempt to contact the device
        self.retry_wait = retry_wait
        # timeout in seconds to be used for urlopen calls
        self.timeout = timeout

    def request(self, command_str, data=None, headers=None):
        """Send a HTTP request to the device and return the response.

        Create a HTTP request with optional data and headers. Send the HTTP
        request to the device as a GET request, obtain the response and return
        the JSON deserialized response is returned. If the response cannot be
        deserialized the value None is returned. URL or timeout errors are
        logged and raised.

        command_str: a string containing the command to be sent,
                     eg: 'get_livedata_info'
        data: a dict containing key:value pairs representing the data to be
              sent
        headers: a dict containing headers to be included in the HTTP request

        Returns a deserialized JSON object or None
        """

        # use empty dicts for data and headers if not provided
        data_dict = {} if data is None else data
        headers_dict = {} if headers is None else headers
        # check if we have a command that we know about
        if command_str in EcowittHttpApi.commands:
            # first convert any data to a percent-encoded ASCII text string
            data_enc = urllib.parse.urlencode(data_dict)
            # construct the scheme and host portions of the URL
            stem = ''.join(['http://', self.ip_address])
            # now add the 'path'
            url = '/'.join([stem, command_str])
            # Finally add the encoded data. We need to add the data in this manner
            # rather than using the Request object's 'data' parameter so the
            # request is sent as a GET request rather than a POST request.
            full_url = '?'.join([url, data_enc])
            # create a Request object
            req = urllib.request.Request(url=full_url, headers=headers_dict)
            for attempt in range(self.max_tries):
                try:
                    # submit the request and obtain the raw response
                    with urllib.request.urlopen(req, timeout=self.timeout) as w:
                        # get charset used so we can decode the stream correctly
                        char_set = w.headers.get_content_charset()
                        # Now get the response and decode it using the headers
                        # character set. Be prepared for charset==None.
                        if char_set is not None:
                            resp = w.read().decode(char_set)
                        else:
                            resp = w.read().decode()
                except socket.timeout as e:
                    # we timed out and failed to obtain data on this attempt,
                    # log it
                    if weewx.debug >= 2:
                        log.debug('Socket - Failed to get device data on attempt %d of %d' % (attempt +1,
                                                                                     self.max_tries))
                except urllib.error.URLError as e:
                    # we encountered an error, log the error and raise it
                    log.error('URL - Failed to get device data on attempt %d of %d' % (attempt + 1,
                                                                                 self.max_tries))
                    log.error('   **** %s' % e)
                    raise
                else:
                    # our attempt was successful, break out of the for loop
                    break
            else:
                # the for loop terminated normally, so we exhausted all
                # attempts without success
                log.debug('Failed to get device data after %d attempts' % self.max_tries)
            # Do a little massaging of the response, Ecowitt refers to some
            # wsxx devices as whxx in the API, fix this at the source. The
            # device model numbers are fairly unique so a simple replace will
            # suffice.
            for old, new in self.sensor_rename_map.items():
                resp = resp.replace(old, new)
            # we have a response but can it be deserialized it to a python
            # object, wrap in a try..except in case it cannot be deserialized
            try:
                resp_json = json.loads(resp)
            except json.JSONDecodeError as e:
                # cannot deserialize the response, log it and return None
                log.error('Cannot deserialize device response')
                log.error('   **** %s' % e)
                return None
            # we have a deserialized response, log it as required
            if weewx.debug >= 3:
                log.debug('Deserialized HTTP response: %s' % json.dumps(resp_json))
            # now return the JSON object
            return resp_json
        # an invalid command
        raise UnknownApiCommand(f"Unknown HTTP API command '{command_str}'")

    def get_version(self):
        """Get the device firmware related information.

        Returns a dict or None if no valid data was returned by the device."""

        try:
            return self.request('get_version')
        except (socket.timeout, urllib.error.URLError) as e:
            raise DeviceIOError(f"Failed to obtain 'get_version' data: {e}")

    def get_livedata_info(self):
        """Get live sensor data from the device.

        Returns a dict or None if no valid data was returned by the device."""

        try:
            return self.request('get_livedata_info')
        except (socket.timeout, urllib.error.URLError) as e:
            raise DeviceIOError(f"Failed to obtain 'get_livedata_info' data: {e}")

    def get_ws_settings(self):
        """Get weather services settings from the device.

        Returns a dict or None if no valid data was returned by the device."""

        try:
            return self.request('get_ws_settings')
        except (socket.timeout, urllib.error.URLError) as e:
            raise DeviceIOError(f"Failed to obtain 'get_ws_settings' data: {e}")

    def get_calibration_data(self):
        """Get calibration settings from the device.

        Returns a dict or None if no valid data was returned by the device."""

        try:
            return self.request('get_calibration_data')
        except (socket.timeout, urllib.error.URLError) as e:
            raise DeviceIOError(f"Failed to obtain 'get_calibration_data' data: {e}")

    def get_rain_totals(self):
        """Get rainfall totals and settings from the device.

        Returns a dict or None if no valid data was returned by the device."""

        try:
            return self.request('get_rain_totals')
        except (socket.timeout, urllib.error.URLError) as e:
            raise DeviceIOError(f"Failed to obtain 'get_rain_totals' data: {e}")

    def get_device_info(self):
        """Get device settings from the device.

        Returns a dict or None if no valid data was returned by the device."""

        try:
            return self.request('get_device_info')
        except (socket.timeout, urllib.error.URLError) as e:
            raise DeviceIOError(f"Failed to obtain 'get_device_info' data: {e}")

    def get_sensors_info(self, page=0):
        """Get sensor ID data from the device.

        Obtains sensor state data via a 'get_sensors_info' API call. Sensor
        state data provided via the API consists of multiple pages with only
        one page being returned for any one API call. Currently there are two
        sensor state data pages; page 1 and page 2. This method returns page 1,
        page 2 or a combined all pages of sensor state data depending on the
        'page' parameter.

        page: specify which page of sensor state data to return, 0 = return all
              pages, 1 = return page 1, 2 = return page 2

        Returns a dict of data from the 'get_sensors_info' API command.
        """

        page_1 = page_2 = None
        if page in [0, 1]:
            try:
                page_1 = self.request('get_sensors_info', data={'page': 1})
            except (socket.timeout, urllib.error.URLError) as e:
                raise DeviceIOError(f"Failed to obtain 'get_sensors_info' page 1 data: {e}")
        if page in [0, 2]:
            try:
                page_2 = self.request('get_sensors_info', data={'page': 2})
            except (socket.timeout, urllib.error.URLError) as e:
                raise DeviceIOError(f"Failed to obtain 'get_sensors_info' page 2 data: {e}")
        if page_1 is not None and page_2 is not None:
            return page_1 + page_2
        if page_1 is None:
            return page_2
        return page_1

    def get_network_info(self):
        """Get network related data/settings from the device.

        Returns a dict or None if no valid data was returned by the device.
        """

        try:
            return self.request('get_network_info')
        except (socket.timeout, urllib.error.URLError) as e:
            raise DeviceIOError(f"Failed to obtain 'get_network_info' data: {e}")

    def get_units_info(self):
        """Get units settings from the device.

        Returns a dict or None if no valid data was returned by the device.
        """

        try:
            return self.request('get_units_info')
        except (socket.timeout, urllib.error.URLError) as e:
            raise DeviceIOError(f"Failed to obtain 'get_units_info' data: {e}")

    def get_cli_soilad(self):
        """Get multichannel soil moisture sensor calibration data from the device.

        Returns a list of dicts or None if no valid data was returned by the
        device.
        """

        try:
            return self.request('get_cli_soilad')
        except (socket.timeout, urllib.error.URLError) as e:
            raise DeviceIOError(f"Failed to obtain 'get_cli_soilad' data: {e}")

    def get_cli_multi_ch(self):
        """Get multichannel temperature/humidity sensor calibration data from
        the device.

        Returns a list of dicts or None if no valid data was returned by the
        device.
        """

        try:
            return self.request('get_cli_multiCh')
        except (socket.timeout, urllib.error.URLError) as e:
            raise DeviceIOError(f"Failed to obtain 'get_cli_multiCh' data: {e}")

    def get_cli_pm25(self):
        """Get PM2.5 sensor offset data from the device.

        Returns a list of dicts or None if no valid data was returned by the
        device.
        """

        try:
            return self.request('get_cli_pm25')
        except (socket.timeout, urllib.error.URLError) as e:
            raise DeviceIOError(f"Failed to obtain 'get_cli_pm25' data: {e}")

    def get_cli_co2(self):
        """Get CO2 sensor offset data from the device.

        Returns a list of dicts or None if no valid data was returned by the
        device.
        """

        try:
            return self.request('get_cli_co2')
        except (socket.timeout, urllib.error.URLError) as e:
            raise DeviceIOError(f"Failed to obtain 'get_cli_co2' data: {e}")

    def get_piezo_rain(self):
        """Get piezo rain sensor data/settings from the device.

        Returns a dict or None if no valid data was returned by the device.
        """

        try:
            return self.request('get_piezo_rain')
        except (socket.timeout, urllib.error.URLError) as e:
            raise DeviceIOError(f"Failed to obtain 'get_piezo_rain' data: {e}")

    def get_cli_wh34(self):
        """Get WN34 sensor offset data from the device.

        Returns a list of dicts or None if no valid data was returned by the
        device.
        """

        try:
            return self.request('get_cli_wh34')
        except (socket.timeout, urllib.error.URLError) as e:
            raise DeviceIOError(f"Failed to obtain 'get_cli_wh34' data: {e}")

    def get_cli_lds(self):
        """Get laser distance sensor (WH54) sensor offset data from the device.

        Returns a list of dicts or None if no valid data was returned by the
        device.
        """

        try:
            return self.request('get_cli_lds')
        except (socket.timeout, urllib.error.URLError) as e:
            raise DeviceIOError(f"Failed to obtain 'get_cli_lds' data: {e}")

    def get_sdmmc_info(self):
        """Get SD card info from the device.

        Returns a dict or None if no valid data was returned by the device.
        """

        try:
            return self.request('get_sdmmc_info')
        except (socket.timeout, urllib.error.URLError) as e:
            raise DeviceIOError(f"Failed to obtain 'get_sdmmc_info' data: {e}")


# ============================================================================
#                          class EcowittHttpParser
# ============================================================================

class EcowittHttpParser:
    """Class to parse data obtained via the local HTTP API.

    The main function of class EcowittHttpParser is to parse raw JSON responses
    obtained from device local HTTP API calls. The entry point to a
    EcowittHttpParser object is one of the parse_xxxxx() methods. The
    parse_xxxxx() methods take the raw JSON response to the local HTTP API
    xxxxx call, parses the response and returns the parsed data in a
    dict/list of dicts. In some cases additional processing of elements of the
    JSON response data is undertaken by process_yyyyy() methods. If a device
    response cannot be parsed a ParseError() is raised. Calls to parse_xxxxx()
    methods should be prepared to handle a ParseError() exception.

    The following HTTP API calls are supported:

        'get_version', 'get_livedata_info', 'get_ws_settings',
        'get_calibration_data', 'get_rain_totals', 'get_device_info',
        'get_sensors_info', 'get_network_info', 'get_units_info',
        'get_cli_soilad', 'get_cli_multiCh', 'get_cli_pm25',
        'get_cli_co2', 'get_piezo_rain', 'get_cli_wh34', 'get_cli_lds',
        'get_sdmmc_info'
    """

    # dict of WeeWX default device units, these units are fixed for all devices
    # and are not user selectable
    default_device_units = {
        'group_volt': 'volt',
        'group_uv': 'uv_index',
        'group_percent': 'percent',
        'group_direction': 'degree_compass',
        'group_fraction': 'ppm',
        'group_concentration': 'microgram_per_meter_cubed',
        'group_boolean': 'boolean'
    }
    # lookup to find WeeWX equivalent of a lower case Ecowitt unit string
    unit_lookup = {
        'c': 'degree_C',
        'f': 'degree_F',
        'km': 'km',
        'mi': 'mile',
        'nmi': 'nautical_mile',
        'hpa': 'hPa',
        'kfc': 'kfc',
        'klux': 'klux',
        'kpa': 'kPa',
        'inhg': 'inHg',
        'mmhg': 'mmHg',
        'mm': 'mm',
        'in': 'inch',
        'ft': 'foot',
        'mm/hr': 'mm_per_hour',
        'in/hr': 'inch_per_hour',
        'km/h': 'km_per_hour',
        'm/s': 'meter_per_second',
        'mph': 'mile_per_hour',
        'knots': 'knot',
        '%': 'percent',
        'w/m2': 'watt_per_meter_squared'
    }
    # processor function lookup used to select an appropriate processor
    # function for enumerated observation fields/codes in various common_list
    # array elements
    processor_fns = {
        '0x01': 'process_temperature_object', # inside temperature
        '0x02': 'process_temperature_object', # outside temperature
        '0x03': 'process_temperature_object', # dewpoint
        # Is field '0x03' the same as field '3'. The local HTTP API
        # get_livedata_info command returns a common_list field identified
        # as '3' that contains temperature data that is at times different to
        # any other temperature field. Use of WS View+ app suggests field '3'
        # is 'feels like'.
        '3': 'process_temperature_object', # feels like (suspected)
        '0x04': 'process_temperature_object', # wind chill
        # Is field '0x04' the same as field '4'. The local HTTP API
        # get_livedata_info command does not return a field identified as
        # '0x04' or as '4'.
        '4': 'process_temperature_object', # unknown field
        '0x05': 'process_temperature_object', # heat index
        # Is field '0x05' the same as field '5'. The local HTTP API
        # get_livedata_info command returns a common_list field identified
        # as '5' that contains data in kPa, inHg or mmHg which is suggestive of
        # VPD.
        '5': 'process_pressure_object', # VPD (suspected)
        '0x07': 'process_humidity_object', # outdoor humidity
        '0x08': 'process_noop_object', # absolute pressure, however absolute
        # pressure appears in the get_livedata_info response under 'WH25'
        '0x09': 'process_noop_object', # relative pressure, however relative
        # pressure appears in the get_livedata_info response under 'WH25'
        '0x0A': 'process_direction_object', # wind direction
        '0x0B': 'process_speed_object', # wind speed
        '0x0C': 'process_speed_object', # gust speed
        '0x0D': 'process_rainfall_object', # rain event
        '0x0E': 'process_rainrate_object', # rain rate
        '0x0F': 'process_rainfall_object', # rain gain
        '0x10': 'process_rainfall_object', # rain day
        '0x11': 'process_rainfall_object', # rain week
        '0x12': 'process_rainfall_object', # rain month
        '0x13': 'process_rainfall_object', # rain year
        '0x14': 'process_rainfall_object', # rain totals
        '0x15': 'process_light_object', # light
        '0x16': 'process_uv_radiation_object', # uv
        '0x17': 'process_index_object', # uv index
        '0x18': 'process_noop_object', # date and time
        '0x19': 'process_speed_object', # day max wind speed
        '0x6D': 'process_direction_object', # wind direction 10min
        '0x7C': 'process_rainfall_object', # rain 24h
        'srain_piezo': 'process_boolean_object' # is raining (?)
    }
    rain_map = {
        'day_rain': 'rainDay',
        '24h_rain': 'rain24',
        'week_rain': 'rainWeek',
        'month_rain': 'rainMonth',
        'year_rain': 'rainYear'
    }
    piezo_rain_map = {
        'day_rain': 'drain_piezo',
        '24h_rain': 'rain24_piezo',
        'week_rain': 'wrain_piezo',
        'month_rain': 'mrain_piezo',
        'year_rain': 'yrain_piezo'
    }
    # sensor IDs for sensors that are not registered (ie learning/registering
    # and disabled)
    not_registered = ('fffffffe', 'ffffffff')

    def __init__(self, unit_system=DEFAULT_UNIT_SYSTEM,
                 show_battery=DEFAULT_FILTER_BATTERY,
                 log_unknown_fields=True,
                 debug=DebugOptions()):
        """Initialise an EcowittHttpParser object."""

        # the unit system we are to use
        self.unit_system = unit_system
        # whether to filter battery state data for sensors that are not
        # registered or show signal == 0
        self.show_battery = show_battery
        # do we log unknown fields at info or leave at debug
        self.log_unknown_fields = log_unknown_fields
        # save the debug options
        self.debug = debug

    @staticmethod
    def parse_get_version(response):
        """Parse the response from a 'get_version' API command.

        Parse the raw JSON response from a 'get_version' API command.

        Example raw 'get_version' data:

            {"version": "Version: GW2000C_V3.1.2",
             "newVersion": "1",
             "platform": "ecowitt"}

        Returns a dict keyed as follows:

        version:          Extended device firmware version string,
                          eg "Version: GW2000C_V3.1.2". String.
        firmware_version: Firmware version string with leading 'V', eg "V3.1.2"
        newVersion:       Available of new firmware version update, 0 = no new
                          version available, 1 = new version available. Integer.
        platform:         Unknown, but 'ecowitt' for Ecowitt devices. String.

        If the device response cannot be parsed a ParseError is raised.
        """

        # Create a copy of the response, this serves as a quick check we have a
        # dict as a response. This saves catching AttributeErrors against each
        # field we convert to a float or int.
        try:
            _ = dict(response)
        except (TypeError, ValueError) as e:
            # we have a malformed or otherwise invalid response, raise a ParseError:
            raise ParseError(f"Error parsing 'parse_get_version' data: {e}")
        # initialise a dict to hold our parsed response
        _parsed_data = dict()
        # first parse the 'version' key/value and extract the short form
        # firmware version from the 'version' key/value
        try:
            _parsed_data['version'] = str(response['version'])
            _parsed_data['firmware_version'] = str(response['version']).split('_')[1].strip()
        except KeyError as e:
            # we have no 'version' key, do nothing and continue
            pass
        except IndexError as e:
            # We have a 'version' key but could not extract a short form
            # firmware version from the 'version' key/value. In this case
            # 'firmware_version' is our own derived key/value so we can be a
            # little forgiving and just set 'firmware_version' to None.
            _parsed_data['firmware_version'] = None
        # parse the 'newVersion' key value
        try:
            _parsed_data['newVersion'] = weeutil.weeutil.to_int(response['newVersion'])
        except KeyError as e:
            # we have no 'newVersion' key, do nothing and continue
            pass
        except ValueError as e:
            # we have a 'newVersion' key but encountered an error parsing the
            # key value, set the 'newVersion' value to None
            _parsed_data['newVersion'] = None

        # parse the 'platform' key/value
        try:
            _parsed_data['platform'] = response.get('platform')
        except KeyError as e:
            # we have no 'platform' key, do nothing and continue
            pass
        # return the parsed data
        return _parsed_data

    def parse_get_livedata_info(self, response, flatten_data=True):
        """Parse the response from a 'get_livedata_info' API command.

        The get_livedata_info API command returns a JSON object containing one
        or more arrays of observations in string format. Process each array to
        obtain a list of dicts containing numeric observation data using the
        designated driver unit system. Flatten the aggregated dicts to
        facilitate a simplified 'dot-field name' mapping to be used later to
        produce user specified loop packet.

        Unknown array elements are logged but otherwise ignored.

        Calls the following methods to process various JSON arrays:
            process_common_list_array - process common_list array (addressed
                                        data including temperature, humidity,
                                        wind speed, wind direction, solar, UV)
            process_rain_array        - process rain array (traditional rain
                                        sensor)
            process_piezoRain_array   - process piezoRain array (piezoelectric
                                        rain sensor)
            process_wh25_array        - process wh25 array (temperature,
                                        humidity and air pressure sensor (built
                                        in or independent))
            process_lightning_array   - process lightning array (lightning
                                        sensor)
            process_ch_pm25_array     - process ch_pm25 (multichannel PM25
                                        sensors)
            process_leak_array        - process leak array (multichannel leak
                                        sensors)
            process_ch_aisle_array    - process ch_aisle array (multichannel
                                        temperature and humidity sensors)
            process_ch_soil_array     - process ch_soil array (multichannel
                                        soil moisture sensors)
            process_ch_temp_array     - process ch_temp array (multichannel
                                        temperature sensors)
            process_ch_lds_array      - process ch_lds array (multichannel
                                        laser distance sensors)
            process_ch_leaf_array     - process leaf array (multichannel leaf
                                        wetness sensors)
            process_co2_array         - process co2 array (CO2 sensor)
            process_rain_array        - process rain array (rain sensor)
            process_debug_array       - process debug array (device info)

        Parameters
            response:     The API JSON response to be parsed. List representing
                          a JSON array.
            flatten_data: Whether to flatten the parsed data structure or not.
                          Boolean, default is True.

        Returns:
            A dict containing numeric and unit converted observation data. If
            no raw JSON data was provided a ParseError exception is raised.
        """

        # obtain an empty dict to hold our result
        data = dict()
        # do we have a response
        if response is not None:
            # iterate over the observation groups in the response
            for group, group_data in response.items():
                # First obtain the processor function we are to use, wrap in a
                # try..except in case it is a group we do not know about.
                try:
                    _fn = getattr(self, '_'.join(['process', group, 'array']))
                except AttributeError as e:
                    # We have most likely encountered a new 'group' for which
                    # we have no processor function. It could also be a known
                    # group that has changed structure. In either case we do
                    # not know how to process the group so log it if necessary
                    # and continue.
                    if weewx.debug or self.debug.parser or self.log_unknown_fields:
                        log.info("Skipped unknown livedata group '%s'",
                                 group)
                    continue
                # Now call the processor function to process the group data.
                # Wrap in a try..except in case we encounter an error.
                try:
                    # process the data and obtain the result
                    processed_data = _fn(group_data)
                except ProcessorError as e:
                    # A ProcessorError was raised, most likely cause is a
                    # malformed or changed group. Log it and continue.
                    if weewx.debug or self.debug.parser or self.log_unknown_fields:
                        log.info("Error processing livedata group '%s': %s",
                                 (group, e))
                else:
                    # we obtained some processed data for the group so add it
                    # to our result
                    data[group] = processed_data
            # finally, return the data, flattened or not
            if flatten_data:
                return flatten(data)
            else:
                return data
        else:
            # there was no data to parse, raise a ParseError exception
            raise ParseError("Error parsing 'get_livedata_info' data: No raw data")

    def parse_get_sensors_info(self, response, connected_only=DEFAULT_ONLY_REGISTERED_SENSORS, flatten_data=True):
        """Parse the response from a 'get_sensors_info' API command.

        The get_sensors_info API command returns a JSON array of metadata for
        each sensor. Each array element is processed, aggregated and formatted
        into a nested dict containing all sensor metadata. The resulting data
        may be limited to connected sensors only depending on the
        'connected_only' parameter. If required, the nested dict is flattened
        to facilitate a simplified 'dot-field name' mapping to be used later to
        produce user specified loop packet.

        Parameters
            response:       The API response to be parsed. List representing a
                            JSON array.
            connected_only: Whether to return data for only connected sensors
                            or for all known sensors. Boolean, default is False.
            flatten_data:   Whether to flatten the parsed data structure or not.
                            Boolean, default is True.

        Returns:
            A flattened dict of sensor metadata. If no raw JSON data was
            provided a ParseError exception is raised.
        """

        # obtain an empty dict to hold our result
        _parsed = dict()
        # do we have a response
        if response is not None:
            # iterate over the sensors in the response
            for sensor in response:
                # process the raw sensor data to obtain the sensor model,
                # channel and processed data
                model, channel, processed_data = self.process_sensor_array(sensor,
                                                                           connected_only=connected_only)
                # do we have a model
                if model is not None:
                    # have we seen this model before
                    if model not in _parsed.keys():
                        # we have not seen this model before, create a new dict
                        # for this model
                        _parsed[model] = dict()
                    # do we have a channelised sensor
                    if channel is not None:
                        # the sensor is channelised, save the data against the
                        # applicable channel number
                        _parsed[model][channel] = processed_data
                    else:
                        # the sensor is not channelised, save the data against
                        # the applicable model
                        _parsed[model] = processed_data
            # finally, return the data, flattened or not
            if flatten_data:
                return flatten(_parsed)
            else:
                return _parsed
        else:
            # there was no data to parse, raise a ParseError exception
            raise ParseError("Error parsing 'get_sensors_info' data: No raw data")

    @staticmethod
    def parse_get_ws_settings(response):
        """Parse the response from a 'get_ws_settings' API command.

        Parse the raw JSON response from a 'get_ws_settings' API command.

        Example raw 'get_ws_settings' JSON data:

        {"platform": "ecowitt",
         "ost_interval": "5",
         "sta_mac": "E8:68:E7:12:9D:D7",
         "wu_interval": "0",
         "wu_id": "",
         "wu_key": "",
         "wcl_interval": "0",
         "wcl_id": "",
         "wcl_key": "",
         "wow_interval": "5",
         "wow_id": "",
         "wow_key": "",
         "Customized": "disable",
         "Protocol": "ecowitt",
         "ecowitt_ip": "192.168.1.10",
         "mqtt_name": "",
         "mqtt_host": "",
         "mqtt_transport": "0",
         "mqtt_port": "0",
         "mqtt_topic": "ecowitt/E868E7129DD7",
         "mqtt_clientid": "",
         "mqtt_username": "",
         "mqtt_password": "",
         "mqtt_keepalive": "0",
         "mqtt_interval": "0",
         "ecowitt_path": "/data/report/",
         "ecowitt_port": "80",
         "ecowitt_upload": "120",
         "usr_wu_path": "/weatherstation/updateweatherstation.php?",
         "usr_wu_id": "",
         "usr_wu_key": "",
         "usr_wu_port": "80",
         "usr_wu_upload": "120"}

        Returns a dict keyed as follows:

        platform:               Unknown, but 'ecowitt' for Ecowitt devices.
                                String.
        ost_interval:           Ecowitt.net upload interval in minutes,
                                0=disabled. Integer.
        sta_mac:                    Station (device) MAC address. String.
        wu_id:                  Weather Underground station ID. String.
        wu_key:                 Weather Underground station key. String.
        wcl_id:                 Weathercloud station ID. String.
        wcl_key:                Weathercloud station key. String.
        wow_id:                 Weather Observation Website station ID. String.
        wow_key:                Weather Observation Website station key.
                                String.
        cus_state:              Custom upload state, enabled=True,
                                disabled=False. Boolean.
        cus_protocol:           Custom upload protocol, 'ecowitt' or
                                'wunderground'. String.
        cus_ecowitt_ip:         Custom upload Ecowitt format destination
                                IP address/server name. String.
        cus_ecowitt_path:       Custom upload Ecowitt format destination path.
                                String.
        cus_ecowitt_port:       Custom upload Ecowitt format destination port.
                                Integer.
        cus_ecowitt_interval:   Custom upload Ecowitt format upload interval in
                                seconds. Integer.
        cus_wu_ip:              Custom upload WU format destination
                                IP address/server name. String.
        cus_wu_path:            Custom upload WU format destination path.
                                String.
        cus_wu_id:              Custom upload WU format station ID. String.
        cus_wu_key:             Custom upload WU format station key. String.
        cus_wu_port:            Custom upload WU format destination port.
                                Integer.
        cus_wu_interval:        Custom upload WU format upload interval in
                                seconds. Integer.

        If the device response cannot be parsed a ParseError is raised.
        """

        # API response fields that need string-to-integer conversion
        to_int_fields = ('ost_interval', 'wu_interval', 'wcl_interval',
                         'wow_interval', 'mqtt_transport', 'mqtt_port',
                         'mqtt_keepalive', 'mqtt_interval', 'ecowitt_port',
                         'ecowitt_upload', 'usr_wu_port', 'usr_wu_upload')
        # create a copy of the response, this will be the starting point for
        # our parsed data, wrap in a try..except in case we have an invalid
        # response
        try:
            _parsed = dict(response)
        except (TypeError, ValueError) as e:
            # we have a malformed or otherwise invalid response, raise a ParseError:
            raise ParseError(f"Error parsing 'parse_get_ws_settings' data: {e}")
        # now process all of the key/value pairs that need some form of
        # conversion
        # process those fields that require string-to-integer conversion
        for field in to_int_fields:
            try:
                _parsed[field] = weeutil.weeutil.to_int(response[field])
            except KeyError as e:
                # we have no field key, do nothing and continue
                pass
            except ValueError as e:
                # we have a field key but encountered an error processing the
                # its value, set key value to None
                _parsed[field] = None
        # process 'Customized'
        try:
            _parsed['Customized'] = response['Customized'].lower() == 'enable'
        except KeyError as e:
            # we have no 'Customized' key, do nothing and continue
            pass
        except AttributeError as e:
            # we have a 'Customized' key but could not coalesce a lower case
            # string from the key value, set 'Customized' to None
            _parsed['Customized'] = None
        # process 'Protocol'
        try:
            _parsed['Protocol'] = response['Protocol'].lower()
        except KeyError:
            # the 'Protocol' key does not exist, do nothing and continue
            pass
        except AttributeError as e:
            # we have an 'Protocol' key but encountered an error processing
            # the 'Protocol' value, set the 'Protocol' key value to None
            _parsed['Protocol'] = None
        # return the parsed data
        return _parsed

    @staticmethod
    def parse_get_calibration_data(response, device_units):
        """Parse the response from a 'get_calibration_data' API command.

        Parse the raw JSON response from a 'get_calibration_data' API command.
        Missing response key/values are ignored, key/values that exist but
        cannot be parsed are set to None. A ParseError is raised if the
        response is malformed.

        Example 'get_calibration_data' response:

            {"SolarRadWave": "1484.8",
             "solarRadGain": "1.00",
             "uvGain": "1.00",
             "windGain": "1.00",
             "inTempOffset": "0.0",
             "inHumiOffset": "0",
             "absOffset": "-2.7",
             "relOffset": "4.9",
             "outTempOffset": "0.0",
             "outHumiOffset": "0",
             "windDirOffset": "0",
             "th_cli": true,
             "wh34_cli": true,
             "pm25_cli": true,
             "soil_cli": true}

        Returns a dict keyed as follows:

        solar_wave:         Unknown data, always 1484.8. Float.
        solar_gain:         Solar radiation gain, 0.10 - 5.00. Float.
        uv_gain:            UV radiation gain, 0.10 - 5.00. Float.
        wind_gain:          Wind speed gain, 0.10 - 5.00. Float.
        intemp_offset:      Inside temperature offset, -10.0C/-18.0F to
                            +10.0C/+18.0F. ValueTuple.
        inhumid_offset:     Inside humidity offset, -10% to +10%. ValueTuple.
        abs_offset:         Absolute pressure offset, -80.0hPa to +80.0hPa.
                            ValueTuple.
        rel_offset:         Relative pressure offset, -80.0hPa to +80.0hPa.
                            ValueTuple.
        outtemp_offset:     Outside temperature offset, -10.0C/-18.0F to
                            +10.0C/+18.0F. ValueTuple.
        outhumid_offset:    Outside humidity offset, -10% to +10%. ValueTuple.
        winddir_offset:     Wind direction offset, -180 to +180. ValueTuple
        th_cli:             Unknown data. Boolean.
        wh34_cli:           Unknown data. Boolean.
        pm25_cli:           Unknown data. Boolean.
        soil_cli:           Unknown data. Boolean.

        If the device response cannot be parsed a ParseError is raised.
        """

        # Create a copy of the response, this serves as a quick check we have a
        # dict as a response. This saves catching AttributeErrors against each
        # field we convert to a float or int.
        try:
            _ = dict(response)
        except (TypeError, ValueError) as e:
            # we have a malformed or otherwise invalid response, raise a ParseError:
            raise ParseError(f"Error parsing 'parse_get_calibration_data' data: {e}")
        # initialise a dict to hold the parsed data
        _parsed_data = dict()
        # parse each response key/value pair adding the parsed data to our
        # result dict, wrap in a try..except in case there is a problem
        try:
            _parsed_data['solar_wave'] = weeutil.weeutil.to_float(response.get('SolarRadWave'))
        except KeyError as e:
            # the 'Customized' key does not exist, do nothing and continue
            pass
        except ValueError as e:
            # we have an 'usr_wu_upload' key but encountered an error
            # processing the 'usr_wu_upload' value, set 'usr_wu_upload' to None
            _parsed_data['solar_wave'] = None
        try:
            _parsed_data['solar_gain'] = weeutil.weeutil.to_float(response.get('solarRadGain'))
        except KeyError as e:
            # the 'solar_gain' key does not exist, do nothing and continue
            pass
        except ValueError as e:
            # we have an 'solar_gain' key but encountered an error processing
            # the 'solar_gain' value, set 'solar_gain' to None
            _parsed_data['solar_gain'] = None
        try:
            _parsed_data['uv_gain'] = weeutil.weeutil.to_float(response.get('uvGain'))
        except KeyError as e:
            # the 'uv_gain' key does not exist, do nothing and continue
            pass
        except ValueError as e:
            # we have an 'uv_gain' key but encountered an error processing the
            # 'uv_gain' value, set 'uv_gain' to None
            _parsed_data['uv_gain'] = None
        try:
            _parsed_data['wind_gain'] = weeutil.weeutil.to_float(response.get('windGain'))
        except KeyError as e:
            # the 'wind_gain' key does not exist, do nothing and continue
            pass
        except ValueError as e:
            # we have an 'wind_gain' key but encountered an error processing
            # the 'wind_gain' value, set 'wind_gain' to None
            _parsed_data['wind_gain'] = None
        try:
            _offset = weeutil.weeutil.to_float(response['inTempOffset'])
        except KeyError as e:
            # we have no key 'inTempOffset', ignore and continue
            pass
        except ValueError as e:
            # we have a 'inTempOffset' key, but encountered an error processing
            # the key value, set the result to None and continue
            _parsed_data['intemp_offset'] = weewx.units.ValueTuple(None, None, None)
        else:
            # we have a value, save the value as a ValueTuple
            _parsed_data['intemp_offset'] = weewx.units.ValueTuple(_offset,
                                                                   device_units['group_deltat'],
                                                                   'group_deltat')
        try:
            _offset = weeutil.weeutil.to_float(response['inHumiOffset'])
        except KeyError as e:
            # we have no key 'inHumiOffset', ignore and continue
            pass
        except ValueError as e:
            # we have a 'inHumiOffset' key, but encountered an error processing
            # the key value, set the result to None and continue
            _parsed_data['inhumid_offset'] = weewx.units.ValueTuple(None, None, None)
        else:
            # we have a value, save the value as a ValueTuple
            _parsed_data['inhumid_offset'] = weewx.units.ValueTuple(_offset,
                                                                    'percent',
                                                                    'group_percent')
        try:
            _offset = weeutil.weeutil.to_float(response['absOffset'])
        except KeyError as e:
            # the 'absOffset' key does not exist, do nothing and continue
            pass
        except ValueError as e:
            # we have a 'absOffset' key, but encountered an error processing
            # the key value, set the result to None and continue
            _parsed_data['abs_offset'] = weewx.units.ValueTuple(None, None, None)
        else:
            # we have a value, save the value as a ValueTuple
            _parsed_data['abs_offset'] = weewx.units.ValueTuple(_offset,
                                                                device_units['group_pressure'],
                                                                'group_pressure')
        try:
            _offset = weeutil.weeutil.to_float(response['relOffset'])
        except KeyError as e:
            # the 'relOffset' key does not exist, do nothing and continue
            pass
        except ValueError as e:
            # we have a 'relOffset' key, but encountered an error processing
            # the key value, set the result to None and continue
            _parsed_data['rel_offset'] = weewx.units.ValueTuple(None, None, None)
        else:
            # we have a value, save the value as a ValueTuple
            _parsed_data['rel_offset'] = weewx.units.ValueTuple(_offset,
                                                                device_units['group_pressure'],
                                                                'group_pressure')
        try:
            _offset = weeutil.weeutil.to_float(response['altitude'])
        except KeyError as e:
            # the 'altitude' key does not exist, do nothing and continue
            pass
        except ValueError as e:
            # we have a 'altitude' key, but encountered an error processing
            # the key value, set the result to None and continue
            _parsed_data['altitude'] = weewx.units.ValueTuple(None, None, None)
        else:
            # we have a value, save the value as a ValueTuple
            _parsed_data['altitude'] = weewx.units.ValueTuple(_offset,
                                                                device_units['group_altitude'],
                                                                'group_altitude')
        try:
            _offset = weeutil.weeutil.to_float(response['outTempOffset'])
        except KeyError as e:
            # we have no key 'outTempOffset', ignore and continue
            pass
        except ValueError as e:
            # we have a 'outTempOffset' key, but encountered an error processing
            # the key value, set the result to None and continue
            _parsed_data['outtemp_offset'] = weewx.units.ValueTuple(None, None, None)
        else:
            # we have a value, save the value as a ValueTuple
            _parsed_data['outtemp_offset'] = weewx.units.ValueTuple(_offset,
                                                                    device_units['group_deltat'],
                                                                    'group_deltat')
        try:
            _offset = weeutil.weeutil.to_float(response['outHumiOffset'])
        except KeyError as e:
            # we have no key 'outHumiOffset', ignore and continue
            pass
        except ValueError as e:
            # we have a 'outHumiOffset' key, but encountered an error processing
            # the key value, set the result to None and continue
            _parsed_data['outhumid_offset'] = weewx.units.ValueTuple(None, None, None)
        else:
            # we have a value, save the value as a ValueTuple
            _parsed_data['outhumid_offset'] = weewx.units.ValueTuple(_offset,
                                                                    'percent',
                                                                    'group_percent')
        try:
            _offset = weeutil.weeutil.to_float(response['windDirOffset'])
        except KeyError as e:
            # we have no key 'windDirOffset', ignore and continue
            pass
        except ValueError as e:
            # we have a 'windDirOffset' key, but encountered an error processing
            # the key value, set the result to None and continue
            _parsed_data['winddir_offset'] = weewx.units.ValueTuple(None, None, None)
        else:
            # we have a value, save the value as a ValueTuple
            _parsed_data['winddir_offset'] = weewx.units.ValueTuple(_offset,
                                                                    'degree_compass',
                                                                    'group_direction')
        # parse 'th_cli'
        try:
            _parsed_data['th_cli'] = weeutil.weeutil.to_bool(response['th_cli'])
        except KeyError as e:
            # the 'winddir_offset' key does not exist, do nothing and continue
            pass
        except ValueError:
            # we have an 'rel_offset' key but encountered an error processing
            # the 'rel_offset' value, set 'rel_offset' to None
            _parsed_data['th_cli'] = None
        # parse 'wh34_cli'
        try:
            _parsed_data['wh34_cli'] = weeutil.weeutil.to_bool(response['wh34_cli'])
        except KeyError as e:
            # the 'wh34_cli' key does not exist, do nothing and continue
            pass
        except ValueError:
            # we have an 'wh34_cli' key but encountered an error processing
            # the 'wh34_cli' value, set 'wh34_cli' to None
            _parsed_data['wh34_cli'] = None
        # parse 'pm25_cli'
        try:
            _parsed_data['pm25_cli'] = weeutil.weeutil.to_bool(response['pm25_cli'])
        except KeyError as e:
            # the 'pm25_cli' key does not exist, do nothing and continue
            pass
        except ValueError:
            # we have an 'pm25_cli' key but encountered an error processing
            # the 'pm25_cli' value, set 'pm25_cli' to None
            _parsed_data['pm25_cli'] = None
        # parse 'soil_cli'
        try:
            _parsed_data['soil_cli'] = weeutil.weeutil.to_bool(response['soil_cli'])
        except KeyError as e:
            # the 'soil_cli' key does not exist, do nothing and continue
            pass
        except ValueError:
            # we have an 'soil_cli' key but encountered an error processing
            # the 'soil_cli' value, set 'soil_cli' to None
            _parsed_data['soil_cli'] = None
        # return the parsed data
        return _parsed_data

    @staticmethod
    def parse_get_rain_totals(response, device_units):
        """Parse the response from a 'get_rain_totals' API command.

        Parse the raw JSON response from a 'get_rain_totals' API command.
        Missing response key/values are ignored, key/values that exist but
        cannot be parsed are set to None. A ParseError is raised if the
        response is malformed.

        Rainfall fields are returned as ValueTuples due to user ability to
        select rainfall units used by the device and to facilitate unit
        conversion when displayed.

        Example 'get_rain_totals' response:

            {"rainFallPriority": "2",
             "list": [{"gauge": "No rain gauge", "value": "0"},
                      {"gauge": "Traditional rain gauge", "value": "1"},
                      {"gauge": "Piezoelectric rain gauge", "value": "2"}],
             "rainDay": "0.0",
             "rainWeek": "0.0",
             "rainMonth": "0.0",
             "rainYear": "0.0",
             "rainGain": "1.00",
             "rstRainDay": "0",
             "rstRainWeek": "0",
             "rstRainYear": "0",
             "piezo": "1"}

        Returns a dict keyed as follows:

        rain_priority:   Which rain gauge data is used to publish to WU, WOW,
                         etc. Uses 'value' from list entries in 'rain_list'
                         key/value. Integer.
        rain_list:       List of dicts with details of available rain gauges.
                         Each dict is keyed as follows:
                         'gauge': Rain gauge name. String.
                         'value': Integer value used in 'rain_priority'
                                  key/value to select this gauge. Integer.
        rain_day:        Current day total rainfall. ValueTuple.
        rain_week:       Current day total rainfall. ValueTuple.
        rain_month:      Current day total rainfall. ValueTuple.
        rain_year:       Current day total rainfall. ValueTuple.
        rain_gain:       Current day total rainfall. Float.
        rain_reset_day:  Current day total rainfall. Float.
        rain_reset_week: Current day total rainfall. Float.
        rain_reset_year: Current day total rainfall. Float.
        piezo_rain:      Unknown field. Appears to be an integer, values of 1
                         observed. Key/value disappears from API response if
                         piezo rainfall gauge (WS90) is disabled.

        If the device response cannot be parsed a ParseError is raised.
        """

        # Create a throwaway copy of the response, this serves as a quick check
        # we have a dict as a response. This saves catching AttributeErrors
        # against each field we convert to a float or int.
        try:
            _ = dict(response)
        except (TypeError, ValueError) as e:
            # we have a malformed or otherwise invalid response, raise a ParseError:
            raise ParseError(f"Error parsing 'get_rain_totals' data: {e}")
        # initialise a dict to hold our parsed data
        _parsed_data = dict()
        # parse each response key/value pair adding the parsed data to our
        # result dict, wrap in a try..except in case there is a problem
        try:
            _parsed_data['rain_priority'] = weeutil.weeutil.to_int(response.get('rainFallPriority'))
        except KeyError as e:
            # the 'rainFallPriority' key does not exist, do nothing and continue
            pass
        except ValueError as e:
            # we have a 'rainFallPriority' key but encountered an error
            # processing the 'rainFallPriority' value, set 'rain_priority' to
            # None
            _parsed_data['rain_priority'] = None
        try:
            _parsed_data['rain_list'] = response['list']
        except KeyError as e:
            # the 'list' key does not exist, do nothing and continue
            pass
        # process the rain key/value pairs
        for dest, src in EcowittHttpParser.rain_map.items():
            try:
                _src_value = weeutil.weeutil.to_float(response[src])
            except KeyError as e:
                # we have no key src, ignore and continue
                continue
            except ValueError as e:
                # we have a src key, but encountered an error processing the
                # key value, set the result to None and continue
                _parsed_data[dest] = weewx.units.ValueTuple(None, None, None)
            else:
                _parsed_data[dest] = weewx.units.ValueTuple(_src_value,
                                                            device_units['group_rain'],
                                                            'group_rain')
        try:
            _parsed_data['rain_gain'] = weeutil.weeutil.to_float(response.get('rainGain'))
        except KeyError as e:
            # the 'rainGain' key does not exist, do nothing and continue
            pass
        except ValueError as e:
            # we have an 'rainGain' key but encountered an error processing the
            # 'rainGain' value, set 'rain_gain' to None
            _parsed_data['rain_gain'] = None
        try:
            _parsed_data['rain_reset_day'] = weeutil.weeutil.to_int(response.get('rstRainDay'))
        except KeyError as e:
            # the 'rstRainDay' key does not exist, do nothing and continue
            pass
        except ValueError as e:
            # we have an 'rstRainDay' key but encountered an error processing
            # the 'rstRainDay' value, set 'rain_reset_day' to None
            _parsed_data['rain_reset_day'] = None
        try:
            _parsed_data['rain_reset_week'] = weeutil.weeutil.to_int(response.get('rstRainWeek'))
        except KeyError as e:
            # the 'rstRainWeek' key does not exist, do nothing and continue
            pass
        except ValueError as e:
            # we have an 'rstRainWeek' key but encountered an error processing
            # the 'rstRainWeek' value, set 'rain_reset_week' to None
            _parsed_data['rain_reset_week'] = None
        try:
            _parsed_data['rain_reset_year'] = weeutil.weeutil.to_int(response.get('rstRainYear'))
        except KeyError as e:
            # the 'rstRainYear' key does not exist, do nothing and continue
            pass
        except ValueError as e:
            # we have an 'rstRainYear' key but encountered an error processing
            # the 'rstRainYear' value, set 'rain_reset_year' to None
            _parsed_data['rain_reset_year'] = None
        try:
            _parsed_data['rain_piezo'] = weeutil.weeutil.to_int(response.get('piezo'))
        except KeyError as e:
            # the 'piezo' key does not exist, do nothing and continue
            pass
        except ValueError as e:
            # we have an 'piezo' key but encountered an error processing the
            # 'piezo' value, set 'rain_piezo' to None
            _parsed_data['rain_piezo'] = None
        # parse the 'list'
        if 'rain_list' in _parsed_data.keys():
            # iterate over each of the 'rain_list' entries
            for gauge in _parsed_data['rain_list']:
                try:
                    gauge['value'] = weeutil.weeutil.to_int(gauge['value'])
                except KeyError as e:
                    # we have no 'value' key so ignore and continue
                    pass
        # return the parsed data
        return _parsed_data

    @staticmethod
    def parse_get_rain_totalspart(response, device_units):
        """Parse the response from a 'get_rain_totals' API command.

        Example 'get_rain_totals' response:

            {"rainFallPriority": "2",
             "list": [{"gauge": "No rain gauge", "value": "0"},
                      {"gauge": "Traditional rain gauge", "value": "1"},
                      {"gauge": "Piezoelectric rain gauge", "value": "2"}],
             "rainDay": "0.0",
             "rainWeek": "0.0",
             "rainMonth": "0.0",
             "rainYear": "0.0",
             "rainGain": "1.00",
             "rstRainDay": "0",
             "rstRainWeek": "0",
             "rstRainYear": "0",
             "piezo": "1"}


        If the device response cannot be parsed a ParseError is raised.
        """

        # Create a throwaway copy of the response, this serves as a quick check
        # we have a dict as a response. This saves catching AttributeErrors
        # against each field we convert to a float or int.
        try:
            _ = dict(response)
        except (TypeError, ValueError) as e:
            # we have a malformed or otherwise invalid response, raise a ParseError:
            raise ParseError(f"Error parsing 'get_rain_totals' data: {e}")
        # initialise a dict to hold our parsed data
        _parsed_data = dict()
        # parse each response key/value pair adding the parsed data to our
        # result dict, wrap in a try..except in case there is a problem
        try:
            _parsed_data['rain_priority'] = weeutil.weeutil.to_int(response.get('rainFallPriority'))
        except KeyError as e:
            # the 'rainFallPriority' key does not exist, do nothing and continue
            pass
        except ValueError as e:
            # we have a 'rainFallPriority' key but encountered an error
            # processing the 'rainFallPriority' value, set 'rain_priority' to
            # None
            _parsed_data['rain_priority'] = None
        try:
            _parsed_data['rain_gain'] = weeutil.weeutil.to_float(response.get('rainGain'))
        except KeyError as e:
            # the 'rainGain' key does not exist, do nothing and continue
            pass
        except ValueError as e:
            # we have an 'rainGain' key but encountered an error processing the
            # 'rainGain' value, set 'rain_gain' to None
            _parsed_data['rain_gain'] = None
        try:
            _parsed_data['rain_reset_day'] = weeutil.weeutil.to_int(response.get('rstRainDay'))
        except KeyError as e:
            # the 'rstRainDay' key does not exist, do nothing and continue
            pass
        except ValueError as e:
            # we have an 'rstRainDay' key but encountered an error processing
            # the 'rstRainDay' value, set 'rain_reset_day' to None
            _parsed_data['rain_reset_day'] = None
        try:
            _parsed_data['rain_reset_week'] = weeutil.weeutil.to_int(response.get('rstRainWeek'))
        except KeyError as e:
            # the 'rstRainWeek' key does not exist, do nothing and continue
            pass
        except ValueError as e:
            # we have an 'rstRainWeek' key but encountered an error processing
            # the 'rstRainWeek' value, set 'rain_reset_week' to None
            _parsed_data['rain_reset_week'] = None
        try:
            _parsed_data['rain_reset_year'] = weeutil.weeutil.to_int(response.get('rstRainYear'))
        except KeyError as e:
            # the 'rstRainYear' key does not exist, do nothing and continue
            pass
        except ValueError as e:
            # we have an 'rstRainYear' key but encountered an error processing
            # the 'rstRainYear' value, set 'rain_reset_year' to None
            _parsed_data['rain_reset_year'] = None
        try:
            _parsed_data['rain_piezo'] = weeutil.weeutil.to_int(response.get('piezo'))
        except KeyError as e:
            # the 'piezo' key does not exist, do nothing and continue
            pass
        except ValueError as e:
            # we have an 'piezo' key but encountered an error processing the
            # 'piezo' value, set 'rain_piezo' to None
            _parsed_data['rain_piezo'] = None
        # return the parsed data
        return _parsed_data


    @staticmethod
    def parse_get_device_infopart(response):
        """Parse the response from a 'get_device_info' API command.

        Parse the raw JSON response from a 'get_device_info' API command.
        Missing response key/values are ignored, key/values that exist but
        cannot be parsed are set to None. A ParseError is raised if the
        response is malformed.

        Example 'get_device_info' response:

            {"sensorType": "1",
             "rf_freq": "0",
             "AFC": "0",
             "tz_auto": "1",
             "tz_name": "Australia/Brisbane",
             "tz_index": "94",
             "dst_stat": "0",
             "radcompensation": "0",
             "date": "2024-07-20T12:31",
             "upgrade": "0",
             "apAuto": "1",
             "newVersion": "1",
             "curr_msg": "New version:V3.1.4\r\n- Optimize RF reception performance",
             "apName": "GW2000C-WIFI8ED2",
             "APpwd": "qwerty12345",
             "time": "20"}

        If the device response cannot be parsed a ParseError is raised.
        """

        # initialise a dict to hold our parsed data
        _parsed_data = dict()
        # parse each response key/value pair adding the parsed data to our
        # result dict, wrap in a try..except in case there is a problem
        try:
            _parsed_data['radcompensation'] = weeutil.weeutil.to_int(response['radcompensation'])
        except KeyError as e:
            # the 'radcompensation' key does not exist, do nothing and continue
            pass
        except ValueError as e:
            # we have an 'radcompensation' key but encountered an error
            # processing the 'radcompensation' value, set 'radcompensation' to None
            _parsed_data['radcompensation'] = None
        try:
            _parsed_data['upgrade'] = weeutil.weeutil.to_int(response['upgrade'])
        except KeyError as e:
            # the 'upgrade' key does not exist, do nothing and continue
            pass
        except ValueError as e:
            # we have an 'upgrade' key but encountered an error processing the
            # 'upgrade' value, set 'upgrade' to None
            _parsed_data['upgrade'] = None
        try:
            _parsed_data['newVersion'] = weeutil.weeutil.to_int(response['newVersion'])
        except KeyError as e:
            # the 'newVersion' key does not exist, do nothing and continue
            pass
        except ValueError as e:
            # we have an 'newVersion' key but encountered an error processing
            # the 'newVersion' value, set 'newVersion' to None
            _parsed_data['newVersion'] = None
        # return the parsed data
        return _parsed_data

    @staticmethod
    def parse_get_device_info(response):
        """Parse the response from a 'get_device_info' API command.

        Parse the raw JSON response from a 'get_device_info' API command.
        Missing response key/values are ignored, key/values that exist but
        cannot be parsed are set to None. A ParseError is raised if the
        response is malformed.

        Example 'get_device_info' response:

            {"sensorType": "1",
             "rf_freq": "0",
             "AFC": "0",
             "tz_auto": "1",
             "tz_name": "Australia/Brisbane",
             "tz_index": "94",
             "dst_stat": "0",
             "radcompensation": "0",
             "date": "2024-07-20T12:31",
             "upgrade": "0",
             "apAuto": "1",
             "newVersion": "1",
             "curr_msg": "New version:V3.1.4\r\n- Optimize RF reception performance",
             "apName": "GW2000C-WIFI8ED2",
             "APpwd": "qwerty12345",
             "time": "20"}

        Returns a dict keyed as follows:

        sensor_type:    Unknown data. Integer.
        rf_freq:        Device sensor receive frequency, 0=433MHz, 1=866MHz,
                        2=915MHz, 3=920MHz. Integer.
        afc:            Unknown data. Integer.
        tz_auto:        Whether device automatically sets timezone, 0=?, 1=?.
                        Integer.
        tz_name:        Device timezone name. String.
        tz_index:       Device timezone index. Integer.
        dst:            Daylight saving status, 0=disabled, 1=enabled. Integer.
        rad_comp:       Temperature radiation compensation status, 0=disabled,
                        1=enabled. Integer.
        date:           Date-time, returned as a Unix epoch timestamp. Integer.
        upgrade:        Device auto firmware upgrade status, 0=disabled,
                        1=enabled. Integer.
        ap_auto:        Whether device access point is automatically disabled,
                        0=disabled, 1=enabled. Integer.
        new_version:    Whether a new firmware version is available, 0=no,
                        1=yes. Integer.
        curr_msg:       Currently available firmware message. String.
        ap:             Device access point name. String.
        ap_pwd:         Obfuscated device access point password. String
        time:           Unknown data. Integer.

        If the device response cannot be parsed a ParseError is raised.
        """

        # initialise a dict to hold our parsed data
        _parsed_data = dict()
        # parse each response key/value pair adding the parsed data to our
        # result dict, wrap in a try..except in case there is a problem
        try:
            _parsed_data['sensor_type'] = weeutil.weeutil.to_int(response['sensorType'])
        except KeyError as e:
            # the 'sensorType' key does not exist, do nothing and continue
            pass
        except ValueError as e:
            # we have an 'sensorType' key but encountered an error processing
            # the 'sensorType' value, set 'sensor_type' to None
            _parsed_data['sensor_type'] = None
        try:
            _parsed_data['rf_freq'] = weeutil.weeutil.to_int(response['rf_freq'])
        except KeyError as e:
            # the 'rf_freq' key does not exist, do nothing and continue
            pass
        except ValueError as e:
            # we have an 'rf_freq' key but encountered an error processing the
            # 'rf_freq' value, set 'rf_freq' to None
            _parsed_data['rf_freq'] = None
        try:
            _parsed_data['afc'] = weeutil.weeutil.to_int(response['AFC'])
        except KeyError as e:
            # the 'AFC' key does not exist, do nothing and continue
            pass
        except ValueError as e:
            # we have an 'AFC' key but encountered an error processing
            # the 'AFC' value, set 'afc' to None
            _parsed_data['afc'] = None
        try:
            _parsed_data['tz_auto'] = weeutil.weeutil.to_int(response['tz_auto'])
        except KeyError as e:
            # the 'tz_auto' key does not exist, do nothing and continue
            pass
        except ValueError as e:
            # we have an 'tz_auto' key but encountered an error processing  the
            # 'tz_auto' value, set 'tz_auto' to None
            _parsed_data['tz_auto'] = None
        try:
            _parsed_data['tz_name'] = response['tz_name']
        except KeyError as e:
            # the 'tz_name' key does not exist, do nothing and continue
            pass
        except ValueError as e:
            # we have an 'tz_name' key but encountered an error processing the
            # 'tz_name' value, set 'tz_name' to None
            _parsed_data['tz_name'] = None
        try:
            _parsed_data['tz_index'] = weeutil.weeutil.to_int(response['tz_index'])
        except KeyError as e:
            # the 'tz_index' key does not exist, do nothing and continue
            pass
        except ValueError as e:
            # we have an 'tz_index' key but encountered an error processing the
            # 'tz_index' value, set 'tz_index' to None
            _parsed_data['tz_index'] = None
        try:
            _parsed_data['dst'] = weeutil.weeutil.to_int(response['dst_stat'])
        except KeyError as e:
            # the 'dst_stat' key does not exist, do nothing and continue
            pass
        except ValueError as e:
            # we have an 'dst_stat' key but encountered an error processing the
            # 'dst_stat' value, set 'dst' to None
            _parsed_data['dst'] = None
        try:
            _parsed_data['rad_comp'] = weeutil.weeutil.to_int(response['radcompensation'])
        except KeyError as e:
            # the 'radcompensation' key does not exist, do nothing and continue
            pass
        except ValueError as e:
            # we have an 'radcompensation' key but encountered an error
            # processing the 'radcompensation' value, set 'rad_comp' to None
            _parsed_data['rad_comp'] = None
        try:
            _parsed_data['upgrade'] = weeutil.weeutil.to_int(response['upgrade'])
        except KeyError as e:
            # the 'upgrade' key does not exist, do nothing and continue
            pass
        except ValueError as e:
            # we have an 'upgrade' key but encountered an error processing the
            # 'upgrade' value, set 'upgrade' to None
            _parsed_data['upgrade'] = None
        try:
            _parsed_data['ap_auto'] = weeutil.weeutil.to_int(response['apAuto'])
        except KeyError as e:
            # the 'apAuto' key does not exist, do nothing and continue
            pass
        except ValueError as e:
            # we have an 'apAuto' key but encountered an error processing the
            # 'apAuto' value, set 'upgrade' to None
            _parsed_data['ap_auto'] = None
        try:
            _parsed_data['newVersion'] = weeutil.weeutil.to_int(response['newVersion'])
        except KeyError as e:
            # the 'newVersion' key does not exist, do nothing and continue
            pass
        except ValueError as e:
            # we have an 'newVersion' key but encountered an error processing
            # the 'newVersion' value, set 'newVersion' to None
            _parsed_data['newVersion'] = None
        try:
            _parsed_data['curr_msg'] = response['curr_msg']
        except KeyError as e:
            # the 'curr_msg' key does not exist, do nothing and continue
            pass
        try:
            _parsed_data['ap'] = response['apName']
        except KeyError as e:
            # the 'apName' key does not exist, do nothing and continue
            pass
        except ValueError as e:
            # we have an 'apName' key but encountered an error processing the
            # 'apName' value, set 'ap' to None
            _parsed_data['ap'] = None
        try:
            _parsed_data['ap_pwd'] = obfuscate(response['APpwd'])
        except KeyError as e:
            # the 'APpwd' key does not exist, do nothing and continue
            pass
        try:
            _parsed_data['time'] = weeutil.weeutil.to_int(response['time'])
        except KeyError as e:
            # the 'time' key does not exist, do nothing and continue
            pass
        except ValueError as e:
            # we have an 'time' key but encountered an error processing the
            # 'time' value, set 'time' to None
            _parsed_data['rain_reset_day'] = None
        # parse 'date'
        # attempt to parse the 'date' key/value and obtain a datetime object,
        # be prepared to catch any exceptions
        try:
            _date_dt = datetime.datetime.strptime(response['date'],
                                                  '%Y-%m-%dT%H:%M')
        except KeyError as e:
            # we have no 'date' key so ignore and continue
            pass
        except (TypeError, ValueError) as e:
            # we have a 'date' key/value pair but we could not parse the value,
            # set 'date' to None
            _parsed_data['date'] = None
        else:
            # we have a datetime object, convert to an epoch timestamp and save
            # as the 'date' value
            _parsed_data['date'] = int(time.mktime(_date_dt.timetuple()))
        # return the parsed data
        return _parsed_data

    @staticmethod
    def parse_get_network_info(response):
        """Parse the response from a 'get_network_info' API command.

        Parse the raw JSON response from a 'get_network_info' API command.
        Missing response key/values are ignored, key/values that exist but
        cannot be parsed are set to None. A ParseError is raised if the
        response is malformed.

        Example 'get_network_info' response:

            {"mac":"1C:69:24:23:DB:6A",
             "ethIpType":"1",
             "ethIP":"0.0.0.0",
             "ethMask":"0.0.0.0",
             "ethGateway":"0.0.0.0",
             "ethDNS":"192.168.2.2",
             "ssid":"MyWifiSSID",
             "wifi_pwd":"ZjFWjDFuZzA=",
             "wifi_DNS":"192.168.2.99",
             "staIpType":"1",
             "wifi_ip":"192.168.2.25",
             "wifi_mask":"255.255.255.0",
             "wifi_gateway":"192.168.2.1"}

        Returns a dict keyed as follows:

        mac:                Device MAC address. String.
        ssid:               SSID the device will connect to. String.
        ethIpType:          Ethernet interface IP type, 0=static IP, 1=DHCP
                            assigned IP. Integer.
        ethIP               Ethernet interface IP address. String.
        ethMask:            Ethernet interface mask. String.
        ethGateway:         Ethernet interface gateway IP address. String.
        ethDNS:"            Ethernet interface DNS IP address. String.
        wifi_pwd:           Obfuscated WiFi password. String
        staIpType:          WiFi interface IP type, 0=static IP, 1=DHCP
                            assigned IP. Integer.
        wifi_ip:            WiFi interface IP address. String.
        wifi_mask:          WiFi interface mask. String.
        wifi_gateway:       WiFi interface gateway IP address. String.
        wifi_DNS:           WiFi DNS IP address. String.

        If the device response cannot be parsed a ParseError is raised.
        """

        # create a copy of the response, this will be the starting point for
        # our parsed data, wrapt in a try..except in case we have an invalid
        # response
        try:
            _parsed_data = dict(response)
        except (TypeError, ValueError) as e:
            # we have a malformed or otherwise invalid response, raise a
            # ParseError
            raise ParseError(f"Error parsing 'parse_get_network_info' data: {e}")
        # just for extra security make a copy of the wifi password and then pop
        # the key from our parsed data, it will be added in obfuscated form
        # later
        wifi_pwd = response.get('wifi_pwd')
        _ = _parsed_data.pop('wifi_pwd', None)
        # now process all of the key/value pairs that need some form of
        # conversion
        # process 'eth_ip_type'
        try:
            _parsed_data['eth_ip_type'] = weeutil.weeutil.to_int(response['ethIpType'])
        except KeyError as e:
            # we have no 'eth_ip_type', ignore and continue
            pass
        except ValueError:
            # we have an 'eth_ip_type' key but encountered an error processing
            # the 'eth_ip_type' value, set 'eth_ip_type' to None
            _parsed_data['eth_ip_type'] = None
        # process 'staIpType'
        try:
            _parsed_data['staIpType'] = weeutil.weeutil.to_int(response['staIpType'])
        except KeyError as e:
            # we have no 'staIpType', ignore and continue
            pass
        except ValueError:
            # we have an 'staIpType' key but encountered an error processing
            # the 'staIpType' value, set 'staIpType' to None
            _parsed_data['staIpType'] = None
        # process 'wifi_pwd'
        # if the 'wifi_pwd' key exists in the response obfuscate it and save to
        # the parsed data, otherwise do nothing
        if wifi_pwd is not None:
            _parsed_data['wifi_pwd'] = obfuscate(wifi_pwd)
        # return the parsed data
        return _parsed_data

    @staticmethod
    def parse_get_units_info(response):
        """Parse the response from a 'get_units_info' API command.

        Parse the raw JSON response from a 'get_units_info' API command.

        Example 'get_units_info' response:

            {"temperature": "0",
             "pressure": "0",
             "wind": "1",
             "rain": "0",
             "light": "1" }

        Ecowitt has adopted a common approach for all units by using an integer
        to represent different units used for different typ os obs. To
        hopefully cater for any future additions to units, parsing of the
        'get_units_info' response will involve iterating over all available
        response keys and converting the corresponding value to an integer.

        Returns a dict keyed as follows:

        temperature:    Device temperature units, 0=°C, 1=°F. Integer.
        pressure:       Device temperature units, 0=hPa, 1=inHg, 2=mmHg.
                        Integer.
        wind:           Device temperature units, 0=m/s, 1=km/h, 2=mph,
                        3=knots. Integer.
        rain:           Device temperature units, 0=mm, 1=in. Integer.
        light:          Device temperature units, 0=Klux, 1=W/m², 2=Kfc.
                        Integer.

        If the device response cannot be parsed a ParseError is raised.
        """


        # create a copy of the response, this will be the starting point for
        # our parsed data, wrapt in a try..except in case we have an invalid
        # response
        try:
            _parsed_data = dict(response)
        except (TypeError, ValueError) as e:
            # we have a malformed or otherwise invalid response, raise a
            # ParseError
            raise ParseError(f"Error parsing 'parse_get_units_info' data: {e}")
        # iterate over the available keys in the response and coalesce an int
        # from each key value
        for key in _parsed_data.keys():
            # attempt to convert the key value to an integer, be prepared to
            # catch any exceptions if fails
            try:
                _parsed_data[key] = weeutil.weeutil.to_int(response[key])
            except ValueError as e:
                # we could not convert the key value to an integer, save the
                # value as None
                _parsed_data[key] = None
        # return the parsed data
        return _parsed_data

    @staticmethod
    def parse_get_cli_soilad(response):
        """Parse the response from a 'get_cli_soilad' API command.

        Parse the raw JSON response from a 'get_cli_soilad' API command.
        Malformed sensor data or sensor data without an integer channel number
        is ignored. Missing sensor key/values are ignored, key/values that
        exist but cannot be parsed are set to None.

        Example 'get_cli_soilad' response:

            [{"id": "0xCD19", "ch": "1", "name": "Trough", "soilVal": "0",
              "nowAd": "136", "minVal": "170", "maxVal": "320",  "checked": true},
             {"id": "0xBA23", "ch": "2", "name": "Flowers", "soilVal": "0",
              "nowAd": "126", "minVal": "160", "maxVal": "350", "checked": true}]

        Returns a list of dicts, one dict per channel sorted in ascending
        channel order. Each dict keyed as follows:

        id:         Sensor ID. String.
        channel:    Sensor channel number, first channel is 1. Integer.
        name:       Sensor name as per WSViewPlus app. String.
        soilVal:    Soil wetness value. Integer.
        nowAd:      Sensor AD value. Integer.
        minVal:     Soil AD value representing 0% when using custom
                    calculated soil moisture. Integer.
        maxVal:     Soil AD value representing 100% when using custom
                    calculated soil moisture. Integer.
        checked:    Custom calculation of soil moisture from 0% and 100%
                    values, false=non-custom, true=custom. Boolean.
        """

        # initialise a list to hold our result
        _parsed_data = []
        # iterate over each sensor in the response
        for sensor in response:
            # Create a copy of the sensor data, this serves as a quick check we
            # have a well formed dict of sensor data. This saves catching
            # AttributeErrors against each field we process.
            try:
                _ = dict(sensor)
            except (TypeError, ValueError) as e:
                # we have malformed or otherwise invalid sensor data, ignore
                # this sensor and continue
                continue
            # create a dict to hold the data for this sensor
            _sensor_data = dict()
            # obtain the channel number
            try:
                _sensor_data['channel'] = int(sensor['ch'])
            except (KeyError, TypeError, ValueError):
                # There is no 'channel' key or we cannot convert the 'channel'
                # key value to a numeric. Either way we cannot continue with
                # this sensor. Move on to the next channel.
                continue
            # process 'id'
            try:
                _sensor_data['id'] = sensor['id']
            except KeyError as e:
                # we have no 'id', ignore and continue
                pass
            # process 'name'
            try:
                _sensor_data['name'] = sensor['name']
            except KeyError as e:
                # we have no 'name', ignore and continue
                pass
            # process the key/value pairs that need to coalesce to an int
            for k in ('soilVal', 'nowAd', 'minVal', 'maxVal'):
                try:
                    _sensor_data[k] = weeutil.weeutil.to_int(sensor[k])
                except KeyError as e:
                    # we have no key k, ignore and continue
                    continue
                except ValueError as e:
                    # we have a k key but encountered an error processing the
                    # key value, set the result to None and continue
                    _sensor_data[k] = None
            try:
                _sensor_data['checked'] = weeutil.weeutil.to_bool(sensor['checked'])
            except KeyError as e:
                # we have no key 'checked', ignore and continue
                pass
            except ValueError as e:
                # we have a 'checked' key, but encountered an error processing
                # the key value, set the result to None and continue
                _sensor_data['checked'] = None
            # add the parsed sensor data dict to our our result list
            _parsed_data.append(_sensor_data)
        # return our list, sorted by channel number
        return sorted(_parsed_data, key=itemgetter('channel'))


    def parse_get_cli_multich(self, response, device_units=None):
        """Parse the response from a 'get_cli_multiCh' API command.

        Parse the raw JSON response from a 'get_cli_multiCh' API command.
        Malformed sensor data or sensor data without an integer channel number
        is ignored. Missing sensor key/values are ignored, key/values that
        exist but cannot be parsed are set to None.

        Example 'get_cli_multiCh' response:

            [{"id": "0x5B", "name": "Garage", "channel": "1", "temp": "0.0", "humi": "0"},
             {"id": "0xBE", "name": "Study", "channel": "2", "temp": "0.0", "humi": "0"},
             {"id": "0xD0", "name": "Kitchen", "channel": "3", "temp": "0.0", "humi": "0"},
             {"id": "0x52", "name": "Greenhouse", "channel": "4", "temp": "0.0", "humi": "0"},
             {"id": "0xEE", "name": "Porch", "channel": "7", "temp": "0.0", "humi": "0"}]

        Returns a list of dicts, one dict per channel sorted in ascending
        channel number order. Each dict keyed as follows:

        id:      Sensor ID. String.
        channel: Sensor channel number, first channel is 1. Integer.
        name:    Sensor name as per WSViewPlus app. String.
        temp:    Sensor temperature value. Float.
        humi:    Sensor humidity value. Integer.
        """

        # initialise a list to hold our result
        _parsed_data = []
        # iterate over each sensor in the response
        for sensor in response:
            # Create a copy of the sensor data, this serves as a quick check we
            # have a well formed dict of sensor data. This saves catching
            # AttributeErrors against each field we process.
            try:
                _ = dict(sensor)
            except (TypeError, ValueError) as e:
                # we have malformed or otherwise invalid sensor data, ignore
                # this sensor and continue
                continue
            # create a dict to hold the data for this sensor
            _sensor = dict()
            # obtain the channel number
            try:
                _sensor['channel'] = int(sensor['channel'])
            except (KeyError, TypeError, ValueError):
                # There is no 'channel' key or we cannot convert the 'channel'
                # key value to a numeric. Either way we cannot continue with
                # this sensor. Move on to the next channel.
                continue
            # process 'id'
            try:
                _sensor['id'] = sensor['id']
            except KeyError as e:
                # we have no 'id', ignore and continue
                pass
            # process 'name'
            try:
                _sensor['name'] = sensor['name']
            except KeyError as e:
                # we have no 'name', ignore and continue
                pass
            # obtain the temperature value, wrap in a try.. except in case
            # there is a problem
            try:
                # first obtain the temperature as a ValueTuple
                _sensor['temp'] = self.parse_obs_value(key='temp',
                                                       json_object=sensor,
                                                       unit_group='group_deltat',
                                                       device_units=device_units)
            except KeyError:
                # we have no 'temp' key so we cannot continue with this sensor
                continue
            except ParseError as e:
                # we have a 'temp' key but there was a problem processing the
                # data, so set the 'temp' key/value to None
                _sensor['temp'] = None
            # process the humidity value, wrap in a try..except in case there
            # is a problem
            try:
                # first obtain the humidity as a ValueTuple
                _sensor['humi'] = self.parse_obs_value(key='humi',
                                                       json_object=sensor,
                                                       unit_group='group_percent',
                                                       device_units=device_units)
            except KeyError:
                # we have no 'humi' key so we cannot continue with this sensor
                continue
            except ParseError as e:
                # the 'humi' key exists but there was a problem processing
                # the data, set the 'humidity' key/value to None
                _sensor['humi'] = None
            # add the parsed sensor data dict to our our result list
            _parsed_data.append(_sensor)
        # return our list, sorted by channel number
        return sorted(_parsed_data, key=itemgetter('channel'))

    def parse_get_cli_pm25(self, response, device_units=None):
        """Parse the response from a 'get_cli_pm25' API command.

        Parse the raw JSON response from a 'get_cli_pm25' API command.
        Malformed sensor data or sensor data without an integer channel number
        is ignored. Missing sensor key/values are ignored, key/values that
        exist but cannot be parsed are set to None.

        Example 'get_cli_pm25' response:

            [{"id": "0xC497", "name": "Kitchen", "channel": "1", "val": "0.0"},
             {"id": "0xA4D7", "name": "Porch", "channel": "2", "val": "0.0"}]

        Returns a list of dicts, one dict per channel sorted in ascending
        channel number order. Each dict keyed as follows:

        id:          Sensor ID. String.
        channel:     Sensor channel number, first channel is 1. Integer.
        name:        Sensor name as per WSViewPlus app. String.
        val:         Sensor PM2.5 value. Float.
        """

        # initialise a list to hold our result
        _parsed_data = []
        # iterate over each sensor in the response
        for sensor in response:
            # Create a copy of the sensor data, this serves as a quick check we
            # have a well formed dict of sensor data. This saves catching
            # AttributeErrors against each field we process.
            try:
                _ = dict(sensor)
            except (TypeError, ValueError) as e:
                # we have malformed or otherwise invalid sensor data, ignore
                # this sensor and continue
                continue
            # create a dict to hold the data for this sensor
            _sensor = dict()
            # obtain the channel number
            try:
                _sensor['channel'] = int(sensor['channel'])
            except (KeyError, TypeError, ValueError):
                # There is no 'channel' key or we cannot convert the 'channel'
                # key value to a numeric. Either way we cannot continue with
                # this sensor. Move on to the next channel.
                continue
            # process 'id'
            try:
                _sensor['id'] = sensor['id']
            except KeyError as e:
                # we have no 'id', ignore and continue
                pass
            # process 'name'
            try:
                _sensor['name'] = sensor['name']
            except KeyError as e:
                # we have no 'name', ignore and continue
                pass
            # process 'val'
            try:
                # obtain the PM2.5 offset as a ValueTuple
                _sensor['val'] = self.parse_obs_value(key='val',
                                                      json_object=sensor,
                                                      unit_group='group_concentration',
                                                      device_units=device_units)
            except KeyError:
                # we have no 'temp' key so we cannot continue with this sensor
                continue
            except ParseError as e:
                # we have a 'temp' key but there was a problem processing the
                # data, so set the 'temp' key/value to None
                _sensor['val'] = None
            # add the parsed sensor data dict to our our result list
            _parsed_data.append(_sensor)
        # return our list, sorted by channel number
        return sorted(_parsed_data, key=itemgetter('channel'))

    def parse_get_cli_co2(self, response, device_units=None):
        """Parse the response from a 'get_cli_co2' API command.

        Parse the raw JSON response from a 'get_cli_co2' API command.
        Missing response key/values are ignored, key/values that exist but
        cannot be parsed are set to None. A ParseError is raised if the
        response is malformed.

        Example 'get_cli_co2' response:

        #TODO Need a proper example response
        {"co2": "10000",
         "pm25": "0.0",
         "pm10": "0.0"}

        Returns a dict keyed as follows:

        # TODO. Need to provide result format

        If the device response cannot be parsed a ParseError is raised.
        """

        # Create a copy of the response, this serves as a quick check we have a
        # dict as a response. This saves catching AttributeErrors against each
        # field we convert to a float or int.
        try:
            _ = dict(response)
        except (TypeError, ValueError) as e:
            # we have a malformed or otherwise invalid response, raise a ParseError:
            raise ParseError(f"Error parsing 'parse_get_cli_co2' data: {e}")
        # initialise a dict to hold our parsed data
        _parsed_data = dict()
        # process the key/value pairs that need to coalesce to a float
        for k in ('pm1', 'pm25', 'pm4', 'pm10'):
            try:
                # obtain the offset value as a ValueTuple
                _parsed_data[k] = self.parse_obs_value(key=k,
                                                       json_object=response,
                                                       unit_group='group_concentration',
                                                       device_units=device_units)
            except KeyError:
                # we have no 'temp' key so we cannot continue with this sensor
                continue
            except ParseError as e:
                # we have a 'temp' key but there was a problem processing the
                # data, so set the 'temp' key/value to None
                _parsed_data[k] = None
        try:
            # obtain the offset value as a ValueTuple
            _parsed_data['co2'] = self.parse_obs_value(key='co2',
                                                       json_object=response,
                                                       unit_group='group_fraction',
                                                       device_units=device_units)
        except KeyError:
            # we have no 'temp' key so we cannot continue with this sensor
            pass
        except ParseError as e:
            # we have a 'temp' key but there was a problem processing the
            # data, so set the 'temp' key/value to None
            _parsed_data['co2'] = None
        # process 'id'
        try:
            _parsed_data['id'] = response['id']
        except KeyError as e:
            # we have no 'id', ignore and continue
            pass
        # process 'name'
        try:
            _parsed_data['name'] = response['name']
        except KeyError as e:
            # we have no 'name', ignore and continue
            pass
        # return the parsed data
        return _parsed_data

    @staticmethod
    def parse_get_piezo_rain(response, device_unit_data):
        """Parse the response from a 'get_piezo_rain' API command.

        Parse the raw JSON response from a 'get_piezo_rain' API command.

        Example 'get_piezo_rain' response:

        {"drain_piezo": "0.0",
         "wrain_piezo": "0.0",
         "mrain_piezo": "27.1",
         "yrain_piezo": "1077.5",
         "rain1_gain": "0.90",
         "rain2_gain": "0.90",
         "rain3_gain": "0.90",
         "rain4_gain": "0.90",
         "rain5_gain": "0.90"}

        Returns a dict keyed depending on the data included in the API
        response. Available keys are:

        day_rain:   Piezo day rain. Optional. Float, may be None.
        week_rain:  Piezo week rain. Optional. Float, may be None.
        month_rain: Piezo month rain. Optional. Float, may be None.
        year_rain:  Piezo year rain. Optional. Float, may be None.
        gain1:      Piezo rain gain 1. Optional. Float, may be None.
        gain2:      Piezo rain gain 2. Optional. Float, may be None.
        gain3:      Piezo rain gain 3. Optional. Float, may be None.
        gain4:      Piezo rain gain 4. Optional. Float, may be None.
        gain5:      Piezo rain gain 5. Optional. Float, may be None.

        If the device response cannot be parsed a ParseError is raised.
        """

        # Create a throwaway copy of the response, this serves as a quick check
        # we have a dict as a response. This saves catching AttributeErrors
        # against each field we convert to a float or int.
        try:
            _ = dict(response)
        except (TypeError, ValueError) as e:
            # we have a malformed or otherwise invalid response, raise a ParseError:
            raise ParseError(f"Error parsing 'get_piezo_rain' data: {e}")
        # initialise a dict to hold our parsed data
        _parsed_data = dict()
        # process the rain key/value pairs
        for dest, src in EcowittHttpParser.piezo_rain_map.items():
            try:
                _src_value = weeutil.weeutil.to_float(response[src])
            except KeyError as e:
                # we have no key src, ignore and continue
                continue
            except ValueError as e:
                # we have a src key, but encountered an error processing the
                # key value, set the result to None and continue
                _parsed_data[dest] = weewx.units.ValueTuple(None, None, None)
            else:
                _parsed_data[dest] = weewx.units.ValueTuple(_src_value,
                                                            device_unit_data['group_rain'],
                                                            'group_rain')
        # process piezo gain settings, this is a simple convert to float
        for gain_channel in range(5):
            src_field_name = f"rain{gain_channel + 1:d}_gain"
            dest_field_name = f"gain{gain_channel + 1:d}"
            try:
                _parsed_data[dest_field_name] = weeutil.weeutil.to_float(response[src_field_name])
            except KeyError as e:
                # we have no key src_field_name, ignore and continue
                continue
            except ValueError as e:
                # we have a src_field_name key, but encountered an error
                # processing the key value, set the result to None and continue
                _parsed_data[dest_field_name] = None
        # return the parsed data
        return _parsed_data

    @staticmethod
    def parse_get_piezo_rainpart(response, device_unit_data):
        """Parse the response from a 'get_piezo_rain' API command.

        Parse the raw JSON response from a 'get_piezo_rain' API command.

        Example 'get_piezo_rain' response:

        {"drain_piezo": "0.0",
         "wrain_piezo": "0.0",
         "mrain_piezo": "27.1",
         "yrain_piezo": "1077.5",
         "rain1_gain": "0.90",
         "rain2_gain": "0.90",
         "rain3_gain": "0.90",
         "rain4_gain": "0.90",
         "rain5_gain": "0.90"}

        If the device response cannot be parsed a ParseError is raised.
        """

        # Create a throwaway copy of the response, this serves as a quick check
        # we have a dict as a response. This saves catching AttributeErrors
        # against each field we convert to a float or int.
        try:
            _ = dict(response)
        except (TypeError, ValueError) as e:
            # we have a malformed or otherwise invalid response, raise a ParseError:
            raise ParseError(f"Error parsing 'get_piezo_rain' data: {e}")
        # initialise a dict to hold our parsed data
        _parsed_data = dict()
        # process piezo gain settings, this is a simple convert to float
        for gain_channel in range(5):
            src_field_name = f"rain{gain_channel + 1:d}_gain"
            dest_field_name = f"gain{gain_channel + 1:d}"
            try:
                _parsed_data[dest_field_name] = weeutil.weeutil.to_float(response[src_field_name])
            except KeyError as e:
                # we have no key src_field_name, ignore and continue
                continue
            except ValueError as e:
                # we have a src_field_name key, but encountered an error
                # processing the key value, set the result to None and continue
                _parsed_data[dest_field_name] = None
        # return the parsed data
        return _parsed_data



    def parse_get_cli_wh34(self, response, device_units=None):
        """Parse the response from a 'get_cli_wh34' API command.

        Parse the raw JSON response from a 'parse_get_cli_wh34' API command.

        Example 'get_cli_wh34' response:

        [{"id": "0x2AE7",
          "name": "pool",
          "channel": "1",
          "temp": "20.1"},
          {"id": "0x2DC1",
          "name": "tank",
          "channel": "3",
          "temp": "19.0"}]

        Returns a list of dicts, one dict per channel sorted in ascending
        channel number order. Each dict keyed as follows:

        id:          Sensor ID. String.
        channel:     Sensor channel number, first channel is 1. Integer.
        name:        Sensor name as per WSViewPlus app. String.
        temp:        Sensor temperature value. Float.

        If the device response cannot be parsed a ParseError is raised.
        """

        # First up, do we have any device temperature unit info? The
        # 'get_cli_wh34' API command does not return any unit info so without
        # any device unit info we cannot parse any sensor temperature data.
        if device_units is None or 'group_temperature' not in device_units.keys():
            raise ParseError('No WN34 or device temperature unit information.')
        # initialise a list to hold our result
        _parsed_data = []
        # iterate over each sensor in the response
        for sensor in response:
            # create a dict to hold the data for this sensor
            _sensor = dict()
            # get the channel number, wrap in try..except in case there is a
            # problem
            try:
                _sensor['channel'] = int(sensor['channel'])
            except (KeyError, TypeError, ValueError) as e:
                # The 'channel' key does not exist or we cannot convert the
                # 'channel' key/value cannot be converted to an int, either way
                # we cannot continue with this sensor.
                continue
            # obtain the temperature value, wrap in a try.. except in case
            # there is a problem
            try:
                # first obtain the temperature as a ValueTuple
                _sensor['temp'] = self.parse_obs_value(key='temp',
                                                       json_object=sensor,
                                                       unit_group='group_deltat',
                                                       device_units=device_units)
            except KeyError:
                # we have no 'temp' key so we cannot continue with this sensor
                continue
            except ParseError as e:
                # we have a 'temp' key but there was a problem processing the
                # data, so set the 'temp' key/value to None
                _sensor['temp'] = None
            # add the sensor ID value
            _sensor['id'] = sensor.get('id')
            # add the sensor name
            _sensor['name'] = sensor.get('name')
            # add the sensor data to our result list
            _parsed_data.append(_sensor)
        # return our list, sorted by channel number
        return sorted(_parsed_data, key=itemgetter('channel'))

    def parse_get_cli_lds(self, response):
        """Parse the response from a 'get_cli_lds' API command.

        Parse the raw JSON response from a 'parse_get_cli_lds' API command.

        Example 'get_cli_lds' response:

        [{"id": "0x28DB",
          "ch": "1",
          "name": "Tank",
          "unit": "mm",
          "offset": "-383",
          "total_height": "2030",
          "total_heat": "1793",
          "level": "0"}]

        Returns a list of dicts of multichannel temperature sensor data sorted by
        ascending channel number. Each dict keyed as follows:

        id:           Sensor ID. String.
        channel:      Sensor channel number, first channel is 1. Integer.
        name:         Sensor name as per WSViewPlus app. String.
        unit:         Offset and total height unit string. String, 'mm' or 'ft'.
        offset:       Sensor offset value. Float.
        total_height: Sensor total height value. Float.
        total_heat:   Total sensor heat count. Integer.
        level:        Data filter factor (suspected). Integer, 0 to 4 inclusive.

        If the device response cannot be parsed a ParseError is raised.
        """

        # initialise a list to hold our result
        _parsed_data = []
        # iterate over each sensor in the response
        for sensor in response:
            # create a dict to hold the data for this sensor
            _sensor = dict()
            # get the channel number, wrap in try..except in case there is a
            # problem
            try:
                _sensor['channel'] = int(sensor['ch'])
            except (KeyError, TypeError, ValueError) as e:
                # The 'channel' key does not exist or we cannot convert the
                # 'channel' key/value cannot be converted to an int, either way
                # we cannot continue with this sensor.
                continue
            # obtain the 'offset' value, wrap in a try.. except in case there
            # is a problem
            try:
                # save the 'offset' key/value as a ValueTuple
                _sensor['offset'] = self.parse_obs_value(key='offset',
                                                         json_object=sensor,
                                                         unit_group='group_depth')
            except KeyError:
                # the 'offset' key does not exist, we cannot continue with this
                # key
                pass
            except ParseError as e:
                # the 'offset' key exists but there was a problem processing
                # the data, set the 'offset' key/value to None
                _sensor['offset'] = weewx.units.ValueTuple(None, None, None)
            # obtain the 'total_height' value, wrap in a try.. except in case
            # there is a problem
            try:
                # save the 'total_height' key/value as a ValueTuple
                _sensor['total_height'] = self.parse_obs_value(key='total_height',
                                                               json_object=sensor,
                                                               unit_group='group_depth')
            except KeyError:
                # the 'total_height' key does not exist, we cannot continue
                # with this key
                pass
            except ParseError as e:
                # the 'total_height' key exists but there was a problem
                # processing the data, set the 'total_height' key/value to None
                _sensor['total_height'] = weewx.units.ValueTuple(None, None, None)
            # get the total_heat number, wrap in try..except in case there is a
            # problem
            try:
                _sensor['total_heat'] = int(sensor['total_heat'])
            except KeyError:
                # the 'total_heat' key does not exist, we cannot continue with
                # this key
                pass
            except (TypeError, ValueError) as e:
                # the 'total_heat' key exists but there was a problem
                # processing the data, set the 'total_heat' key/value to None
                _sensor['total_heat'] = None
            # get the data filter factor, wrap in try..except in case there is a
            # problem
            try:
                _sensor['level'] = int(sensor['level'])
            except KeyError:
                # the 'level' key does not exist, we cannot continue with this
                # key
                pass
            except (TypeError, ValueError) as e:
                # the 'level' key exists but there was a problem processing the
                # data, set the 'total_heat' key/value to None
                _sensor['level'] = None
            # if we don't have either an 'offset', 'total_height' or
            # 'total_heat' key/value pair in our results for this sensor we
            # should ignore the sensor
            if not(set(_sensor.keys()) & {'offset', 'total_height', 'total_heat'}):
                continue
            # add the sensor id
            _sensor['id'] = sensor.get('id')
            # add the sensor name
            _sensor['name'] = sensor.get('name')
            # add the parsed sensor data to our result list
            _parsed_data.append(_sensor)
        # return our list, sorted by channel number
        return sorted(_parsed_data, key=itemgetter('channel'))

    @staticmethod
    def parse_get_sdmmc_info(response):
        """Parse the response from a 'get_sdmmc_info' API command.

        Parse the raw JSON response from a 'get_sdmmc_info' API command. The
        only conversion required is to convert the 'info', 'Interval' field
        from a string to numeric.

        Example 'get_sdmmc_info' response:

            {"info": {"Name": "SC16G",
                      "Type": "SDHC/SDXC",
                      "Speed": "20 MHz",
                      "Size": "15193 MB",
                      "Interval": "5"},
            "file_list": [{"name": "202412B.csv",
                           "type": "file",
                           "size": "249 KB"},
                          {"name": "202412Allsensors_B.csv",
                           "type": "file",
                           "size": "581 KB"},
                          {"name": "202412C.csv",
                           "type": "file",
                           "size": "2 KB"},
                          {"name": "202412Allsensors_C.csv",
                           "type": "file",
                           "size": "210 KB"},
                          {"name": "202501A.csv",
                           "type": "file",
                           "size": "46 KB"},
                          {"name": "202501Allsensors_A.csv",
                           "type": "file",
                           "size": "153 KB"}]}

        Returns a dict keyed as follows:

        info:       a dict of SD card data
        file_list:  a list of dicts of file information for history data files
                    on the SD card

        If the device response cannot be parsed a ParseError is raised.
        """

        # The only processing of the response we need do is convert the 'info',
        # 'interval' key to a numeric. Make a copy of the response and then try
        # to convert the 'info' ,'interval' key/value to an int. Wrap in a
        # try..except in case we have a problem.
        try:
            _parsed_data = dict(response)
            _parsed_data['info']['interval'] = int(response['info']['Interval'])
        except (KeyError, TypeError, ValueError) as e:
            raise ParseError(f"Error parsing 'get_sdmmc_info' data: {e}")
        return _parsed_data

    def process_common_list_array(self, response):
        """Process a common_list array.

        Processes a common_list JSON array resulting from a get_livedata_info
        local HTTP API call. The process_common_list_array method:

        - converts observation values to a unit consistent with the WeeWX unit
          system being used by the driver
        - converts observation values from string to numeric values
        - unit labels and unit label keys are removed
        - removes sensor battery keys as sensor battery state info is obtained
          via the 'get_sensors_info' API command
        - formats the array data in a manner suitable for later flattening to
          support a 'dot-field' mapping system

        Example common_list JSON array:

            "common_list": [{"id": "0x02",
                             "val": "26.5",
                             "unit": "C"},
                            {"id": "0x07",
                             "val": "85%"},
                            {"id": "3",
                             "val": "26.5",
                             "unit": "C"},
                            {"id": "0x03",
                             "val": "23.8",
                             "unit": "C",
                             "battery": "0"},
                            {"id": "0x0B",
                             "val": "0.00 km/h"},
                            {"id": "0x0C",
                             "val": "0.00 km/h"},
                            {"id": "0x19",
                             "val": "21.24 km/h"},
                            {"id": "0x15",
                             "val": "0.00 W/m2"},
                            {"id": "0x17",
                             "val": "0"}]

        Iterate over the elements of the common_list array and process each
        element as required. Returns a dict of observations that have been
        converted in accordance with the unit system being used by the driver.
        Any unit labels/unit label fields are removed. Any elements that cannot
        be converted to a numeric are set to None. The original response is
        unchanged. If the common_list array contains no observations an empty
        dict is returned.

        Parameters:

        response: The common list observation group obtained from the response a
        get_livedata_info API call

        Returns a dict of processed common list observations and data.
        """

        # Whilst the common_list is a JSON array, in order to keep our
        # 'dot-field' mapping simple we need to return a dict of data not a
        # list of dicts. Create an empty dict to hold our results.
        result = dict()
        # iterate over the array elements in the response
        for item in response:
            # we need an id to identify the observation we are to process
            if 'id' in item:
                # call the relevant method to process each observation
                # first obtain the method name, wrap in a try..except in case
                # it is an observation we do not know about
                try:
                    processor_fn = self.processor_fns[item['id']]
                except KeyError:
                    # A KeyError means there is no processor function entry for
                    # this id in the processor function lookup. We have an id
                    # we cannot lookup, log it and continue.
                    if weewx.debug or self.debug.parser or self.log_unknown_fields:
                        log.info("Skipped unknown livedata observation ID '%s'",
                                 item['id'])
                    continue
                except AttributeError:
                    # An AttributeError was raised. This means there is no
                    # processor function for this id. This should never occur,
                    # but if it does log it and continue.
                    if weewx.debug or self.debug.parser:
                        log.info("Processor function not found for livedata "
                                 "observation ID '%s'", item['id'])
                    continue
                # We have a processor function so process the item. Wrap in a
                # try..except in case an error is encountered during processing
                try:
                    # process the observation and obtain the result
                    processed_item = getattr(self, processor_fn)(item)
                except ProcessorError as e:
                    # an object processor encountered an error, depending on
                    # our debug settings log it and set the item to None
                    if weewx.debug >= 2 or self.debug.parser:
                        log.info("Error processing common_list ID '%s': %s",
                                 item['id'], e)
                    result[item['id']] = {'val': None}
                else:
                    # we obtained some processed data for the observation
                    # so add it to our result
                    result[item['id']] = processed_item
        # finally, return the result
        return result

    def process_ch_aisle_array(self, response):
        """Process a ch_aisle JSON array.

        Processes a ch_aisle JSON array resulting from a get_livedata_info
        local HTTP API call. This method:

        - ignores sensors where the 'channel' key cannot be converted to a
          numeric or there is no temperature and humidity data
        - converts observation values to a unit consistent with the WeeWX unit
          system (self.unit_system) used by the driver
        - returns numeric observation values rather than as a string as used in
          the API response
        - returns a value of None if a key exists but it's contents could not
          be converted to a numeric value
        - does not change the original JSON data

        Example JSON array:

        "ch_aisle": [{"channel": "1",
                      "name": "",
                      "battery": "0",
                      "temp": "31.7",
                      "unit": "C",
                      "humidity": "53%"},
                     {"channel": "3",
                      "name": "",
                      "battery": "0",
                      "temp": "27.8",
                      "unit": "C",
                      "humidity": "63%"}]

        Returns a list of dicts where each dict contains the data from a single
        sensor. Each dict includes a 'channel' key and other keys depending on
        the data included in the API response. Available keys are:

        channel:    Sensor channel number, first channel is 1. Mandatory. Integer.
        name:       Sensor name as per WSViewPlus app. Optional. String, may be None.
        temp:       Sensor temperature value. Optional. Float, may be None.
        humidity:   Sensor humidity value. Optional. Integer, may be None.

        The list is sorted in ascending channel order.
        """

        # create an empty list to hold our result
        result = []
        # iterate over the elements/sensors in the JSON array
        for sensor in response:
            # create a dict to hold the data for this sensor
            _sensor = dict()
            # obtain the channel number
            try:
                _sensor['channel'] = int(sensor['channel'])
            except (KeyError, TypeError, ValueError):
                # There is no channel number or we cannot convert the channel
                # value to an int. Either way we cannot continue with this
                # sensor. Move on to the next channel.
                continue
            # obtain the temperature value, wrap in a try..except in case there is
            # a problem
            try:
                # first obtain the temperature as a ValueTuple
                temp_vt = self.parse_obs_value(key='temp',
                                               json_object=sensor,
                                               unit_group='group_temperature')
            except KeyError:
                # the 'temp' key does not exist, we cannot continue with this
                # key
                pass
            except ParseError as e:
                # the 'temp' key exists but there was a problem processing the
                # data, set the 'temp' key/value to None
                _sensor['temp'] = None
            else:
                # we have a numeric value, convert it to the unit system used by the
                # driver and save against the 'val' key
                _sensor['temp'] = weewx.units.convert(temp_vt,
                                                      weewx.units.std_groups[self.unit_system]['group_temperature']).value
            # process the humidity value, wrap in a try..except in case there
            # is a problem
            try:
                # first obtain the humidity as a ValueTuple
                hum_vt = self.parse_obs_value(key='humidity',
                                              json_object=sensor,
                                              unit_group='group_percent')
            except KeyError as e:
                # the 'humidity' key does not exist, we cannot continue with
                # this key
                pass
            except ParseError as e:
                # the 'humidity' key exists but there was a problem processing
                # the data, set the 'humidity' key/value to None
                _sensor['humidity'] = None
            else:
                # we have a numeric value, there is no unit conversion required
                # so coalesce to an int and save against the 'humidity' key
                _sensor['humidity'] = int(hum_vt.value)
            # if we don't have either a 'temp' or 'humidity' key/value pair in
            # our result for this sensor we should ignore the sensor
            if not(set(_sensor.keys()) & {'temp', 'humidity'}):
                continue
            # add the sensor name
            _sensor['name'] = sensor.get('name')
            # add the sensor data to our result list
            result.append(_sensor)
        # return the result
        return result

    def process_ch_temp_array(self, response):
        """Process a ch_temp JSON array.

        Processes a ch_temp JSON array resulting from a get_livedata_info local
        HTTP API call. This method:

        - ignores sensors where the 'channel' key cannot be converted to a
          numeric or there is no temperature data
        - converts observation values to a unit consistent with the WeeWX unit
          system (self.unit_system) used by the driver
        - returns numeric observation values rather than as a string as used in
          the API response
        - returns a value of None if a key exists but it's contents could not
          be converted to a numeric value
        - does not change the original JSON data

        If a value cannot be converted to a float or integer the value None is
        returned.

        Example JSON array:

        "ch_temp": [{"channel": "1",
                     "name": "Flower Soil",
                     "temp": "60.0",
                     "unit": "C",
                     "battery": "3",
                     "voltage": "1.54"},
                     {"channel": "2",
                     "name": "Vegetable Soil",
                     "temp": "23.0",
                     "unit": "C",
                     "battery": "3",
                     "voltage": "1.54"}]

        Note: the 'voltage' field did not originally exist but was added in a
              firmware update

        Returns a list of dicts where each dict contains the data from a single
        sensor. Each dict includes a 'channel' key and other keys depending on
        the data included in the API response. Available keys are:

        channel:    Sensor channel number, first channel is 1. Integer.
        name:       Sensor name as per WSViewPlus app. Optional. String, may be
                    None.
        temp:       Sensor temperature value. Optional. Float, may be None.
        voltage:    Sensor battery voltage value. Optional. Float, may be None.

        The list is sorted in ascending channel order.
        """

        # create an empty list to hold our result
        result = []
        # iterate over the elements/sensors in the JSON array
        for sensor in response:
            # create a dict to hold the data for this sensor
            _sensor = dict()
            # obtain the channel number
            try:
                _sensor['channel'] = int(sensor['channel'])
            except (KeyError, TypeError, ValueError):
                # There is no channel number or we cannot convert the channel
                # value to an int. Either way we cannot continue with this
                # sensor. Move on to the next channel.
                continue
            # obtain the temperature value, wrap in a try.. except in case there is
            # a problem
            try:
                # first obtain the temperature as a ValueTuple
                temp_vt = self.parse_obs_value(key='temp',
                                               json_object=sensor,
                                               unit_group='group_temperature')
            except KeyError as e:
                # the 'temp' key does not exist, we cannot continue with this
                # sensor
                continue
            except ParseError as e:
                # the 'temp' key exists but there was a problem processing the
                # data, set the 'temp' key/value to None
                _sensor['temp'] = None
            else:
                # we have a numeric value, convert it to the unit system used
                # by the driver and save against the 'temp' key
                _sensor['temp'] = weewx.units.convert(temp_vt,
                                                      weewx.units.std_groups[self.unit_system]['group_temperature']).value
            # add the sensor name
            _sensor['name'] = sensor.get('name')
            # process the 'voltage' key/value if it exists, wrap in a
            # try..except in case there is a problem
            try:
                # first obtain the voltage as a ValueTuple
                voltage_vt = self.parse_obs_value('voltage', sensor, 'group_volt')
                # we have a numeric value, save it against the 'voltage' key
                _sensor['voltage'] = voltage_vt.value
            except KeyError as e:
                # no 'voltage' key exists, ignore and continue
                pass
            except ParseError as e:
                # the key 'voltage' exists, but the value could not be converted to
                # a float, so save None to the 'voltage' key/value
                _sensor['voltage'] = None
            # add the sensor data to our result list
            result.append(_sensor)
        # return the result
        return result

    def process_ch_lds_array(self, response):
        """Process a ch_lds JSON array.

        Process a ch_lds JSON array resulting from a get_livedata_info local
        HTTP API call. This method:

        - ignores sensors where the 'channel' key cannot be converted to a
          numeric or there is no temperature data
        - converts observation values to a unit consistent with the WeeWX unit
          system (self.unit_system) used by the driver
        - returns numeric observation values rather than as a string as used in
          the API response
        - returns a value of None if a key exists but it's contents could not
          be converted to a numeric value
        - does not change the original JSON data

        Example JSON array:

        "ch_lds": [{"channel": "1",
                    "name": "",
                    "unit": "mm",
                    "battery": "5",
                    "voltage": "3.22",
                    "air": "3735 mm",
                    "depth": "--.-"},
                   {"channel": "2",
                    "name": "",
                    "unit": "mm",
                    "battery": "4",
                    "voltage": "3.23",
                    "air": "735 mm",
                    "depth": "341 mm"
                    "total_height": "2050",
                    "total_heat": "504" }]


        Returns a list of dicts where each dict contains the data from a single
        sensor. Each dict includes a 'channel' key and other keys depending on
        the data included in the API response. Available keys are:

        channel: Channel number. Mandatory. Integer.
        name:    Sensor name. Optional. String, may be None.
        air:     Sensor 'air' value. Optional. Float, may be None.
        depth:   Sensor 'depth' value. Optional. Float, may be None.
        voltage: Sensor battery voltage in volts. Optional. Float, may be None.

        Note the key 'battery' was dropped as get_sensors_info is considered
        the primary source for battery state data. Key 'unit' is dropped as it
        may not represent the 'air' and 'depth' units after unit conversion.

        The list is sorted in ascending channel order.
        """

        # create an empty list to hold our result
        result = []
        # iterate over the elements/sensors in the JSON array
        for sensor in response:
            # create a dict to hold the data for this sensor
            _sensor = dict()
            # obtain the channel number
            try:
                _sensor['channel'] = int(sensor['channel'])
            except (KeyError, TypeError, ValueError):
                # There is no channel number or we cannot convert the channel
                # value to an int. Either way we cannot continue with this
                # sensor. Move on to the next channel.
                continue
            # obtain the 'air' value, wrap in a try.. except in case there is a
            # problem
            try:
                # first obtain the 'air' key/value as a ValueTuple
                air_vt = self.parse_obs_value(key='air',
                                              json_object=sensor,
                                              unit_group='group_depth')
            except KeyError as e:
                # the 'air' key does not exist, we cannot continue with this
                # sensor
                pass
            except ParseError as e:
                # the 'air' key exists but there was a problem processing the
                # data, we cannot continue with this sensor
                _sensor['air'] = None
            else:
                # we have a numeric value, convert it to the unit system used by
                # the driver and save against the 'air' key
                _sensor['air'] = weewx.units.convert(air_vt,
                                                     weewx.units.std_groups[self.unit_system]['group_depth']).value
            # obtain the 'depth' value if it exists, wrap in a try..except in
            # case there is a problem
            try:
                # first obtain the 'depth' key/value as a ValueTuple
                depth_vt = self.parse_obs_value(key='depth',
                                                json_object=sensor,
                                                unit_group='group_depth')
            except KeyError as e:
                # the 'depth' key does not exist, we cannot continue with this
                # sensor
                pass
            except  ParseError as e:
                # the 'depth' key exists but there was a problem processing the
                # data, set the 'depth' key/value to None
                _sensor['depth'] = None
            else:
                # we have a numeric value, convert it to the unit system used by
                # the driver and save against the 'depth' key
                _sensor['depth'] = weewx.units.convert(depth_vt,
                                                       weewx.units.std_groups[self.unit_system]['group_depth']).value

            try:
                # first obtain the 'total_height' key/value as a ValueTuple
                total_height_vt = self.parse_obs_value(key='total_height',
                                                json_object=sensor,
                                                unit_group='group_depth')
            except KeyError as e:
                # the 'total_height' key does not exist, we cannot continue with this
                # sensor
                pass
            except  ParseError as e:
                # the 'depth' key exists but there was a problem processing the
                # data, set the 'depth' key/value to None
                _sensor['total_height'] = None
            else:
                # we have a numeric value, convert it to the unit system used by
                # the driver and save against the 'depth' key
                _sensor['total_height'] = weewx.units.convert(total_height_vt,
                                                       weewx.units.std_groups[self.unit_system]['group_depth']).value

            # if we don't have either an 'air' or 'depth' key/value pair in our
            # results for this sensor we should ignore the sensor
            if not(set(_sensor.keys()) & {'air', 'depth'}):
                continue
            # add the total_heat
            try:
                _sensor['total_heat'] = int(sensor['total_heat'])
                # process the 'heat' key/value if it exists, wrap in a try.. except
                # in case there is a problem
            except (KeyError, TypeError, ValueError):
                # There is no heat number or we cannot convert the heat
                # value to an int. Either way we cannot continue with this
                # sensor. 
                pass
            # add the sensor name
            _sensor['name'] = sensor.get('name')
            # process the 'voltage' key/value if it exists, wrap in a try.. except
            # in case there is a problem
            try:
                # first obtain the voltage as a ValueTuple
                voltage_vt = self.parse_obs_value(key='voltage',
                                                  json_object=sensor,
                                                  unit_group='group_volt')
                # we have a numeric value, save it against the 'voltage' key
                _sensor['voltage'] = voltage_vt.value
            except KeyError:
                # no 'voltage' key exists, ignore and continue
                pass
            except ParseError as e:
                # the key 'voltage' exists, but the value could not be converted to
                # a float, so save None to the 'voltage' key/value
                _sensor['voltage'] = None
            # add the sensor data to our result list
            result.append(_sensor)
        # return the result
        return result

    def process_ch_soil_array(self, response):
        """Process a ch_soil JSON array.

        Processes a ch_soil JSON array resulting from a get_livedata_info local
        HTTP API call. This method:

        - ignores sensors where the 'channel' key cannot be converted to a
          numeric or there is no temperature data
        - converts observation values to a unit consistent with the WeeWX unit
          system (self.unit_system) used by the driver
        - returns numeric observation values rather than as a string as used in
          the API response
        - returns a value of None if a key exists but it's contents could not
          be converted to a numeric value
        - does not change the original JSON data

        Example JSON array:

        "ch_soil": [{"channel": "1",
                     "name": "Trough",
                     "battery": "5",
                     "voltage": "1.60",
                     "humidity": "23%"},
                     {"channel": "2",
                     "name": "Garden",
                     "battery": "5",
                     "voltage": "1.60",
                     "humidity": "42%"}]

        Note: the key 'voltage' did not originally exist but was added in a
              firmware update

        Returns a list of dicts where each dict contains the data from a single
        sensor. Each dict includes a 'channel' key and other keys depending on
        the data included in the API response. Available keys are:

        channel:  channel number. Mandatory. Integer.
        name:     sensor name. Optional. String, may be None.
        humidity: sensor 'humidity' value in %. Optional. Integer, may be None.
        voltage:  battery voltage in volts. Optional. Float, may be None.

        Note the key 'battery' was dropped as get_sensors_info is considered the
        primary source for battery state data.

        The list is sorted in ascending channel order.
        """

        # create an empty list to hold our result
        result = []
        # iterate over the elements/sensors in the JSON array
        for sensor in response:
            # create a dict to hold the data for this sensor
            _sensor = dict()
            # obtain the channel number
            try:
                _sensor['channel'] = int(sensor['channel'])
            except (KeyError, TypeError, ValueError) as e:
                # There is no channel number or we cannot convert the channel
                # value to an int. Either way we cannot continue with this
                # sensor. Move on to the next channel.
                continue
            # process the humidity value, wrap in a try..except in case there
            # is a problem
            try:
                # first obtain the humidity as a ValueTuple
                hum_vt = self.parse_obs_value(key='humidity',
                                              json_object=sensor,
                                              unit_group='group_percent')
            except KeyError as e:
                # the 'humidity' key does not exist, we cannot continue with
                # this sensor
                continue
            except ParseError as e:
                # the 'humidity' key exists but there was a problem processing
                # the data, set the 'humidity' key/value to None
                _sensor['humidity'] = None
            else:
                # we have a numeric value, there is no unit conversion required
                # so coalesce to an int and save against the 'humidity' key
                _sensor['humidity'] = int(hum_vt.value)
            # add the sensor name
            _sensor['name'] = sensor.get('name')
            # process the 'voltage' key/value if it exists, wrap in a try.. except
            # in case there is a problem
            try:
                # first obtain the voltage as a ValueTuple
                voltage_vt = self.parse_obs_value('voltage', sensor, 'group_volt')
                # we have a numeric value, save it against the 'voltage' key
                _sensor['voltage'] = voltage_vt.value
            except KeyError as e:
                # no 'voltage' key exists, ignore and continue
                pass
            except ParseError as e:
                # the key 'voltage' exists, but the value could not be converted to
                # a float, so save None to the 'voltage' key/value
                _sensor['voltage'] = None
            # add the sensor data to our result list
            result.append(_sensor)
        # return the result
        return result

    @staticmethod
    def process_ch_pm25_array(response):
        """Process a ch_pm25 JSON array.

        Processes a ch_pm25 JSON array resulting from a get_livedata_info local
        HTTP API call. This method:

        - ignores sensors where the 'channel' key cannot be converted to a
          numeric or there is no temperature data
        - converts observation values to a unit consistent with the WeeWX unit
          system (self.unit_system) used by the driver
        - returns numeric observation values rather than as a string as used in
          the API response
        - returns a value of None if a key exists but it's contents could not
          be converted to a numeric value
        - does not change the original JSON data

        Example JSON array:

        "ch_pm25": [{"channel": "1",
                     "PM25": "7.0",
                     "PM25_24H": "7.3",
                     "PM25_RealAQI": "29",
                     "PM25_24HAQI": "28",
                     "battery": "6"}]

        Returns a list of dicts ordered in ascending channel order. Each dict
        may contain the following fields:

        channel:      channel number, integer.
        PM25:         sensor PM2.5 value, float. May be None.
        PM25_24H:     sensor PM2.5 24h value, float. May be None.
        PM25_RealAQI: realtime PM2.5 AQI value, int. May be None.
        PM25_24HAQI:  24-hour average PM2.5 AQI value, int. May be None.

        Note that 'battery' was dropped as get_sensors_info is considered the
        primary source for battery state data.
        """

        # create an empty list to hold our result
        result = []
        # iterate over the elements in the JSON array
        for sensor in response:
            # create a dict to hold the data for this sensor
            _sensor = dict()
            # obtain the channel number
            try:
                _sensor['channel'] = int(sensor['channel'])
            except (KeyError, TypeError, ValueError):
                # There is no channel number or we cannot convert the channel
                # value to an int. Either way we cannot continue with this
                # sensor. Move on to the next channel.
                continue
            # process the PM2.5 value
            try:
                _sensor['PM25'] = float(sensor['PM25'])
            except KeyError:
                # there is no key 'PM25', do nothing
                pass
            except (TypeError, ValueError):
                # the 'PM25' value cannot be converted to a float, save as None
                # instead
                _sensor['PM25'] = None

            # process the PM2.5 24h value
            try:
                _sensor['PM25_24H'] = float(sensor['PM25_24H'])
            except KeyError:
                # there is no key 'PM25_24H', do nothing
                pass
            except (TypeError, ValueError):
                # the 'PM25_24H' value cannot be converted to a float, save as None
                # instead
                _sensor['PM25_24H'] = None
            # process the PM2.5 realtime AQI value
            try:
                _sensor['PM25_RealAQI'] = int(sensor['PM25_RealAQI'])
            except KeyError:
                # there is no key 'PM25_RealAQI', do nothing
                pass
            except (TypeError, ValueError):
                # the 'PM25_RealAQI' value cannot be converted to an int, save
                # as None instead
                _sensor['PM25_RealAQI'] = None
            # process the PM2.5 24 hour average AQI value
            try:
                _sensor['PM25_24HAQI'] = int(sensor['PM25_24HAQI'])
            except KeyError:
                # there is no key 'PM25_24HAQI', do nothing
                pass
            except (TypeError, ValueError):
                # the 'PM25_24HAQI' value cannot be converted to a float, save
                # as None instead
                _sensor['PM25_24HAQI'] = None
            # if we don't have either a 'PM25', 'PM25_RealAQI' or 'PM25_24HAQI'
            # key/value pair in our results for this sensor we should ignore
            # the sensor
            if not(set(_sensor.keys()) & {'PM25', 'PM25_RealAQI', 'PM25_24HAQI'}):
                continue
            # add the item to our result list
            result.append(_sensor)
        # return the result
        return result

    # processing of piezoRain and rain JSON arrays are identical to the
    # processing of a common_list array.
    process_piezoRain_array = process_common_list_array
    process_rain_array = process_common_list_array

    def process_wh25_array(self, response):
        """Process a wh25 JSON array.

        Processes a 'wh25' JSON array resulting from a 'get_livedata_info'
        local HTTP API call. The 'wh25' array does not represent a
        multi-channel response as with most other local HTTP API responses,
        rather the array contains a single element containing key/value pairs.
        In order to maintain a simplified 'dot-field' mapping system this
        single element is parsed and the parsed data returned as a dict rather
        than a list of dicts.

        This method:

        - ignores sensors where the 'channel' key cannot be converted to a
          numeric or there is no temperature data
        - converts observation values to a unit consistent with the WeeWX unit
          system (self.unit_system) used by the driver
        - returns numeric observation values rather than as a string as used in
          the API response
        - returns a value of None if a key exists but it's contents could not
          be converted to a numeric value
        - does not change the original JSON data

        Returns a dict.

        Example local HTTP API response 'wh25' JSON array:

        "wh25": [{"intemp": "30.6",
                  "unit": "C",
                  "inhumi": "47%",
                  "abs": "1013.6 hPa",
                  "rel": "1019.1 hPa",
                  "CO2": "495",
                  "CO2_24H": "538"}]
        """

        # obtain the first (and only) array element, wrap in a try..except in
        # case there is a problem
        try:
            item = response[0]
        except (KeyError, TypeError) as e:
            # we have something other than a JSON array, raise a ParseError
            # with an appropriate error message
            raise ParseError("Cannot parse 'wh25' array: %s" % e)
        # we have the raw response, create a dict to hold the parsed data for
        # this item
        _item = dict()
        # obtain the inside temperature value, wrap in a try..except in
        # case there is a problem
        try:
            # first obtain the temperature as a ValueTuple
            temp_vt = self.parse_obs_value(key='intemp',
                                           json_object=item,
                                           unit_group='group_temperature')
        except KeyError:
            # there is no key 'intemp', do nothing
            pass
        except ParseError:
            # the 'intemp' value cannot be converted to a float, save as
            # None instead
            _item['intemp'] = None
        else:
            # we have a numeric value, convert it to the unit system used
            # by the driver and save against the 'intemp' key
            _item['intemp'] = weewx.units.convert(temp_vt,
                                                  weewx.units.std_groups[self.unit_system]['group_temperature']).value
        # process the inside humidity value, wrap in a try..except in case
        # there is a problem
        try:
            # first obtain the humidity as a ValueTuple
            hum_vt = self.parse_obs_value(key='inhumi',
                                          json_object=item,
                                          unit_group='group_percent')
        except KeyError:
            # there is no key 'inhumi', do nothing
            pass
        except ParseError:
            # the 'inhumi' value cannot be converted to a float, save as
            # None instead
            _item['inhumi'] = None
        else:
            # we have a numeric value, there is no unit conversion required
            # so coalesce to an int and save against the 'humidity' key
            _item['inhumi'] = int(hum_vt.value)
        # process the absolute pressure value, wrap in a try..except in
        # case there is a problem
        try:
            # first obtain the pressure as a ValueTuple
            press_vt = self.parse_obs_value(key='abs',
                                            json_object=item,
                                            unit_group='group_pressure')
        except KeyError:
            # there is no key 'abs', do nothing
            pass
        except ParseError:
            # the 'abs' value cannot be converted to a float, save as
            # None instead
            _item['abs'] = None
        else:
            # we have a numeric value, convert it to the unit system used by the
            # driver and save against the 'abs' key
            _item['abs'] = weewx.units.convert(press_vt,
                                               weewx.units.std_groups[self.unit_system]['group_pressure']).value
        # process the relative pressure value, wrap in a try..except in
        # case there is a problem
        try:
            # first obtain the pressure as a ValueTuple
            press_vt = self.parse_obs_value(key='rel',
                                            json_object=item,
                                            unit_group='group_pressure')
        except KeyError:
            # there is no key 'rel', do nothing
            pass
        except ParseError:
            # the 'rel' value cannot be converted to a float, save as
            # None instead
            _item['rel'] = None
        else:
            # we have a numeric value, convert it to the unit system used by the
            # driver and save against the 'abs' key
            _item['rel'] = weewx.units.convert(press_vt,
                                               weewx.units.std_groups[self.unit_system]['group_pressure']).value
        # process the CO2 value if it exists, wrap in a try..except in case
        # there is a problem
        try:
            _item['CO2'] = int(item['CO2'])
        except KeyError:
            # there is no key 'CO2', do nothing
            pass
        except (TypeError, ValueError):
            # the 'CO2' value cannot be converted to an int, save as None
            # instead
            _item['CO2'] = None
        # process the CO2_24H value if it exists, wrap in a try..except in
        # case there is a problem
        try:
            _item['CO2_24H'] = int(item['CO2_24H'])
        except KeyError:
            # there is no key 'CO2_24H', do nothing
            pass
        except (TypeError, ValueError):
            # the 'CO2_24H' value cannot be converted to an int, save as None
            # instead
            _item['CO2_24H'] = None
        # return the parsed data
        return _item

    def process_lightning_array(self, response):
        """Process a lightning sensors JSON array.

        Processes a 'lightning' JSON array resulting from a
        'get_livedata_info' local HTTP API call. The 'lightning' array
        consists of a single element containing key/value pairs for a single
        sensor. In order to maintain a consistent 'dot-field' mapping system
        this single element is parsed and the parsed data returned as a dict
        rather than a list of dicts.

        This method:

        - ignores sensors where the 'channel' key cannot be converted to a
          numeric or there is no temperature data
        - converts observation values to a unit consistent with the WeeWX unit
          system (self.unit_system) used by the driver
        - returns numeric observation values rather than as a string as used in
          the API response
        - returns a value of None if a key exists but it's contents could not
          be converted to a numeric value
        - does not change the original JSON data

        Example JSON array:

        "lightning": [{"distance": "14 km",
                       "date": "2024-03-21T20:45:37",
                       "timestamp": "03/21/2024 20:45:37",
                       "count": "0",
                       "battery": "4"}]

        Returns a dict keyed as follows (some keys may not be present or may
        be None):

        distance:  distance to the last strike in km, float.
        date:      date-time string of the last recorded strike, string.
        timestamp: epoch timestamp of the last recorded strike, integer.
        count:     total number of strikes recorded today, integer.

        Note the 'battery' key/value pair is ignored as 'get_sensors_info' is
        considered the primary source for sensor battery state data.
        """

        # obtain the first (and only) array element, wrap in a try..except in
        # case there is a problem
        try:
            item = response[0]
        except (KeyError, TypeError) as e:
            # we have something other than a JSON array, raise a ParseError
            # with an appropriate error message
            raise ParseError("Cannot parse 'lightning' array: %s" % e)
        # we have the raw response, create a dict to hold the parsed data for
        # this item
        _item = dict()
        # We have a 'count' field, now convert to an integer. Wrap in a
        # try..except in case there is a problem.
        try:
            _item['count'] = int(item['count'])
        except KeyError:
            # the item has no 'count' key, so continue
            pass
        except (TypeError, ValueError):
            # the 'count' value could not be converted to an integer,
            # so save None to the 'count' field
            _item['count'] = None
        # obtain the 'distance' value if it exists, wrap in a try..except in
        # case there is a problem
        try:
            # first obtain the 'distance' key/value as a ValueTuple
            dist_vt = self.parse_obs_value(key='distance',
                                           json_object=item,
                                           unit_group='group_distance')
        except KeyError as e:
            # the 'distance' key does not exist, we cannot continue with this
            # sensor key
            pass
        except UnitError as e:
            # The 'distance' key exists, but there was a problem obtaining the
            # unit. Log it and set the 'distance' key/value to None.
            log.error("process_lightning_array: Error processing distance "
                           "unit: %s", e)
            _item['distance'] = None
        except  ParseError as e:
            # The 'distance' key exists but there was a problem processing the
            # data. Log it and set the 'distance' key/value to None
            log.error("process_lightning_array: Error processing distance: %s", e)
            _item['distance'] = None
        else:
            # we have a numeric value, convert it to the unit system used by
            # the driver and save against the 'distance' key
            _item['distance'] = weewx.units.convert(dist_vt,
                                                   weewx.units.std_groups[self.unit_system]['group_distance']).value
        # pass through the 'date' key/value as is if it exists
        try:
            _item['date'] = item['date']
        except KeyError:
            # we have no 'date' key, do nothing and continue processing
            pass
        # obtain and parse the 'timestamp' key/value
        try:
            _timestamp_dt = datetime.datetime.strptime(item['timestamp'],
                                                       '%m/%d/%Y %H:%M:%S')
        except KeyError:
            # we have no 'timestamp' key, do nothing and continue processing
            pass
        except (TypeError, ValueError):
            # the 'timestamp' key exists, but we cannot convert it to a
            # datetime object, save as None and continue
            _item['timestamp'] = None
        else:
            # we have a datetime object, convert to and save as an epoch timestamp
            timestamp_ts = int(time.mktime(_timestamp_dt.timetuple()))
            _item['timestamp'] = timestamp_ts
        # return the parsed data
        return _item

    def process_co2_array(self, response):
        """Process a CO2 JSON array.

        Processes a co2 JSON array resulting from a get_livedata_info local
        HTTP API call. This method:

        - ignores sensors where the 'channel' key cannot be converted to a
          numeric or there is no temperature data
        - converts observation values to a unit consistent with the WeeWX unit
          system (self.unit_system) used by the driver
        - returns numeric observation values rather than as a string as used in
          the API response
        - returns a value of None if a key exists but it's contents could not
          be converted to a numeric value
        - does not change the original JSON data

        Example JSON array:

        "co2": [{ //Co2 sensors
            "temp": "81.0",
            "unit": "F",
            "humidity": "60%",
            "PM25": "15.0",
            "PM25_RealAQI": "57",
            "PM25_24HAQI": "57",
            "PM10": "15.1",
            "PM10_RealAQI": "14",
            "PM10_24HAQI": "14",
            "CO2": "314",
            "CO2_24H": "314",
            "battery": "6"
        }]
        #WH46 WS3910
        "co2": [{ //Co2 sensors
            "temp": "29.3", 
            "unit": "C", 
            "humidity": "40%",  
            "PM25": "2.6", 
            "PM25_RealAQI": "11", 
            "PM25_24HAQI": "17", 
            "PM10": "2.8", 
            "PM10_RealAQI": "3", 
            "PM10_24HAQI": "4", 
            "PM1": "2.3", 
            "PM1_RealAQI": "10", 
            "PM1_24HAQI": "15", 
            "PM4": "2.7", 
            "PM4_RealAQI": "11",  
            "PM4_24HAQI": "17", 
            "CO2": "439", 
            "CO2_24H": "486", 
            "battery": "6"
        }], 
        #WH46 GW3000
        "co2":[{ 
            "temp": "28.4", 
            "unit": "C", 
            "humidity": "46%", 
            "PM25": "4.1", 
            "PM25_RealAQI": "17", 
            "PM25_24HAQI": "17", 
            "PM25_24H": "4.0", 
            "PM10": "4.3", 
            "PM10_RealAQI": "4", 
            "PM10_24HAQI": "4", 
            "PM10_24H": "4.1", 
            "PM1": "3.7", 
            "PM1_RealAQI": "15", 
            "PM1_24HAQI": "15", 
            "PM1_24H": "3.7", 
            "PM4": "4.3", 
            "PM4_RealAQI": "18", 
            "PM4_24HAQI": "17", 
            "PM4_24H": "4.1", 
            "CO2": "443", 
            "CO2_24H": "487", 
            "battery": "6" 
        }],


        Returns a dict keyed as follows (some keys may not be present or may
        be None):

        distance:  distance to the last strike in km, float.
        date:      date-time string of the last recorded strike, string.
        timestamp: epoch timestamp of the last recorded strike, integer.
        count:     total number of strikes recorded today, integer.

        Note the 'battery' key/value pair is ignored as 'get_sensors_info' is
        considered the primary source for sensor battery state data.
        """

        # create an empty list to hold our result
        result = []

        """
        # iterate over the elements in the JSON array
        for item in response:
            # make a copy of the current item as we will be modifying it
            _item = dict(item)
            # temperature
            if 'temp' in _item:
                # We have a 'temp' field, now obtain the WeeWX unit applicable
                # to the Ecowitt unit string in the 'unit' field. Be prepared
                # to catch the exception if we have an invalid or unknown unit
                # string.
                try:
                    src_unit = self.get_weewx_unit(item['unit'],
                                                   'group_temperature')
                except UnitError as e:
                    # an unknown Ecowitt unit string was encountered, log it,
                    # set the 'temp' field to None and continue
                    log.error("process_co2_array: Error processing temperature "
                              "unit: %s", e)
                    _item['temp'] = None
                else:
                    # Construct a ValueTuple from the temperature and unit data, we
                    # need this to do any necessary unit conversion. Wrap in a
                    # try..except in case there is a problem.
                    try:
                        temp_vt = weewx.units.ValueTuple(float(item['temp']),
                                                         src_unit,
                                                         'group_temperature')
                    except (TypeError, ValueError):
                        # the 'temp' field could not be converted to a float, so
                        # save None to the 'temp' field
                        _item['temp'] = None
                    else:
                        # convert to the appropriate unit and save in the 'temp' field
                        _item['temp'] = weewx.units.convert(temp_vt,
                                                            weewx.units.std_groups[self.unit_system]['group_temperature']).value
            # humidity
            if 'humidity' in item:
                # we have a 'humidity' field, extract the humidity value from
                # the humidity field and save it as a float. Wrap in a
                # try..except in case there is a problem.
                try:
                    _item['humidity'] = float(_item['humidity'].split('%')[0])
                except KeyError:
                    # the humidity field does not exist, so just leave things as
                    # they are
                    pass
                except (TypeError, ValueError):
                    # the humidity field cannot be converted to a float so save
                    # as None
                    _item['humidity'] = None
            # PM2.5, PM10 and CO2
            # iterate over the key, value pairs
            for k, v in item.items():
                # if we have a PM2.5, PM10 or CO2 field convert the value to a
                # float and save in the field of the same name, wrap in a
                # try..except in case we encounter a problem
                if 'PM' in k or 'CO2' in k:
                    try:
                        _item[k] = float(v)
                    except (TypeError, ValueError):
                        # the field cannot be converted to a float so save as
                        # None
                        _item[k] = None
            # add the item to our result list
            result.append(_item)
        # return the result
        return result
        """

        try:
            item = response[0]
        except (KeyError, TypeError) as e:
            # we have something other than a JSON array, raise a ParseError
            # with an appropriate error message
            raise ParseError("Cannot parse 'co2' array: %s" % e)
        # we have the raw response, create a dict to hold the parsed data for
        # this item
        _item = dict()

        try:
            # first obtain the temperature as a ValueTuple
            temp_vt = self.parse_obs_value(key='temp',
                                           json_object=item,
                                           unit_group='group_temperature')
        except KeyError:
            # there is no key 'temp', do nothing
            pass
        except ParseError:
            # the 'temp' value cannot be converted to a float, save as
            # None instead
            _item['temp'] = None
        else:
            # we have a numeric value, convert it to the unit system used
            # by the driver and save against the 'temp' key
            _item['temp'] = weewx.units.convert(temp_vt,
                                                  weewx.units.std_groups[self.unit_system]['group_temperature']).value
        # process the inside humidity value, wrap in a try..except in case
        # there is a problem
        try:
            # first obtain the humidity as a ValueTuple
            hum_vt = self.parse_obs_value(key='humidity',
                                          json_object=item,
                                          unit_group='group_percent')
        except KeyError:
            # there is no key 'humidity', do nothing
            pass
        except ParseError:
            # the 'humidity' value cannot be converted to a float, save as
            # None instead
            _item['humidity'] = None
        else:
            # we have a numeric value, there is no unit conversion required
            # so coalesce to an int and save against the 'humidity' key
            _item['humidity'] = int(hum_vt.value)
        # process the absolute pressure value, wrap in a try..except in
        # case there is a problem

        try:
            _item['CO2'] = int(item['CO2'])
        except KeyError:
            # there is no key 'CO2', do nothing
            pass
        except (TypeError, ValueError):
            # the 'CO2' value cannot be converted to an int, save as None
            # instead
            _item['CO2'] = None
        # process the CO2_24H value if it exists, wrap in a try..except in
        # case there is a problem
        try:
            _item['CO2_24H'] = int(item['CO2_24H'])
        except KeyError:
            # there is no key 'CO2_24H', do nothing
            pass
        except (TypeError, ValueError):
            # the 'CO2_24H' value cannot be converted to an int, save as None
            # instead
            _item['CO2_24H'] = None

        # process the PM2.5 value
        try:
            _item['PM25'] = float(item['PM25'])
        except KeyError:
            # there is no key 'PM25', do nothing
            pass
        except (TypeError, ValueError):
            # the 'PM25' value cannot be converted to a float, save as None
            # instead
            _item['PM25'] = None

        # process the PM2.5 24h value
        try:
            _item['PM25_24H'] = float(item['PM25_24H'])
        except KeyError:
            # there is no key 'PM25_24H', do nothing
            pass
        except (TypeError, ValueError):
            # the 'PM25_24H' value cannot be converted to a float, save as None
            # instead
            _item['PM25_24H'] = None
        # process the PM2.5 realtime AQI value
        try:
            _item['PM25_RealAQI'] = int(item['PM25_RealAQI'])
        except KeyError:
            # there is no key 'PM25_RealAQI', do nothing
            pass
        except (TypeError, ValueError):
            # the 'PM25_RealAQI' value cannot be converted to an int, save
            # as None instead
            _item['PM25_RealAQI'] = None
        # process the PM2.5 24 hour average AQI value
        try:
            _item['PM25_24HAQI'] = int(item['PM25_24HAQI'])
        except KeyError:
            # there is no key 'PM25_24HAQI', do nothing
            pass
        except (TypeError, ValueError):
            # the 'PM25_24HAQI' value cannot be converted to a float, save
            # as None instead
            _item['PM25_24HAQI'] = None

        # if we don't have either a 'PM25', 'PM25_RealAQI' or 'PM25_24HAQI'
        # key/value pair in our results for this sensor we should ignore
        # the sensor
        
        #if not(set(_sensor.keys()) & {'PM25', 'PM25_RealAQI', 'PM25_24HAQI'}):
        #    continue
        # add the item to our result list
        #result.append(_sensor)

        # process the PM10 value
        try:
            _item['PM10'] = float(item['PM10'])
        except KeyError:
            # there is no key 'PM10', do nothing
            pass
        except (TypeError, ValueError):
            # the 'PM10' value cannot be converted to a float, save as None
            # instead
            _item['PM10'] = None

        # process the PM10 24h value
        try:
            _item['PM10_24H'] = float(item['PM10_24H'])
        except KeyError:
            # there is no key 'PM10_24H', do nothing
            pass
        except (TypeError, ValueError):
            # the 'PM10_24H' value cannot be converted to a float, save as None
            # instead
            _item['PM10_24H'] = None
        # process the PM10 realtime AQI value
        try:
            _item['PM10_RealAQI'] = int(item['PM10_RealAQI'])
        except KeyError:
            # there is no key 'PM10_RealAQI', do nothing
            pass
        except (TypeError, ValueError):
            # the 'PM10_RealAQI' value cannot be converted to an int, save
            # as None instead
            _item['PM10_RealAQI'] = None
        # process the PM10 24 hour average AQI value
        try:
            _item['PM10_24HAQI'] = int(item['PM10_24HAQI'])
        except KeyError:
            # there is no key 'PM10_24HAQI', do nothing
            pass
        except (TypeError, ValueError):
            # the 'PM10_24HAQI' value cannot be converted to a float, save
            # as None instead
            _item['PM10_24HAQI'] = None

        # process the PM1 value
        try:
            _item['PM1'] = float(item['PM1'])
        except KeyError:
            # there is no key 'PM1', do nothing
            pass
        except (TypeError, ValueError):
            # the 'PM1' value cannot be converted to a float, save as None
            # instead
            _item['PM1'] = None

        # process the PM1 24h value
        try:
            _item['PM1_24H'] = float(item['PM1_24H'])
        except KeyError:
            # there is no key 'PM1_24H', do nothing
            pass
        except (TypeError, ValueError):
            # the 'PM1_24H' value cannot be converted to a float, save as None
            # instead
            _item['PM1_24H'] = None
        # process the PM1 realtime AQI value
        try:
            _item['PM1_RealAQI'] = int(item['PM1_RealAQI'])
        except KeyError:
            # there is no key 'PM1_RealAQI', do nothing
            pass
        except (TypeError, ValueError):
            # the 'PM1_RealAQI' value cannot be converted to an int, save
            # as None instead
            _item['PM1_RealAQI'] = None
        # process the PM1 24 hour average AQI value
        try:
            _item['PM1_24HAQI'] = int(item['PM1_24HAQI'])
        except KeyError:
            # there is no key 'PM1_24HAQI', do nothing
            pass
        except (TypeError, ValueError):
            # the 'PM1_24HAQI' value cannot be converted to a float, save
            # as None instead
            _item['PM1_24HAQI'] = None

        # process the PM4 value
        try:
            _item['PM4'] = float(item['PM4'])
        except KeyError:
            # there is no key 'PM4', do nothing
            pass
        except (TypeError, ValueError):
            # the 'PM4' value cannot be converted to a float, save as None
            # instead
            _item['PM4'] = None

        # process the PM4 24h value
        try:
            _item['PM4_24H'] = float(item['PM4_24H'])
        except KeyError:
            # there is no key 'PM4_24H', do nothing
            pass
        except (TypeError, ValueError):
            # the 'PM4_24H' value cannot be converted to a float, save as None
            # instead
            _item['PM4_24H'] = None
        # process the PM4 realtime AQI value
        try:
            _item['PM4_RealAQI'] = int(item['PM4_RealAQI'])
        except KeyError:
            # there is no key 'PM4_RealAQI', do nothing
            pass
        except (TypeError, ValueError):
            # the 'PM4_RealAQI' value cannot be converted to an int, save
            # as None instead
            _item['PM4_RealAQI'] = None
        # process the PM4 24 hour average AQI value
        try:
            _item['PM4_24HAQI'] = int(item['PM4_24HAQI'])
        except KeyError:
            # there is no key 'PM4_24HAQI', do nothing
            pass
        except (TypeError, ValueError):
            # the 'PM4_24HAQI' value cannot be converted to a float, save
            # as None instead
            _item['PM4_24HAQI'] = None

        # return the parsed data
        return _item


    #@staticmethod
    def process_ch_leaf_array(self, response):
        """Process a multichannel leaf wetness sensors JSON array.

        Processes a ch_leaf JSON array resulting from a get_livedata_info local
        HTTP API call. This method:

        - converts observation value fields from a string (with or without a
          trailing unit) to a float or integer
        - does not change the original JSON data

        If a value cannot be converted to a float or integer the value None is
        used.

        Returns a list of dicts.

        Example JSON array:

        """

        # create an empty list to hold our result
        result = []
        # iterate over the elements in the JSON array
        for item in response:
            # make a copy of the current item as we will be modifying it
            _item = dict(item)
            if 'humidity' in item:
                # we have a 'humidity' field, extract the humidity value from
                # the humidity field and save it as a float. Wrap in a
                # try..except in case there is a problem.
                try:
                    _item['humidity'] = float(_item['humidity'].split('%')[0])
                except KeyError:
                    # the humidity field does not exist, so just leave things as
                    # they are
                    pass
                except (TypeError, ValueError):
                    # the humidity field cannot be converted to a float so save as
                    # None
                    _item['humidity'] = None
    
            # add the sensor name
            _item['name'] = item.get('name')

            # process the 'voltage' key/value if it exists, wrap in a try.. except
            # in case there is a problem
            if 'voltage' in item:
                try:
                    # first obtain the voltage as a ValueTuple
                    voltage_vt = self.parse_obs_value('voltage', item, 'group_volt')
                    # we have a numeric value, save it against the 'voltage' key
                    _item['voltage'] = voltage_vt.value
                except KeyError:
                    # no 'voltage' key exists, ignore and continue
                    pass
                except UnitError as e:
                    # the key 'voltage' exists, but the value could not be converted to
                    # a float, so save None to the 'voltage' key/value
                    _item['voltage'] = None

            # add the item to our result list
            result.append(_item)



        # return the result
        return result


    def process_ch_leak_array(self, response):
        """Process a multichannel leak sensors JSON array.

        Processes a ch_leak JSON array resulting from a get_livedata_info local
        HTTP API call. This method:

        - converts observation values to a unit consistent with the WeeWX unit
          system used by the driver
        - converts observation value fields from a string (with or without a
          trailing unit) to a float or integer
        - does not change the original JSON data

        If a value cannot be converted to a float or integer the value None is
        used.

        Returns a list of dicts.

        Example JSON array:
        "ch_leak": [{"channel": "1",
                     "name": "",
                     "battery": "4",
                     "status": "Normal"}]
        """

        result = []
        if len(response) > 0:
            for item in response:
                _item = dict(item)
                if 'status' in item:
                    if str(item['status']).lower() == 'normal':
                        _item['status'] = 0
                    elif str(item['status']).lower() == 'leaking':
                        _item['status'] = 1
                    else:
                        _item['status'] = None
                # Ecowitt has added 'battery' and (battery) 'voltage' fields to some
                # objects. In case they have added them to more objects go ahead and
                # look for them and if they exist process and include them in the
                # response.
                try:
                    _item['battery'] = int(item['battery'])
                except KeyError:
                    # no 'battery' field exists, ignore and continue
                    pass
                except (TypeError, ValueError):
                    # the 'battery' field could not be converted to an int, so save
                    # None to the 'battery' field
                    _item['battery'] = None
                # process the 'voltage' key/value if it exists, wrap in a try.. except
                # in case there is a problem
                try:
                    # first obtain the voltage as a ValueTuple
                    voltage_vt = self.parse_obs_value('voltage', item, 'group_volt')
                    # we have a numeric value, save it against the 'voltage' key
                    _item['voltage'] = voltage_vt.value
                except KeyError:
                    # no 'voltage' key exists, ignore and continue
                    pass
                except UnitError as e:
                    # the key 'voltage' exists, but the value could not be converted to
                    # a float, so save None to the 'voltage' key/value
                    _item['voltage'] = None
                result.append(_item)
        return result

    @staticmethod
    def process_debug_array(response):
        """Process a debug JSON array.

        Processes a debug JSON array resulting from a get_livedata_info local
        HTTP API call. This method:

        - returns numeric observation values rather than as a string as used in
          the API response
        - returns a value of None if a key exists but it's contents could not
          be converted to a numeric value
        - does not change the original JSON data

        Returns a dict.

        Example JSON array:
        'debug': [{"heap": "114512",
                   "runtime": "1009602",
                   "usr_interval": "30",
                   "is_cnip": false}]
        """

        # obtain the first (and only) array element, wrap in a try..except in
        # case there is a problem
        try:
            item = response[0]
        except (KeyError, TypeError) as e:
            # we have something other than a JSON array, raise a ParseError
            # with an appropriate error message
            raise ParseError("Cannot parse 'debug' array: %s" % e)
        # we have the raw response, create a dict to hold the parsed data for
        # this item
        _item = dict()
        # parse the 'heap' key/value pair, wrap in a try..except in case there
        # is a problem
        try:
            _item['heap'] = int(item['heap'])
        except KeyError:
            # the item has no 'heap' key, so continue
            pass
        except (TypeError, ValueError):
            # the 'heap' value could not be converted to an integer,
            # so save None to the 'heap' field
            _item['heap'] = None
        # parse the 'runtime' key/value pair, wrap in a try..except in case
        # there is a problem
        try:
            _item['runtime'] = int(item['runtime'])
        except KeyError:
            # the item has no 'runtime' key, so continue
            pass
        except (TypeError, ValueError):
            # the 'runtime' value could not be converted to an integer,
            # so save None to the 'runtime' field
            _item['runtime'] = None
        # parse the 'usr_interval' key/value pair, wrap in a try..except in
        # case there is a problem
        try:
            _item['usr_interval'] = int(item['usr_interval'])
        except KeyError:
            # the item has no 'usr_interval' key, so continue
            pass
        except (TypeError, ValueError):
            # the 'usr_interval' value could not be converted to an integer,
            # so save None to the 'usr_interval' field
            _item['usr_interval'] = None
        # parse the 'is_cnip' key/value pair, wrap in a try..except in case
        # there is a problem
        try:
            _item['is_cnip'] = weeutil.weeutil.to_bool(item['is_cnip'])
        except KeyError:
            # the item has no 'is_cnip' key, so continue
            pass
        except ValueError:
            # the 'is_cnip' value could not be coalesced to a boolean, so save
            # as None
            _item['is_cnip'] = None
        # return the parsed data
        return _item

    def process_sensor_array(self, sensor, connected_only):
        """Process sensor data obtained via the 'get_sensors_info' API command.

        Process sensor metadata


        Returns a 3-way tuple consisting of:
            sensor model:   Lower case string containing sensor model, eg wn31.
            channel number: String in the format 'chx' where x is the channel
                            number. None if sensor is non-channelised, eg WH45.
            sensor data:    Dict containing sensor metadata keyed as follows:
                            address: sensor address. Integer.
                            id: sensor ID. String.
                            battery: sensor battery state. Integer.
                            rssi: sensor rssi state. Integer
                            signal: sensor signal state. Integer.
                            enabled: whether sensor is enabled. Boolean.
                            version: sensor firmware version. String, None if
                                     no sensor firmware data available.
        """

        if connected_only and sensor.get('id').lower() in self.not_registered:
            # we are only interested in connected and enabled sensors and this
            # sensor was neither, so return three Nones
            return None, None, None
        else:
            # initialise a dict to hold our sensor data
            data = {}
            # attempt to obtain the sensor address, be prepared to catch any
            # exceptions encountered when parsing the data
            try:
                # obtain the sensor address as an integer
                data['address'] = int(sensor.get('type'))
            except (TypeError, ValueError):
                # could not convert field 'type' to an integer so use None
                data['address'] = None

            # obtain the sensor ID, it is a straight copy of field 'id'
            data['id'] = sensor.get('id')
            # attempt to obtain the sensor battery state, be prepared to catch
            # any exceptions encountered when parsing the data
            try:
                if not self.show_battery and int(sensor.get('signal')) == 0:
                    data['battery'] = None
                else:
                    # obtain the sensor battery state as an integer
                    data['battery'] = int(sensor.get('batt'))
            except (TypeError, ValueError):
                data['battery'] = None

            if sensor.get('id').lower() in self.not_registered:
              data['rssi'] = None
            else:
             try:
                # obtain the sensor rssi state as an integer
                data['rssi'] = int(sensor.get('rssi'))
             except (TypeError, ValueError):
                data['rssi'] = None

            # attempt to obtain the sensor signal state, be prepared to catch
            # any exceptions encountered when parsing the data
            if sensor.get('id').lower() in self.not_registered:
              data['signal'] = None
            else:
             try:
                # obtain the sensor signal state as an integer
                data['signal'] = int(sensor.get('signal'))
             except (TypeError, ValueError):
                data['signal'] = None


             # attempt to determine if the sensor is enabled, be prepared to
             # catch any exceptions encountered when parsing the data
            try:
                # obtain the sensor enabled state as an integer
                data['enabled'] = int(sensor.get('idst')) == 1
            except (TypeError, ValueError):
                data['enabled'] = None
            # Obtain the sensor firmware version, not all sensors have
            # firmware/make firmware version data available. For those sensors
            # the 'version' key/value pair is omitted.
            if 'version' in sensor.keys():
                data['version'] = sensor.get('version')
            # obtain the sensor model
            model = sensor.get('img')
            # Obtain the channel number if the sensor is part of a channelised
            # sensor group, if the sensor is not part of a channelised group
            # the channel will be set to None.
            # assume we do not have a channel number
            channel = None
            # the channel is part of the sensor 'name' field
            _name = sensor.get('name')
            if _name is not None:
                # look for a sub-string starting with 'CH' and ending with an
                # integer
                _match = re.search(r'CH\d+', _name)
                #_match = re.search('CH\d+', _name)
                # if a 'CH-integer' sub-string was found convert to lower case
                # and use the sub-string as the channel
                if _match is not None:
                    channel = _match.group(0).lower()
            return model, channel, data

    def get_model_from_firmware(self, firmware_string):
        """Determine the device model from the firmware version.

        To date device firmware versions have included the device model in
        the firmware version string returned via the device API. Whilst
        this is not guaranteed to be the case for future firmware releases,
        in the absence of any other direct means of obtaining the device
        model number it is a useful means for determining the device model.

        The check is a simple check to see if the model name is contained
        in the firmware version string returned by the device API.

        If a known model is found in the firmware version string the model
        is returned as a string. None is returned if (1) the firmware
        string is None or (2) a known model is not found in the firmware
        version string.
        """

        # do we have a firmware string
        if firmware_string is not None:
            # we have a firmware string so look for a known model in the
            # string and return the result
            return self.get_model(firmware_string)
        # for some reason we have no firmware string, so return None
        return None

    @staticmethod
    def get_model(t):
        """Determine the device model from a string.

        To date firmware versions have included the device model in the
        firmware version string or the device SSID. Both the firmware
        version string and device SSID are available via the device API so
        checking the firmware version string or SSID provides a de facto
        method of determining the device model.

        This method uses a simple check to see if a known model name is
        contained in the string concerned.

        Known model strings are contained in a tuple Station.known_models.

        If a known model is found in the string the model is returned as a
        string. None is returned if a known model is not found in the
        string.
        """

        # do we have a string to check
        if t is not None:
            # we have a string, now do we have a know model in the string,
            # if so return the model string
            for model in KNOWN_DEVICES:
                if model in t.upper():
                    return model
            # we don't have a known model so return None
            return None
        # we have no string so return None
        return None

    def process_temperature_object(self, item):
        """Process a temperature dict that uses both a 'val' and 'unit' key.

        Some temperature observation dicts contain the temperature value in
        field 'val' and temperature unit value in field 'unit'. This method
        extracts the temperature value and returns the temperature converted
        to the designated driver unit group temperature unit.

        Ecowitt has added 'battery' and (battery) 'voltage' fields to some
        observations. However, the driver obtains battery state data via the
        get_sensors_info HTTP API command so the battery state data in this
        object is not required. On the other hand, battery voltage may be
        included the get_livedata_info response, but may not in the
        get_sensors_info response. To protect against this situation this
        method checks for the 'voltage' key/value and if it exists it is
        converted to a float and included in the response. If the 'voltage' key
        does not exist it is ignored.

        The original observation dict is unchanged.

        Returns a dict keyed as follows:

        id:      common_list observation ID number. String.
        val:     temperature value in driver temperature units. Float.
        voltage: sensor battery voltage, if provided. Float.

        If the 'id' or 'val' keys do not exist or if the 'val' key value cannot
        be converted to an integer a ProcessorError exception is raised.
        """

        # initialise a dict to hold the result
        _item = dict()
        # attempt to save the 'id' value, wrap in try..except in case there is
        # a problem
        try:
            _item['id'] = item['id']
        except KeyError as e:
            # The 'id' key does not exist, we cannot continue with this object.
            # Raise a ProcessorError with a suitable message.
            raise ProcessorError(e) from e
        # obtain the temperature value, wrap in a try.. except in case there is
        # a problem
        try:
            # first obtain the temperature as a ValueTuple
            temp_vt = self.parse_obs_value('val',
                                           item,
                                          'group_temperature')
        except (KeyError, UnitError) as e:
            # Either the 'val' key does not exist or there was some other
            # problem processing the data, irrespective we cannot continue.
            # Raise a ProcessorError with a suitable message.
            raise ProcessorError(e) from e
        except  ParseError as e:
            # the 'val' key exists but there was a problem processing the
            # data, set the 'val' key/value to None
            _item['val'] = None
        else:
            # we have a numeric value, convert it to the unit system used by the
            # driver and save against the 'val' key
            _item['val'] = weewx.units.convert(temp_vt,
                                               weewx.units.std_groups[self.unit_system]['group_temperature']).value
        # process the 'voltage' key/value if it exists, wrap in a try.. except
        # in case there is a problem
        try:
            # first obtain the voltage as a ValueTuple
            voltage_vt = self.parse_obs_value('voltage', item, 'group_volt')
            # we have a numeric value, save it against the 'voltage' key
            _item['voltage'] = voltage_vt.value
        except KeyError:
            # no 'voltage' key exists, ignore and continue
            pass
        except  ParseError as e:
            # the 'voltage' key exists but there was a problem processing the
            # data, set the 'voltage' key/value to None
            _item['voltage'] = None
        # return our result dict
        return _item

    def process_pressure_object(self, item):
        """Process a pressure dict that uses a 'val' key.

        Some pressure observation dicts contain both the wind speed value and
        unit in field 'val'. This method extracts the pressure value and
        returns the pressure value converted to the designated driver unit
        group pressure unit.

        Ecowitt has added 'battery' and (battery) 'voltage' fields to some
        observations. However, the driver obtains battery state data via the
        get_sensors_info HTTP API command so the battery state data in this
        object is not required. On the other hand, battery voltage may be
        included the get_livedata_info response, but may not in the
        get_sensors_info response. To protect against this situation this
        method checks for the 'voltage' key/value and if it exists it is
        converted to a float and included in the response. If the 'voltage' key
        does not exist it is ignored.

        The original observation dict is unchanged.

        Returns a dict keyed as follows:

        id:      common_list observation ID number. String.
        val:     pressure value in driver pressure units. Float.
        voltage: sensor battery voltage, if provided. Float.

        If the 'id' or 'val' keys do not exist or if the 'val' key value cannot
        be converted to a float a ProcessorError exception is raised.
        """

        # initialise a dict to hold the result
        _item = dict()
        # attempt to save the 'id' value, wrap in try..except in case there is
        # a problem
        try:
            _item['id'] = item['id']
        except KeyError as e:
            # The 'id' key does not exist, we cannot continue with this object.
            # Raise a ProcessorError with a suitable message.
            raise ProcessorError(e) from e
        # obtain the pressure value, wrap in a try.. except in case there is a
        # problem
        try:
            # first obtain the pressure as a ValueTuple
            pressure_vt = self.parse_obs_value('val', item, 'group_pressure')
        except (KeyError, UnitError) as e:
            # Either the 'val' key does not exist or there was some other
            # problem processing the data, irrespective we cannot continue.
            # Raise a ProcessorError with a suitable message.
            raise ProcessorError(e) from e
        except  ParseError as e:
            # the 'val' key exists but there was a problem processing the
            # data, set the 'val' key/value to None
            _item['val'] = None
        else:
            # we have a numeric value, convert it to the unit system used by the
            # driver and save against the 'val' key
            _item['val'] = weewx.units.convert(pressure_vt,
                                               weewx.units.std_groups[self.unit_system]['group_pressure']).value
        # process the 'voltage' key/value if it exists, wrap in a try.. except
        # in case there is a problem
        try:
            # first obtain the voltage as a ValueTuple
            voltage_vt = self.parse_obs_value('voltage', item, 'group_volt')
            # we have a numeric value, save it against the 'voltage' key
            _item['voltage'] = voltage_vt.value
        except KeyError:
            # no 'voltage' key exists, ignore and continue
            pass
        except  ParseError as e:
            # the 'voltage' key exists but there was a problem processing the
            # data, set the 'voltage' key/value to None
            _item['voltage'] = None
        # return our result dict
        return _item

    def process_speed_object(self, item):
        """Process a wind speed dict that uses a 'val' key.

        Some wind speed observation dicts contain both the wind speed value and
        unit in field 'val'. This method extracts the wind speed and returns
        the wind speed converted to the designated driver unit group speed
        unit.

        Ecowitt has added 'battery' and (battery) 'voltage' fields to some
        observations. However, the driver obtains battery state data via the
        get_sensors_info HTTP API command so the battery state data in this
        object is not required. On the other hand, battery voltage may be
        included the get_livedata_info response, but may not in the
        get_sensors_info response. To protect against this situation this
        method checks for the 'voltage' key/value and if it exists it is
        converted to a float and included in the response. If the 'voltage' key
        does not exist it is ignored.

        The original observation dict is unchanged.

        Returns a dict keyed as follows:

        id:      common_list observation ID number. String.
        val:     wind speed value in driver speed units. Float.
        voltage: sensor battery voltage, if provided. Float.

        If the 'id' or 'val' keys do not exist or if the 'val' key value cannot
        be converted to a float a ProcessorError exception is raised.
        """

        # initialise a dict to hold the result
        _item = dict()
        # attempt to save the 'id' value, wrap in try..except in case there is
        # a problem
        try:
            _item['id'] = item['id']
        except KeyError as e:
            # The 'id' key does not exist, we cannot continue with this object.
            # Raise a ProcessorError with a suitable message.
            raise ProcessorError(e) from e
        # obtain the speed value, wrap in a try.. except in case there is a
        # problem
        try:
            # first obtain the speed as a ValueTuple
            speed_vt = self.parse_obs_value('val', item, 'group_speed')
        except (KeyError, UnitError) as e:
            # Either the 'val' key does not exist or there was some other
            # problem processing the data, irrespective we cannot continue.
            # Raise a ProcessorError with a suitable message.
            raise ProcessorError(e) from e
        except  ParseError as e:
            # the 'val' key exists but there was a problem processing the
            # data, set the 'val' key/value to None
            _item['val'] = None
        else:
            # we have a numeric value, convert it to the unit system used by the
            # driver and save against the 'val' key
            _item['val'] = weewx.units.convert(speed_vt,
                                               weewx.units.std_groups[self.unit_system]['group_speed']).value
        # process the 'voltage' key/value if it exists, wrap in a try.. except
        # in case there is a problem
        try:
            # first obtain the voltage as a ValueTuple
            voltage_vt = self.parse_obs_value('voltage', item, 'group_volt')
            # we have a numeric value, save it against the 'voltage' key
            _item['voltage'] = voltage_vt.value
        except KeyError:
            # no 'voltage' key exists, ignore and continue
            pass
        except  ParseError as e:
            # the 'voltage' key exists but there was a problem processing the
            # data, set the 'voltage' key/value to None
            _item['voltage'] = None
        # return our result dict
        return _item

    def process_direction_object(self, item):
        """Process a wind direction dict that uses a 'val' key.

        This method extracts the wind direction from the 'val' key/value and
        returns the wind direction value as an integer.

        Ecowitt has added 'battery' and (battery) 'voltage' fields to some
        observations. However, the driver obtains battery state data via the
        get_sensors_info HTTP API command so the battery state data in this
        object is not required. On the other hand, battery voltage may be
        included the get_livedata_info response, but may not in the
        get_sensors_info response. To protect against this situation this
        method checks for the 'voltage' key/value and if it exists it is
        converted to a float and included in the response. If the 'voltage' key
        does not exist it is ignored.

        The original observation dict is unchanged.

        Returns a dict keyed as follows:

        id:      common_list observation ID number. String.
        val:     wind direction value in degrees. Integer.
        voltage: sensor battery voltage, if provided. Float.

        If the 'id' or 'val' keys do not exist or if the 'val' key value cannot
        be converted to an integer a ProcessorError exception is raised.
        """

        # initialise a dict to hold the result
        _item = dict()
        # attempt to save the 'id' value, wrap in try..except in case there is
        # a problem
        try:
            _item['id'] = item['id']
        except KeyError as e:
            # The 'id' key does not exist, we cannot continue with this object.
            # Raise a ProcessorError with a suitable message.
            raise ProcessorError(e) from e
        # obtain the wind direction value, wrap in a try.. except in case there
        # is a problem
        try:
            # first obtain the wind direction as a ValueTuple
            dir_vt = self.parse_obs_value('val', item, 'group_direction')
        except (KeyError, UnitError) as e:
            # Either the 'val' key does not exist or there was some other
            # problem processing the data, irrespective we cannot continue.
            # Raise a ProcessorError with a suitable message.
            raise ProcessorError(e) from e
        except  ParseError as e:
            # the 'val' key exists but there was a problem processing the
            # data, set the 'val' key/value to None
            _item['val'] = None
        else:
            # we have a numeric value, coalesce to an int and save against the
            # 'val' key
            _item['val'] = int(dir_vt.value)
        # process the 'voltage' key/value if it exists, wrap in a try.. except
        # in case there is a problem
        try:
            # first obtain the voltage as a ValueTuple
            voltage_vt = self.parse_obs_value('voltage', item, 'group_volt')
            # we have a numeric value, save it against the 'voltage' key
            _item['voltage'] = voltage_vt.value
        except KeyError:
            # no 'voltage' key exists, ignore and continue
            pass
        except ParseError as e:
            # the 'voltage' key exists but there was a problem processing the
            # data, set the 'voltage' key/value to None
            _item['voltage'] = None
        # return our result dict
        return _item

    def process_humidity_object(self, item):
        """Process a humidity dict that uses a 'val' key.

        This method extracts the humidity value from the 'val' key/value and
        returns the value as an integer.

        Ecowitt has added 'battery' and (battery) 'voltage' fields to some
        observations. However, the driver obtains battery state data via the
        get_sensors_info HTTP API command so the battery state data in this
        object is not required. On the other hand, battery voltage may be
        included the get_livedata_info response, but may not in the
        get_sensors_info response. To protect against this situation this
        method checks for the 'voltage' key/value and if it exists it is
        converted to a float and included in the response. If the 'voltage' key
        does not exist it is ignored.

        The original observation dict is unchanged.

        Returns a dict keyed as follows:

        id:      common_list observation ID number. String.
        val:     humidity value in percent. Integer.
        voltage: sensor battery voltage, if provided. Float.

        If the 'id' or 'val' keys do not exist or if the 'val' key value cannot
        be converted to an integer a ProcessorError exception is raised.
        """

        # initialise a dict to hold the result
        _item = dict()
        # attempt to save the 'id' value, wrap in try..except in case there is
        # a problem
        try:
            _item['id'] = item['id']
        except KeyError as e:
            # The 'id' key does not exist, we cannot continue with this object.
            # Raise a ProcessorError with a suitable message.
            raise ProcessorError(e) from e
        # obtain the humidity value, wrap in a try.. except in case there is a
        # problem
        try:
            # first obtain the humidity as a ValueTuple
            hum_vt = self.parse_obs_value('val', item, 'group_percent')
        except (KeyError, UnitError) as e:
            # Either the 'val' key does not exist or there was some other
            # problem processing the data, irrespective we cannot continue.
            # Raise a ProcessorError with a suitable message.
            raise ProcessorError(e) from e
        except  ParseError as e:
            # the 'val' key exists but there was a problem processing the
            # data, set the 'val' key/value to None
            _item['val'] = None
        else:
            # we have a numeric value, coalesce to an int and save against the
            # 'val' key
            _item['val'] = int(hum_vt.value)
        # process the 'voltage' key/value if it exists, wrap in a try.. except
        # in case there is a problem
        try:
            # first obtain the voltage as a ValueTuple
            voltage_vt = self.parse_obs_value('voltage', item, 'group_volt')
            # we have a numeric value, save it against the 'voltage' key
            _item['voltage'] = voltage_vt.value
        except KeyError:
            # no 'voltage' key exists, ignore and continue
            pass
        except ParseError as e:
            # the 'voltage' key exists but there was a problem processing the
            # data, set the 'voltage' key/value to None
            _item['voltage'] = None
        # return our result dict
        return _item

    process_uv_radiation_object = process_humidity_object
    process_index_object = process_direction_object

    def process_boolean_object(self, item):
        """Process a 'boolean' dict that uses a 'val' key.

        This method extracts the boolean value from the 'val' key/value and
        returns the value as an integer.

        Ecowitt has added 'battery' and (battery) 'voltage' fields to some
        observations. However, the driver obtains battery state data via the
        get_sensors_info HTTP API command so the battery state data in this
        object is not required. On the other hand, battery voltage may be
        included the get_livedata_info response, but may not in the
        get_sensors_info response. To protect against this situation this
        method checks for the 'voltage' key/value and if it exists it is
        converted to a float and included in the response. If the 'voltage' key
        does not exist it is ignored.

        The original observation dict is unchanged.

        Returns a dict keyed as follows:

        id:      common_list observation ID number. String.
        val:     boolean value. Integer, 0 = False, 1 = True.
        voltage: sensor battery voltage, if provided. Float.

        If the 'id' or 'val' keys do not exist or if the 'val' key value cannot
        be converted to an integer a ProcessorError exception is raised.
        """

        # initialise a dict to hold the result
        _item = dict()
        # attempt to save the 'id' value, wrap in try..except in case there is
        # a problem
        try:
            _item['id'] = item['id']
        except KeyError as e:
            # The 'id' key does not exist, we cannot continue with this object.
            # Raise a ProcessorError with a suitable message.
            raise ProcessorError(e) from e
        # obtain the boolean value, wrap in a try.. except in case there
        # is a problem
        try:
            # first obtain the boolean value as a ValueTuple
            bool_vt = self.parse_obs_value('val', item, 'group_boolean')
        except (KeyError, UnitError) as e:
            # Either the 'val' key does not exist or there was some other
            # problem processing the data, irrespective we cannot continue.
            # Raise a ProcessorError with a suitable message.
            raise ProcessorError(e) from e
        except  ParseError as e:
            # the 'val' key exists but there was a problem processing the
            # data, set the 'val' key/value to None
            _item['val'] = None
        else:
            # we have a numeric value, coalesce to an int and save against the
            # 'val' key
            _item['val'] = int(bool_vt.value)
        # process the 'voltage' key/value if it exists, wrap in a try.. except
        # in case there is a problem
        try:
            # first obtain the voltage as a ValueTuple
            voltage_vt = self.parse_obs_value('voltage', item, 'group_volt')
            # we have a numeric value, save it against the 'voltage' key
            _item['voltage'] = voltage_vt.value
        except KeyError:
            # no 'voltage' key exists, ignore and continue
            pass
        except ParseError as e:
            # the 'voltage' key exists but there was a problem processing the
            # data, set the 'voltage' key/value to None
            _item['voltage'] = None
        # return our result dict
        return _item

    @staticmethod
    def process_noop_object(item):
        """Process a field and return the value None.

        Always returns the value None irrespective of the field. The original
        observation dict is always unchanged.
        """

        # always return None
        return None

    def process_light_object(self, item):
        """Process a light dict with 'val' field only.

        Ecowitt devices do not support a pyranometer, rather they support a
        sensor suite that uses a light sensor to measure light intensity,
        also known as illuminance, in lux. If selected by the user, an
        approximation is used to estimate solar irradiance. WeeWX does not
        natively support such conversion nor will it likely support it in the
        future. As Ecowitt devices are really measuring light intensity and not
        solar irradiance, any Ecowitt 'light' values are converted to the Weewx
        light intensity/illuminance unit lux. This is done by the driver
        without reference to the WeeWX unit conversion machinery. In the case
        of light values that have been converted to solar irradiance by the
        device, the same Ecowitt approximation is used to convert solar
        irradiance value back to light intensity/illuminance.

        Some light observation dicts contain both the light value and unit in
        field 'val'. This method extracts the light value and returns the value
        as a float.

        Ecowitt has added 'battery' and (battery) 'voltage' fields to some
        observations. However, the driver obtains battery state data via the
        get_sensors_info HTTP API command so the battery state data in this
        object is not required. To avoid confusion pop the 'battery' key if it
        exists. Also check for the 'voltage' key/value, if it exists convert
        the value to a float and return the key/value in the response. If the
        'voltage' key does not exist it is ignored.

        The original observation dict is always unchanged.

        Returns a dict keyed as follows:

        id:      common_list observation ID number. String.
        val:     light value in lux. Integer.
        voltage: sensor battery voltage if provided. Float.

        If the 'id' or 'val' keys do not exist or if the 'val' key value cannot
        be converted to an integer a ProcessorError exception is raised.
        """

        # initialise a dict to hold the result
        _item = dict()
        # attempt to save the 'id' value, wrap in try..except in case there is
        # a problem
        try:
            _item['id'] = item['id']
        except KeyError as e:
            # The 'id' key does not exist, we cannot continue with this object.
            # Raise a ProcessorError with a suitable message.
            raise ProcessorError(e) from e
        # obtain the 'light' value, wrap in a try.. except in case there is a
        # problem
        try:
            # first obtain the light as a ValueTuple
            light_vt = self.parse_obs_value('val', item, 'group_radiation')
        except (KeyError, UnitError) as e:
            # Either the 'val' key does not exist or there was some other
            # problem processing the data, irrespective we cannot continue.
            # Raise a ProcessorError with a suitable message.
            raise ProcessorError(e) from e
        except  ParseError as e:
            # the 'val' key exists but there was a problem processing the
            # data, set the 'val' key/value to None
            _item['val'] = None
        else:
            # we have a numeric value, convert it to the unit system used by the
            # driver and save against the 'val' key
            _item['val'] = weewx.units.convert(light_vt,
                                               weewx.units.std_groups[self.unit_system]['group_radiation']).value
        # process the 'voltage' key/value if it exists, wrap in a try.. except
        # in case there is a problem
        try:
            # first obtain the voltage as a ValueTuple
            voltage_vt = self.parse_obs_value('voltage', item, 'group_volt')
            # we have a numeric value, save it against the 'voltage' key
            _item['voltage'] = voltage_vt.value
        except KeyError:
            # no 'voltage' key exists, ignore and continue
            pass
        except ParseError as e:
            # the 'voltage' key exists but there was a problem processing the
            # data, set the 'voltage' key/value to None
            _item['voltage'] = None
        # return our result dict
        return _item

    def process_rainfall_object(self, item):
        """Process a rain dict with 'val' field only.

        Some rain dicts contain both the rainfall value and unit in field
        'val'. This method extracts the rainfall and unit values and returns
        the rainfall converted to the designated driver unit group rainfall
        unit.

        Ecowitt has added 'battery' and (battery) 'voltage' fields to some
        observations. However, the driver obtains battery state data via the
        get_sensors_info HTTP API command so the battery state data in this
        object is not required. To avoid confusion pop the 'battery' key if it
        exists. Also check for the 'voltage' key/value, if it exists convert
        the value to a float and return the key/value in the response. If the
        'voltage' key does not exist it is ignored.

        The original observation dict is always unchanged.

        Returns a dict keyed as follows:

        id:      common_list observation ID number. String.
        val:     rain value in driver rainfall unit. float.
        voltage: sensor battery voltage if provided. Float.

        If the 'id' or 'val' keys do not exist or if the 'val' key value cannot
        be converted to an integer a ProcessorError exception is raised.
        """

        # initialise a dict to hold the result
        _item = dict()
        # attempt to save the 'id' value
        try:
            _item['id'] = item['id']
        except KeyError as e:
            # The 'id' key does not exist, we cannot continue with this object.
            # Raise a ProcessorError with a suitable message.
            raise ProcessorError(e) from e
        # obtain the rainfall value, wrap in a try.. except in case there is a
        # problem
        try:
            # first obtain the rainfall as a ValueTuple
            rain_vt = self.parse_obs_value('val', item, 'group_rain')
        except (KeyError, UnitError) as e:
            # Either the 'val' key does not exist or there was some other
            # problem processing the data, irrespective we cannot continue.
            # Raise a ProcessorError with a suitable message.
            raise ProcessorError(e) from e
        except  ParseError as e:
            # the 'val' key exists but there was a problem processing the
            # data, set the 'val' key/value to None
            _item['val'] = None
        else:
            # we have a numeric value, convert it to the unit system used by the
            # driver and save against the 'val' key
            _item['val'] = weewx.units.convert(rain_vt,
                                               weewx.units.std_groups[self.unit_system]['group_rain']).value
        # process the 'voltage' key/value if it exists, wrap in a try.. except
        # in case there is a problem
        try:
            # first obtain the voltage as a ValueTuple
            voltage_vt = self.parse_obs_value('voltage', item, 'group_volt')
            # we have a numeric value, save it against the 'voltage' key
            _item['voltage'] = voltage_vt.value
        except KeyError:
            # no 'voltage' key exists, ignore and continue
            pass
        except ParseError as e:
            # the 'voltage' key exists but there was a problem processing the
            # data, set the 'voltage' key/value to None
            _item['voltage'] = None
        # return our result dict
        return _item

    def process_rainrate_object(self, item):
        """Process a rain rate dict with 'val' field only.

        Some rain rate dicts contain both the rain rate value and unit in field
        'val'. This method extracts the rain rate and unit values and returns
        the rain rate converted to the designated driver unit group rain rate
        unit. If the 'val' field does not exist, or if the 'val' field cannot
        be processed or unit converted, a ProcessorError is raised.

        Ecowitt has added 'battery' and (battery) 'voltage' fields to some
        observations. However, the driver obtains battery state data via the
        get_sensors_info HTTP API command so the battery state data in this
        object is not required. To avoid confusion pop the 'battery' key if it
        exists. Also check for the 'voltage' key/value, if it exists convert
        the value to a float and return the key/value in the response. If the
        'voltage' key does not exist it is ignored.

        The original observation dict is always unchanged.

        Returns a dict keyed as follows:

        id:      common_list observation ID number. String.
        val:     rain rate value in driver rainfall rate unit. float.
        voltage: sensor battery voltage if provided. Float.

        If the 'id' or 'val' keys do not exist or if the 'val' key value cannot
        be converted to an integer a ProcessorError exception is raised.
        """

        # initialise a dict to hold the result
        _item = dict()
        # attempt to save the 'id' value
        try:
            _item['id'] = item['id']
        except KeyError as e:
            # The 'id' key does not exist, we cannot continue with this object.
            # Raise a ProcessorError with a suitable message.
            raise ProcessorError(e) from e
        # obtain the rain rate value, wrap in a try.. except in case there is a
        # problem
        try:
            # first obtain the rain rate as a ValueTuple
            rainrate_vt = self.parse_obs_value('val', item, 'group_rainrate')
        except (KeyError, UnitError) as e:
            # Either the 'val' key does not exist or there was some other
            # problem processing the data, irrespective we cannot continue.
            # Raise a ProcessorError with a suitable message.
            raise ProcessorError(e) from e
        except  ParseError as e:
            # the 'val' key exists but there was a problem processing the
            # data, set the 'val' key/value to None
            _item['val'] = None
        else:
            # we have a numeric value, convert it to the unit system used by the
            # driver and save against the 'val' key
            _item['val'] = weewx.units.convert(rainrate_vt,
                                               weewx.units.std_groups[self.unit_system]['group_rainrate']).value
        # process the 'voltage' key/value if it exists, wrap in a try.. except
        # in case there is a problem
        try:
            # first obtain the voltage as a ValueTuple
            voltage_vt = self.parse_obs_value('voltage', item, 'group_volt')
            # we have a numeric value, save it against the 'voltage' key
            _item['voltage'] = voltage_vt.value
        except KeyError:
            # no 'voltage' key exists, ignore and continue
            pass
        except ParseError as e:
            # the 'voltage' key exists but there was a problem processing the
            # data, set the 'voltage' key/value to None
            _item['voltage'] = None
        # return our result dict
        return _item

    def parse_obs_value(self, key, json_object, unit_group, device_units=None):
        """Parse an observation in a JSON object and return a ValueTuple.

        Ecowitt HTTP API JSON responses identify the units for an observation in
        one of four ways:
        1.  the unit string is appended to the observation value and the combined
            value-unit string stored in the JSON key/value pair
            (eg: 'dayRain': '12.5mm')
        2.  the unit string is stored in a different key/value pair to the value
            concerned (eg: 'unit': 'km/h')
        3.  the unit string is implicit (eg: humidity values are expressed only
            in percent (%)
        4.  the unit string is not included in the API response, rather it is
            taken from the device unit settings

        Given a key and json_object this method determines the numeric value and
        WeeWX unit string of the key value. The numeric value and unit string are
        determined using the following approach:

        1. the value and Ecowitt unit string are extracted from the key value
        2. if there is no unit string in the key value the Ecowitt unit string is
           taken from the 'unit' key value in the JSON object if it exists
        3. if the 'unit' key does not exist the unit string is extracted from
           the 'device_units' dict using the 'unit_group' as the key

        Parameters:
            key:            The key of a key/value pair in the JSON object that
                            contains the obs value
            json_object:    The JSON object that contains the obs value
            unit_group:     WeeWX unit group (eg 'group_temperature') use by
                            the obs value of interest
            device_units:   Dict, keyed by WeeWX unit group, containing details
                            of the WeeWX unit used by the device for each unit
                            group. If not provided a default dict is used.
        """

        # Do we have any device unit data? If not we can safely assume and use
        # those units that are universal across unit
        # systems (eg direction - degrees, humidity - percent)
        if device_units is None:
            device_units = self.default_device_units
        # look for the unit string in the obs value field
        try:
            # extract the value and label via a regex
            _value, _unit = re.match("([0-9.,+-]+)(.*)", json_object[key]).group(1,2)
            # remove any leading or trailing whitespace from the unit string
            # and convert to lower case
            _unit = _unit.strip().lower()
        except KeyError as e:
            # the JSON object does not have the required key, raise
            raise
        except AttributeError:
            # we have no matches, raise a ParseError with a suitable message
            raise ParseError(f"Could not determine value and unit for '{key}' "
                             f"in JSON object '{json_object}'")
        # try to coalesce a float from the extracted value, wrap in a
        # try..except in case there is a problem
        try:
            _numeric = float(_value)
        except (TypeError, ValueError):
            # we cannot convert the value to a float, raise a ParseError with a
            # suitable message
            raise ParseError("Could not convert '%s' to a float" % _value)
        # process the unit
        if len(_unit) > 0:
            # We have a unit string, determine the applicable WeeWX unit. Be
            # prepared to catch the exception if we have an unknown unit
            # string.
            try:
                weewx_unit = self.get_weewx_unit(_unit, unit_group=unit_group)
            except UnitError as e:
                # we have an unknown unit string, log it and raise a ParseError
                log.error("parse_obs_value: Could not determine unit applicable to field '%s: %s': %s",
                          key, _numeric, e)
                # raise a ParseError with a suitable message
                raise ParseError(f"Could not equate Ecowitt unit '{_unit}' with "
                                 f"a WeeWX unit")
            else:
                # we have a WeeWX unit, construct and return a ValueTuple
                return weewx.units.ValueTuple(_numeric, weewx_unit, unit_group)
        else:
            # we could not extract the unit string from the key value, look for a
            # 'unit' key in the JSON object
            if 'unit' in json_object.keys():
                # The 'unit' key exists, use it's content to determine the
                # WeeWX unit string. Be prepared to catch the exception if we
                # have an unknown unit string.
                try:
                    weewx_unit = self.get_weewx_unit(json_object['unit'],
                                                     unit_group=unit_group)
                except UnitError as e:
                    # we have an unknown unit string, log it and raise a
                    # ParseError
                    _msg = f"unknown Ecowitt unit string '{json_object['unit']}' in field 'unit'"
                    log.error("parse_obs_value: Could not determine unit applicable to field '%s: %s': %s",
                              key, _numeric, _msg)
                    # raise a ParseError with a suitable message
                    raise ParseError(f"Could2 not equate Ecowitt unit '{json_object['unit']}' with "
                                     f"a WeeWX unit")
                else:
                    # we have a WeeWX unit, construct and return a ValueTuple
                    return weewx.units.ValueTuple(_numeric, weewx_unit, unit_group)
            else:
                # we have no 'unit' key and we cannot extract the unit from a
                # field in the JSON object, do we have a device_units dict
                if device_units is not None:
                    # determine the WeeWX unit string
                    try:
                        weewx_unit = device_units[unit_group]
                    except KeyError:
                        # we have a unit group that is not a key in device_units,
                        # raise a ParseError with a suitable message
                        raise UnitError(f"Could not determine device units "
                                         f"for '{unit_group}'")
                    else:
                        return weewx.units.ValueTuple(_numeric, weewx_unit, unit_group)
                else:
                    # we do not have device_units lookup data, raise a
                    # ParseError with a suitable message
                    raise ParseError("Device unit lookup is None")

    @staticmethod
    def get_weewx_unit(unit_string, unit_group=None):
        """Determine the WeeWX unit given a unit group and Ecowitt unit string.

        Ecowitt uses various unit strings in API responses to indicate the
        units used by a particular value. These units strings are not
        necessarily the same as used by WeeWX meaning that some form of
        translation is required.

        This method uses a look-up table to determine the equivalent WeeWX unit
        from an Ecowitt unit string. If the Ecowitt unit string is not a key in
        the look-up table a UnitError is raised with details on the unknown
        unit string.

        The Ecowitt HTTP driver implements a number of additional unit groups
        and units to support obs available from Ecowitt devices that are not
        available under WeeWX. As some of these unit groups use units similar
        to WeeWX but requiring different properties, eg unit conversion
        formulae (eg delta temperature), some units also depend on the unit
        group being used.

        Returns a WeeWX unit or raises a UnitError if no WeeWX unit could be
        determined.
        """

        # obtain the WeeWX unit equivalent of the Ecowitt unit string, wrap in
        # a try..except in case an unknown unit string is encountered
        try:
            # lookup the WeeWX unit given the unit string
            _unit = EcowittHttpParser.unit_lookup[unit_string.lower()]
        except (AttributeError, KeyError):
            # we do not know about this unit string or it could not be
            # converted to a lower, either way it is unknown so raise a
            # UnitError exception with an appropriate message
            raise UnitError("unknown Ecowitt unit string: '%s'" % unit_string)
        else:
            # we have a WeeWX unit based on the Ecowitt unit string, but
            # do we need to make any changes given the unit group
            if unit_group is not None:
                if unit_group.lower() == 'group_depth':
                    # our group_depth uses a hybrid mixture of group_rain and
                    # group_altitude units, we delineate these units by
                    # appending a '2'
                    _unit = ''.join([_unit, '2'])
                elif unit_group.lower() == 'group_deltat':
                    # our group_deltat uses the same units as
                    # group_temperature, but with a '2' appended
                    _unit = ''.join([_unit, '2'])
            # return the WeeWX unit
            return _unit


# ============================================================================
#                            class EcowittSensors
# ============================================================================

class EcowittSensors:
    """Class for processing Ecowitt sensor metadata.

    The Ecowitt local HTTP API provides various sensor metadata information via
    multiple API calls. Class EcowittSensors processes this disparate
    information and makes formatted sensor metadata available via a number of
    properties.

    To ensure up-to-data data an EcowittSensors object should be updated with
    current get_sensor_info and get_livedata_info before accessing the
    EcowittSensors object properties.
    """

    # tuple of lowercase sensor models for which Ecowitt has provided no low
    # battery state definition
    no_low = ('ws80', 'ws85', 'ws90')
    # sensors whose battery state is determined from a binary value (0|1)
    batt_binary = ('wh68', 'wh69', 'wh25', 'wh26', 'wn31', 'wn32')
    # sensors whose battery state is determined from an integer value
    batt_int = ('wn20', 'wh40', 'wh41', 'wh43', 'wh45', 'wh55', 'wh57')
    # sensors whose battery state is determined from a battery voltage value
    batt_volt = ('wh68', 'wh51', 'wh54', 'wn34', 'wn35', 'ws80', 'ws85', 'ws90')
    # map of 'dotted' get_livedata_info sensor voltage fields to sensor address
    sensor_with_voltage = {
        'rain.0x13.voltage': 3,		#wh40 
        'rain.0x13.voltage': 70,		#wn20 
        'piezoRain.0x13.voltage': 48,     #WH90
        'piezoRain.0x13.voltage': 49,	#WH85
        'ch_soil.1.voltage': 14,
        'ch_soil.2.voltage': 15,
        'ch_soil.3.voltage': 16,
        'ch_soil.4.voltage': 17,
        'ch_soil.5.voltage': 18,
        'ch_soil.6.voltage': 19,
        'ch_soil.7.voltage': 20,
        'ch_soil.8.voltage': 21,
        'ch_soil.9.voltage': 58,
        'ch_soil.10.voltage': 59,
        'ch_soil.11.voltage': 60,
        'ch_soil.12.voltage': 61,
        'ch_soil.13.voltage': 62,
        'ch_soil.14.voltage': 63,
        'ch_soil.15.voltage': 64,
        'ch_soil.16.voltage': 65,
        'ch_temp.1.voltage': 31,
        'ch_temp.2.voltage': 32,
        'ch_temp.3.voltage': 33,
        'ch_temp.4.voltage': 34,
        'ch_temp.5.voltage': 35,
        'ch_temp.6.voltage': 36,
        'ch_temp.7.voltage': 37,
        'ch_temp.8.voltage': 38,
        'ch_leaf.1.voltage': 40,
        'ch_leaf.2.voltage': 41,
        'ch_leaf.3.voltage': 42,
        'ch_leaf.4.voltage': 43,
        'ch_leaf.5.voltage': 44,
        'ch_leaf.6.voltage': 45,
        'ch_leaf.7.voltage': 46,
        'ch_leaf.8.voltage': 47,
        'ch_lds.1.voltage': 66,
        'ch_lds.2.voltage': 67,
        'ch_lds.3.voltage': 68,
        'ch_lds.4.voltage': 69
    }
    # map of sensor address to composite sensor name (ie sensor model and
    # channel (as applicable))
    sensor_address = {
        0: 'wh69',
        1: 'wh68',
        2: 'ws80',
        3: 'wh40',
        4: 'wh25',
        5: 'wh26',
        6: 'wn31_ch1',
        7: 'wn31_ch2',
        8: 'wn31_ch3',
        9: 'wn31_ch4',
        10: 'wn31_ch5',
        11: 'wn31_ch6',
        12: 'wn31_ch7',
        13: 'wn31_ch8',
        14: 'wh51_ch1',
        15: 'wh51_ch2',
        16: 'wh51_ch3',
        17: 'wh51_ch4',
        18: 'wh51_ch5',
        19: 'wh51_ch6',
        20: 'wh51_ch7',
        21: 'wh51_ch8',
        22: 'wh41_ch1',
        23: 'wh41_ch2',
        24: 'wh41_ch3',
        25: 'wh41_ch4',
        26: 'wh57',
        27: 'wh55_ch1',
        28: 'wh55_ch2',
        29: 'wh55_ch3',
        30: 'wh55_ch4',
        31: 'wn34_ch1',
        32: 'wn34_ch2',
        33: 'wn34_ch3',
        34: 'wn34_ch4',
        35: 'wn34_ch5',
        36: 'wn34_ch6',
        37: 'wn34_ch7',
        38: 'wn34_ch8',
        39: 'wh45',
        40: 'wn35_ch1',
        41: 'wn35_ch2',
        42: 'wn35_ch3',
        43: 'wn35_ch4',
        44: 'wn35_ch5',
        45: 'wn35_ch6',
        46: 'wn35_ch7',
        47: 'wn35_ch8',
        48: 'ws90',
        49: 'ws85',
        58: 'wh51_ch9',
        59: 'wh51_ch10',
        60: 'wh51_ch11',
        61: 'wh51_ch12',
        62: 'wh51_ch13',
        63: 'wh51_ch14',
        64: 'wh51_ch15',
        65: 'wh51_ch16',
        66: 'wh54_ch1',
        67: 'wh54_ch2',
        68: 'wh54_ch3',
        69: 'wh54_ch4',
        70: 'wn20',
    }

    def __init__(self, all_sensor_data=None, live_data=None):
        """Initialise an EcowittSensors object."""

        # initialise a property to hold all sensor data
        self.all_sensor_data = None
        # save the get_sensor_info API data and update with get_livedata_info
        # API data
        self.update_sensor_data(all_sensor_data=all_sensor_data,
                                live_data=live_data)

    def update_sensor_data(self, all_sensor_data, live_data=None):
        """Update the stored sensor data with fresh API data."""

        # save the get_sensor_info API data
        self.all_sensor_data = all_sensor_data if all_sensor_data is not None else {}
        # update the current stored sensor data with get_livedata_info API data
        self.merge_live_data(live_data)

    def merge_live_data(self, live_data):
        """Update our sensor data with live data."""

        # do we have any live data
        if live_data is not None:
            # we have live data, iterate over the live data fields (and
            # corresponding sensor addresses) we know that contain voltage data
            for source_field, sensor_address in self.sensor_with_voltage.items():
                # does the live data have a key that matches the source field
                if source_field in live_data.keys():
                    # we have a match, set a flag so we know if we have
                    # corresponding sensor in our sensor data
                    found = False
                    # now iterate over the sensors we know about in our sensor data
                    for model, data in self.all_sensor_data.items():
                        # do we have a channelised or non-channelised sensor,
                        # a non-channelised sensor will have an 'address' key
                        if 'address' in data.keys():
                            # we have a non-channelised sensor, check if the
                            # sensor address in our metadata matches the
                            # livedata sensor address
                            if data['address'] == sensor_address:
                                # we have a match, add/update a voltage
                                # key/value pair in our sensor metadata
                                data['voltage'] = live_data[source_field]
                                # set our flag
                                found = True
                        else:
                            # we have a channelised sensor, iterate over all of
                            # the possible channels
                            for channel, channel_data in data.items():
                                # check if the sensor address in our metadata
                                # matches the livedata sensor address
                                if int(channel_data.get('address', 999)) == sensor_address:
                                    # we have a match, add/update a voltage
                                    # key/value pair in our sensor metadata
                                    channel_data['voltage'] = live_data[source_field]
                                    # set our flag
                                    found = True
                                    # break out of the 'channel' loop
                                    break
                        # if we found our sensor break out of the 'sensor' loop
                        if found:
                            break

    @property
    def data(self):
        """Return the current sensor metadata.

        Return a dict, keyed by lowercase sensor model, of my current sensor
        metadata. Available key/value pairs for each sensor includes:

        'name':     ???
        'id':       The sensor ID, uppercase string. 'FFFFFFFE' for
                    disconnected sensors, 'FFFFFFFF' for sensors that are
                    'learning'/connecting.
        'battery':  Sensor battery state, integer. Anecdotally 0-6 and 9.
                    Meaning depends on the sensor, 9 (appears to) indicate no
                    battery data is available.
        'signal':   Sensor signal state, integer. 0-4. Indicates number of the
                    last four sensor data that were successfully received.
        'voltage':  Sensor battery voltage, float. Not supported for all
                    sensors. Key is omitted for unsupported sensors.

        For channelised sensors the 'model' key value consists of a dict,
        keyed by channel number, containing data in the same format as above.
        """

        return self.all_sensor_data

    @property
    def all_models(self):
        """Returns a tuple of known sensor models.

        Includes all sensor models returned in provided get_sensor_info API
        response whether connected or not connected. Sensor model is short form
        only, eg. 'wh51', 'wn34' etc.
        """

        # our models are the keys in all_sensor_data, return a sorted tuple of
        # these keys
        return tuple(sorted(self.all_sensor_data.keys()))

    @property
    def all(self):
        """Returns a tuple of known sensors.

        Includes all sensors returned in provided get_sensor_info API response
        whether connected or not connected. Sensor data includes channel number
        where applicable, eg. 'wh51_ch1', 'wn34_ch3' etc.
        """

        # initialise a list to hold our result
        all_sensors = []
        # iterate over each sensor_data key value pair, this will yield the
        # sensor model and either a dict sensor metadata or, for channelised
        # sensors, a dict keyed by channel of channel data
        for model, data in self.all_sensor_data.items():
            # iterate over the key value pairs in the 'data', then determine
            # whether we have a channelised sensor
            for ch, ch_data in data.items():
                # is the channel data a dict
                if hasattr(ch_data, 'keys'):
                    # we have channelised sensor, add the sensor and channel
                    # number
                    all_sensors.append(f'{model}_{ch}')
                else:
                    # we have a non-channelised sensor
                    all_sensors.append(model)
                    # we have finished with this sensor, move onto the next
                    break
        # return our result as a sorted tuple
        return tuple(sorted(all_sensors))

    @property
    def enabled(self):
        """Returns a tuple of enabled sensors.

        Includes all sensors returned in provided get_sensor_info API response
        that are enabled whether connected or not connected. Sensor data
        includes channel number where applicable, eg. 'wh51_ch1', 'wn34_ch3'
        etc.
        """

        # initialise a list to hold our result
        enabled = []
        # iterate over each sensor_data key value pair, this will yield the
        # sensor model and either a dict sensor metadata or, for channelised
        # sensors, a dict keyed by channel of channel data
        for model, data in self.all_sensor_data.items():
            # iterate over the key value pairs in the 'data', then determine
            # whether we have a channelised sensor
            for ch, ch_data in data.items():
                # is the channel data a dict
                if hasattr(ch_data, 'keys'):
                    # we have channelised sensor, now check if the sensor is
                    # enabled
                    if ch_data.get('enabled'):
                        # the sensor is connected, add it to our list
                        enabled.append(f'{model}_{ch}')
                else:
                    # we have a non-channelised sensor
                    if data.get('enabled'):
                        # the sensor is connected, add it to our list
                        enabled.append(model)
                    # we have finished with this sensor, move onto the next
                    break
        # return our result as a sorted tuple
        return tuple(sorted(enabled))

    @property
    def disabled(self):
        """Returns a tuple of disabled sensors.

        Includes all sensors returned in provided get_sensor_info API response
        that are disabled. Sensor data includes channel number where
        applicable, eg. 'wh51_ch1', 'wn34_ch3' etc.
        """

        # initialise a list to hold our result
        disabled = []
        # iterate over each sensor_data key value pair, this will yield the
        # sensor model and either a dict sensor metadata or, for channelised
        # sensors, a dict keyed by channel of channel data
        for model, data in self.all_sensor_data.items():
            # iterate over the key value pairs in the 'data', then determine
            # whether we have a channelised sensor
            for ch, ch_data in data.items():
                # is the channel data a dict
                if hasattr(ch_data, 'keys'):
                    # we have channelised sensor, now check if the sensor is
                    # disabled
                    if not ch_data.get('enabled'):
                        # the sensor is disabled, add it to our list
                        disabled.append(f'{model}_{ch}')
                else:
                    # we have a non-channelised sensor
                    if not data.get('enabled'):
                        # the sensor is disabled, add it to our list
                        disabled.append(model)
                    # we have finished with this sensor, move onto the next
                    break
        # return our result as a sorted tuple
        return tuple(sorted(disabled))

    @property
    def learning(self):
        """Returns a tuple of sensors that are 'learning'.

        Includes all sensors returned in provided get_sensor_info API response
        that are 'learning'. Sensor data includes channel number where
        applicable, eg. 'wh51_ch1', 'wn34_ch3' etc.
        """

        # initialise a list to hold our result
        learning = []
        # iterate over each sensor_data key value pair, this will yield the
        # sensor model and either a dict sensor metadata or, for channelised
        # sensors, a dict keyed by channel of channel data
        for model, data in self.all_sensor_data.items():
            # iterate over the key value pairs in the 'data', then determine
            # whether we have a channelised sensor
            for ch, ch_data in data.items():
                # is the channel data a dict
                if hasattr(ch_data, 'keys'):
                    # we have channelised sensor, now check if the sensor is connected
                    if ch_data.get('id') == 'FFFFFFFF':
                        # the sensor is learning, add it to our list
                        learning.append(f'{model}_{ch}')
                else:
                    # we have a non-channelised sensor
                    if data.get('id') == 'FFFFFFFF':
                        # the sensor is learning, add it to our list
                        learning.append(model)
                    # we have finished with this sensor, move onto the next
                    break
        # return our result as a sorted tuple
        return tuple(sorted(learning))

    @property
    def connected(self):
        """Returns a tuple of connected sensors.

        Includes all sensors returned in provided get_sensor_info API response
        that are connected. Sensor data includes channel number where
        applicable, eg. 'wh51_ch1', 'wn34_ch3' etc.
        """

        # initialise a list to hold our result
        connected = []
        # iterate over each sensor_data key value pair, this will yield the
        # sensor model and either a dict sensor metadata or, for channelised
        # sensors, a dict keyed by channel of channel data
        for model, data in self.all_sensor_data.items():
            # iterate over the key value pairs in the 'data', then determine
            # whether we have a channelised sensor
            for ch, ch_data in data.items():
                # is the channel data a dict
                if hasattr(ch_data, 'keys'):
                    # we have channelised sensor, now check if the sensor is connected
                    if (ch_data.get('enabled') and
                            ch_data.get('id') != 'FFFFFFFE' and
                            ch_data.get('id') != 'FFFFFFFF'):
                        # the sensor is connected, add it to our list
                        connected.append(f'{model}_{ch}')
                else:
                    # we have a non-channelised sensor
                    if (data.get('enabled') and
                            data.get('id') != 'FFFFFFFE'
                            and data.get('id') != 'FFFFFFFF'):
                        # the sensor is connected, add it to our list
                        connected.append(model)
                    # we have finished with this sensor, move onto the next
                    break
        # return our result as a sorted tuple
        return tuple(sorted(connected))

    def batt_state_desc(self, model, sensor_data):
        """Return the descriptive text for the battery state of a given sensor.

        Different sensor models report different battery state
        data, eg binary (0|1), integer or battery volts. Each of these
        different battery states is interpreted differently when determining
        whether the battery state is normal or low.

        This method determines the descriptive state for a sensor given the
        battery state value and returns descriptive text for the battery state.
        If a descriptive battery state cannot be determined (eg an unknown
        sensor or battery state data is invalid) the value None is returned.
        """

        try:
            if model in self.no_low:
                # we have a sensor for which no low battery cut-off data exists
                return "--"
            elif model in self.batt_binary:
                if sensor_data['battery'] == 0:
                    # battery is OK
                    return "OK"
                elif sensor_data['battery'] == 1:
                    # battery is low
                    return "low"
                else:
                    # we do not know how to interpret binary battery state data
                    # that is not 0 or 1, we have battery state data from a
                    # known sensor so return 'unknown'
                    return '--'
            elif model in self.batt_int:
                if sensor_data['battery'] == None:
                    # no valid data
                    return "--"
                elif sensor_data['battery'] <= 1:
                    # 0 or 1 is considered low
                    return "low"
                elif sensor_data['battery'] == 6:
                    # 6 means we are on DC power
                    return "DC"
                elif sensor_data['battery'] <= 5:
                    # 2, 3, 4 or 5 is OK
                    return "OK"
                elif sensor_data['battery'] == 9:
                    # 9 sometimes appears for sensors that do not exist but
                    # are included in API responses, we likely will not see
                    # any but if we do return 'unknown'
                    return '--'
                else:
                    # we do not know how to interpret integer battery state data
                    # that is not 0 to 6 or 9, we have battery state data from a
                    # known sensor so return 'unknown'
                    return '--'
            elif model in self.batt_volt:
                if 'voltage' in sensor_data.keys():
                    # 1.2V or less is considered low
                    if sensor_data['voltage'] <= 1.2:
                        return "low"
                    # greater than 1.2V is considered OK
                    else:
                        return "OK"
                elif sensor_data['battery'] <= 1:
                    # 0 or 1 is considered low
                    return "low"
                elif sensor_data['battery'] <= 5:
                    # 2, 3, 4 or 5 is OK
                    return "OK"
                else:
                    # we do not know how to interpret integer battery state data
                    # that is not 0 to 6 or 9, we have battery state data from a
                    # known sensor so return 'unknown'
                    return '--'
            else:
                return "Unknown sensor"
        except KeyError as e:
            raise


# ============================================================================
#                             class EcowittDevice
# ============================================================================

class EcowittDevice:
    """Class to obtain and parse data from an Ecowitt device.

    Some Ecowitt consoles (including gateway devices) can be interrogated
    directly via one or both of the following APIs:
    1. the legacy Ecowitt LAN/Wi-Fi Gateway API
    2. the Ecowitt local HTTP API

    The Ecowitt HTTP driver predominantly uses the Ecowitt local HTTP API to
    obtain observation and metadata from the Ecowitt device. The Ecowitt HTTP
    driver also has the ability to use limited portions of the legacy Ecowitt
    LAN/Wi-Fi Gateway API with compatible gateway devices to obtain additional
    metadata not available via the local HTTP API.

    These APIs use a library of commands for reading and setting various
    parameters in the device. The WeeWX Ecowitt HTTP driver uses a small subset
    of these commands to obtain sensor data which is presented to WeeWX via
    loop packets emitted by the driver.

    The local HTTP API uses HTTP GET requests and involves the decoding/parsing
    of JSON format message data. The legacy Ecowitt LAN/Wi-Fi Gateway API uses
    socket based requests and involves exchange of data that must be
    encoded/decoded at the byte/bit level.

    An EcowittDevice object uses the following classes for interacting with the
    device:

    - class EcowittHttpApi. Communicates directly with the device via the
                            device local HTTP API and obtains and validates
                            device responses.
    - class EcowittHttpParser. Parses local HTTP API responses from Ecowitt
                               devices and returns data suitable for passing to
                               a WeeWX driver/service.
    """

    # list of dicts of weather services that I know about
    services = [{'name': 'ecowitt_net_params',
                 'long_name': 'Ecowitt.net'
                 },
                {'name': 'wunderground_params',
                 'long_name': 'Wunderground'
                 },
                {'name': 'weathercloud_params',
                 'long_name': 'Weathercloud'
                 },
                {'name': 'wow_params',
                 'long_name': 'Weather Observations Website'
                 },
                {'name': 'custom_params',
                 'long_name': 'Customized'
                 }
                ]
    # lookup for the type of battery state data provided for each sensor type
    sensor_battery_type = {'wh25': 'binary', 'wh26': 'binary',
                           'wn31': 'binary', 'wn34': 'integer',
                           'wn35': 'integer', 'wh40': 'integer', 'wn20': 'integer',
                           'wh41': 'integer', 'wh45': 'integer',
                           'wh51': 'integer', 'wh55': 'integer',
                           'wh57': 'integer', 'wh65': 'binary',
                           'wh68': 'binary', 'wh69': 'binary', 'ws80': 'integer',
                           'ws85': 'integer', 'ws90': 'integer'}
    # Ecowitt device units to WeeWX unit group/name lookup
    unit_code_to_string = {'temperature': {'group': 'group_temperature',
                                           'unit': {0: 'degree_C',
                                                    1: 'degree_F'}
                                           },
                           'pressure': {'group': 'group_pressure',
                                        'unit': {0: 'hPa',
                                                 1: 'inHg',
                                                 2: 'mmHg'}
                                        },
                           'wind': {'group': 'group_speed',
                                    'unit': {0: 'meter_per_second',
                                             1: 'km_per_hour',
                                             2: 'mile_per_hour',
                                             3: 'knot'}
                                    },
                           'rain': {'group': 'group_rain',
                                    'unit': {0: 'mm',
                                             1: 'inch'}
                                    },
                           'light': {'group': 'group_illuminance',
                                     'unit': {0: 'klux',
                                              1: 'watt_per_meter_squared',
                                              2: 'kfc'}
                                     },
                           'deltat': {'group': 'group_deltat',
                                      'unit': {0: 'degree_C2',
                                               1: 'degree_F2'}
                                      },
                           'rain_rate': {'group': 'group_rainrate',
                                         'unit': {0: 'mm_per_hour',
                                                  1: 'inch_per_hour'}
                                         },
                           'depth': {'group': 'group_depth',
                                     'unit': {0: 'mm2',
                                              1: 'foot2'}
                                    },
                           'altitude': {'group': 'group_altitude',
                                        'unit': {0: 'meter',
                                                 1: 'foot'}
                                       }
                           }
    # tuple of lowercase sensor models known to have user updatable firmware
    sensors_with_firmware = ('ws80', 'ws85', 'ws90')

    def __init__(self, ip_address,
                 unit_system=DEFAULT_UNIT_SYSTEM,
                 max_tries=DEFAULT_MAX_TRIES,
                 retry_wait=DEFAULT_RETRY_WAIT,
                 url_timeout=DEFAULT_URL_TIMEOUT,
                 show_battery=DEFAULT_FILTER_BATTERY,
                 log_unknown_fields=False,
                 debug=DebugOptions()):
        """Initialise an EcowittDevice object."""

        # dow we have a non-None IP address, we cannot continue unless we have
        # an IP address
        if ip_address is None:
            raise weewx.ViolatedPrecondition('device IP address cannot be None')
        # get an EcowittHttpApi object to handle the interaction with the device
        # via the local HTTP API
        self.api = EcowittHttpApi(ip_address=ip_address,
                                  max_tries=max_tries,
                                  retry_wait=retry_wait,
                                  timeout=url_timeout)
        # get an EcowittHttpParser object to parse any local HTTP API responses
        self.parser = EcowittHttpParser(unit_system=unit_system,
                                        show_battery=show_battery,
                                        log_unknown_fields=log_unknown_fields,
                                        debug=debug)
        # get an EcowittSensors object to handle the specialised processing of
        # sensor metadata
        self.sensors = EcowittSensors()
        # start off logging failures
        self.log_failures = True

    def get_live_data(self, flatten_data=True):
        """Return live sensor observation data.

        Obtain live sensor data via the API. The live sensor data is parsed and
        optionally flattened. Returns a dict containing the parsed data.

        Raises a DeviceIOError exception if the device could not be contacted.
        Raises a ParseError exception if there was no sensor metadata to parse.
        """

        live_data = self.api.get_livedata_info()
        return self.parser.parse_get_livedata_info(live_data,
                                                   flatten_data=flatten_data)

    def get_sensors_data(self, connected_only=DEFAULT_ONLY_REGISTERED_SENSORS, flatten_data=True):
        """Return sensor metadata.

        Obtain live sensor metadata via the API. The sensor metadata is parsed
        and optionally flattened. Returns a dict containing the parsed data.

        Raises a DeviceIOError exception if the device could not be contacted.
        Raises a ParseError exception if there was no sensor metadata to parse.
        """

        sensors_data = self.api.get_sensors_info()
        return self.parser.parse_get_sensors_info(sensors_data,
                                                  connected_only=connected_only,
                                                  flatten_data=flatten_data)

    def get_rain_totals(self):
        """Return traditional rainfall aggregate and setting data.

        Obtain traditional rainfall aggregate, gain and reset data via the API.
        The data is parsed and returned as a dict.

        Raises a DeviceIOError exception if the device could not be contacted.
        Raises a ParseError exception if the raw device response is not a dict.
        """

        rain_data = self.api.get_rain_totals()
        _unit_data = self.get_device_units()
        return self.parser.parse_get_rain_totals(rain_data,
                                                 device_units=_unit_data)

    def get_rain_totalspart(self):
        """Return traditional rainfall aggregate and setting data.

        Obtain traditional rainfall aggregate, gain and reset data via the API.
        The data is parsed and returned as a dict.

        Raises a DeviceIOError exception if the device could not be contacted.
        Raises a ParseError exception if the raw device response is not a dict.
        """

        rain_data = self.api.get_rain_totals()
        _unit_data = self.get_device_units()
        return self.parser.parse_get_rain_totalspart(rain_data,
                                                 device_units=_unit_data)

    def get_piezo_rain_data(self):
        """Return piezo rainfall aggregate and gain data.

        Obtain piezo rainfall aggregate and gain data via the API. The data is
        parsed and returned as a dict.

        Raises a DeviceIOError exception if the device could not be contacted.
        Raises a ParseError exception if the raw device response is not a dict.
        """

        rain_data = self.api.get_piezo_rain()
        _unit_data = self.get_device_units()
        return self.parser.parse_get_piezo_rain(rain_data, _unit_data)

    def get_piezo_rain_datapart(self):
        """Return piezo rainfall aggregate and gain data.

        Obtain piezo rainfall aggregate and gain data via the API. The data is
        parsed and returned as a dict.

        Raises a DeviceIOError exception if the device could not be contacted.
        Raises a ParseError exception if the raw device response is not a dict.
        """

        rain_data = self.api.get_piezo_rain()
        _unit_data = self.get_device_units()
        return self.parser.parse_get_piezo_rainpart(rain_data, _unit_data)

    def get_wn34_offset_data(self):
        """Return offset data for connected WN34 sensors.

        Obtain WN34 offset data via the API. The data is
        parsed and returned as a list of dicts in ascending channel number
        order.

        Raises a DeviceIOError exception if the device could not be contacted.
        Raises a ParseError exception if device unit information is not
        available or if temperature data not included in the raw device
        response.
        """

        offset_data = self.api.get_cli_wh34()
        _unit_data = self.get_device_units()
        return self.parser.parse_get_cli_wh34(offset_data,
                                              device_units=_unit_data)

    def get_pm25_offset_data(self):
        """Return PM2.5 offset data for connected WH41/WH43 sensors..

        Obtain WH41/WH43 PM2.5 offset data via the API. The data is parsed and
        returned as a list of dicts in ascending channel number order.

        Raises a DeviceIOError exception if the device could not be contacted.
        Raises a ParseError exception if device unit information is not
        available or if temperature data not included in the raw device
        response.
        """

        offset_data = self.api.get_cli_pm25()
        _unit_data = self.get_device_units()
        return self.parser.parse_get_cli_pm25(offset_data,
                                              device_units=_unit_data)

    def get_co2_offset_data(self):
        """Return offset data for the WH45 sensor.

        Obtain WH45 offset data via the API. The data is parsed and
        returned as a dict.

        Raises a DeviceIOError exception if the device could not be contacted.
        Raises a ParseError exception if the raw device response is not a dict.
        """

        offset_data = self.api.get_cli_co2()
        _unit_data = self.get_device_units()
        return self.parser.parse_get_cli_co2(offset_data,
                                             device_units=_unit_data)

    def get_lds_offset_data(self):
        """Return offset data for the WH54 sensor.

        Obtain WH54 offset data via the API. The data is parsed and returned as
        a dict.

        Raises a DeviceIOError exception if the device could not be contacted.
        Raises a ParseError exception if the raw device response is not a dict.
        """

        offset_data = self.api.get_cli_lds()
        return self.parser.parse_get_cli_lds(offset_data)

    def get_calibration_data(self):
        """Get device calibration data."""

        cal_data = self.api.get_calibration_data()
        _unit_data = self.get_device_units()
        return self.parser.parse_get_calibration_data(cal_data,
                                                      device_units=_unit_data)

    def get_multich_calibration_data(self):
        """Get multi-channel temperature-humidity calibration data."""

        cal_data = self.api.get_cli_multi_ch()
        _unit_data = self.get_device_units()
        return self.parser.parse_get_cli_multich(cal_data,
                                                 device_units=_unit_data)

    def get_soil_calibration_data(self):
        """Get soil moisture calibration data."""

        cal_data = self.api.get_cli_soilad()
        return self.parser.parse_get_cli_soilad(cal_data)

    def get_device_info_data(self):
        """Get device info data."""

        device_info_data = self.api.get_device_info()
        return self.parser.parse_get_device_info(device_info_data)

    def get_device_info_datapart(self):
        """Get device info data."""

        device_info_data = self.api.get_device_info()
        return self.parser.parse_get_device_infopart(device_info_data)

    def get_ws_settings(self):
        """Get weather services settings."""

        ws_settings = self.api.get_ws_settings()
        return self.parser.parse_get_ws_settings(ws_settings)

    def get_sdmmc_info_data(self):
        """Get SD card info data."""

        sd_info = self.api.get_sdmmc_info()
        return self.parser.parse_get_sdmmc_info(sd_info)

    def get_device_units(self):
        """Obtain details of units used by device API calls.

        Unlike the so called Ecowitt telnet API where response units were
        fixed, the Ecowitt local HTTP API responses use units based on the
        device units settings set by the user. These unit settings are normally
        made via the WS View+ app or the local device web page.

        The majority of Ecowitt HTTP API responses identify units for variable
        unit data by including a unit string either appended to the value
        concerned (eg '16mm') or in another field, often named 'units'
        (eg 'units': 'mm'). However, at time of release at least one HTTP API
        response (response to 'get_cli_wh34') does not include any unit
        information meaning it is not possible to determine the units used for
        some data values. To properly parse such responses unit information is
        obtained via the HTTP API command 'get_units_info'.

        This method obtains the device units information via the
        'get_units_info' API command. The raw response is parsed and then
        translated via look-up table to provide a dict containing WeeWX unit
        names for each group of observation types. If a unit cannot be
        determined the value None is used. Not all WeeWX unit names are
        supported, the only WeeWX unit names supported are those that are also
        supported by the Ecowitt HTTP API.

        Returns a dict keyed as follows:

        temperature: WeeWX temperature unit being used, 'degree_C' or
                     'degree_F'. String, may be None.
        pressure:    WeeWX pressure unit being used, 'hPa', 'inHg' or 'mmHg'.
                     String, may be None.
        wind:        WeeWX speed unit being used, 'meter_per_second',
                     'km_per_hour', 'mile_per_hour' or 'knot'. String, may be
                     None.
        rain:        WeeWX rain unit being used, 'mm' or 'inch'. String, may be
                     None.
        light:       WeeWX light unit being used, 'lux',
                     'watt_per_meter_squared' or 'foot_candle'. String, may be
                     None.
        """

        # obtain the raw device units data via the API
        _units_resp = self.api.get_units_info()
        # parse the raw device units data
        _parsed_units = self.parser.parse_get_units_info(_units_resp)
        device_units = {'group_percent': 'percent',
                        'group_direction': 'degree_compass',
                        'group_uv': 'uv_index',
                        'group_fraction': 'ppm',
                        'group_concentration': 'microgram_per_meter_cubed'}
        for ecowitt_group, ecowitt_unit in _parsed_units.items():
            try:
                _lookup = self.unit_code_to_string[ecowitt_group]
            except KeyError as e:
                continue
            unit_group = _lookup['group']
            try:
                _unit = _lookup['unit'][ecowitt_unit]
            except KeyError:
                # we do not have an Ecowitt unit for this Ecowitt unit code,
                # skip this unit
                continue
            device_units[unit_group] = _unit
        # add in implied derived units
        # rain rate, depth and altitude derived from and implied by rain
        if 'group_rain' in device_units.keys():
            _lookup = self.unit_code_to_string['rain']
            device_units['group_rainrate'] = _lookup['unit'][_parsed_units['rain']]
            _lookup = self.unit_code_to_string['depth']
            device_units['group_depth'] = _lookup['unit'][_parsed_units['rain']]
            _lookup = self.unit_code_to_string['altitude']
            device_units['group_altitude'] = _lookup['unit'][_parsed_units['rain']]
        # delta temperature derived from and implied by temperature
        if 'group_temperature' in device_units.keys():
            _lookup = self.unit_code_to_string['deltat']
            device_units['group_deltat'] = _lookup['unit'][_parsed_units['temperature']]
        return device_units

    @property
    def ip_address(self):
        """The device IP address."""

        return self.api.ip_address

    @property
    def model(self):
        """Device model."""

        version_data = self.api.get_version()
        version = self.parser.parse_get_version(version_data).get('version')
        #return self.parser.get_model_from_firmware(version)
        ergebnis = version[8:]
        #log.info("Hardware is %s" % (ergebnis))
        return ergebnis

    @property
    def mac_address(self):
        """Device MAC address."""

        network_data = self.api.get_network_info()
        return self.parser.parse_get_network_info(network_data).get('mac')

    @property
    def firmware_version(self):
        """Device firmware version."""

        version_data = self.api.get_version()
        return self.parser.parse_get_version(version_data).get('firmware_version')

    @property
    def firmware_update_avail(self):
        """Whether a device firmware update is available or not.

        Return True if a device firmware update is available, False if there is
        no available firmware update or None if firmware update availability
        cannot be determined.
        """

        # get firmware version info
        version = self.api.get_version()
        # do we have current firmware version info and availability of a new
        # firmware version ?
        if version is not None and 'newVersion' in version:
            # we can now determine with certainty whether there is a new
            # firmware update or not
            return version['newVersion'] == '1'
        # we cannot determine the availability of a firmware update so return
        # None
        return None

    @property
    def firmware_update_message(self):
        """The device firmware update message.

        Returns the 'curr_msg' field in the 'get_device_info' response in the
        device HTTP API. This field is usually used for firmware update release
        notes.

        Returns a string containing the 'curr_msg' field contents of the
        'get_device_info' response. Return None if the 'get_device_info'
        response could not be obtained or the 'curr_msg' field was not included
        in the 'get_device_info' response.
        """

        # get device info
        device_info = self.api.get_device_info()
        # return the 'curr_msg' field contents or None
        return device_info.get('curr_msg') if device_info is not None else None

    @property
    def sensor_firmware_versions(self):
        """Obtain sensor firmware versions.

        Return a dict, keyed by uppercase sensor version, of the installed
        firmware version for attached sensors that have a user updatable
        firmware. If the firmware version for an attached sensor with updatable
        firmware cannot be obtained, the string 'not available' is returned for
        that sensor. If no attached sensors have user updatable firmware an
        empty dict is returned.
        """

        # first obtain the sensors data
        sensors_data = self.get_sensors_data()
        # initialise a dict to hold the results
        fw_data = dict()
        # iterate over the sensor models with user updatable firmware
        for sensor in self.sensors_with_firmware:
            # obtain the sensor battery state so we can easily discard sensors
            # that do not exist
            sensor_battery = sensors_data.get('.'.join([sensor, 'battery']))
            # if the sensor battery state is 9 the sensor does not exist (the
            # HTTP API returns placeholders for all sensors including those
            # that do not exist, those that don't exist have battery == 9)
            if sensor_battery is not None and sensor_battery != 9:
                # obtain the sensor firmware version and save it to our dict
                fw_data[sensor.upper()] = sensors_data.get('.'.join([sensor, 'version']),
                                                           'not available')
        # return the results dict
        return fw_data

    @property
    def paired_rain_gauges(self):
        """Obtain paired rain gauge types.

        Returns a tuple containing the types of paired rain gauges. An Ecowitt
        device may be paired with either a tipping rain gauge, a piezoelectric
        (piezo) rain gauge, both tipping and piezo rain gauges or no rain
        gauge. A rain gauge is considered paired if the gauge is included in a
        'get_sensors_info' response and the ID key/value is not
        disabled ('FFFFFFFE') or not 'is registering' ('FFFFFFFF').

        Known rain gauge models and their type are:

            WH40: tipping gauge
            WH69: tipping gauge
            WS85: piezo gauge
            WS90: piezo gauge

        Returns a tuple. Possible responses are:

            ()                  - no rain gauges are attached
            ('tipping',)        - a tipping gauge only is attached
            ('piezo',)          - a piezo gauge only is attached
            ('tipping', 'piezo) - both a tipping and piezo gauge is attached
        """

        # initialise a set to hold our result, we will convert to a tuple later
        result = set()
        # obtain the parse 'get_sensors_info' response
        sensor_info = self.get_sensors_data(connected_only=True,
                                            flatten_data=False)
        # do we have a tipping gauge
        if 'wh69' in sensor_info.keys() or 'wh40' in sensor_info.keys():
            result.add('tipping')
        # do we have a piezo gauge
        if 'ws85' in sensor_info.keys() or 'ws90' in sensor_info.keys():
            result.add('piezo')
        # return the result as a tuple
        return tuple(result)


# ============================================================================
#                             Utility functions
# ============================================================================

def define_units():
    """Define formats and conversions used by the driver.

    This could be done in user/extensions.py or the driver. The
    user/extensions.py approach will make the conversions and formats available
    for all drivers and services, but requires manual editing of the file by
    the user. Inclusion in the driver removes the need for the user to edit
    user/extensions.py, but means the conversions and formats are only defined
    when the driver is being used. Given the specialised nature of the
    conversions and formats the latter is an acceptable approach. In any case,
    there is nothing preventing the user manually adding these entries to
    user/extensions.py.

    As of v5.0.0 WeeWX defines the unit group 'group_data' with member units
    'byte' and 'bit'. We will define additional group_data member units of
    'kilobyte' and 'megabyte'.

    All additions to the core conversion, label and format dicts are done in a
    way that do not overwrite and previous customisations the user may have
    made through another driver or user/extensions.py.
    """

    # create group for depth
    weewx.units.USUnits['group_depth'] = 'foot2'
    weewx.units.MetricUnits['group_depth'] = 'mm2'
    weewx.units.MetricWXUnits['group_depth'] = 'mm2'


    weewx.units.obs_group_dict['vpd'] = 'group_pressurevpd'
    weewx.units.USUnits["group_pressurevpd"] = "inHg"
    weewx.units.MetricUnits["group_pressurevpd"] = "hPa"
    weewx.units.MetricWXUnits["group_pressurevpd"] = "hPa"

    # set default formats and labels for depth
    weewx.units.default_unit_format_dict['foot2'] = '%.2f'
    weewx.units.default_unit_label_dict['foot2'] = ' ft'
    weewx.units.default_unit_format_dict['mm2'] = '%.0f'
    weewx.units.default_unit_label_dict['mm2'] = ' mm'
    weewx.units.default_unit_format_dict['microgram_per_meter_cubed'] = '%.1f'

    # define conversion functions for depth
    weewx.units.conversionDict['mm2'] = {'inch2': lambda x: x / 25.4,
                                         'foot2': lambda x: x / 304.8,
                                         'cm2': lambda x: x / 10.0,
                                         'meter2': lambda x: x / 1000.0}
    weewx.units.conversionDict['cm2'] = {'inch2': lambda x: x / 2.54,
                                         'foot2': lambda x: x / 30.48,
                                         'mm2': lambda x: x * 10.0,
                                         'meter2': lambda x: x / 100.0}
    weewx.units.conversionDict['m2'] = {'inch2': lambda x: x / 0.0254,
                                        'foot2': lambda x: x / 0.3048,
                                        'mm2': lambda x: x * 1000.0,
                                        'cm2': lambda x: x * 100.0}
    weewx.units.conversionDict['inch2'] = {'foot2': lambda x: x / 12.0,
                                           'mm2': lambda x: x * 25.4,
                                           'cm2': lambda x: x * 2.54,
                                           'meter2': lambda x: x * 0.0254}
    weewx.units.conversionDict['foot2'] = {'inch2': lambda x: x * 12.0,
                                           'mm2': lambda x: x * 304.8,
                                           'cm2': lambda x: x * 30.48,
                                           'meter2': lambda x: x * 0.3048}

    # add 'nautical_mile' conversions
    if 'nautical_mile' not in weewx.units.conversionDict:
        # 'nautical_mile' is not a key in the conversion dict, so we add all
        # conversions
        weewx.units.conversionDict['nautical_mile'] = {'meter': lambda x: x * 1852.0,
                                                       'km': lambda x: x * 1.852,
                                                       'mile': lambda x: x * 1.151}
    else:
        # 'nautical_mile' already exists as a key in the conversion dict, so we
        # add all conversions individually if they do not already exist
        if 'meter' not in weewx.units.conversionDict['nautical_mile'].keys():
            weewx.units.conversionDict['nautical_mile']['meter'] = lambda x: x * 1852.0
        if 'km' not in weewx.units.conversionDict['nautical_mile'].keys():
            weewx.units.conversionDict['nautical_mile']['km'] = lambda x: x * 1.852
        if 'mile' not in weewx.units.conversionDict['nautical_mile'].keys():
            weewx.units.conversionDict['nautical_mile']['mile'] = lambda x: x * 1.151
    # The 'nautical_mile' entry in the conversion dict but the 'meter', 'km'
    # and 'mile' entries do not have a 'nautical_mile' entry. We need to add
    # them.
    if 'nautical_mile' not in weewx.units.conversionDict['meter'].keys():
        weewx.units.conversionDict['meter']['nautical_mile'] = lambda x: x / 1852.0
    if 'nautical_mile' not in weewx.units.conversionDict['km'].keys():
        weewx.units.conversionDict['km']['nautical_mile'] = lambda x: x / 1.852
    if 'nautical_mile' not in weewx.units.conversionDict['mile'].keys():
        weewx.units.conversionDict['mile']['nautical_mile'] = lambda x: x / 1.151

    # add 'knot' conversions
    if 'knot' not in weewx.units.conversionDict:
        # 'knot' is not a key in the conversion dict, so we add all conversions
        weewx.units.conversionDict['knot'] = {'meter_per_second': lambda x: x * 1852.0,
                                              'km_per_hour': lambda x: x * 1.852,
                                              'mile_per_hour': lambda x: x * 1.151}
    else:
        # 'knot' already exists as a key in the conversion dict, so we add all
        # conversions individually if they do not already exist
        if 'meter_per_second' not in weewx.units.conversionDict['knot'].keys():
            weewx.units.conversionDict['knot']['meter_per_second'] = lambda x: x * 1852.0
        if 'km_per_hour' not in weewx.units.conversionDict['knot'].keys():
            weewx.units.conversionDict['knot']['km_per_hour'] = lambda x: x * 1.852
        if 'mile_per_hour' not in weewx.units.conversionDict['knot'].keys():
            weewx.units.conversionDict['knot']['mile_per_hour'] = lambda x: x * 1.151
    # The 'knot' entry in the conversion dict but the 'meter_per_second',
    # 'km_per_hour' and 'mile_per_hour' entries do not have a 'nautical_mile'
    # entry. We need to add them.
    if 'knot' not in weewx.units.conversionDict['meter_per_second'].keys():
        weewx.units.conversionDict['meter_per_second']['knot'] = lambda x: x / 1852.0
    if 'knot' not in weewx.units.conversionDict['km_per_hour'].keys():
        weewx.units.conversionDict['km_per_hour']['knot'] = lambda x: x / 1.852
    if 'knot' not in weewx.units.conversionDict['mile'].keys():
        weewx.units.conversionDict['mile_per_hour']['knot'] = lambda x: x / 1.151

    # add kilobyte and megabyte conversions
    if 'byte' not in weewx.units.conversionDict:
        # 'byte' is not a key in the conversion dict, so we add all conversions
        weewx.units.conversionDict['byte'] = {'bit': lambda x: x * 8,
                                              'kilobyte': lambda x: x / 1024.0,
                                              'megabyte': lambda x: x / 1024.0 ** 2}
    else:
        # byte already exists as a key in the conversion dict, so we add all
        # conversions individually if they do not already exist
        if 'bit' not in weewx.units.conversionDict['byte'].keys():
            weewx.units.conversionDict['byte']['bit'] = lambda x: x * 8
        if 'kilobyte' not in weewx.units.conversionDict['byte'].keys():
            weewx.units.conversionDict['byte']['kilobyte'] = lambda x: x / 1024.0
        if 'megabyte' not in weewx.units.conversionDict['byte'].keys():
            weewx.units.conversionDict['byte']['megabyte'] = lambda x: x / 1024.0 ** 2
    if 'kilobyte' not in weewx.units.conversionDict:
        weewx.units.conversionDict['kilobyte'] = {'bit': lambda x: x * 8192,
                                                  'byte': lambda x: x * 1024,
                                                  'megabyte': lambda x: x / 1024.0}
    else:
        # kilobyte already exists as a key in the conversion dict, so we add
        # all conversions individually if they do not already exist
        if 'bit' not in weewx.units.conversionDict['kilobyte'].keys():
            weewx.units.conversionDict['kilobyte']['bit'] = lambda x: x * 8192
        if 'byte' not in weewx.units.conversionDict['kilobyte'].keys():
            weewx.units.conversionDict['kilobyte']['byte'] = lambda x: x * 1024
        if 'megabyte' not in weewx.units.conversionDict['kilobyte'].keys():
            weewx.units.conversionDict['kilobyte']['megabyte'] = lambda x: x / 1024.0
    if 'megabyte' not in weewx.units.conversionDict:
        weewx.units.conversionDict['megabyte'] = {'bit': lambda x: x * 8 * 1024 ** 2,
                                                  'byte': lambda x: x * 1024 ** 2,
                                                  'kilobyte': lambda x: x * 1024}
    else:
        # megabyte already exists as a key in the conversion dict, so we add
        # all conversions individually if they do not already exist
        if 'bit' not in weewx.units.conversionDict['megabyte'].keys():
            weewx.units.conversionDict['megabyte']['bit'] = lambda x: x * 8 * 1024 ** 2
        if 'byte' not in weewx.units.conversionDict['megabyte'].keys():
            weewx.units.conversionDict['megabyte']['byte'] = lambda x: x * 1024 ** 2
        if 'kilobyte' not in weewx.units.conversionDict['megabyte'].keys():
            weewx.units.conversionDict['megabyte']['kilobyte'] = lambda x: x * 1024

    # add lux, klux, watt_per_meter_squared and kfc conversions
    if 'klux' not in weewx.units.conversionDict:
        # 'klux' is not a key in the conversion dict, so we add all conversions
        weewx.units.conversionDict['klux'] = {'lux': lambda x: x * 1000,
                                              'watt_per_meter_squared': lambda x: x * 1000 / 126.7,
                                              'kfc': lambda x: x * 10.76 / 0.1267 ** 2}
    else:
        # klux already exists as a key in the conversion dict, so we add all
        # conversions individually if they do not already exist
        if 'lux' not in weewx.units.conversionDict['klux'].keys():
            weewx.units.conversionDict['klux']['lux'] = lambda x: x * 1000
        if 'watt_per_meter_squared' not in weewx.units.conversionDict['klux'].keys():
            weewx.units.conversionDict['klux']['watt_per_meter_squared'] = lambda x: x * 1000 / 126.7
        if 'kfc' not in weewx.units.conversionDict['klux'].keys():
            weewx.units.conversionDict['klux']['kfc'] = lambda x: x * 10.76 / 0.1267 ** 2
    if 'lux' not in weewx.units.conversionDict:
        # 'lux' is not a key in the conversion dict, so we add all conversions
        weewx.units.conversionDict['lux'] = {'klux': lambda x: x / 1000.0,
                                             'watt_per_meter_squared': lambda x: x / 126.7,
                                             'kfc': lambda x: x * 0.01076 / 0.1267 ** 2}
    else:
        # lux already exists as a key in the conversion dict, so we add all
        # conversions individually if they do not already exist
        if 'klux' not in weewx.units.conversionDict['lux'].keys():
            weewx.units.conversionDict['lux']['klux'] = lambda x: x / 1000.0
        if 'watt_per_meter_squared' not in weewx.units.conversionDict['lux'].keys():
            weewx.units.conversionDict['lux']['watt_per_meter_squared'] = lambda x: x / 126.7
        if 'kfc' not in weewx.units.conversionDict['lux'].keys():
            weewx.units.conversionDict['lux']['kfc'] = lambda x: x * 0.01076 / 0.1267 ** 2
    if 'watt_per_meter_squared' not in weewx.units.conversionDict:
        # 'watt_per_meter_squared' is not a key in the conversion dict, so we add all conversions
        weewx.units.conversionDict['watt_per_meter_squared'] = {'klux': lambda x: x * 0.1267,
                                                                'lux': lambda x: x * 126.7,
                                                                'kfc': lambda x: x * 10.76 / 0.1267}
    else:
        # watt_per_meter_squared already exists as a key in the conversion
        # dict, so we add all conversions individually if they do not already
        # exist
        if 'klux' not in weewx.units.conversionDict['watt_per_meter_squared'].keys():
            weewx.units.conversionDict['watt_per_meter_squared']['klux'] = lambda x: x * 0.1267
        if 'lux' not in weewx.units.conversionDict['watt_per_meter_squared'].keys():
            weewx.units.conversionDict['watt_per_meter_squared']['lux'] = lambda x: x * 126.7
        if 'kfc' not in weewx.units.conversionDict['watt_per_meter_squared'].keys():
            weewx.units.conversionDict['watt_per_meter_squared']['kfc'] = lambda x: x * 10.76 / 0.1267
    if 'kfc' not in weewx.units.conversionDict:
        # 'kfc' is not a key in the conversion dict, so we add all conversions
        weewx.units.conversionDict['kfc'] = {'klux': lambda x: x * 0.1267 ** 2 / 10.76,
                                             'lux': lambda x: x * 126.7 ** 2 / 10.76,
                                             'watt_per_meter_squared': lambda x: x * 0.1267 / 10.76}
    else:
        # kfc already exists as a key in the conversion dict, so we add all
        # conversions individually if they do not already exist
        if 'klux' not in weewx.units.conversionDict['kfc'].keys():
            weewx.units.conversionDict['kfc']['klux'] = lambda x: x * 0.1267 ** 2 / 10.76
        if 'lux' not in weewx.units.conversionDict['kfc'].keys():
            weewx.units.conversionDict['kfc']['lux'] = lambda x: x * 126.7 ** 2 / 10.76
        if 'watt_per_meter_squared' not in weewx.units.conversionDict['kfc'].keys():
            weewx.units.conversionDict['kfc']['watt_per_meter_squared'] = lambda x: x * 0.1267 / 10.76

    # set default formats and labels for byte, kilobyte and megabyte, but only
    # if they do not already exist
    weewx.units.default_unit_format_dict['byte'] = weewx.units.default_unit_format_dict.get('byte') or '%.d'
    weewx.units.default_unit_label_dict['byte'] = weewx.units.default_unit_label_dict.get('byte') or ' B'
    weewx.units.default_unit_format_dict['kilobyte'] = weewx.units.default_unit_format_dict.get('kilobyte') or '%.3f'
    weewx.units.default_unit_label_dict['kilobyte'] = weewx.units.default_unit_label_dict.get('kilobyte') or ' kB'
    weewx.units.default_unit_format_dict['megabyte'] = weewx.units.default_unit_format_dict.get('megabyte') or '%.3f'
    weewx.units.default_unit_label_dict['megabyte'] = weewx.units.default_unit_label_dict.get('megabyte') or ' MB'

    # create group for delta temperatures
    weewx.units.USUnits['group_deltat'] = 'degree_F2'
    weewx.units.MetricUnits['group_deltat'] = 'degree_C2'
    weewx.units.MetricWXUnits['group_deltat'] = 'degree_C2'

    # set default formats and labels for depth
    weewx.units.default_unit_format_dict['degree_C2'] = '%.1f'
    weewx.units.default_unit_label_dict['degree_C2'] = '°C'
    weewx.units.default_unit_format_dict['degree_E2'] = '%.1f'
    weewx.units.default_unit_label_dict['degree_E2'] = '°C'
    weewx.units.default_unit_format_dict['degree_F2'] = '%.1f'
    weewx.units.default_unit_label_dict['degree_F2'] = '°F'
    weewx.units.default_unit_format_dict['degree_K2'] = '%.1f'
    weewx.units.default_unit_label_dict['degree_K2'] = '°C'

    # define conversion functions for deltat
    weewx.units.conversionDict['degree_C2'] = {'degree_F2': lambda x: x * 9 / 5,
                                               'degree_E2': lambda x: x * 7 / 5,
                                               'degree_K2': lambda x: x}
    weewx.units.conversionDict['degree_E2'] = {'degree_C2': lambda x: x * 5 / 7,
                                               'degree_F2': lambda x: x * 9 / 7,
                                               'degree_K2': lambda x: x * 5 / 7}
    weewx.units.conversionDict['degree_F2'] = {'degree_C2': lambda x: x * 5 / 9,
                                               'degree_E2': lambda x: x * 7 / 9,
                                               'degree_K2': lambda x: x * 5 / 9}
    weewx.units.conversionDict['degree_K2'] = {'degree_C2': lambda x: x,
                                               'degree_E2': lambda x: x * 7 / 5,
                                               'degree_F2': lambda x: x * 9 / 5}


def natural_sort_keys(source_dict):
    """Return a naturally sorted list of keys for a dict."""

    def atoi(text):
        return int(text) if text.isdigit() else text

    def natural_keys(text):
        """Natural key sort.

        Allows use of key=natural_keys to sort a list in human order, eg:
            alist.sort(key=natural_keys)

        https://nedbatchelder.com/blog/200712/human_sorting.html (See
        Toothy's implementation in the comments)
        """

        return [atoi(c) for c in re.split(r'(\d+)', text.lower())]

    # create a list of keys in the dict
    keys_list = list(source_dict.keys())
    # naturally sort the list of keys where, for example, xxxxx16 appears in the
    # correct order
    keys_list.sort(key=natural_keys)
    # return the sorted list
    return keys_list


def natural_sort_dict(source_dict):
    """Return a string representation of a dict sorted naturally by key.

    When represented as a string a dict is displayed in the format:
        {key a:value a, key b: value b ... key z: value z}
    but the order of the key:value pairs is unlikely to be alphabetical.
    Displaying dicts of key:value pairs in logs or on the console in
    alphabetical order by key assists in the analysis of the dict data.
    Where keys are strings with leading digits a natural sort is useful.
    """

    # first obtain a list of key:value pairs as string sorted naturally by key
    sorted_dict_fields = [f"'{k}': '{source_dict[k]}'" for k in natural_sort_keys(source_dict)]
    # return as a string of comma separated key:value pairs in braces
    return f'{{{", ".join(sorted_dict_fields)}}}'


def bytes_to_hex(iterable, separator=' ', caps=True):
    """Produce a hex string representation of a sequence of bytes."""

    # assume 'iterable' can be iterated by iterbytes and the individual
    # elements can be formatted with {:02X}
    format_str = "{:02X}" if caps else "{:02x}"
    try:
        return separator.join(format_str.format(c) for c in iterable)
    except ValueError:
        # most likely we are running python3 and iterable is not a bytestring,
        # try again coercing iterable to a bytestring
        return separator.join(format_str.format(c) for c in str.encode(iterable))
    except (TypeError, AttributeError):
        # TypeError - 'iterable' is not iterable
        # AttributeError - likely because separator is None
        # either way we can't represent as a string of hex bytes
        return f"cannot represent '{iterable}' as hexadecimal bytes"


def obfuscate(plain, obf_char='*'):
    """Obfuscate all but the last x characters in a string.

    Obfuscate all but (at most) the last four characters of a string. Always
    reveal no more than 50% of the characters. The obfuscation character
    defaults to '*' but can be set when the function is called.
    """

    if plain is not None and len(plain) > 0:
        # obtain the number of the characters to be retained
        stem = 4
        stem = 3 if len(plain) < 8 else stem
        stem = 2 if len(plain) < 6 else stem
        stem = 1 if len(plain) < 4 else stem
        stem = 0 if len(plain) < 3 else stem
        if stem > 0:
            # we are retaining some characters so do a little string
            # manipulation
            obfuscated = obf_char * (len(plain) - stem) + plain[-stem:]
        else:
            # we are obfuscating everything
            obfuscated = obf_char * len(plain)
        return obfuscated
    # if we received None or a zero length string then return it
    return plain


def flatten(dictionary, parent_key=False, separator='.'):
    """
    Turn a nested dictionary into a flattened dictionary
    :param dictionary: The dictionary to flatten
    :param parent_key: The string to prepend to dictionary's keys
    :param separator: The string used to separate flattened keys
    :return: A flattened dictionary
    """

    # do a check to ensure we have a dict
    if not hasattr(dictionary, 'keys'):
        # 'dictionary' is not a dict, return the value None
        return None
    else:
        items = []
        for key, value in dictionary.items():
            new_key = str(parent_key) + separator + key if parent_key else key
            if isinstance(value, MutableMapping):
                if not value.items():
                    items.append((new_key, None))
                else:
                    items.extend(flatten(value, new_key, separator).items())
            elif isinstance(value, list):
                if len(value):
                    for k, v in channelise_enumerate(value, channelise=True):
                        items.extend(flatten({str(k): v}, new_key, separator).items())
                else:
                    items.append((new_key,None))
            else:
                items.append((new_key, value))
        return dict(items)


def channelise_enumerate(iterable, start=0, channelise=False):
    """Specialised version of enumerate to yield channel/ID numbers.

    The Python enumerate function is a generator that emits tuples containing a
    count (from start which defaults to 0) and the values obtained from
    iterating over the argument. This specialised version of enumerate looks
    for a 'channel' key or 'id' key in each iterable element and if found uses
    this key value in place of the count used by the enumerate function. This
    facilitates processing of lists of non-consecutive channelised sensor data.

    If 'channelise' is True the function looks for (in order) key 'channel' or
    key 'id' in iterable element. If either key is found the corresponding key
    value is used in place of the incrementing count value in the emitted
    tuples. If both 'channel' and 'id' keys exist the 'channel' key value takes
    precedence over the 'id' key value.

    If 'channelise' is not set or set to False or iterable is not a dict, the
    function operates in a manner identical to the built-in function enumerate.
    """

    n = start
    for elem in iterable:
        i = None
        if channelise and 'channel' in elem:
            i = int(elem['channel'])
        elif channelise and 'id' in elem:
            i = int(elem['id'])
        p = i if i is not None else n
        yield p, elem
        n += 1


def calc_checksum(data):
    """Calculate the checksum for an API call or response.

    The checksum used in an API response is simply the LSB of the sum
    of the command, size and data bytes. The fixed header and checksum
    bytes are excluded.

    data: The data on which the checksum is to be calculated. Byte
          string.

    Returns the checksum as an integer.
    """

    # initialise the checksum to 0
    checksum = 0
    # iterate over each byte in the response
    for b in data:
        # add the byte to the running total
        checksum += b
    # we are only interested in the least significant byte
    return checksum % 256


# ============================================================================
#                         class DirectEcowittDevice
# ============================================================================

class DirectEcowittDevice:
    """Class to interact with Ecowitt HTTP driver when run directly.

    Would normally run a driver directly by calling from main() only, but when
    run directly the Ecowitt HTTP driver has many options so pushing the detail
    into its own class/object makes sense. Also simplifies some test suite
    routines/calls.

    Once created the process_options() method is called to process the
    respective command line options.
    """
    known_fields = ['rain.0x0D.val', 'rain.0x0D.voltage',
                    'rain.0x0E.val', 'rain.0x0E.voltage',
                    'rain.0x10.val', 'rain.0x10.voltage',
                    'rain.0x11.val', 'rain.0x11.voltage',
                    'rain.0x12.val', 'rain.0x12.voltage',
                    'rain.0x13.val', 'rain.0x13.voltage',
                    'rain.0x7C.val',
                    'piezoRain.srain_piezo.val',
                    'piezoRain.0x0D.val', 'piezoRain.0x0D.voltage',
                    'piezoRain.0x0E.val', 'piezoRain.0x0E.voltage',
                    'piezoRain.0x10.val', 'piezoRain.0x10.voltage',
                    'piezoRain.0x11.val', 'piezoRain.0x11.voltage',
                    'piezoRain.0x12.val', 'piezoRain.0x12.voltage',
                    'piezoRain.0x13.val', 'piezoRain.0x13.voltage',
                    'piezoRain.0x7C.val',
                    'wh25.intemp', 'wh25.inhumi', 'wh25.abs', 'wh25.rel',
                    'wh25.CO2', 'wh25.CO2_24H',
                    'common_list.0x02.val', 'common_list.0x02.voltage',
                    'common_list.0x03.val', 'common_list.0x03.voltage',
                    'common_list.0x07.val', 'common_list.0x07.voltage',
                    'common_list.0x0A.val', 'common_list.0x0A.voltage',
                    'common_list.0x0B.val', 'common_list.0x0B.voltage',
                    'common_list.0x0C.val', 'common_list.0x0C.voltage',
                    'common_list.0x19.val', 'common_list.0x19.voltage',
                    'common_list.0x15.val', 'common_list.0x15.voltage',
                    'common_list.0x16.val', 'common_list.0x16.voltage',
                    'common_list.0x17.val', 'common_list.0x17.voltage',
                    'common_list.0x6D.val',
                    'co2.temperature', 'co2.temp', 'co2.humidity', 'co2.CO2', 'co2.CO2_24H', 'co2.battery',
                    'co2.PM25', 'co2.PM25_RealAQI', 'co2.PM25_24HAQI', 'co2.PM25_24H',
                    'co2.PM10', 'co2.PM10_RealAQI', 'co2.PM10_24HAQI', 'co2.PM10_24H',
                    'co2.PM1', 'co2.PM1_RealAQI', 'co2.PM1_24HAQI', 'co2.PM1_24H',
                    'co2.PM4', 'co2.PM4_RealAQI', 'co2.PM4_24HAQI', 'co2.PM4_24H',
                    'lightning.distance', 'lightning.timestamp', 'lightning.count',
                    'ch_aisle.1.temp', 'ch_aisle.1.humidity', 'ch_aisle.2.temp', 'ch_aisle.2.humidity',
                    'ch_aisle.3.temp', 'ch_aisle.3.humidity', 'ch_aisle.4.temp', 'ch_aisle.4.humidity',
                    'ch_aisle.5.temp', 'ch_aisle.5.humidity', 'ch_aisle.6.temp', 'ch_aisle.6.humidity',
                    'ch_aisle.7.temp', 'ch_aisle.7.humidity', 'ch_aisle.8.temp', 'ch_aisle.8.humidity',
                    'ch_pm25.1.PM25', 'ch_pm25.1.PM25_24H', 'ch_pm25.1.PM25_RealAQI', 'ch_pm25.1.PM25_24HAQI',
                    'ch_pm25.2.PM25', 'ch_pm25.2.PM25_24H', 'ch_pm25.2.PM25_RealAQI', 'ch_pm25.2.PM25_24HAQI',
                    'ch_pm25.3.PM25', 'ch_pm25.3.PM25_24H', 'ch_pm25.3.PM25_RealAQI', 'ch_pm25.3.PM25_24HAQI',
                    'ch_pm25.4.PM25', 'ch_pm25.4.PM25_24H', 'ch_pm25.4.PM25_RealAQI', 'ch_pm25.4.PM25_24HAQI',
                    'ch_soil.1.humidity', 'ch_soil.1.voltage', 'ch_soil.2.humidity', 'ch_soil.2.voltage',
                    'ch_soil.3.humidity', 'ch_soil.3.voltage', 'ch_soil.4.humidity', 'ch_soil.4.voltage',
                    'ch_soil.5.humidity', 'ch_soil.5.voltage', 'ch_soil.6.humidity', 'ch_soil.6.voltage',
                    'ch_soil.7.humidity', 'ch_soil.7.voltage', 'ch_soil.8.humidity', 'ch_soil.8.voltage',
                    'ch_temp.1.temp', 'ch_temp.1.voltage', 'ch_temp.2.temp', 'ch_temp.2.voltage',
                    'ch_temp.3.temp', 'ch_temp.3.voltage', 'ch_temp.4.temp', 'ch_temp.4.voltage',
                    'ch_temp.5.temp', 'ch_temp.5.voltage', 'ch_temp.6.temp', 'ch_temp.6.voltage',
                    'ch_temp.7.temp', 'ch_temp.7.voltage', 'ch_temp.8.temp', 'ch_temp.8.voltage',
                    'ch_lds.1.air', 'ch_lds.1.depth', 'ch_lds.1.battery', 'ch_lds.1.voltage', 'ch_lds.1.total_height', 'ch_lds.1.total_heat',
                    'ch_lds.2.air', 'ch_lds.2.depth', 'ch_lds.2.battery', 'ch_lds.2.voltage', 'ch_lds.2.total_height', 'ch_lds.2.total_heat',
                    'ch_lds.3.air', 'ch_lds.3.depth', 'ch_lds.3.battery', 'ch_lds.3.voltage', 'ch_lds.3.total_height', 'ch_lds.3.total_heat',
                    'ch_lds.4.air', 'ch_lds.4.depth', 'ch_lds.4.battery', 'ch_lds.4.voltage', 'ch_lds.4.total_height', 'ch_lds.4.total_heat',
                    'ch_leak.1.status', 'ch_leak.1.voltage', 'ch_leak.2.status', 'ch_leak.2.voltage',
                    'ch_leak.3.status', 'ch_leak.3.voltage', 'ch_leak.4.status', 'ch_leak.4.voltage',
                    'debug.heap', 'debug.runtime', 'debug.is_cnip', 'debug.usr_interval',
                    'wh24.battery', 'wh24.signal', 'wh25.battery', 'wh25.signal', 'wh25.rssi',
                    'wh26.battery', 'wh26.signal', 'wh26.rssi',
                    'wn20.battery', 'wn20.signal', 'wn20.rssi',
                    'wn31.ch1.battery', 'wn31.ch1.signal', 'wn31.ch2.battery', 'wn31.ch2.signal', 'wn31.ch1.rssi', 'wn31.ch2.rssi',
                    'wn31.ch3.battery', 'wn31.ch3.signal', 'wn31.ch4.battery', 'wn31.ch4.signal', 'wn31.ch3.rssi', 'wn31.ch4.rssi',
                    'wn31.ch5.battery', 'wn31.ch5.signal', 'wn31.ch6.battery', 'wn31.ch6.signal', 'wn31.ch5.rssi', 'wn31.ch5.rssi',
                    'wn31.ch7.battery', 'wn31.ch7.signal', 'wn31.ch8.battery', 'wn31.ch8.signal', 'wn31.ch7.rssi', 'wn31.ch8.rssi',
                    'wn32.battery', 'wn32.signal', 'wn32.rssi',
                    'wn34.ch1.battery', 'wn34.ch1.signal', 'wn34.ch2.battery', 'wn34.ch2.signal', 'wn34.ch1.rssi', 'wn34.ch2.rssi',
                    'wn34.ch3.battery', 'wn34.ch3.signal', 'wn34.ch4.battery', 'wn34.ch4.signal', 'wn34.ch3.rssi', 'wn34.ch4.rssi',
                    'wn34.ch5.battery', 'wn34.ch5.signal', 'wn34.ch6.battery', 'wn34.ch6.signal', 'wn34.ch5.rssi', 'wn34.ch6.rssi',
                    'wn34.ch7.battery', 'wn34.ch7.signal', 'wn34.ch8.battery', 'wn34.ch8.signal', 'wn34.ch7.rssi', 'wn34.ch8.rssi',
                    'wn35.ch1.battery', 'wn35.ch1.signal', 'wn35.ch2.battery', 'wn35.ch2.signal', 'wn34.ch9.rssi', 'wn34.ch10.rssi',
                    'wn35.ch3.battery', 'wn35.ch3.signal', 'wn35.ch4.battery', 'wn35.ch4.signal', 'wn34.ch11.rssi', 'wn34.ch12.rssi',
                    'wn35.ch5.battery', 'wn35.ch5.signal', 'wn35.ch6.battery', 'wn35.ch6.signal', 'wn34.ch13.rssi', 'wn34.ch14.rssi',
                    'wn35.ch7.battery', 'wn35.ch7.signal', 'wn35.ch8.battery', 'wn35.ch8.signal', 'wn34.ch15.rssi', 'wn34.ch16.rssi',
                    'wh40.battery', 'wh40.signal', 'wh40.rssi',
                    'wh41.ch1.battery', 'wh41.ch1.signal', 'wh41.ch2.battery', 'wh41.ch2.signal', 'wh41.ch1.rssi', 'wh41.ch2.rssi',
                    'wh41.ch3.battery', 'wh41.ch3.signal', 'wh41.ch4.battery', 'wh41.ch4.signal', 'wh41.ch3.rssi', 'wh41.ch4.rssi',
                    'wh45.battery', 'wh45.signal', 'wh46.battery', 'wh46.signal', 'wh45.rssi', 'wh46.rssi',
                    'wh51.ch1.battery', 'wh51.ch1.signal', 'wh51.ch2.battery', 'wh51.ch2.signal', 'wh51.ch1.rssi', 'wh51.ch2.rssi',
                    'wh51.ch3.battery', 'wh51.ch3.signal', 'wh51.ch4.battery', 'wh51.ch4.signal', 'wh51.ch3.rssi', 'wh51.ch4.rssi',
                    'wh51.ch5.battery', 'wh51.ch5.signal', 'wh51.ch6.battery', 'wh51.ch6.signal', 'wh51.ch5.rssi', 'wh51.ch6.rssi',
                    'wh51.ch7.battery', 'wh51.ch7.signal', 'wh51.ch8.battery', 'wh51.ch8.signal', 'wh51.ch7.rssi', 'wh51.ch8.rssi',
                    'wh51.ch9.battery', 'wh51.ch9.signal', 'wh51.ch10.battery', 'wh51.ch10.signal', 'wh51.ch9.rssi', 'wh51.ch10.rssi',
                    'wh51.ch11.battery', 'wh51.ch11.signal', 'wh51.ch12.battery', 'wh51.ch12.signal', 'wh51.ch11.rssi', 'wh51.ch12.rssi',
                    'wh51.ch13.battery', 'wh53.ch11.signal', 'wh51.ch14.battery', 'wh51.ch14.signal', 'wh51.ch13.rssi', 'wh51.ch14.rssi',
                    'wh51.ch15.battery', 'wh51.ch15.signal', 'wh51.ch16.battery', 'wh51.ch16.signal', 'wh51.ch15.rssi', 'wh51.ch16.rssi',
                    'wh54.ch1.battery', 'wh54.ch1.signal', 'wh54.ch2.battery', 'wh54.ch2.signal', 'wh54.ch1.rssi', 'wh54.ch2.rssi',
                    'wh54.ch3.battery', 'wh54.ch3.signal', 'wh54.ch4.battery', 'wh54.ch4.signal', 'wh54.ch3.rssi', 'wh54.ch4.rssi',
                    'wh55.ch1.battery', 'wh55.ch1.signal', 'wh55.ch2.battery', 'wh55.ch2.signal', 'wh55.ch1.rssi', 'wh55.ch2.rssi',
                    'wh55.ch3.battery', 'wh55.ch3.signal', 'wh55.ch4.battery', 'wh55.ch4.signal', 'wh55.ch3.rssi', 'wh55.ch4.rssi',
                    'wh57.battery', 'wh57.signal', 'wh57.rssi',
                    'wh65.battery', 'wh65.signal', 'wh68.battery', 'wh68.signal', 'wh65.rssi', 'wh68.rssi',
                    'wh69.battery', 'wh69.signal', 'wh69.rssi',
                    'ws80.battery', 'ws80.signal', 'ws80.rssi',
                    'ws85.battery', 'ws85.signal', 'ws90.battery', 'ws90.signal', 'ws85.rssi', 'ws90.rssi'
                    ]

    sensor_display_order = ( 'wn20', 'wh25', 'wh26', 'wn31', 'wn34', 'wn35', 'wh40', 
                             'wh41', 'wh45', 'wh51', 'wh54', 'wh55', 'wh57',
                             'wh68', 'wh69', 'ws80', 'ws85', 'ws90')
    def __init__(self, namespace, arg_parser, stn_dict, **kwargs):
        """Initialise a DirectEcowittDevice object."""

        # save the argparse namespace
        self.namespace = namespace
        # save a reference to our argparse instance
        self.arg_parser = arg_parser
        # save the WeeWX station dict
        self.stn_dict = stn_dict
        # save the unit system we will use
        self.unit_system = DEFAULT_UNIT_SYSTEM
        # save discovery parameters
        self.discovery_port = kwargs.get('discovery_port',
                                         DEFAULT_DISCOVERY_PORT)
        self.discovery_period = kwargs.get('discovery_period',
                                           DEFAULT_DISCOVERY_PERIOD)
        self.discovery_timeout = kwargs.get('discovery_timeout',
                                            DEFAULT_DISCOVERY_TIMEOUT)

        # obtain the IP address to use
        self.ip_address = self.ip_from_config_opts()
        # do we filter battery state data
        self.show_battery, source = self.bool_from_config('show_battery',
                                                          DEFAULT_FILTER_BATTERY)
        # if weewx.debug is set display the battery filter state
        if weewx.debug >= 1:
            _state_str = 'disabled' if self.show_battery else 'enabled'
            if source == 'default':
                _src_str = 'using the default'
            elif source == 'station':
                _src_str = 'obtained from station config'
            elif source == 'command':
                _src_str = 'obtained from command line options'
            else:
                # we should never end up here but just in case...
                _src_str = 'unknown config source'
            print(f'Battery state filtering is {_state_str} ({_src_str})')
        # do we show registered sensor data only
        self.only_registered, source = self.bool_from_config('only_registered',
                                                             DEFAULT_ONLY_REGISTERED_SENSORS)
        # if weewx.debug is set display the registered sensor data filter state
        if weewx.debug >= 1:
            _state_str = 'disabled' if not self.only_registered else 'enabled'
            if source == 'default':
                _src_str = 'using the default'
            elif source == 'station':
                _src_str = 'obtained from station config'
            elif source == 'command':
                _src_str = 'obtained from command line options'
            else:
                # we should never end up here but just in case...
                _src_str = 'unknown config source'
            if self.only_registered:
                _reg_str = "Only registered sensors will be shown"
            else:
                _reg_str = "All sensors will be shown"
            print(f'{_reg_str} ({_src_str})')
        # set our debug level
        self.driver_debug = namespace.driver_debug

    def ip_from_config_opts(self):
        """Obtain the IP address from station config or command line options.

        Determine the IP address to use given a station config dict and command
        line options. The IP address is chosen in order as follows:
        - if specified the command line IP address is used
        - if a command line IP address was not specified the IP address is
          obtained from the station config dict
        - if the station config dict does not specify an IP address the value
          None is returned

        Returns a string or the value None.
        """

        # obtain an IP address from the command line options
        ip_address = self.namespace.ip_address if self.namespace.ip_address else None
        # if we didn't get an IP address check the station config dict
        if ip_address is None:
            # obtain the IP address from the station config dict
            ip_address = self.stn_dict.get('ip_address')
            # if the station config dict specifies some variation of 'auto'
            # then we need to return None to force device discovery
            if ip_address is not None:
                if weewx.debug >= 1:
                    print()
                    print('IP address obtained from station config')
            elif weewx.debug >= 1:
                print()
                print('IP address not specified')
        else:
            if weewx.debug >= 1:
                print()
                print('IP address obtained from command line options')
        return ip_address

    def bool_from_config(self, option, default):
        """Obtain a boolean option from the command line, station config or default.

        Determine an option value as follows:
        - if specified use the option from the command line
        - if the option was not specified on the command line obtain the option
          value from the station config dict
        - if the station config dict does not specify the option use the
          default value
        """

        # get the option value, default to None if the option does not exist
        _opt = getattr(self.namespace, option, None)
        # if the option exists and it is not None
        if _opt is not None:
            # try to coalesce a boolean value from the option
            try:
                _opt_bool = weeutil.weeutil.tobool(_opt)
            except ValueError:
                # we could not get the option from the command line
                pass
            else:
                # we have the option from the command line so use it
                return _opt_bool, 'command'
        # we couldn't get the option fromm the command line, now try the
        # station config
        try:
            _opt_bool = weeutil.weeutil.tobool(self.stn_dict.get(option))
        except ValueError:
            # we could not get the option from the station config
            pass
        else:
            # we have the option from the station config so use it
            return _opt_bool, 'station'
        # we could not get the option from the command line or station
        # config so use the default
        return default, 'default'

    def get_device(self):
        """Get an EcowittDevice object.

        Attempts to obtain an EcowittDevice object. If successful an
        EcowittDevice instance is returned, otherwise the value None is
        returned.
        """

        device = None
        # wrap in a try..except in case there is an error
        try:
            # get an EcowittDevice object
            device = EcowittDevice(ip_address=self.ip_address,
                                   max_tries=self.namespace.max_tries,
                                   retry_wait=self.namespace.retry_wait,
                                   url_timeout=self.namespace.timeout,
                                   unit_system=self.unit_system,
                                   debug=self.driver_debug)
        except weewx.ViolatedPrecondition as e:
            print()
            print(f'Unable to obtain EcowittDevice object: {e}')
        except DeviceIOError as e:
            # we encountered an IO error with the device, advise the user and
            # return None
            print()
            print(f'Unable to connect to device at {self.ip_address}: {e}')
        except socket.timeout:
            # we encountered a device timeout, advise the user and return None
            print()
            print(f'Timeout. Device at {self.ip_address} did not respond.')
        # return the object(or None)
        return device

    def process_options(self):
        """Call the appropriate method based on the optparse options."""

        # run the driver
        if hasattr(self.namespace, 'test_driver') and self.namespace.test_driver:
            self.test_driver()
        # run the service with simulator
        elif hasattr(self.namespace, 'test_service') and self.namespace.test_service:
            self.test_service()
        elif hasattr(self.namespace, 'weewx_fields') and self.namespace.weewx_fields:
            self.weewx_fields()
        elif hasattr(self.namespace, 'sys_params') and self.namespace.sys_params:
            self.display_system_params()
        elif hasattr(self.namespace, 'rain_totals') and self.namespace.rain_totals:
            self.display_rain_totals()
        elif hasattr(self.namespace, 'mulch_offset') and self.namespace.mulch_offset:
            self.display_mulch_offset()
        elif hasattr(self.namespace, 'temp_calibration') and self.namespace.temp_calibration:
            self.display_mulch_t_offset()
        elif hasattr(self.namespace, 'pm25_offset') and self.namespace.pm25_offset:
            self.display_pm25_offset()
        elif hasattr(self.namespace, 'co2_offset') and self.namespace.co2_offset:
            self.display_co2_offset()
        elif hasattr(self.namespace, 'lds_offset') and self.namespace.lds_offset:
            self.display_lds_offset()
        elif hasattr(self.namespace, 'calibration') and self.namespace.calibration:
            self.display_calibration()
        elif hasattr(self.namespace, 'soil_calibration') and self.namespace.soil_calibration:
            self.display_soil_calibration()
        elif hasattr(self.namespace, 'services') and self.namespace.services:
            self.display_services()
        elif hasattr(self.namespace, 'mac') and self.namespace.mac:
            self.display_mac()
        elif hasattr(self.namespace, 'firmware') and self.namespace.firmware:
            self.display_firmware()
        elif hasattr(self.namespace, 'sensors') and self.namespace.sensors:
            self.display_sensors()
        elif hasattr(self.namespace, 'live') and self.namespace.live:
            self.display_live_data()
        elif hasattr(self.namespace, 'discover') and self.namespace.discover:
            self.display_discovered_devices()
        elif hasattr(self.namespace, 'map'): #and self.field_map:
            self.display_field_map()
        elif hasattr(self.namespace, 'driver_map'): #and self.driver_map:
            self.display_driver_field_map()
        elif hasattr(self.namespace, 'service_map'): #and self.namespace.service_map:
            self.display_service_field_map()
        else:
            print()
            print('No option selected, nothing done')
            print()
            self.arg_parser.print_help()
            return

    def display_system_params(self):
        """Display system parameters.

        Obtain and display the device system parameters.
        """

        # dict for decoding system parameters frequency byte, at present all we
        # know is 0 = 433MHz
        freq_decode = {
            0: '433MHz',
            1: '868Mhz',
            2: '915MHz',
            3: '920MHz'
        }
        afc_decode = {
            0: 'off',
            1: 'on'
        }
        # as of GW3000 firmware v1.0.3/WS View+ v2.0.53 TZ auto decode is shown
        # as 'off' in WS View+ but the device HTTP API returns '1' for tz_auto
        tz_auto_decode = {
            0: 'on',
            1: 'off'
        }
        temp_comp_decode = dst_decode = afc_decode
        upgrade_decode = ap_auto_decode  = afc_decode
        sensor_decode = {0: 'WH24',
                         1: 'WH65'}
        # obtain an EcowittDevice object
        device = self.get_device()
        # if we have a device interrogate it and display the data
        if device is not None:
            # identify the device being used
            print()
            try:
                print(f'Interrogating {bcolors.BOLD}{device.model}{bcolors.ENDC} '
                      f'at {bcolors.BOLD}{device.ip_address}{bcolors.ENDC}')
                # get the device system parameters, wrap in a try..except to catch
                # any exceptions
                device_info = device.get_device_info_data()
            except DeviceIOError as e:
                print()
                print(f'Error obtaining a response from the device: {e}')
            except ParseError as e:
                print()
                print(f'Error parsing device response: {e}')
            except Exception as e:
                raise
            else:
                afc = device_info.get('afc')
                temp_comp = device_info.get('rad_comp')
                tz_auto = device_info.get('tz_auto')
                dst_status = device_info.get("dst")
                upgrade = device_info.get('upgrade')
                ap_auto = device_info.get('ap_auto')
                # create a meaningful string for frequency representation
                freq_str = freq_decode.get(device_info.get('rf_freq'), 'Unknown')
                # If the sensor_type field is 0 there is a WH24 connected, if it's
                # a 1 there is a WH65, if the sensor_type field is missing it's
                # unknown
                _type = device_info.get('sensor_type') if device_info.get('sensor_type') is not None else None
                _type_str = sensor_decode.get(_type) if sensor_decode.get(_type) is not None else 'unknown'
                # print the system parameters
                print()
                print(f'{"sensor type":>35}: {device_info.get("sensor_type")} ({_type_str})')
                print(f'{"frequency":>35}: {device_info.get("rf_freq")} ({freq_str})')
                if afc is not None:
                    print(f'{"automatic frequency control (AFC)":>35}: {afc} '
                          f'({afc_decode.get(afc, "unknown")})')
                else:
                    print(f'{"automatic frequency control (AFC)":>35}: unavailable')
                if temp_comp is not None:
                    print(f'{"temperature compensation":>35}: {temp_comp} '
                          f'({temp_comp_decode.get(temp_comp, "unknown")})')
                else:
                    print(f'{"temperature compensation":>35}: unavailable')
                if tz_auto is not None:
                    print(f'{"auto timezone":>35}: {tz_auto} '
                          f'({tz_auto_decode.get(tz_auto, "unknown")})')
                else:
                    print(f'{"auto timezone":>35}: unavailable')
                # do a little pre-processing of the tz name, sometimes the API
                # provides a zero length string as the tz name
                _tz_name = device_info.get("tz_name", "name not provided")
                tz_name = _tz_name if len(_tz_name) > 0 else "name not provided"
                print(f'{"timezone index":>35}: {device_info.get("tz_index")} ({tz_name})')
                print(f'{"DST status":>35}: {dst_status} '
                      f'({dst_decode.get(dst_status, "unknown")})')
                # The HTTP API returns 'date' as a date-time string, but it is
                # parsed to an epoch timestamp. Format the timestamp as a string.
                date_time_str = time.strftime("%-d %B %Y %H:%M:%S",
                                              time.localtime(device_info['date']))
                print(f'{"date-time":>35}: {date_time_str}')
                if upgrade is not None:
                    print(f'{"auto upgrade":>35}: {upgrade} '
                          f'({upgrade_decode.get(upgrade, "unknown")})')
                else:
                    print(f'{"auto upgrade":>35}: unavailable')
                if ap_auto is not None:
                    print(f'{"device AP auto off":>35}: {ap_auto} '
                          f'({ap_auto_decode.get(ap_auto, "unknown")})')
                else:
                    print(f'{"device AP auto off":>35}: unavailable')
                print(f'{"device AP SSID":>35}: {device_info.get("ap")}')

    def display_rain_totals(self):
        """Display the device rain gauge rain totals and rain settings.

        Obtain and display rainfall priority and traditional and piezo rain
        gauge totals and gains. The displayed data is obtained via the
        'get_rain_totals' and 'get_piezo_rain' HTTP API commands.
        """

        # obtain an EcowittDevice object
        device = self.get_device()
        # if we have a device interrogate it and display the data
        if device is not None:
            print()
            # wrap in a try..except in case there is an error
            try:
                # identify the device being used
                print(f'Interrogating {bcolors.BOLD}{device.model}{bcolors.ENDC} '
                      f'at {bcolors.BOLD}{device.ip_address}{bcolors.ENDC}')
                # get the rain totals data from the device
                rain_totals_data = device.get_rain_totals()
                # get the piezo rain data from the device
                rain_piezo_data = device.get_piezo_rain_data()
                # get the device units
                device_units = device.get_device_units()
            except weewx.ViolatedPrecondition as e:
                print()
                print(f'Unable to obtain EcowittDevice object: {e}')
            except DeviceIOError as e:
                print()
                print(f'Unable to connect to device at {self.ip_address}: {e}')
            except socket.timeout:
                print()
                print(f'Timeout. Device at {self.ip_address} did not respond.')
            else:
                # obtain a converter to do unit conversion, the unit system does
                # not matter
                c = weewx.units.StdUnitConverters[weewx.METRICWX]
                # now get a formatter, the default string formats and labels will
                # be fine
                f = weewx.units.Formatter(unit_format_dict=weewx.defaults.defaults['Units']['StringFormats'],
                                          unit_label_dict=weewx.defaults.defaults['Units']['Labels'])
                # set the display units/labels based on the device units
                gain_label = dict()
                if device_units.get('rain') == 'inch':
                    units = ('inch', 'mm')
                    gain_label[1] = '(< 0.16 in/hr / < 4 mm/hr)'
                    gain_label[2] = '(< 0.39 in/hr / < 10 mm/hr)'
                    gain_label[3] = '(< 1.18 in/hr / < 30 mm/hr)'
                    gain_label[4] = '(< 2.36 in/hr / < 60 mm/hr)'
                    gain_label[5] = '(> 2.36 in/hr / > 60 mm/hr)'
                else:
                    units = ('mm', 'inch')
                    gain_label[1] = '(< 4 mm/hr / < 0.16 in/hr)'
                    gain_label[2] = '(< 10 mm/hr / < 0.39 in/hr)'
                    gain_label[3] = '(< 30 mm/hr / < 1.18 in/hr)'
                    gain_label[4] = '(< 60 mm/hr / < 2.36 in/hr)'
                    gain_label[5] = '(> 60 mm/hr / > 2.36 in/hr)'
                # get priority rainfall data gauge name
                gauge_name = 'Unable to determine rainfall data priority'
                for gauge in rain_totals_data['rain_list']:
                    if gauge['value'] == rain_totals_data['rain_priority']:
                        gauge_name = gauge['gauge']
                print()
                print(f'Rainfall data priority: {gauge_name} ({rain_totals_data["rain_priority"]})')
                print()
                print(f'  Traditional gauge rain data:')
                _vh = weewx.units.ValueHelper(rain_totals_data['day_rain'], formatter=f, converter=c)
                print(f'{"Day rain":>15}: {_vh.convert(units[0]).toString()} ({_vh.convert(units[1]).toString()})')

                #_vh = weewx.units.ValueHelper(rain_totals_data['24h_rain'], formatter=f, converter=c)
                #print(f'{"24h rain":>15}: {_vh.convert(units[0]).toString()} ({_vh.convert(units[1]).toString()})')

                _vh = weewx.units.ValueHelper(rain_totals_data['week_rain'], formatter=f, converter=c)
                print(f'{"Week rain":>15}: {_vh.convert(units[0]).toString()} ({_vh.convert(units[1]).toString()})')
                _vh = weewx.units.ValueHelper(rain_totals_data['month_rain'], formatter=f, converter=c)
                print(f'{"Month rain":>15}: {_vh.convert(units[0]).toString()} ({_vh.convert(units[1]).toString()})')
                _vh = weewx.units.ValueHelper(rain_totals_data['year_rain'], formatter=f, converter=c)
                print(f'{"Year rain":>15}: {_vh.convert(units[0]).toString()} ({_vh.convert(units[1]).toString()})')
                _data = rain_totals_data.get('rain_gain')
                _data_str = f'{_data:.2f}' if _data is not None else '---'
                print(f'{"Rain gain":>15}: {_data_str}')
                print()
                print(f'  Piezo gauge rain data:')
                _vh = weewx.units.ValueHelper(rain_piezo_data['day_rain'], formatter=f, converter=c)
                print(f'{"Day rain":>15}: {_vh.convert(units[0]).toString()} ({_vh.convert(units[1]).toString()})')

                #_vh = weewx.units.ValueHelper(rain_piezo_data['24h_rain'], formatter=f, converter=c)
                #print(f'{"24h rain":>15}: {_vh.convert(units[0]).toString()} ({_vh.convert(units[1]).toString()})')

                _vh = weewx.units.ValueHelper(rain_piezo_data['week_rain'], formatter=f, converter=c)
                print(f'{"Week rain":>15}: {_vh.convert(units[0]).toString()} ({_vh.convert(units[1]).toString()})')
                _vh = weewx.units.ValueHelper(rain_piezo_data['month_rain'], formatter=f, converter=c)
                print(f'{"Month rain":>15}: {_vh.convert(units[0]).toString()} ({_vh.convert(units[1]).toString()})')
                _vh = weewx.units.ValueHelper(rain_piezo_data['year_rain'], formatter=f, converter=c)
                print(f'{"Year rain":>15}: {_vh.convert(units[0]).toString()} ({_vh.convert(units[1]).toString()})')
                for gain_channel in range(5):
                    gain_field = f"gain{gain_channel + 1:d}"
                    _data = rain_piezo_data.get(gain_field)
                    _data_str = f'{_data:.2f} {gain_label[gain_channel + 1]}' if _data is not None \
                        else f'-- {gain_label[gain_channel + 1]}'
                    _label_str = f'Rain{gain_channel + 1:d} gain'
                    print(f'{_label_str:>15}: {_data_str}')
                print()
                print(f'  Rainfall reset times:')
                _data = rain_totals_data.get('rain_reset_day')
                _data_str = f'{_data:02d}:00' if _data is not None else '-----'
                print(f'{"Daily rainfall reset time":>30}: {_data_str}')
                _data = rain_totals_data.get('rain_reset_week')
                _data_str = f'{calendar.day_name[(_data + 6) % 7]}' if _data is not None else '-----'
                print(f'{"Weekly rainfall reset":>30}: {_data_str}')
                _data = rain_totals_data.get('rain_reset_year')
                _data_str = f'{calendar.month_name[_data + 1]}' if _data is not None else '-----'
                print(f'{"Annual rainfall reset":>30}: {_data_str}')

    def display_mulch_offset(self):
        """Display device multichannel temperature and humidity offset data.

        Obtain and display the multichannel temperature and humidity offset
        data from the selected device.
        """

        # obtain an EcowittDevice object
        device = self.get_device()
        # if we have a device interrogate it and display the data
        if device is not None:
            print()
            # wrap in a try..except in case there is an error
            try:
                # identify the device being used
                print(f'Interrogating {bcolors.BOLD}{device.model}{bcolors.ENDC} '
                      f'at {bcolors.BOLD}{device.ip_address}{bcolors.ENDC}')
                # get the mulch offset data from the API
                mulch_offset_data = device.get_multich_calibration_data()
                # get the device units
                device_units = device.get_device_units()
            except weewx.ViolatedPrecondition as e:
                print()
                print(f'Unable to obtain EcowittDevice object: {e}')
            except DeviceIOError as e:
                print()
                print(f'Unable to connect to device at {self.ip_address}: {e}')
            except socket.timeout:
                print()
                print(f'Timeout. Device at {self.ip_address} did not respond.')
            else:
                # did we get any mulch offset data
                if mulch_offset_data is not None:
                    # obtain a converter to do unit conversion, the unit system does
                    # not matter
                    c = weewx.units.StdUnitConverters[weewx.METRICWX]
                    # now get a formatter, the default string formats and labels will
                    # be fine
                    f = weewx.units.Formatter(unit_format_dict=weewx.defaults.defaults['Units']['StringFormats'],
                                              unit_label_dict=weewx.defaults.defaults['Units']['Labels'])
                    # obtain the order of the units we will display for multi-unit
                    # offsets
                    if device_units['group_deltat'] == 'degree_F2':
                        dt_units = ['degree_F2', 'degree_C2']
                    else:
                        dt_units = ['degree_C2', 'degree_F2']
                    # now format and display the data
                    print()
                    print('Multi-channel Temperature and Humidity Calibration')
                    # do we have any results to display?
                    if len(mulch_offset_data) > 0:
                        # iterate over each channel for which we have data
                        for sensor in mulch_offset_data:
                            # print the channel and offset data
                            channel_str = f'{"Channel":>11} {sensor["channel"]:d}'
                            _vh = weewx.units.ValueHelper(sensor["temp"], formatter=f, converter=c)
                            print(f'{channel_str:>13}: {"Temperature offset":>18}: '
                                  f'{_vh.convert(dt_units[0]).toString()} '
                                  f'({_vh.convert(dt_units[1]).toString()})')
                            _vh = weewx.units.ValueHelper(sensor["humi"], formatter=f, converter=c)
                            print(f'{"":>13}  {"Humidity offset":>18}: {_vh.toString()}')
                    else:
                        # we have no results, so display a suitable message
                        print(f'{"No Multi-channel temperature and humidity sensors found":>59}')
                else:
                    print()
                    print(f'Device at {self.ip_address} did not respond.')

    def display_mulch_t_offset(self):
        """Display device multichannel temperature (WN34) offset data.

        Obtain and display the multichannel temperature (WN34) offset data from
        the selected device.
        """

        # obtain an EcowittDevice object
        device = self.get_device()
        # if we have a device interrogate it and display the data
        if device is not None:
            print()
            # wrap in a try..except in case there is an error
            try:
                # identify the device being used
                print(f'Interrogating {bcolors.BOLD}{device.model}{bcolors.ENDC} '
                      f'at {bcolors.BOLD}{device.ip_address}{bcolors.ENDC}')
                # get the mulch temp offset data via the API
                wn34_offset_data = device.get_wn34_offset_data()
                # get the device units
                device_units = device.get_device_units()
            except weewx.ViolatedPrecondition as e:
                print()
                print(f'Unable to obtain EcowittDevice object: {e}')
            except DeviceIOError as e:
                print()
                print(f'Unable to connect to device at {self.ip_address}: {e}')
            except socket.timeout:
                print()
                print(f'Timeout. Device at {self.ip_address} did not respond.')
            else:
                # did we get any mulch temp offset data
                if wn34_offset_data is not None:
                    # obtain a converter to do unit conversion, the unit system does
                    # not matter
                    c = weewx.units.StdUnitConverters[weewx.METRICWX]
                    # now get a formatter, the default string formats and labels will
                    # be fine
                    f = weewx.units.Formatter(unit_format_dict=weewx.defaults.defaults['Units']['StringFormats'],
                                              unit_label_dict=weewx.defaults.defaults['Units']['Labels'])
                    # obtain the order of the units we will display for multi-unit
                    # offsets
                    if device_units['group_deltat'] == 'degree_F2':
                        dt_units = ['degree_F2', 'degree_C2']
                    else:
                        dt_units = ['degree_C2', 'degree_F2']
                    print()
                    print('Multi-channel Temperature Calibration')
                    # do we have any results to display?
                    if len(wn34_offset_data) > 0:
                        # we have results, now format and display the data
                        # iterate over each channel for which we have data
                        for sensor in wn34_offset_data:
                            # Print the channel and offset data. The API returns
                            # channels starting at 0x63, but the WSView Plus app
                            # displays channels starting at 1, so subtract 0x62
                            # (or 98) from our channel number
                            channel_str = f'{"Channel":>11} {sensor["channel"]:d}'
                            _vh = weewx.units.ValueHelper(sensor['temp'], formatter=f, converter=c)
                            print(f'{channel_str:>13}: {"Temperature offset":>18}: '
                                  f'{_vh.convert(dt_units[0]).toString()} '
                                  f'({_vh.convert(dt_units[1]).toString()})')
                    else:
                        # we have no results, so display a suitable message
                        print(f'{"No Multi-channel temperature sensors found":>46}')
                    print()
                else:
                    print()
                    print(f'Device at {self.ip_address} did not respond.')
                    print()

    def display_pm25_offset(self):
        """Display the device PM2.5 offset data.

        Obtain and display the PM2.5 offset data from the selected device.
        """

        # obtain an EcowittDevice object
        device = self.get_device()
        # if we have a device interrogate it and display the data
        if device is not None:
            print()
            # wrap in a try..except in case there is an error
            try:
                # identify the device being used
                print(f'Interrogating {bcolors.BOLD}{device.model}{bcolors.ENDC} '
                      f'at {bcolors.BOLD}{device.ip_address}{bcolors.ENDC}')
                # get the PM2.5 offset data from the API
                pm25_offset_data = device.get_pm25_offset_data()
            except weewx.ViolatedPrecondition as e:
                print()
                print(f'Unable to obtain EcowittDevice object: {e}')
            except DeviceIOError as e:
                print()
                print(f'Unable to connect to device at {self.ip_address}: {e}')
            except socket.timeout:
                print()
                print(f'Timeout. Device at {self.ip_address} did not respond.')
            else:
                # did we get any PM2.5 offset data
                if pm25_offset_data is not None:
                    # obtain a converter to do unit conversion, the unit system does
                    # not matter
                    c = weewx.units.StdUnitConverters[weewx.METRICWX]
                    # now get a formatter, the default string formats and labels will
                    # be fine
                    f = weewx.units.Formatter(unit_format_dict=weewx.defaults.defaults['Units']['StringFormats'],
                                              unit_label_dict=weewx.defaults.defaults['Units']['Labels'])
                    # do we have any results to display?
                    if len(pm25_offset_data) > 0:
                        # now format and display the data
                        print()
                        print('PM2.5 Calibration')
                        # iterate over each channel for which we have data
                        for sensor in pm25_offset_data:
                            # print the channel and offset data
                            channel_str = f'{"Channel":>11} {sensor["channel"]:d}'
                            _vh = weewx.units.ValueHelper(sensor['val'], formatter=f, converter=c)
                            print(f'{channel_str:>13}: {"PM2.5 offset":>15}: '
                                  f'{_vh.toString()}')
                    else:
                        # we have no results, so display a suitable message
                        print(f'{"No PM2.5 sensors found":>26}')
                    print()
                else:
                    print()
                    print(f'Device at {self.ip_address} did not respond.')
                    print()

    def display_co2_offset(self):
        """Display the device WH45 CO2, PM10 and PM2.5 offset data.

        Obtain and display the WH45 CO2, PM10 and PM2.5 offset data from the
        selected device.
        """

        # obtain an EcowittDevice object
        device = self.get_device()
        # if we have a device interrogate it and display the data
        if device is not None:
            print()
            # wrap in a try..except in case there is an error
            try:
                # identify the device being used
                print(f'Interrogating {bcolors.BOLD}{device.model}{bcolors.ENDC} '
                      f'at {bcolors.BOLD}{device.ip_address}{bcolors.ENDC}')
                # get the offset data from the API
                co2_offset_data = device.get_co2_offset_data()
            except weewx.ViolatedPrecondition as e:
                print()
                print(f'Unable to obtain EcowittDevice object: {e}')
            except DeviceIOError as e:
                print()
                print(f'Unable to connect to device at {self.ip_address}: {e}')
            except socket.timeout:
                print()
                print(f'Timeout. Device at {self.ip_address} did not respond.')
            else:
                # did we get any offset data
                if co2_offset_data is not None:
                    # obtain a converter to do unit conversion, the unit system does
                    # not matter
                    c = weewx.units.StdUnitConverters[weewx.METRICWX]
                    # Now get a formatter, we could use the default formatter, but
                    # we need microgram_per_meter_cubed formatted with one decimal
                    # places. So create a custom formatter using a modified
                    # defaults StringFormats stanza and the defaults Labels stanza.
                    # obtain a copy of the defaults StringFormats stanza
                    unit_format_dict = dict(weewx.defaults.defaults['Units']['StringFormats'])
                    # modify the 'microgram_per_meter_cubed' format
                    unit_format_dict['microgram_per_meter_cubed'] = '%.1f'
                    # now get the formatter
                    f = weewx.units.Formatter(unit_format_dict=unit_format_dict,
                                              unit_label_dict=weewx.defaults.defaults['Units']['Labels'])
                    # now format and display the data
                    print()
                    print('CO2 Calibration')
                    _vh = weewx.units.ValueHelper(co2_offset_data['co2'],
                                                  formatter=f,
                                                  converter=c)
                    print(f'{"CO2 offset":>16}: {_vh.toString()}')
                    if co2_offset_data.get("pm1") is not None:
                        _vh = weewx.units.ValueHelper(co2_offset_data['pm1'],
                                                      formatter=f,
                                                      converter=c)
                        print(f'{"PM1 offset":>16}: {_vh.toString()}')
                    _vh = weewx.units.ValueHelper(co2_offset_data['pm25'],
                                                  formatter=f,
                                                  converter=c)
                    print(f'{"PM2.5 offset":>16}: {_vh.toString()}')
                    if co2_offset_data.get("pm4") is not None:
                        _vh = weewx.units.ValueHelper(co2_offset_data['pm4'],
                                                      formatter=f,
                                                      converter=c)
                        print(f'{"PM4 offset":>16}: {_vh.toString()}')
                    _vh = weewx.units.ValueHelper(co2_offset_data['pm10'],
                                                  formatter=f,
                                                  converter=c)
                    print(f'{"PM10 offset":>16}: {_vh.toString()}')
                else:
                    print()
                    print(f'Device at {self.ip_address} did not respond.')
                print()

    def display_lds_offset(self):
        """Display the device WH54 LDS offset data.

        Obtain and display the WH54 LDS offset and calibration data from the
        selected device.
        """

        # obtain an EcowittDevice object
        device = self.get_device()
        # if we have a device interrogate it and display the data
        if device is not None:
            print()
            # wrap in a try..except in case there is an error
            try:
                # identify the device being used
                print(f'Interrogating {bcolors.BOLD}{device.model}{bcolors.ENDC} '
                      f'at {bcolors.BOLD}{device.ip_address}{bcolors.ENDC}')
                # get the offset data from the API
                lds_offset_data = device.get_lds_offset_data()
                # get the device units
                device_units = device.get_device_units()
            except weewx.ViolatedPrecondition as e:
                print()
                print(f'Unable to obtain EcowittDevice object: {e}')
            except DeviceIOError as e:
                print()
                print(f'Unable to connect to device at {self.ip_address}: {e}')
            except socket.timeout:
                print()
                print(f'Timeout. Device at {self.ip_address} did not respond.')
            else:
                # did we get any offset data
                if lds_offset_data is not None:
                    # do we have any results to display?
                    if len(lds_offset_data) > 0:
                        # obtain a converter to do unit conversion, the unit system does
                        # not matter
                        c = weewx.units.StdUnitConverters[weewx.METRICWX]
                        # now get a formatter, the default string formats and labels will
                        # be fine
                        f = weewx.units.Formatter(unit_format_dict=weewx.defaults.defaults['Units']['StringFormats'],
                                                  unit_label_dict=weewx.defaults.defaults['Units']['Labels'])
                        # obtain the order of the units we will display for multi-unit
                        # offsets
                        if device_units['group_depth'] == 'foot2':
                            units = ['foot2', 'mm2']
                        else:
                            units = ['mm2', 'foot2']
                        print()
                        print('LDS Calibration')
                        # iterate over each channel printing the channel data
                        for sensor in lds_offset_data:
                            _name = sensor.get("name")
                            if _name is not None and len(_name) > 0:
                                _name_str = f' ({_name})'
                            else:
                                _name_str = ''
                            print(f'    Channel {sensor["channel"]:d}{_name_str}')
                            _vh = weewx.units.ValueHelper(sensor['offset'],
                                                          formatter=f,
                                                          converter=c)
                            print(f'{"Offset":>15}: {_vh.convert(units[0]).toString()} '
                                  f'({_vh.convert(units[1]).toString()})')
                            _vh = weewx.units.ValueHelper(sensor['total_height'],
                                                          formatter=f,
                                                          converter=c)
                            print(f'{"Height":>15}: {_vh.convert(units[0]).toString()} '
                                  f'({_vh.convert(units[1]).toString()})')
                            print(f'{"Heat":>15}: {sensor["total_heat"]:d}')
                            print(f'{"Level":>15}: {sensor["level"]:d}')
                    else:
                        # we have no results, so display a suitable message
                        print(f'{"No LDS sensors found":>26}')
                    print()
                else:
                    print()
                    print(f'Device at {self.ip_address} did not respond.')
                print()

    def display_calibration(self):
        """Display the device calibration data.

        Obtain and display the calibration data from the selected device.
        """

        # obtain an EcowittDevice object
        device = self.get_device()
        # if we have a device interrogate it and display the data
        if device is not None:
            print()
            # wrap in a try..except in case there is an error
            try:
                # identify the device being used
                print(f'Interrogating {bcolors.BOLD}{device.model}{bcolors.ENDC} '
                      f'at {bcolors.BOLD}{device.ip_address}{bcolors.ENDC}')
                # get the calibration data from the collector object's calibration
                # property
                calibration_data = device.get_calibration_data()
                # get the device units
                device_units = device.get_device_units()
            except weewx.ViolatedPrecondition as e:
                print()
                print(f'Unable to obtain EcowittDevice object: {e}')
            except DeviceIOError as e:
                print()
                print(f'Unable to connect to device at {self.ip_address}: {e}')
            except socket.timeout:
                print()
                print(f'Timeout. Device at {self.ip_address} did not respond.')
            else:
                # did we get any calibration data
                if calibration_data is not None:
                    # obtain a converter to do unit conversion, the unit system does
                    # not matter
                    c = weewx.units.StdUnitConverters[weewx.METRICWX]
                    # now get a formatter, the default string formats and labels will
                    # be fine
                    f = weewx.units.Formatter(unit_format_dict=weewx.defaults.defaults['Units']['StringFormats'],
                                              unit_label_dict=weewx.defaults.defaults['Units']['Labels'])
                    # obtain the order of the units we will display for multi-unit
                    # offsets
                    if device_units['group_deltat'] == 'degree_F2':
                        dt_units = ['degree_F2', 'degree_C2']
                    else:
                        dt_units = ['degree_C2', 'degree_F2']
                    if device_units['group_pressure'] == 'mmHg':
                        p_units = ['mmHg', 'hPa', 'inHg']
                    elif device_units['group_pressure'] == 'inHg':
                        p_units = ['inHg', 'hPa', 'mmHg']
                    else:
                        p_units = ['hPa', 'inHg', 'mmHg']
                    if device_units['group_altitude'] == 'foot':
                        a_units = ['foot', 'meter']
                    else:
                        a_units = ['meter', 'foot']
                    # now format and display the data
                    print()
                    print('Calibration')
                    print(f'{"Irradiance gain":>26}: {calibration_data["solar_gain"]:.2f}')
                    print(f'{"UV gain":>26}: {calibration_data["uv_gain"]:.2f}')
                    print(f'{"Wind gain":>26}: {calibration_data["wind_gain"]:.2f}')
                    _vh = weewx.units.ValueHelper(calibration_data["intemp_offset"],
                                                  formatter=f,
                                                  converter=c)
                    print(f'{"Inside temperature offset":>26}: {_vh.convert(dt_units[0]).toString()} '
                          f'({_vh.convert(dt_units[1]).toString()})')
                    _vh = weewx.units.ValueHelper(calibration_data["inhumid_offset"],
                                                  formatter=f,
                                                  converter=c)
                    print(f'{"Inside temperature offset":>26}: {_vh.toString()}')
                    _vh = weewx.units.ValueHelper(calibration_data["outtemp_offset"],
                                                  formatter=f,
                                                  converter=c)
                    print(f'{"Outside temperature offset":>26}: {_vh.convert(dt_units[0]).toString()} '
                          f'({_vh.convert(dt_units[1]).toString()})')
                    _vh = weewx.units.ValueHelper(calibration_data["outhumid_offset"],
                                                  formatter=f,
                                                  converter=c)
                    print(f'{"Outside temperature offset":>26}: {_vh.toString()}')
                    _vh = weewx.units.ValueHelper(calibration_data["abs_offset"],
                                                  formatter=f,
                                                  converter=c)
                    print(f'{"Absolute pressure offset":>26}: {_vh.convert(p_units[0]).toString()} '
                          f'({_vh.convert(p_units[1]).toString()}/{_vh.convert(p_units[2]).toString()})')
                    # older firmware uses a simple relative pressure calibration
                    # procedure that uses a fixed offset, check if we have a fixed
                    # offset in key value 'rel_offset'
                    if 'rel_offset' in calibration_data:
                        _vh = weewx.units.ValueHelper(calibration_data["rel_offset"],
                                                      formatter=f,
                                                      converter=c)
                        print(f'{"Relative pressure offset":>26}: {_vh.convert(p_units[0]).toString()} '
                              f'({_vh.convert(p_units[1]).toString()}/{_vh.convert(p_units[2]).toString()})')
                    # newer firmware (eg GW3000 v1.0.5 and later) uses an altitude
                    # based pressure calibration procedure that uses an altitude,
                    # check if we have an 'altitude' key value
                    if 'altitude' in calibration_data:
                        _vh = weewx.units.ValueHelper(calibration_data["altitude"],
                                                      formatter=f,
                                                      converter=c)
                        print(f'{"Altitude for REL":>26}: {_vh.convert(a_units[0]).toString()} '
                              f'({_vh.convert(a_units[1]).toString()})')
                    _vh = weewx.units.ValueHelper(calibration_data["winddir_offset"],
                                                  formatter=f,
                                                  converter=c)
                    print(f'{"Wind direction offset":>26}: {_vh.toString(useThisFormat="%d")}')
                else:
                    print()
                    print(f'Device at {self.ip_address} did not respond.')
                print()

    def display_soil_calibration(self):
        """Display the device soil moisture sensor calibration data.

        Obtain and display the soil moisture sensor calibration data from the
        selected device.
        """

        # obtain an EcowittDevice object
        device = self.get_device()
        # if we have a device interrogate it and display the data
        if device is not None:
            print()
            # wrap in a try..except in case there is an error
            try:
                print(f'Interrogating {bcolors.BOLD}{device.model}{bcolors.ENDC} '
                      f'at {bcolors.BOLD}{device.ip_address}{bcolors.ENDC}')
                # get the device soil_calibration_data property
                calibration_data = device.get_soil_calibration_data()
            except weewx.ViolatedPrecondition as e:
                print()
                print(f'Unable to obtain EcowittDevice object: {e}')
            except DeviceIOError as e:
                print()
                print(f'Unable to connect to device at {self.ip_address}: {e}')
            except socket.timeout:
                print()
                print(f'Timeout. Device at {self.ip_address} did not respond.')
            else:
                # did we get any calibration data
                if calibration_data is not None:
                    print()
                    print('Soil Calibration')
                    # iterate over each channel printing the channel data
                    for sensor in calibration_data:
                        print(f'    Channel {sensor["channel"]:d} ({sensor["soilVal"]:d}%)')
                        print(f'{"Now AD":>16}: {sensor["nowAd"]:d}')
                        print(f'{"0% AD":>16}: {sensor["minVal"]:d}')
                        print(f'{"100% AD":>16}: {sensor["maxVal"]:d}')
                else:
                    print()
                    print(f'Device at {self.ip_address} did not respond.')
                print()

    def display_services(self):
        """Display the device Weather Services settings.

        Obtain and display the settings for the various weather services
        supported by the device.
        """

        # obtain an EcowittDevice object
        device = self.get_device()
        # if we have a device interrogate it and display the data
        if device is not None:
            print()
            # obtain an EcowittDevice object and fetch the weather services data
            # from the device, wrap in a try..except in case there is an error
            try:
                # identify the device being used
                print(f'Interrogating {bcolors.BOLD}{device.model}{bcolors.ENDC} '
                      f'at {bcolors.BOLD}{device.ip_address}{bcolors.ENDC}')
                # get the settings for each service known to the device, store them
                # in a dict keyed by the service name
                services_data = device.get_ws_settings()
            except weewx.ViolatedPrecondition as e:
                # something precluded us obtaining an EcowittDevice object
                print()
                print(f'Unable to obtain EcowittDevice object: {e}')
            except DeviceIOError as e:
                # we could not communicate with the device
                print()
                print(f'Unable to connect to device at {self.ip_address}: {e}')
            except socket.timeout:
                # there was a timeout error contacting the device
                print()
                print(f'Timeout. Device at {self.ip_address} did not respond.')
            else:
                # we have a response but did we get any service data
                if len(services_data) > 0:
                    # we did, now format and display the data
                    print()
                    print('Weather Services')
                    print()

                    # Ecowitt.net
                    print('  Ecowitt.net')
                    # upload interval, 0 means disabled, otherwise it's the number
                    # of minutes
                    if services_data['ost_interval'] == 0:
                        print(f'{"Upload Interval":>22}: Upload to Ecowitt.net is disabled')
                    elif services_data['ost_interval'] > 1:
                        print(f'{"Upload Interval":>22}: {services_data["ost_interval"]:d} minutes')
                    else:
                        print(f'{"Upload Interval":>22}: {services_data["ost_interval"]:d} minute')
                    # device MAC
                    print(f'{"MAC":>22}: {services_data["sta_mac"]}')
                    print()

                    # Weather Underground
                    print('  Wunderground')
                    # upload interval
                    try:
                     interval = services_data['wu_interval']
                     if interval is not None:
                        if interval == 0:
                            interval_str = '0 minutes (disabled)'
                        elif interval == 1:
                            interval_str = '1 minute'
                        elif 1 < interval < 16:
                            interval_str = f'{interval:d} minutes'
                        elif interval >= 16:
                            interval_str = f'{interval:d} seconds'
                        else:
                            interval_str = '--'
                     else:
                        interval_str = '--'
                     print(f'{"Upload Interval":>22}: {interval_str}')
                     # Station ID, obfuscate part of the Station ID unless told not
                     # to
                     wu_id = services_data['wu_id'] if self.namespace.unmask \
                        else obfuscate(services_data['wu_id'])
                     print(f'{"Station ID":>22}: {wu_id}')
                     # Station key, obfuscate part of the Station key unless told
                     # not to
                     wu_key = services_data['wu_key'] if self.namespace.unmask \
                        else obfuscate(services_data['wu_key'])
                     print(f'{"Station Key":>22}: {wu_key}')
                     print()
                    except:
                     print('       no data')
                     print()

                    # Weather Cloud
                    print('  Weathercloud')
                    # upload interval in minutes
                    try:
                     interval = services_data['wcl_interval']
                     if interval is not None:
                        if interval == 0:
                            interval_str = f'{interval:d} minutes (disabled)'
                        elif interval > 1:
                            interval_str = f'{interval:d} minutes'
                        elif interval == 1:
                            interval_str = '1 minute'
                        else:
                            interval_str = '--'
                     else:
                        interval_str = '--'
                     print(f'{"Upload Interval":>22}: {interval_str}')
                     # Weathercloud ID (WSView+ refers to it as Station ID),
                     # obfuscate part of the Weathercloud ID unless told not to
                     wcl_id = services_data['wcl_id'] if self.namespace.unmask \
                        else obfuscate(services_data['wcl_id'])
                     print(f'{"Station ID":>22}: {wcl_id}')
                     # Weathercloud key (WSView+ refers to it as Station key),
                     # obfuscate part of the Weathercloud ID unless told not to
                     wcl_key = services_data['wcl_key'] if self.namespace.unmask \
                        else obfuscate(services_data['wcl_key'])
                     print(f'{"Station Key":>22}: {wcl_key}')
                     print()
                    except:
                     print('       no data')
                     print()

                    # Weather Observations Website
                    # upload interval in minutes
                    print('  Weather Observations Website')
                    try:  
                     interval = services_data['wow_interval']
                     if interval is not None:
                        if interval == 0:
                            interval_str = f"{interval:d} minutes (disabled)"
                        elif interval > 1:
                            interval_str = f"{interval:d} minutes"
                        elif interval == 1:
                            interval_str = "1 minute"
                        else:
                            interval_str = "--"
                     else:
                        interval_str = "--"
                     print(f'{"Upload Interval":>22}: {interval_str}')
                     # Station ID, obfuscate part of the Station ID unless told not
                     # to
                     wow_id = services_data['wow_id'] if self.namespace.unmask \
                        else obfuscate(services_data['wow_id'])
                     print(f'{"Station ID":>22}: {wow_id}')
                     # Station key, obfuscate part of the Station key unless told
                     # not to
                     wow_key = services_data['wow_key'] if self.namespace.unmask \
                        else obfuscate(services_data['wow_key'])
                     print(f'{"Station Key":>22}: {wow_key}')
                     print()
                    except:
                     print('       no data')
                     print()

                    # Customised
                    print('  Customized')
                    # Is upload enabled, WSView+ only displays enabled/disabled,
                    # but include 'unknown' just in case
                    if services_data['Customized'] is None:
                        print(f'{"Upload":>22}: {"Unknown"}')
                    elif services_data['Customized']:
                        print(f'{"Upload":>22}: {"Enabled"}')
                    else:
                        print(f'{"Upload":>22}: {"Disabled"}')
                    # upload protocol, WSView+ only displays Ecowitt, Wunderground
                    # and MQTT, but include 'unknown' just in case
                    if services_data['Protocol'].lower() in ('ecowitt', 'wunderground'):
                        if services_data['Protocol'].lower() == 'ecowitt':
                            print(f'{"Upload Protocol":>22}: {"Ecowitt"}')
                            remote_server = services_data['ecowitt_ip']
                            path = services_data['ecowitt_path']
                            port_str = f"{services_data['ecowitt_port']:d}"
                            interval_str = f"{services_data['ecowitt_upload']:d}"
                        elif services_data['Protocol'].lower() == 'wunderground':
                            print(f'{"Upload Protocol":>22}: {"Wunderground"}')
                            remote_server = services_data['usr_wu_ip']
                            path = services_data['usr_wu_path']
                            port_str = f"{services_data['usr_wu_port']:d}"
                            interval_str = f"{services_data['usr_wu_upload']:d}"
                        else:
                            print(f'{"Upload Protocol":>22}: {"Unknown"}')
                            remote_server = "Unknown"
                            path = "Unknown"
                            port_str = "Unknown"
                            interval_str = "Unknown"
                        # remote server IP address
                        print(f'{"Server IP/Hostname":>22}: {remote_server}')
                        # remote server path, if using wunderground protocol we have
                        # Station ID and Station key as well
                        print(f'{"Path":>22}: {path}')
                        # if using the Wunderground protocol then Station ID and
                        # Station key are also available for use
                        if services_data['Protocol'] == 'wunderground':
                            usr_wu_id = services_data['usr_wu_id'] if self.namespace.unmask \
                                else obfuscate(services_data['usr_wu_id'])
                            print(f'{"Station ID":>22}: {usr_wu_id}')
                            usr_wu_key = services_data['usr_wu_key'] if self.namespace.unmask \
                                else obfuscate(services_data['usr_wu_key'])
                            print(f'{"Station Key":>22}: {usr_wu_key}')
                        # port
                        print(f'{"Port":>22}: {port_str}')
                        # upload interval in seconds
                        print(f'{"Upload Interval":>22}: {interval_str}')
                    elif services_data['Protocol'].lower() == 'mqtt':
                            print(f'{"Upload Protocol":>22}: MQTT')
                            print(f'{"Host":>22}: {services_data["mqtt_host"]}')
                            print(f'{"Port":>22}: {services_data["mqtt_port"]:d}')
                            print(f'{"Topic":>22}: {services_data["mqtt_topic"]}')
                            print(f'{"Upload Interval":>22}: {services_data["mqtt_interval"]:d}')
                            print(f'{"Keep Alive":>22}: {services_data["mqtt_keepalive"]:d}')
                            # obtain an obfuscated client name if required
                            mqtt_name = services_data["mqtt_name"] if self.namespace.unmask \
                                else obfuscate(services_data["mqtt_name"])
                            print(f'{"Client Name":>22}: {mqtt_name}')
                            # obtain an obfuscated client ID if required
                            mqtt_clientid = services_data["mqtt_clientid"] if self.namespace.unmask \
                                else obfuscate(services_data["mqtt_clientid"])
                            print(f'{"Client ID":>22}: {mqtt_clientid}')
                            print(f'{"Username":>22}: {services_data["mqtt_username"]}')
                            # obtain an obfuscated password if required
                            mqtt_password = services_data["mqtt_password"] if self.namespace.unmask \
                                else obfuscate(services_data["mqtt_password"])
                            print(f'{"Password":>22}: {mqtt_password}')
                else:
                    # we received no data, the assumption being the device did not
                    # respond
                    print()
                    print(f'Device at {self.ip_address} did not respond.')

    def display_mac(self):
        """Display the device hardware MAC address.

        Obtain and display the hardware MAC address of the selected device.
        """

        # obtain an EcowittDevice object
        device = self.get_device()
        print()
        # if we have a device interrogate it and display the data
        if device is not None:
            # wrap in a try..except in case there is an error
            try:
                # identify the device being used
                print(f'Interrogating {bcolors.BOLD}{device.model}{bcolors.ENDC} '
                      f'at {bcolors.BOLD}{device.ip_address}{bcolors.ENDC}')
                print()
                # get the device MAC address
                print(f'{"MAC address":>15}: {device.mac_address}')
            except weewx.ViolatedPrecondition as e:
                print()
                print(f'Unable to obtain EcowittDevice object: {e}')
            except DeviceIOError as e:
                print()
                print(f'Unable to connect to device at {self.ip_address}: {e}')
            except socket.timeout:
                print()
                print(f'Timeout. Device at {self.ip_address} did not respond.')

    def display_firmware(self):
        """Display device firmware details.

        Obtain and display the firmware version string from the selected
        device. User is advised whether a firmware update is available or not.
        """

        # obtain an EcowittDevice object
        device = self.get_device()
        # if we have a device interrogate it and display the data
        if device is not None:
            print()
            # wrap in a try..except in case there is an error
            try:
                # get the device model, we will use this multiple times
                model = device.model
                # identify the device being used
                print(f'Interrogating {bcolors.BOLD}{device.model}{bcolors.ENDC} '
                      f'at {bcolors.BOLD}{device.ip_address}{bcolors.ENDC}')
                print()
                # get the firmware version via the API
                model_str = f'installed {model} firmware version'
                print(f'{model_str:>35}: {device.firmware_version}')
                sensor_fw = device.sensor_firmware_versions
                if sensor_fw is not None:
                    for sensor, sensor_fw_ver in sensor_fw.items():
                        sensor_fw_model_str = f"installed {sensor} firmware version"
                        print(f'{sensor_fw_model_str:>35}: {sensor_fw_ver}')
                print()
                fw_update_avail = device.firmware_update_avail
                if fw_update_avail:
                    # we have an available firmware update
                    # obtain the 'curr_msg' from the device HTTP API
                    # 'get_device_info' command, this field usually contains the
                    # firmware change details
                    curr_msg = device.firmware_update_message
                    # now print the firmware update details
                    print(f'    a firmware update is available for this {model}')
                    print(f'    update at http://{self.ip_address} or via the WSView Plus app')
                    # if we have firmware update details print them
                    if curr_msg is not None:
                        print()
                        # Ecowitt have not documented the HTTP API calls so we are
                        # not exactly sure what the 'curr_msg' field is used for,
                        # it might be for other things as well
                        print('    likely firmware update message:')
                        # multi-line messages seem to have \r\n at the end of each
                        # line, split the string so we can format it a little better
                        if '\r\n' in curr_msg:
                            for line in curr_msg.split('\r\n'):
                                # print each line
                                print(f'      {line}')
                        else:
                            # print as a single line
                            print(f'      {curr_msg}')
                    else:
                        # we had no 'curr_msg' for one reason or another
                        print('    no firmware update message found')
                elif fw_update_avail is None:
                    # we don't know if we have an available firmware update
                    print(f'    could not determine if a firmware update is available for this {model}')
                else:
                    # there must be no available firmware update
                    print(f'    the firmware is up to date for this {model}')
            except weewx.ViolatedPrecondition as e:
                print()
                print(f'Unable to obtain EcowittDevice object: {e}')
                print()
                self.device_connection_help()
            except DeviceIOError as e:
                print()
                print(f'Unable to connect to device at {self.ip_address}: {e}')
                print()
                self.device_connection_help()
            except socket.timeout:
                print()
                print(f'Timeout. Device at {self.ip_address} did not respond.')
                print()
                self.device_connection_help()

    def display_sensors(self):
        """Display the device sensor ID information.

        Obtain and display the sensor ID information from the selected device.
        Output is provided for all possible sensors unless registered_only is
        True.

        Outputs a formatted summary of sensor metadata for a device, one line
        per sensor.
        """

        def is_disabled(sensor_data):
            """Is the sensor disabled.

            Given a stanza of sensor data determine is a sensor is disabled.

            Returns True or False.
            """

            # a sensor is disabled if the sensor ID == 'fffffffe'
            if sensor_data['id'].lower() == 'fffffffe':
                return True
            return False

        def is_registering(sensor_data):
            """Is the sensor registering.

            Given a stanza of sensor data determine is a sensor is registering.

            Returns True or False.
            """

            # a sensor is registering if the sensor ID == 'ffffffff'
            if sensor_data['id'].lower() == 'ffffffff':
                return True
            return False

        def get_sensor_id_string(sensor_data):
            """Create a sensor ID string based on a sensor ID."""

            # do we have any sensor data and does it contain an 'id' field
            if sensor_data is not None and 'id' in sensor_data:
                # we have the required data, create suitable text based on the
                # 'id' field content
                if is_disabled(sensor_data):
                    # the sensor is disabled
                    id_str = 'sensor is disabled'
                elif is_registering(sensor_data):
                    # the sensor is registering
                    id_str = 'sensor is registering...'
                else:
                    # the sensor is registered, state the sensor ID
                    id_str = f"sensor ID: {sensor_data['id']}"
            else:
                # we have no sensor data containing an 'id' field so create
                # suitable text
                id_str = 'unknown sensor ID'
            # return the resulting text
            return id_str

        def print_sensor(model, sensor_data, channel=''):
            """Print sensor state.

            Print a formatted line of sensor metadata.
            """

            # create a string to display sensor model and channel as applicable
            sensor_name_str = ' '.join([model.upper(), channel])
            # create signal strength and battery state text
            if is_disabled(sensor_data) or is_registering(sensor_data):
                # the sensor is disabled or registering so do not provide any
                # signal strength or battery state text
                if self.namespace.registered_only:
                    return
                signal_str = ''
                battery_str = ''
                rssi_str = ''
            else:
                # the sensor is registered
                # create the signal strength text
                signal_str = f"signal: {sensor_data.get('signal', '--')}"
                # create rssi  strength text
                rssi_str = f"rssi: {sensor_data.get('rssi', '--')}"

                # create suitable descriptive battery state text
                desc_str = device.sensors.batt_state_desc(model=model,
                                                          sensor_data=sensor_data)

                # create rssi  strength text
                rssi_str = f"rssi: {sensor_data.get('rssi', '--')}"

                # create a suitable voltage string
                volt_str = f" ({sensor_data['voltage']}V)" if 'voltage' in sensor_data else ""
                if sensor_data.get('battery', '--') is None:
                    _batt_str = '--'
                else:
                    _batt_str = sensor_data.get('battery', '--')
                # create the overall battery state text by combining the
                # battery state value and battery state descriptive text
                if desc_str is not None:
                    battery_str = f"battery: {_batt_str}{volt_str} ({desc_str})"
                else:
                    battery_str = f"battery: {_batt_str}{volt_str}"
            # obtain a suitable text string describing the state of the
            # sensor's connection based on the sensor ID
            sensor_id_str = get_sensor_id_string(sensor_data)
            # print the overall sensor metadata text
            print(f'{sensor_name_str.upper():<10} {sensor_id_str:<25} {signal_str} {rssi_str} {battery_str}')

        # obtain an EcowittDevice object
        device = self.get_device()
        # if we have a device interrogate it and display the data
        if device is not None:
            print()
            # wrap in a try..except in case there is an error
            try:
                # identify the device being used
                print(f'Interrogating {bcolors.BOLD}{device.model}{bcolors.ENDC} '
                      f'at {bcolors.BOLD}{device.ip_address}{bcolors.ENDC}')
            except weewx.ViolatedPrecondition as e:
                print()
                print(f'Unable to obtain EcowittDevice object: {e}')
            except DeviceIOError as e:
                print()
                print(f'Unable to connect to device at {self.ip_address}: {e}')
                print()
                self.device_connection_help()
            except socket.timeout:
                print()
                print(f'Timeout. Device at {self.ip_address} did not respond.')
                print()
                self.device_connection_help()
            else:
                # get the latest sensors data from the device
                sensors_data = device.get_sensors_data(connected_only=False,
                                                       flatten_data=False)
                # get the latest live data  from the device
                live_data = device.get_live_data(flatten_data=True)
                # update the device' EcowittSensors object
                device.sensors.update_sensor_data(all_sensor_data=sensors_data,
                                                  live_data=live_data)
                # now get the sensor metadata from the device
                sensors_metadata = device.sensors.data
                # do we have any sensor data
                if sensors_metadata is not None and len(sensors_metadata) > 0:
                    # iterate over each sensor model in display order
                    for model in self.sensor_display_order:
                        # get the sensor metadata
                        data = sensors_metadata.get(model)
                        # do we have any data for this model, if not skip this
                        # model
                        if data is None:
                            continue
                        # do we have a channelised or non-channelised model
                        if 'address' in data.keys():
                            # we have a non-channelised sensor
                            print_sensor(model=model, sensor_data=data)
                        else:
                            # we have a channelised sensor
                            for channel, channel_data in data.items():
                                print_sensor(model=model,
                                             sensor_data=channel_data,
                                             channel=channel)
                elif len(sensors_data) == 0:
                    # we were given no sensor data, inform the user
                    print()
                    print(f'Device at {self.ip_address} did not return any sensor data.')
                else:
                    # the device did not respond, inform the user
                    print()
                    print(f'Device at {self.ip_address} did not respond.')

    def display_live_data(self):
        """Display the device live sensor data.

        Obtain and display live sensor data from the selected device. Data is
        presented as read from the device except for conversion to US customary
        or Metric units and the addition of unit labels.
        """

        # wrap in a try..except in case there is an error
        try:
            # get an EcowittHttpCollector object, normally we would reach into
            # an EcowittDevice object for data but in this case the
            # EcowittHttpCollector.get_current_data() method can be used to
            # assemble all disparate pieces of data for us
            collector = EcowittHttpCollector(ip_address=self.ip_address,
                                             show_battery=self.show_battery)
            # identify the device being used
            print()
            print(f'Interrogating {collector.device.model} at '
                  f'{self.ip_address}')
            # call the EcowittHttpCollector.get_current_data() method to obtain
            # the live sensor data
            current_data = collector.get_current_data()
        except weewx.ViolatedPrecondition as e:
            print()
            print(f'Unable to obtain EcowittDevice object: {e}')
        except DeviceIOError as e:
            print()
            print(f'Unable to connect to device at {self.ip_address}: {e}')
            print()
            self.device_connection_help()
        except socket.timeout:
            print()
            print(f'Timeout. Device at {self.ip_address} did not respond.')
            print()
            self.device_connection_help()
        else:
            # Obtain a HttpMapper object to map our data, use the default field
            # map
            mapper = HttpMapper(driver_debug=None)
            # now map the data
            mapped_data = mapper.map_data(current_data)
            # we have a data dict to work with, but we need to format the
            # values and may need to convert units

            # the live sensor data dict is a dict of sensor values and a
            # timestamp only, whilst all sensor values are in a given unit
            # system there is no usUnits field present. We need usUnits to do
            # our unit conversion so add in the usUnits field.
            mapped_data['usUnits'] = self.unit_system
            # we will use the timestamp separately so pop it from the dict and
            # save for later
            datetime = mapped_data.pop('datetime', int(time.time()))
            # TODO. Is this needed?
            # extend the WeeWX obs_group_dict with our Ecowitt device
            # obs_group_dict
            weewx.units.obs_group_dict.prepend(DEFAULT_GROUPS)
            # the live data is in self.unit_system units, if required get a
            # suitable converter based on our display units
            display_unit_system = weewx.units.unit_constants[self.namespace.units.upper()]
            c = weewx.units.StdUnitConverters[display_unit_system]
            # Now get a formatter, we could use the default formatter, but we
            # need voltages formatted to two decimal places. So create a custom
            # formatter using a modified defaults StringFormats stanza and the
            # defaults Labels stanza.
            # obtain a copy of the defaults StringFormats stanza
            unit_format_dict = dict(weewx.defaults.defaults['Units']['StringFormats'])
            # modify the 'volt' format
            unit_format_dict['volt'] = '%.2f'
            unit_format_dict['microgram_per_meter_cubed'] = '%.1f'
            # obtain a custom formatter
            f = weewx.units.Formatter(unit_format_dict=unit_format_dict,
                                      unit_label_dict=weewx.defaults.defaults['Units']['Labels'])
            # now build a new data dict with our converted and formatted data
            result = {}
            # iterate over the fields in our original data dict
            for key in mapped_data:
                # we don't need usUnits in the result so skip it
                if key == 'usUnits' or key == 'ws90_ver' or key == 'ws85_ver':
                    continue
                # get our key as a ValueTuple
                try:
                 key_vt = weewx.units.as_value_tuple(mapped_data, key)
                 # get a ValueHelper which will do the conversion and formatting
                 key_vh = weewx.units.ValueHelper(key_vt, formatter=f, converter=c)
                 # and add the converted and formatted value to our dict
                 result[key] = key_vh.toString(None_string='None')
                except:
                 pass
            # finally, sort our dict by key and print the data
            print()
            print(f'Displaying data using the WeeWX '
                  f'{weewx.units.unit_nicknames.get(display_unit_system)} unit group.')
            print()
            print(f'{collector.device.model} live sensor data ({timestamp_to_string(datetime)}): '
                  f'{weeutil.weeutil.to_sorted_string(result)}')

    def display_discovered_devices(self):
        """Display discovered devices.

        Discover and display details of Ecowitt devices on the local network.
        """

        print()
        print('Discovering Ecowitt devices...')
        print()
        # discover the devices
        device_list = self.discover()
        # did we discover any devices
        if len(device_list) > 0:
            # we have at least one result
            # Check if any of the discovered devices might be supported (ie the
            # device is not included in the supported or unsupported lists).
            # First obtain a list of such devices.
            possible = [d for d in device_list if d['model'] not in KNOWN_DEVICES]
            possible_supported_ip = []
            if len(possible) > 0:
                # we have some unknown devices that may be supported
                for device in possible:
                    if self.is_supported(device):
                        possible_supported_ip += [device['ip_address'],]
            # first sort our list by IP address
            sorted_list = sorted(device_list, key=itemgetter('ip_address'))
            # now display our results
            printed_anything = False
            # first the supported devices
            print_label = False
            for device in sorted_list:
                if (device['ip_address'] is not None and
                        device['model'] is not None and
                        device['model'] in SUPPORTED_DEVICES):
                    if not print_label:
                        print('Supported Devices')
                        printed_anything = True
                        print_label = True
                    print(f'  {device["model"]} discovered at IP address {device["ip_address"]}')
            # now the possibly supported devices (if any)
            print_label = False
            for device in sorted_list:
                if (device['ip_address'] is not None and
                        device['ip_address'] in possible_supported_ip):
                    if not print_label:
                        if not printed_anything:
                            print()
                        print('Possibly Supported Devices')
                        printed_anything = True
                        print_label = True
                    # By definition, we don't know the model of 'possibly'
                    # supported devices. However, we can take an educated guess
                    # at the device model from the device AP SSID.
                    # do we have a model
                    if device['model'] is None:
                        # we don't have a model, so guess the model based on
                        # the SSID
                        if device.get('ssid') is not None:
                            # The model is usually the first six characters of
                            # the SSID. Construct a string to use when
                            # displaying the device model, add a rider that the
                            # model is unconfirmed.
                            model_string = ' '.join([device.get('ssid')[0:6], '(model unconfirmed)'])
                        else:
                            # we don't have an SSID for some reason, we cannot
                            # guess the model so leave it as 'unknown'
                            model_string = 'unknown'
                    else:
                        # we have a properly identified and decoded model so
                        # use that
                        model_string = device['model']
                    print(f'  {model_string} discovered at IP address {device["ip_address"]}')
            # and finally unsupported devices (if any)
            print_label = False
            for device in sorted_list:
                if (device['ip_address'] is not None and
                        device['model'] is not None and
                        device['model'] in UNSUPPORTED_DEVICES):
                    if not print_label:
                        if not printed_anything:
                            print()
                        print('Unsupported Devices')
                        printed_anything = True
                        print_label = True
                    print(f'  {device["model"]} discovered at IP address {device["ip_address"]}')
        else:
            # we have no results
            print('No devices were discovered.')

    @staticmethod
    def is_supported(device):
        """Perform a basic check to see if a device supports the HTTP API."""

        ip_address = device.get('ip_address')
        # try to obtain an EcowittDevice object using the IP address we
        # received, be prepared to handle any exceptions raised
        try:
            device = EcowittDevice(ip_address=ip_address)
        except Exception:
            # We could not obtain an Ecowitt Device object, this means we
            # cannot support the device. For now just continue.
            pass
        else:
            # We have an EcowittDevice object. Try to obtain the device info
            # data via the HTTP API, be prepared to catch any exceptions.
            try:
                device_info_data = device.get_device_info_data()
            except (DeviceIOError, ParseError):
                # We encountered an error, this means we cannot support the
                # device. For now just continue.
                pass
            else:
                # We have some device info. Do a basic validity check on the
                # data, in this case check that the 'ap' field is not None and
                # non-zero length.
                #if device_info_data['ap'] is not None and len(device_info_data['ap']) > 0:
                    # our basic check passed, so assume this device is
                    # supported
                    # now take a guess at the model
                return True
        # we encountered an exception somewhere, assume this device is not
        # supported
        return False

    def discover(self):
        """Discover any devices on the local network.

        There is no published method of discovering Ecowitt devices on the
        local network using the Ecowitt HTTP API. According to the Ecowitt
        telnet API the CMD_BROADCAST API command can be used to identify
        Ecowitt devices on the local network segment; however, this approach
        has been found to be unreliable and the telnet API may not be supported
        by all devices in the future. Another more reliable approach is to make
        use of the regular UDP broadcast made by each Ecowitt device on
        port 59387.

        To discover Ecowitt devices monitor UDP port 59387 for a set period of
        time and capture all port 59387 UDP broadcasts received. Decode each
        reply to obtain details of any devices on the local network. Create a
        dict of details for each device including a derived model name.
        Construct a list of dicts with details of each unique (ie each unique
        MAC address) device that responded. When complete return the list of
        devices found.
        """

        # get an EcowittDevice object
        parser = EcowittHttpParser()
        # create a socket object so we can receive IPv4 UDP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # set timeout
        s.settimeout(self.namespace.discovery_timeout)
        # bind our socket to the port we are using
        s.bind(("", self.namespace.discovery_port))
        # initialise a list for the results as multiple devices may respond
        result_list = []
        # get the current time
        start_ts = time.time()
        # start receiving continuously, we will stop once our discovery period
        # has elapsed
        while True:
            # wrap in try .. except to capture any errors
            try:
                # receive a response
                response = s.recv(1024)
                # # if required display the response packet
                # if self.debug:
                #     _first_row = True
                #     for row in gen_pretty_bytes_as_hex(response, quote=False):
                #         if _first_row:
                #             print()
                #             print(f'Received broadcast packet: {row["hex"]}')
                #             _first_row = False
                #         else:
                #             print(f'                           {row["hex"]}')
                #         print(f'                           {row["printable"]}')
            except socket.timeout:
                # if we time out then we are done with this attempt
                break
            except socket.error:
                # raise any other socket error
                raise
            # Check the response is valid. As it happens the broadcast from
            # each device on port 59387 is identical to the response to a
            # device response to CMD_BROADCAST telnet API command. The validity
            # of the response can be checked by (1) confirming byte 2 is 0x12
            # and (2) verifying the packet checksum in last byte.
            # first check we have a response
            if response is not None and len(response) > 3:
                # now check that byte 2 == 0x12
                if response[2] != 0x12:
                    continue
                # and finally verify the checksum
                if calc_checksum(response[2:-1]) != response[-1]:
                    continue
            else:
                continue
            # if we made it here we have a valid broadcast response, so decode
            # the response and obtain a dict of device data
            found_device_dict = self.decode_broadcast_response(response)
            # if we haven't seen this MAC before attempt to obtain and save the
            # device model then add the device to our result list
            if not any((d['mac'] == found_device_dict['mac']) for d in result_list):
                # determine the device model based on the device SSID and add
                # the model to the device dict
                found_device_dict['model'] = parser.get_model_from_firmware(found_device_dict.get('ssid'))
                # append the device to our list
                result_list.append(found_device_dict)
            # has our discovery period elapsed, if it has break out of the
            # loop
            if time.time() - start_ts > self.discovery_period:
                break
        # we are done, close our socket
        s.close()
        # now return our results
        return result_list

    @staticmethod
    def decode_broadcast_response(raw_data):
        """Decode a broadcast response and return the results as a dict.

        A device response to a CMD_BROADCAST API command consists of a
        number of control structures around a payload of a data. The API
        response is structured as follows:

        bytes 0-1 incl                  preamble, literal 0xFF 0xFF
        byte 2                          literal value 0x12
        bytes 3-4 incl                  payload size (big endian short integer)
        bytes 5-5+payload size incl     data payload (details below)
        byte 6+payload size             checksum

        The data payload is structured as follows:

        bytes 0-5 incl      device MAC address
        bytes 6-9 incl      device IP address
        bytes 10-11 incl    device port number
        bytes 11-           device AP SSID

        Note: The device AP SSID for a given device is fixed in size but
        this size can vary from device to device and across firmware
        versions.

        There also seems to be a peculiarity in the CMD_BROADCAST response
        data payload whereby the first character of the device AP SSID is a
        non-printable ASCII character. The WSView app appears to ignore or
        not display this character nor does it appear to be used elsewhere.
        Consequently, this character is ignored.

        raw_data:   a bytestring containing a validated (structure and
                    checksum verified) raw data response to the
                    CMD_BROADCAST API command

        Returns a dict with decoded data keyed as follows:
            'mac':          device MAC address (string)
            'ip_address':   device IP address (string)
            'port':         device port number (integer)
            'ssid':         device AP SSID (string)
        """

        # obtain the response size, it's a big endian short (two byte)
        # integer
        resp_size = struct.unpack('>H', raw_data[3:5])[0]
        # now extract the actual data payload
        data = raw_data[5:resp_size + 2]
        # initialise a dict to hold our result
        data_dict = {'mac': bytes_to_hex(data[0:6], separator=":"),
                     'ip_address': '%d.%d.%d.%d' % struct.unpack('>BBBB',
                                                                 data[6:10]),
                     'port': struct.unpack('>H', data[10: 12])[0]
                     }
        # get the SSID as a bytestring
        ssid_b = data[13:]
        # create a format string so the SSID string can be unpacked into its
        # bytes, remember the length can vary
        ssid_format = "B" * len(ssid_b)
        # unpack the SSID bytestring, we now have a tuple of integers
        # representing each of the bytes
        ssid_t = struct.unpack(ssid_format, ssid_b)
        # convert the sequence of bytes to unicode characters and assemble
        # as a string and return the result
        data_dict['ssid'] = "".join([chr(x) for x in ssid_t])
        # return the result dict
        return data_dict

    @staticmethod
    def display_field_map():
        """Display the default field map."""

        # first obtain a HttpMapper object without passing any config, this
        # will initialise the HttpMapper object with the default field map
        mapper = HttpMapper(driver_debug=None)
        print()
        print('Ecowitt HTTP driver/service default field map:')
        print('(format is WeeWX field name: Ecowitt HTTP driver field name)')
        print()
        # obtain a list of naturally sorted field map keys so that, for
        # example, xxxxx16 appears in the correct order
        keys_list = natural_sort_keys(mapper.field_map)
        # iterate over the sorted keys and print the key and item
        for key in keys_list:
            print(f'{key:>23}: {mapper.field_map[key]}')

    def display_driver_field_map(self):
        """Display the driver field map that would be used.

        By default, the default field map is used by the driver; however, the
        user may alter the field map used by the driver via the [EcowittHttp]
        stanza. This method displays the actual field map that would be used by
        the driver.
        """

        # this may take a moment to set up so inform the user
        print()
        print('This may take a moment...')
        # place an entry in the log so that if we encounter errors that are
        # logged we can tell they were not caused by a live WeeWX instance
        log.info('Obtaining an Ecowitt HTTP driver...')
        driver = None
        # wrap in a try..except in case there is an error obtaining and
        # interacting with the driver
        try:
            # get an EcowittHttpDriver object
            driver = EcowittHttpDriver(**self.stn_dict)
        except DeviceIOError as e:
            print()
            print(f'Unable to connect to device: {e}')
            print()
            print('Unable to display actual driver field map')
            print()
            self.device_connection_help()
        except KeyboardInterrupt:
            # we have a keyboard interrupt so shut down
            if driver:
                driver.closePort()
        else:
            # now display the field map defined in the driver's field_map
            # property
            print()
            print('Ecowitt HTTP driver actual field map:')
            print('(format is WeeWX field name: driver field name)')
            print()
            # obtain a list of naturally sorted dict keys so that, for example,
            # xxxxx16 appears in the correct order
            keys_list = natural_sort_keys(driver.mapper.field_map)
            # iterate over the sorted keys and print the key and item
            for key in keys_list:
                print(f'{key:>23}: {driver.mapper.field_map[key]}')
        log.info('Finished using Ecowitt local HTTP driver')

    def display_service_field_map(self):
        """Display the Ecowitt HTTP driver service field map that would be used.

        By default, the default field map is used by the service; however, the
        user may alter the field map used by the service via the [EcowittHttp]
        stanza. This method displays the actual field map that would be used by
        the service.
        """

        # this may take a moment to set up so inform the user
        print()
        print('This may take a moment...')
        # place an entry in the log so that if we encounter errors that are
        # logged we can tell they were not caused by a live WeeWX instance
        log.info('Obtaining an Ecowitt HTTP service...')
        # Create a dummy config so we can stand up a dummy engine with a dummy
        # simulator emitting arbitrary loop packets. Include the driver
        # service and StdPrint. StdPrint will take care of printing our loop
        # packets (no StdArchive so loop packets only, no archive records)
        config = {
            'Station': {
                'station_type': 'Simulator',
                'altitude': [0, 'meter'],
                'latitude': 0,
                'longitude': 0},
            'Simulator': {
                'driver': 'weewx.drivers.simulator',
                'mode': 'simulator'},
            'EcowittHttp': {},
            'Engine': {
                'Services': {
                    'archive_services': 'user.ecowitt_http.EcowittHttpService',
                    'report_services': 'weewx.engine.StdPrint'}}}
        # set the IP address and port in the dummy config
        config['EcowittHttp']['ip_address'] = self.ip_address
        engine = None
        # wrap in a try..except in case there is an error
        try:
            # create a dummy engine
            engine = weewx.engine.StdEngine(config)
            # Our driver service will have been instantiated by the engine
            # during its startup. Whilst access to the service is not normally
            # required we require access here, so we can obtain some info about
            # the station we are using for this test. The engine does not
            # provide a ready means to access the driver service, so we can
            # do a bit of guessing and iterate over all the engine's services
            # and select the one that has a 'collector' property. Unlikely to
            # cause a problem since there are only two services in the dummy
            # engine.
            http_svc = None
            for svc in engine.service_obj:
                if hasattr(svc, 'collector'):
                    http_svc = svc
            if http_svc is not None:
                # we have a driver service, it's not much use, but it has the
                # field map we need so go ahead and display its field map
                print()
                print('Ecowitt HTTP driver service actual field map:')
                print('(format is WeeWX field name: service field name)')
                print()
                # obtain a list of naturally sorted dict keys so that, for example,
                # xxxxx16 appears in the correct order
                keys_list = natural_sort_keys(http_svc.mapper.field_map)
                # iterate over the sorted keys and print the key and item
                for key in keys_list:
                    print(f'{key:>23}: {http_svc.mapper.field_map[key]}')
        except DeviceIOError as e:
            print()
            print(f'Unable to connect to device: {e}')
            print()
            print('Unable to display actual service field map')
            print()
            self.device_connection_help()
        except KeyboardInterrupt:
            if engine:
                engine.shutDown()
        log.info('Finished using Ecowitt HTTP driver service')

    def test_driver(self):
        """Exercise the Ecowitt HTTP driver as a driver.

        Exercises the Ecowitt HTTP driver only. Loop packets, but no archive
        records, are emitted to the console continuously until a keyboard
        interrupt is received. A station config dict is coalesced from any
        relevant command line parameters and the config file in use with
        command line parameters overriding those in the config file.
        """

        log.info('Testing Ecowitt HTTP driver...')
        # set the IP address and port in the station config dict
        self.stn_dict['ip_address'] = self.ip_address
        if self.namespace.poll_interval:
            self.stn_dict['poll_interval'] = self.namespace.poll_interval
        if self.namespace.max_tries:
            self.stn_dict['max_tries'] = self.namespace.max_tries
        if self.namespace.retry_wait:
            self.stn_dict['retry_wait'] = self.namespace.retry_wait
        if self.namespace.timeout:
            self.stn_dict['url_timeout'] = self.namespace.timeout
        # initialise a variable to hold our EcowittHttpDriver object
        driver = None
        # wrap in a try..except in case there is an error
        try:
            # get an EcowittHttpDriver object
            driver = EcowittHttpDriver(**self.stn_dict)
            # identify the device being used
            print()
            print(f'Interrogating {bcolors.BOLD}{driver.collector.device.model}{bcolors.ENDC} '
                  f'at {bcolors.BOLD}{driver.collector.device.ip_address}{bcolors.ENDC}')
            print()
            # continuously get loop packets and print them to console
            for pkt in driver.genLoopPackets():
                print(f'{weeutil.weeutil.timestamp_to_string(pkt["dateTime"])}: '
                      f'{weeutil.weeutil.to_sorted_string(pkt)}')
        except DeviceIOError as e:
            print()
            print(f'Unable to connect to device: {e}')
            print()
            self.device_connection_help()
        except KeyboardInterrupt:
            # we have a keyboard interrupt, we need to shutdown
            pass
        finally:
            if driver is not None:
                driver.closePort()
        log.info('Ecowitt HTTP driver testing complete')

    def test_service(self):
        """Exercise the Ecowitt HTTP driver as a service.

        Uses a dummy engine/simulator to generate arbitrary loop packets for
        augmenting. Use a 10-second loop interval so we don't get too many bare
        packets.
        """

        log.info('Testing Ecowitt HTTP driver as a service...')
        # Create a dummy config, so we can stand up a dummy engine with a dummy
        # simulator emitting arbitrary loop packets. Include the Ecowitt HTTP
        # service and StdPrint. StdPrint will take care of printing our loop
        # packets (no StdArchive so loop packets only, no archive records)
        config = {
            'Station': {
                'station_type': 'Simulator',
                'altitude': [0, 'meter'],
                'latitude': 0,
                'longitude': 0},
            'Simulator': {
                'driver': 'weewx.drivers.simulator',
                'mode': 'simulator'},
            'EcowittHttp': {},
            'Engine': {
                'Services': {
                    'archive_services': 'user.ecowitt_http.EcowittHttpService',
                    'report_services': 'weewx.engine.StdPrint'}}}
        # set the IP address and port in the dummy config
        config['EcowittHttp']['ip_address'] = self.ip_address
        # these command line options should only be added if they exist
        if self.namespace.poll_interval:
            config['EcowittHttp']['poll_interval'] = self.namespace.poll_interval
        if self.namespace.max_tries:
            config['EcowittHttp']['max_tries'] = self.namespace.max_tries
        if self.namespace.retry_wait:
            config['EcowittHttp']['retry_wait'] = self.namespace.retry_wait
        # assign our dummyTemp field to a unit group so unit conversion works
        # properly
        weewx.units.obs_group_dict['dummyTemp'] = 'group_temperature'
        # initialise a variable to hold an instance of StdEngine
        engine = None
        # wrap in a try..except in case there is an error
        try:
            # create a dummy engine
            engine = weewx.engine.StdEngine(config)
            # Our Ecowitt HTTP service will have been instantiated by the
            # engine during its startup. Whilst access to the service is not
            # normally required we require access here, so we can obtain some
            # info about the station we are using for this test. The engine
            # does not provide a ready means to access that service, so we can
            # do a bit of guessing and iterate over all the engine's services
            # and select the one that has a 'collector' property. Unlikely to
            # cause a problem since there are only two services in the dummy
            # engine.
            http_svc = None
            for svc in engine.service_obj:
                if hasattr(svc, 'collector'):
                    http_svc = svc
            if http_svc is not None:
                # identify the device being used
                print()
                print(f'Interrogating {bcolors.BOLD}{http_svc.collector.device.model}{bcolors.ENDC} '
                      f'at {bcolors.BOLD}{http_svc.collector.device.ip_address}{bcolors.ENDC}')
            print()
            while True:
                # create an arbitrary loop packet, all it needs is a timestamp, a
                # defined unit system and a token obs
                packet = {'dateTime': int(time.time()),
                          'usUnits': weewx.US,
                          'dummyTemp': 96.3
                          }
                # send out a NEW_LOOP_PACKET event with the dummy loop packet
                # to trigger the Ecowitt local HTTP API service to augment the
                # loop packet
                engine.dispatchEvent(weewx.Event(weewx.NEW_LOOP_PACKET,
                                                 packet=packet,
                                                 origin='software'))
                # sleep for a bit to emulate the simulator
                time.sleep(10)
        except DeviceIOError as e:
            print()
            print(f'Unable to connect to device: {e}')
            print()
            self.device_connection_help()
        except KeyboardInterrupt:
            pass
        finally:
            if engine:
                engine.shutDown()
        log.info('Ecowitt HTTP driver service testing complete')

    def weewx_fields(self):
        """Display WeeWX loop packet fields emitted when used as a driver.

        Exercises the Ecowitt HTTP driver as a driver and displays the WeeWX
        fields to be emitted in loop packets using the specified WeeWX config
        file. A station config dict is coalesced from any relevant command line
        parameters and the config file in use with command line parameters
        overriding those in the config file.
        """

        log.info('Displaying WeeWX loop packet fields emitted by the Ecowitt HTTP driver...')
        # we already have a station config dict, but we will accept a command
        # line specified device IP address if provided
        self.stn_dict['ip_address'] = self.ip_address
        # initialise a variable to hold the driver object
        driver = None
        # obtain an EcowittHttpDriver object and get a single loop packet, wrap
        # in a try..except in case there is an error
        try:
            # get an EcowittHttpDriver object
            driver = EcowittHttpDriver(**self.stn_dict)
            # identify the device being used
            print()
            print(f'Interrogating {bcolors.BOLD}{driver.collector.device.model}{bcolors.ENDC} '
                  f'at {bcolors.BOLD}{driver.collector.device.ip_address}{bcolors.ENDC}')
            print()
            # continuously get loop packets but we will exit after we have the
            # first and presented our output
            for pkt in driver.genLoopPackets():
                # get a suitable converter based on our output units
                if self.namespace.units.lower() == 'us':
                    _unit_system = weewx.US
                elif self.namespace.units.lower() == 'metric':
                    _unit_system = weewx.METRIC
                else:
                    _unit_system = weewx.METRICWX
                c = weewx.units.StdUnitConverters[_unit_system]
                # Now get a formatter, we could use the default formatter, but we
                # need voltages formatted to two decimal places. So create a custom
                # formatter using a modified defaults StringFormats stanza and the
                # defaults Labels stanza.
                # obtain a copy of the defaults StringFormats stanza
                _unit_format_dict = dict(weewx.defaults.defaults['Units']['StringFormats'])
                # modify the 'volt' format
                _unit_format_dict['volt'] = '%.2f'
                _unit_format_dict['microgram_per_meter_cubed'] = '%.1f'
                # obtain a custom formatter
                f = weewx.units.Formatter(unit_format_dict=_unit_format_dict,
                                          unit_label_dict=weewx.defaults.defaults['Units']['Labels'])
                # now build a new data dict with our converted and formatted data
                result = {}
                # iterate over the fields in our original data dict
                for key in pkt.keys():
                    # we don't need usUnits in the result so skip it
                    if key == 'usUnits':
                        continue
                    # get our key as a ValueTuple
                    key_vt = weewx.units.as_value_tuple(pkt, key)
                    # get a ValueHelper which will do the conversion and formatting
                    key_vh = weewx.units.ValueHelper(key_vt, formatter=f, converter=c)
                    # and add the converted and formatted value to our dict
                    try:
                        result[key] = key_vh.toString(None_string='None')
                    except:
                        result[key] = f"Unable to convert/format '{key}'"
                        continue
                # display the packet key value pairs in natural key sort order
                for key in natural_sort_keys(result):
                    print(f'{key:>25}: {result[key]}')
                break
        except DeviceIOError as e:
            print()
            print(f'Unable to connect to device: {e}')
            print()
            self.device_connection_help()
        finally:
            # before we exit shutdown the driver
            if driver:
                driver.closePort()

    @staticmethod
    def device_connection_help():
        """Console output help message for device connection problems."""

        print('    Things to check include that the correct device IP address is being used,')
        print('    the device is powered on and the device is not otherwise disconnected from')
        print('    the local network.')


# To use this driver in standalone mode for testing or development, use one of
# the following commands (depending on your WeeWX install type):
#
#   for pip installs use:
#       $ source ~/weewx-venv/bin/activate
#       $ python3 -m user.ecowitt_http
#   for git installs use:
#       $ source ~/weewx-venv/bin/activate
#       $ PYTHONPATH=~/weewx/src:~/weewx-data/bin python3 -m user.ecowitt_http
#   for package installs use:
#       $ python3 -m user.ecowitt_http
#
# The above commands will run the driver directly and display details of
# available command line options.
#
# Note. Whilst the driver may be run independently of WeeWX the driver still
# requires WeeWX and it's dependencies be installed. Consequently, the driver
# must be run under the same Python installation (or Python virtual
# environment) as used by WeeWX.

def main():
    import argparse

    usage = f"""{bcolors.BOLD}%(prog)s --help
                --version
                --test-driver|--test-service
                     [CONFIG_FILE|--config=CONFIG_FILE]
                     [--ip-address=IP_ADDRESS] [--poll-interval=INTERVAL]
                     [--max-tries=MAX_TRIES] [--retry-wait=RETRY_WAIT]
                     [--show-all-batt] [--debug=0|1|2|3]
                --live-data
                     [CONFIG_FILE|--config=CONFIG_FILE]
                     [--units=us|metric|metricwx]
                     [--ip-address=IP_ADDRESS]
                     [--show-all-batt] [--debug=0|1|2|3]
                --weewx-fields
                     [CONFIG_FILE|--config=CONFIG_FILE]
                     [--ip-address=IP_ADDRESS]
                     [--show-all-batt] [--debug=0|1|2|3]
                --default-map|--driver-map|--service-map
                     [CONFIG_FILE|--config=CONFIG_FILE]
                     [--debug=0|1|2|3]
                --discover
                     [CONFIG_FILE|--config=CONFIG_FILE]
                     [--debug=0|1|2|3]{bcolors.ENDC}
    """
    description = """Interact with an Ecowitt device via the Ecowitt local HTTP API."""
    parser = argparse.ArgumentParser(usage=usage,
                                     description=description,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--version',
                            dest='version',
                            action='store_true',
                            help='display driver version number')
    parser.add_argument('--discover',
                        dest='discover',
                        action='store_true',
                        help='display details of discovered devices')
    parser.add_argument('--live-data',
                        dest='live',
                        action='store_true',
                        help='display device live sensor data')
    parser.add_argument('--sensors',
                        dest='sensors',
                        action='store_true',
                        help='display device sensor data')
    parser.add_argument('--test-driver',
                        dest='test_driver',
                        action='store_true',
                        help='exercise the driver')
    parser.add_argument('--test-service',
                        dest='test_service',
                        action='store_true',
                        help='exercise the driver as a WeeWX service')
    parser.add_argument('--weewx-fields',
                        dest='weewx_fields',
                        action='store_true',
                        help='display WeeWX loop packet fields emitted by the '
                             'current configuration')
    parser.add_argument('--default-map',
                        dest='map',
                        action='store_true',
                        help='display the default field map')
    parser.add_argument('--driver-map',
                        dest='driver_map',
                        action='store_true',
                        help='display the field map that would be used by the '
                             'driver')
    parser.add_argument('--service-map',
                        dest='service_map',
                        action='store_true',
                        help='display the field map that would be used by the '
                             'service')
    parser.add_argument('--firmware',
                        dest='firmware',
                        action='store_true',
                        help='display device firmware information')
    parser.add_argument('--mac',
                        dest='mac',
                        action='store_true',
                        help='display device MAC address')
    parser.add_argument('--system',
                        dest='sys_params',
                        action='store_true',
                        help='display device system parameters')
    parser.add_argument('--get-rain-totals',
                        dest='rain_totals',
                        action='store_true',
                        help='display rain gauge totals and gains, rainfall'
                             'priority and rainfall reset times')
    parser.add_argument('--get-calibration',
                        dest='calibration',
                        action='store_true',
                        help='display device calibration data')
    parser.add_argument('--get-th-cal',
                        dest='mulch_offset',
                        action='store_true',
                        help='display device multi-channel temperature and '
                             'humidity calibration data')
    parser.add_argument('--get-soil-cal',
                        dest='soil_calibration',
                        action='store_true',
                        help='display device multi-channel soil moisture '
                             'calibration data')
    parser.add_argument('--get-t-cal',
                        dest='temp_calibration',
                        action='store_true',
                        help='display device multi-channel temperature '
                             'calibration data')
    parser.add_argument('--get-pm25-cal',
                        dest='pm25_offset',
                        action='store_true',
                        help='display device multi-channel PM2.5 calibration '
                             'data')
    parser.add_argument('--get-co2-cal',
                        dest='co2_offset',
                        action='store_true',
                        help='display device CO2 (WH45) calibration data')
    parser.add_argument('--get-lds-cal',
                        dest='lds_offset',
                        action='store_true',
                        help='display device LDS (WH54) calibration data')
    parser.add_argument('--get-services',
                        dest='services',
                        action='store_true',
                        help='display device weather services configuration '
                             'data')
    parser.add_argument('--ip-address',
                        dest='ip_address',
                        help='device IP address to use')
    parser.add_argument('--poll-interval',
                        dest='poll_interval',
                        type=int,
                        help='how often to poll the device API')
    parser.add_argument('--max-tries',
                        dest='max_tries',
                        type=int,
                        default=DEFAULT_MAX_TRIES,
                        help='max number of attempts to contact the device')
    parser.add_argument('--retry-wait',
                        dest='retry_wait',
                        type=int,
                        help='how long to wait between attempts to contact the device')
    parser.add_argument('--timeout',
                        dest='timeout',
                        type=int,
                        help='how long to wait for the device to respond to a HTTP request')
    parser.add_argument('--discovery-port',
                        dest='discovery_port',
                        type=int,
                        default=DEFAULT_DISCOVERY_PORT,
                        help='port to listen to when discovering devices')
    parser.add_argument('--discovery-timeout',
                        dest='discovery_timeout',
                        type=int,
                        default=DEFAULT_DISCOVERY_TIMEOUT,
                        help='how long to listen when discovering devices')
    parser.add_argument('--show-all-batt',
                        dest='show_battery',
                        action='store_true',
                        help='show all available battery state data regardless of '
                             'sensor state')
    parser.add_argument('--registered-only',
                        dest='registered_only',
                        action='store_true',
                        help='show only registered sensors')
    parser.add_argument('--unmask',
                        dest='unmask',
                        action='store_true',
                        help='unmask sensitive settings')
    parser.add_argument('--units',
                        dest='units',
                        metavar='UNIT SYSTEM',
                        default=weewx.units.unit_nicknames[DEFAULT_UNIT_SYSTEM],
                        help='unit system to use when displaying live data')
    parser.add_argument('--config',
                        dest='config',
                        metavar='CONFIG_FILE',
                        help="Use configuration file CONFIG_FILE.")
    parser.add_argument('--debug',
                        dest='driver_debug',
                        type=int,
                        default=0,
                        help='How much status to display, 0-3')
    namespace = parser.parse_args()

    if len(sys.argv) == 1:
        # we have no arguments, display the help text and exit
        parser.print_help()
        sys.exit(0)

    # if we have been asked for the version number we can display that now
    if namespace.version:
        print(f'{DRIVER_NAME} driver version {DRIVER_VERSION}')
        sys.exit(0)

    # any other option will require the config_dict, get the config_dict now
    config_path, config_dict = weecfg.read_config(namespace.config)
    print(f'Using configuration file {bcolors.BOLD}{config_path}{bcolors.ENDC}')
    stn_config_dict = config_dict.get('EcowittHttp', {})
    # set weewx.debug as necessary
    if namespace.driver_debug is not None:
        _debug = weeutil.weeutil.to_int(namespace.driver_debug)
    else:
        _debug = weeutil.weeutil.to_int(config_dict.get('debug', 0))
    weewx.debug = _debug
    # inform the user if the debug level is 'higher' than 0
    if _debug > 0:
        print(f'debug level is {_debug:d}')

    # set up user customized logging
    weeutil.logger.setup('ecowitt_http', config_dict)

    # define custom unit settings used by the driver
    define_units()

    # get a DirectEcowittDevice object
    direct_device = DirectEcowittDevice(namespace, parser, stn_config_dict)
    # now let the DirectEcowittDevice object process the options
    direct_device.process_options()


if __name__ == '__main__':
    main()
