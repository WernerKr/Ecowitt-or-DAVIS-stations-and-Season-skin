#
#    Copyright (c) 2009-2021 Tom Keffer <tkeffer@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

"""User extensions module

This module is imported from the main executable, so anything put here will be
executed before anything else happens. This makes it a good place to put user
extensions.
"""

import locale
# This will use the locale specified by the environment variable 'LANG'
# Other options are possible. See:
# http://docs.python.org/2/library/locale.html#locale.setlocale
locale.setlocale(locale.LC_ALL, '')

#
#"group_percent"     : "percent",		'] = 'group_percent'
#"group_volt"        : "volt",		'] = 'group_volt'
#"group_time"        : "unix_epoch",	'] = 'group_time'
#"group_fraction"    : "ppm",		'] = 'group_fraction'
#"group_count"       : "count",		'] = 'group_count'
#"group_distance"    : "km",		'] = 'group_distance'
#"group_speed2"      : "km_per_hour2",	'] = 'group_speed2'
#"group_rain"        : "cm",              '] = 'group_rain'
#"group_rainrate"    : "cm_per_hour",     '] = 'group_rainrate'

import weewx.units
weewx.units.obs_group_dict['sunshine_hours'] = 'group_radiation'
weewx.units.obs_group_dict['sunshine_time'] = 'group_interval'

weewx.units.obs_group_dict['co2'] = 'group_fraction'
weewx.units.obs_group_dict['co2_24h'] = 'group_fraction'
weewx.units.obs_group_dict['co2_Temp'] = 'group_temperature'
weewx.units.obs_group_dict['co2_Hum'] = 'group_percent'

weewx.units.obs_group_dict['pm2_5'] = 'group_concentration'
weewx.units.obs_group_dict['pm10_0'] = 'group_concentration'
weewx.units.obs_group_dict['pm25_1'] = 'group_concentration'
weewx.units.obs_group_dict['pm25_2'] = 'group_concentration'
weewx.units.obs_group_dict['pm25_3'] = 'group_concentration'
weewx.units.obs_group_dict['pm25_4'] = 'group_concentration'

weewx.units.obs_group_dict['pm25_24h_co2'] = 'group_concentration'
weewx.units.obs_group_dict['pm10_24h_co2'] = 'group_concentration'
weewx.units.obs_group_dict['pm25_avg_24h_ch1'] = 'group_concentration'
weewx.units.obs_group_dict['pm25_avg_24h_ch2'] = 'group_concentration'
weewx.units.obs_group_dict['pm25_avg_24h_ch3'] = 'group_concentration'
weewx.units.obs_group_dict['pm25_avg_24h_ch4'] = 'group_concentration'

weewx.units.obs_group_dict['soilTemp1'] = 'group_temperature'
weewx.units.obs_group_dict['soilTemp2'] = 'group_temperature'
weewx.units.obs_group_dict['soilTemp3'] = 'group_temperature'
weewx.units.obs_group_dict['soilTemp4'] = 'group_temperature'
weewx.units.obs_group_dict['soilTemp5'] = 'group_temperature'
weewx.units.obs_group_dict['soilTemp6'] = 'group_temperature'
weewx.units.obs_group_dict['soilTemp7'] = 'group_temperature'
weewx.units.obs_group_dict['soilTemp8'] = 'group_temperature'
#weewx.units.obs_group_dict['leafWet1'] = 'group_percent'
#weewx.units.obs_group_dict['leafWet2'] = 'group_percent'
weewx.units.obs_group_dict['leafWet3'] = 'group_percent'
weewx.units.obs_group_dict['leafWet4'] = 'group_percent'
weewx.units.obs_group_dict['leafWet5'] = 'group_percent'
weewx.units.obs_group_dict['leafWet6'] = 'group_percent'
weewx.units.obs_group_dict['leafWet7'] = 'group_percent'
weewx.units.obs_group_dict['leafWet8'] = 'group_percent'
#weewx.units.obs_group_dict['soilMoist1'] = 'group_percent'
#weewx.units.obs_group_dict['soilMoist2'] = 'group_percent'
#weewx.units.obs_group_dict['soilMoist3'] = 'group_percent'
#weewx.units.obs_group_dict['soilMoist4'] = 'group_percent'
weewx.units.obs_group_dict['soilMoist5'] = 'group_percent'
weewx.units.obs_group_dict['soilMoist6'] = 'group_percent'
weewx.units.obs_group_dict['soilMoist7'] = 'group_percent'
weewx.units.obs_group_dict['soilMoist8'] = 'group_percent'
weewx.units.obs_group_dict['lightning_distance'] = 'group_count'
weewx.units.obs_group_dict['lightning_disturber_count'] = 'group_time'
weewx.units.obs_group_dict['lightning_strike_count'] = 'group_count'
weewx.units.obs_group_dict['runtime'] = 'group_deltatime'

weewx.units.obs_group_dict['rainrate'] = 'group_rainrate'
weewx.units.obs_group_dict['eventRain'] = 'group_rain'
weewx.units.obs_group_dict['weekRain'] = 'group_rain'
weewx.units.obs_group_dict['raintotal'] = 'group_rain'
weewx.units.obs_group_dict['rainBatteryStatus'] = 'group_volt'
weewx.units.obs_group_dict['hailBatteryStatus'] = 'group_volt'
weewx.units.obs_group_dict['windBatteryStatus'] = 'group_volt'
weewx.units.obs_group_dict['ws80_batt'] = 'group_volt'
weewx.units.obs_group_dict['ws90_batt'] = 'group_volt'
weewx.units.obs_group_dict['ws1900batt'] = 'group_volt'

weewx.units.obs_group_dict['rrain_piezo'] = 'group_rainrate'
weewx.units.obs_group_dict['erain_piezo'] = 'group_rain'
weewx.units.obs_group_dict['hrain_piezo'] = 'group_rain'
weewx.units.obs_group_dict['drain_piezo'] = 'group_rain'
weewx.units.obs_group_dict['wrain_piezo'] = 'group_rain'
weewx.units.obs_group_dict['mrain_piezo'] = 'group_rain'
weewx.units.obs_group_dict['yrain_piezo'] = 'group_rain'
weewx.units.obs_group_dict['rain_piezo'] = 'group_rain'

weewx.units.obs_group_dict['ws90cap_volt'] = 'group_volt'
weewx.units.obs_group_dict['ws90_ver'] = 'group_count'

weewx.units.obs_group_dict['soilMoistBatt1'] = 'group_volt'
weewx.units.obs_group_dict['soilMoistBatt2'] = 'group_volt'
weewx.units.obs_group_dict['soilMoistBatt3'] = 'group_volt'
weewx.units.obs_group_dict['soilMoistBatt4'] = 'group_volt'
weewx.units.obs_group_dict['soilMoistBatt5'] = 'group_volt'
weewx.units.obs_group_dict['soilMoistBatt6'] = 'group_volt'
weewx.units.obs_group_dict['soilMoistBatt7'] = 'group_volt'
weewx.units.obs_group_dict['soilMoistBatt8'] = 'group_volt'
weewx.units.obs_group_dict['soilTempBatt1'] = 'group_volt'
weewx.units.obs_group_dict['soilTempBatt2'] = 'group_volt'
weewx.units.obs_group_dict['soilTempBatt3'] = 'group_volt'
weewx.units.obs_group_dict['soilTempBatt4'] = 'group_volt'
weewx.units.obs_group_dict['soilTempBatt5'] = 'group_volt'
weewx.units.obs_group_dict['soilTempBatt6'] = 'group_volt'
weewx.units.obs_group_dict['soilTempBatt7'] = 'group_volt'
weewx.units.obs_group_dict['soilTempBatt8'] = 'group_volt'
weewx.units.obs_group_dict['leafWetBatt1'] = 'group_volt'
weewx.units.obs_group_dict['leafWetBatt2'] = 'group_volt'
weewx.units.obs_group_dict['leafWetBatt3'] = 'group_volt'
weewx.units.obs_group_dict['leafWetBatt4'] = 'group_volt'
weewx.units.obs_group_dict['leafWetBatt5'] = 'group_volt'
weewx.units.obs_group_dict['leafWetBatt6'] = 'group_volt'
weewx.units.obs_group_dict['leafWetBatt7'] = 'group_volt'
weewx.units.obs_group_dict['leafWetBatt8'] = 'group_volt'

weewx.units.obs_group_dict['maxdailygust'] = 'group_speed2'
weewx.units.obs_group_dict['winddir_avg10m'] = 'group_direction'
weewx.units.obs_group_dict['windspdmph_avg10m'] = 'group_speed2'

weewx.units.obs_group_dict['co2_Batt'] = 'group_count'
weewx.units.obs_group_dict['pm25_Batt1'] = 'group_count'
weewx.units.obs_group_dict['pm25_Batt2'] = 'group_count'
weewx.units.obs_group_dict['pm25_Batt3'] = 'group_count'
weewx.units.obs_group_dict['pm25_Batt4'] = 'group_count'
#weewx.units.obs_group_dict['leak_1'] = 'group_count'
#weewx.units.obs_group_dict['leak_2'] = 'group_count'
#weewx.units.obs_group_dict['leak_3'] = 'group_count'
#weewx.units.obs_group_dict['leak_4'] = 'group_count'
weewx.units.obs_group_dict['leak_Batt1'] = 'group_count'
weewx.units.obs_group_dict['leak_Batt2'] = 'group_count'
weewx.units.obs_group_dict['leak_Batt3'] = 'group_count'
weewx.units.obs_group_dict['leak_Batt4'] = 'group_count'
weewx.units.obs_group_dict['lightning_Batt'] = 'group_count'

# VantagePro
weewx.units.obs_group_dict['stormRain'] = 'group_rain'
weewx.units.obs_group_dict['stormRainlast'] = 'group_rain'
weewx.units.obs_group_dict['rain24'] = 'group_rain'
weewx.units.obs_group_dict['rain60'] = 'group_rain'
weewx.units.obs_group_dict['rain15'] = 'group_rain'
weewx.units.obs_group_dict['hourRain'] = 'group_rain'
weewx.units.obs_group_dict['totalRain'] = 'group_rain'
weewx.units.obs_group_dict['monthET'] = 'group_rain'
weewx.units.obs_group_dict['yearET'] = 'group_rain'
weewx.units.obs_group_dict['stormStart'] = 'group_time'
weewx.units.obs_group_dict['windSpeed2'] = 'group_speed2'



