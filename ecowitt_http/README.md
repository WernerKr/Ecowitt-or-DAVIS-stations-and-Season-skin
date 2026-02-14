## Driver ecowitt_http
forked from 
https://github.com/gjr80/weewx-ecowitt_local_http/blob/master

(C) 2024-25 Gary Roderick                     gjroderick<at>gmail.com

### For this driver there is also a database schema "weewx_ecowitt.py" or "weewx_ecowittrssi.py" or "weewx_ecowittrssisoilad.py"
https://github.com/WernerKr/Ecowitt-or-DAVIS-stations-and-Season-skin/blob/main/ecowitt_http/wview_ecowitt.py

under https://github.com/WernerKr/Ecowitt-or-DAVIS-stations-and-Season-skin

you can find script files that extend an existing database schema for the values of Ecowitt stations 

    X  May 2025            v0.1.0a28  Gary Roderick
	
    July 2025
        - WH45/WH46 = co2 missed - added
        - changed some keys that are the same as my ecowittcustom driver
        - add some keys
        - completed all data from the SDcard GW3000
        - completed all data from the device 
    
    4 July 2025           
        - corrected radiation
        - corrected co2_Temp
        - corrected wh51 - forget to add sensors wh51 at sensors
        - corrected signal to None if signal id is "FFFFFFFE" or "FFFFFFFF"
        - add some unit-settings
        - corrected rain, piezo_rain, lightning_count for loop packets
    
    5 July 2025
        - add missed wh40_sig
        - changed daymaxwind to maxdailygust (because customecowitt driver)
        - hail, hailrate is Piezo Rain too
        - add wh40_batt, wh80_batt, wh85_batt, wh95_bat
        - now is 'hailBatteryStatus': 'piezoRain.0x13.voltage',
        - add correction for rain, piezo_rain, lightning_count with data from sdcard
    
    6 July 2025
        - added more values (soilmoist9..soilmoist16, ...) to history data
          added debug option "archive"
    
    7 July 2025 
        - added voltage for/from leaf sensors
        - increased the default url_timeout to 10 - but seems do be better with 20 
        - corrected history - mapping from ecowitt.net
    
    8 July 2025
        - added ws85_ver, ws90_ver, radiationcompensation, upgrade, newVersion,
                rain_source, rain_priority, rain_day_reset, rain_week_reset, rain_annual_reset,
                piezo, raingain, gain0, gain1, gain2, gain3, gain4
                to the supported fields, because compatible with Ecowitt Custom Driver and the GW1000 Driver
       - if app_key, api_key or mac are not set, no further attempts will be made to retrieve data from Ecowitt.net
    
    10 July 2025            v0.1.0
        - initial release
    
    11 July 2025	    v0.1.1
        - corrected lightning 
    
    12 July 2025		v0.1.2
        - piezo, leak_Batt3, rain, piezo rain wasn't set to new value
    
    13 July 2025		v0.1.3
        - calc vpd if data from Ecowitt.net - because this value is not provided.
        - changed lighting_distance to lighting_dist 
    
    14 July 2025		v0.1.4         
        - 'ch_lds1', 'ch_lds2', 'ch_lds3', 'ch_lds4' from Ecowitt.net added
        - wh68_batt, wh69_batt
    
    15 July 2025		v0.1.5     
        - p_rain is back  (for people who used this field )
    
    25 July 2025		v0.1.6     
        - new rssi, rain voltage, winddir_avg10m, last24hrainin, last24hrain_piezo, LDS total_heat, wn20 (Mini rain)      
          ws85cap_volt, ws90cap_volt 
    
    31 July 2025            v0.2.0
        - Compatibility with WeeWx 4.x established!
        - test_service: 
          Distinguishes between WeeWx V4.x and V5.x
        - correction for rain, hail (p_rain). This data was missed, wenn data from SDcard 
        - new debug Option: raindelta
    
    07 Aug 2025            v0.2.1
        - wn31_sig and wn31_rssi renamed to wh31_sig and wh31_rssi
        - missed co2_Batt, wh45_sig, wh45_rssi added
    
    08 Aug 2025            v0.2.2
        - dB -> dBm
    
    21 Aug 2025            v0.2.3
        - correction if lightning timestamp = "--/--/---- --:--:--"
        - Error message hidden: process_lightning_array: Error processing distance: Could not convert '--.-' to a float
        - added console_batt, consoleext_batt, charge_stat (WS6210)
    
    04 Oct 2025            v0.2.4
        - if driver is used as a service, Rain and Piezo Rain are only mapped as t_rain and p_rain in loop data, 
          in archive ( SDcard, cloud ) Rain and Hail are still mapped as rain and hail! 
          Reason for this: if Ecowittcustom is used as a station, Rain and Piezo Rain are recorded multiple times.
        - new Sensor wn38 (BGT)
        - bug with 'PM2.5 ch1' .. 'ch4' and Data from SDCard solved (correct is 'PM2.5 CH1' )
        - added soilad1..16

    13 Oct 2025            v0.2.5
	    - added apName - need 
          [Accumulator]
            [[apName]]
              accumulator = firstlast
              extractor = last
        - added stationtype 
		  After firmware update (and not restart weewx) then shows the current hardware version
        - Calculates WBGT when not transmitted
        - 24h rain (piezo) from Ecowitt cloud
        - workaround if no SDCard inserted (thanks to rosensama )  
	22 Oct 2025            v0.2.6
        - Checks if a soil moisture sensor is present and if not, no further attempts are made 
          to query the soilad values
    27 Oct 2025            v0.2.7
        - Stored Lightning time (lightning_disturber_count) didn't use local time
		  workaround for firmware bug: This affects all current firmware versions of the gateways
    10 Nov 2025            v0.2.8
        - Correction for WS6210 and SDCard data (now supports downloads from SDCard - but PM2.5 1..4 here are missing!)
        - for WS6210 use ecowittws6210_http driver -> With Firmware V1.1.1.2: 
		  here uses original Thunder time and too PM2.5 1..4 
		  because this data differs from the other Ecowitt supported gateways/stations 
    30 Nov 2025            v0.2.9
        - added rain_batt and piezorain_bat (0..5)
        - lightning_distance/lightning_dist group_count changed to group_distance  
    30 Dec 2025            v0.3.0
        - livedata 0xA1, 0xA2 -> WN38 Sensor = BGT Sensor
		  
Tested and completed:
```
PYTHONPATH=/usr/share/weewx python3 /etc/weewx/bin/user/ecowitt_http.py --ip-address=%IP-GW% --live-data
PYTHONPATH=/usr/share/weewx python3 /etc/weewx/bin/user/ecowitt_http.py --ip-address=%IP-GW% --weewx-fields
PYTHONPATH=/usr/share/weewx python3 /etc/weewx/bin/user/ecowitt_http.py --ip-address=%IP-GW% --firmware
PYTHONPATH=/usr/share/weewx python3 /etc/weewx/bin/user/ecowitt_http.py --ip-address=%IP-GW% --mac
PYTHONPATH=/usr/share/weewx python3 /etc/weewx/bin/user/ecowitt_http.py --ip-address=%IP-GW% --system
PYTHONPATH=/usr/share/weewx python3 /etc/weewx/bin/user/ecowitt_http.py --ip-address=%IP-GW% --sensors
PYTHONPATH=/usr/share/weewx python3 /etc/weewx/bin/user/ecowitt_http.py --ip-address=%IP-GW% --get-rain-totals
PYTHONPATH=/usr/share/weewx python3 /etc/weewx/bin/user/ecowitt_http.py --discover

PYTHONPATH=/usr/share/weewx python3 /etc/weewx/bin/user/ecowitt_http.py --ip-address=%IP-GW% --discover
PYTHONPATH=/usr/share/weewx python3 /etc/weewx/bin/user/ecowitt_http.py --ip-address=%IP-GW% --default-map
PYTHONPATH=/usr/share/weewx python3 /etc/weewx/bin/user/ecowitt_http.py --ip-address=%IP-GW% --driver-map
PYTHONPATH=/usr/share/weewx python3 /etc/weewx/bin/user/ecowitt_http.py --ip-address=%IP-GW% --service-map
PYTHONPATH=/usr/share/weewx python3 /etc/weewx/bin/user/ecowitt_http.py --ip-address=%IP-GW% --get-services

PYTHONPATH=/usr/share/weewx python3 /etc/weewx/bin/user/ecowitt_http.py --ip-address=%IP-GW% --weewx-fields
PYTHONPATH=/usr/share/weewx python3 /etc/weewx/bin/user/ecowitt_http.py --ip-address=%IP-GW% --test-driver
PYTHONPATH=/usr/share/weewx python3 /etc/weewx/bin/user/ecowitt_http.py --ip-address=%IP-GW% --test-service

WeeWx 4.x.x example (and all the same as WeeWx5):
PYTHONPATH=/usr/share/weewx python3 -m user.ecowitt_http --ip-address=%IP-GW% --test-service
PYTHONPATH=/usr/share/weewx python3 -m user.ecowitt_http --ip-address=%IP-GW% --sensors
```

### To get api_key, app_key for Ecowitt.net:
https://doc.ecowitt.net/web/#/apiv3en?page_id=11
```
Getting Started
1. Register for developer’s account
Please go to Ecowitt.net platform, Register and Login.

2. Create Application Key and API key
Go to “Private Center”, and generate your:

Application Key: key for identifying application scenario, and it must be used together with API key together.
API Key: key for identifying user profile, interface privilege, and must work with Application Key.
```

### Settings in weewx.conf

```
# The WeeWX 'loop_on_init' setting can be used to mitigate such
# problems by having WeeWX retry startup indefinitely. Set to '0' to attempt
# startup once only or '1' to attempt startup indefinitely.
# Whether to try indefinitely to load the driver
loop_on_init = 1

[Station]
    station_type = EcowittHttp

[EcowittHttp]
    # the driver to use
    driver = user.ecowitt_http
   
    # how often to poll the device
    poll_interval = 20
    # how many attempts to contact the device before giving up
    max_tries = 3
    # wait time in seconds between retries to contact the device
    retry_wait = 5
    # max wait for device to respond to a HTTP request
    url_timeout = 10
    
    # whether to show all battery state data including nonsense data and 
    # sensors that are disabled sensors and connecting
    show_all_batt = False

    # whether to always log unknown API fields, unknown fields are always 
    # logged at the debug level, this will log them at the info level
    log_unknown_fields = True

    # How often to check for device firmware updates, 0 disables firmware 
    # update checks. Available firmware updates are logged.
    firmware_update_check_interval = 86400

    # do we show registered sensor data only
    only_registered = False

    # Is a WN32P used for indoor temperature, humidity and pressure - default = False   
    #wn32_indoor = True
    # Is a WN32 used for outdoor temperature and humidity - default = False
    #wn32_outdoor = True

    #former debug_logging (here for wind) not more supported!:
    #debug_wind = False

    #debug_logging new with list:
    #debug = rain, wind, loop, sensors, parser, catchup, collector, archive

    debug = parser, sensors, catchup  

    catchup_grace = 0

    ip_address = 192.168.0.110
    api_key = 00000000-1111-2222-3333-444444444444
    app_key = DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD
    mac = 5C:01:3B:46:C3:FF

   [[catchup]]
     # source = either, both, net, device  ## not set = None, default is then either or both

##########################################################################
[StdReport]

    [[SeasonsEcowitt]]
        # lang = de
        lang = en
        skin = SeasonsEcowitt
        enable = false
        HTML_ROOT = /var/www/html/weewx

##########################################################################
[StdArchive]
    record_generation = software

##########################################################################
# If the driver is to be used as a service 
[Engine]
    [[Services]]
        data_services = user.ecowitt_http.EcowittHttpService

###########################################################################
[StdCalibrate]
    
    [[Corrections]]
        foo = foo + 0.2
        luminosity = radiation * 126.7
        
        rxCheckPercent = ws80_sig * 25 if ws80_sig is not None else None
        
        # rxCheckPercent = wh25_sig * 25 if wh25_sig is not None else None
        # rxCheckPercent = wh68_sig * 25 if wh68_sig is not None else None
        # rxCheckPercent = wh65_sig * 25 if wh65_sig is not None else None
        
        # hail = p_rain if p_rain is not None else None                  # mapped in driver
        # hailRate = p_rainrate if p_rainrate is not None else None      # mapped in driver

        # from v0.2.4  is this required if the driver is used as a Data_Service
        # data_services = user.ecowitt_http.EcowittHttpService
        #rain = t_rain if t_rain is not None
        #hail = p_rain if p_rain is not None #if hail is used as default piezo rain

        pb = heap if heap is not None else None
        lightning_distance_save = lightning_dist if lightning_dist is not None else None
        lightning_distance = lightning_dist if lightning_strike_count > 0 else None 
        #lightning_distance_save = lightning_distance if lightning_distance is not None else None        #old setting
        #lightning_distance = lightning_distance if lightning_strike_count > 0 else None                 #old setting
        lightning_noise_count = lightning_strike_count if lightning_strike_count > 0 else None

        #example to get signals in procent: 
        #signal1 = ws80_sig * 25 if ws80_sig is not None else None
        #signal2 = wh31_ch1_sig * 25 if wh31_ch1_sig is not None else None
        #signal3 = wn34_ch1_sig * 25 if wn34_ch1_sig is not None else None
        #signal4 = wh40_sig * 25 if wh40_sig is not None else None
        #signal5 = wh45_sig * 25 if wh45_sig is not None else None
        #signal6 = wh57_sig * 25 if wh57_sig is not None else None
        #signal7 = wh51_ch1_sig * 25 if wh51_ch1_sig is not None else None
        #signal8 = wn35_ch1_sig * 25 if wn35_ch1_sig is not None else None
        
        ws90_sig = ws90_sig * 25 if ws90_sig is not None else None
        ws85_sig = ws85_sig * 25 if ws85_sig is not None else None
        wh54_ch1_sig = wh54_ch1_sig * 25 if wh54_ch1_sig is not None else None

        #wh31_ch1_sig = wh31_ch1_sig *25 if wh31_ch1_sig is not None else None
        #wh31_ch2_sig = wh31_ch2_sig *25 if wh31_ch2_sig is not None else None
        #wh31_ch3_sig = wh31_ch3_sig *25 if wh31_ch3_sig is not None else None
        #wh31_ch4_sig = wh31_ch4_sig *25 if wh31_ch4_sig is not None else None
        #wh31_ch5_sig = wh31_ch5_sig *25 if wh31_ch5_sig is not None else None
        #wh31_ch6_sig = wh31_ch6_sig *25 if wh31_ch6_sig is not None else None
        #wh31_ch7_sig = wh31_ch7_sig *25 if wh31_ch7_sig is not None else None
        #wh31_ch8_sig = wh31_ch8_sig *25 if wh31_ch8_sig is not None else None

##############################################################################
#   This section controls the origin of derived values.
[StdWXCalculate]
    
    [[Calculations]]
        # How to calculate derived quantities.  Possible values are:
        #  hardware        - use the value provided by hardware
        #  software        - use the value calculated by weewx
        #  prefer_hardware - use value provide by hardware if available,
        #                      otherwise use value calculated by weewx
        
        pressure = prefer_hardware
        altimeter = prefer_hardware
        appTemp = prefer_hardware
        barometer = prefer_hardware
        cloudbase = prefer_hardware
        dewpoint = prefer_hardware
        ET = prefer_hardware
        heatindex = prefer_hardware
        humidex = prefer_hardware
        inDewpoint = prefer_hardware
        maxSolarRad = prefer_hardware
        rainRate = prefer_hardware
        windchill = prefer_hardware
        windrun = prefer_hardware
        GTS = "software,archive"
        GTSdate = "software,archive"
        utcoffsetLMT = "software,archive"
        dayET = "prefer_hardware,archive"
        ET24 = "prefer_hardware,archive"
        yearGDD = "software,archive"
        seasonGDD = "software,archive"
        rain = prefer_hardware
        hail = prefer_hardware

    #  [[WXXTypes]]
    #    [[[windDir]]]
    #       force_null = True
    #    [[[maxSolarRad]]]
    #      algorithm = rs
    #      atc = 0.8
    #      nfac = 2
    #    [[[ET]]]
    #      wind_height = 2.0
    #      et_period = 3600
    #    [[[heatindex]]]
    #      algorithm = new
    #  [[PressureCooker]]
    #    max_delta_12h = 1800
    #    [[[altimeter]]]
    #      algorithm = aaASOS    # Case-sensitive!
    #  [[RainRater]]
    #    rain_period = 900
    #    retain_period = 930
    #  [[Delta]]
    #    [[[rain]]]
    #      input = totalRain
    
    [[WXXTypes]]
        [[[maxSolarRad]]]
            algorithm = rs
            atc = 0.9

   # These settings are not necessary because rain and hail (p_rain) are assigned in the driver!
   # [[Delta]]
   #     [[[rain]]]
   #         input = t_rainyear
   #     [[[hail]]]
   #         input = p_rainyear
   #     [[[lightning_strike_count]]]
   #         input = lightningcount
   #     [[[lightning_distance]]]
   #         input = lightning_distance

##############################################################################
#   This section binds a data store to a database.
[DataBindings]
    [[wx_binding]]
        # The database must match one of the sections in [Databases].
        # This is likely to be the only option you would want to change.
        database = archive_sqlite
        # The name of the table within the database.
        table_name = archive
        # The manager handles aggregation of data for historical summaries.
        manager = weewx.manager.DaySummaryManager
        # The schema defines the structure of the database.
        # It is *only* used when the database is created.
        #schema = schemas.wview_ecowitt.schema
        #schema = schemas.wview_ecowittrssi.schema
        schema = schemas.wview_ecowittrssisoilad.schema
##############################################################################
# Options for extension Ecowittcustom, GW1000, Interceptor or EcowittHttp
[Accumulator]
    
    [[model]]
        accumulator = firstlast
        extractor = last
    [[stationtype]]
        accumulator = firstlast
        extractor = last
    [[apName]]
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
    [[p_rain]]
        extractor = sum    
    [[t_rain]]
        extractor = sum

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



```
All mapping and unit assignments are done now in the driver

## Loop packets are captured but not used
Found the problem: to use the loop packets, this setting in weewx.conf is necessary
```
[StdArchive]
    record_generation = software
```
#### Inconsistent data handling between Ecowitt cloud (ecowitt.net), SDCard (GW3000) and local http-Api
This data can you get via ecowitt.net, but not from the local http-Api (get_livedata_info)
```
This data applies to (battery are in Volt):
battery.wind_sensor

from the displays:
battery.console
battery.ws1900
battery.ws1800
battery.ws6006

```
#### Problem with GW3000:
If the driver fails to connect to the GW3000 (even though all settings are correct), a restart of the GW3000 is necessary!

#### log from this driver:
```
weewxd[647056]: INFO __main__: Initializing weewxd version 5.1.0
weewxd[647056]: INFO __main__: Command line: /usr/share/weewx/weewxd.py --daemon --pidfile=/var/run/weewx4.pid /etc/weewx/weewx4.conf
weewxd[647056]: INFO __main__: Using Python: 3.11.2 (main, Apr 28 2025, 14:11:48) [GCC 12.2.0]
weewxd[647056]: INFO __main__: Located at:   /bin/python3
weewxd[647056]: INFO __main__: Platform:     Linux-6.12.25+rpt-rpi-2712-aarch64-with-glibc2.36
weewxd[647056]: INFO __main__: Locale:       'de_DE.UTF-8'
weewxd[647056]: INFO __main__: Entry path:   /usr/share/weewx/weewxd.py
weewxd[647056]: INFO __main__: WEEWX_ROOT:   /etc/weewx
weewxd[647056]: INFO __main__: Config file:  /etc/weewx/weewx4.conf
weewxd[647056]: INFO __main__: User module:  /etc/weewx/bin/user
weewxd[647056]: INFO __main__: Debug:        0
weewxd[647056]: INFO __main__: User:         root
weewxd[647056]: INFO __main__: Group:        root
weewxd[647056]: INFO __main__: Groups:       
weewxd[647056]: INFO __main__: PID file is /var/run/weewx4.pid
weewxd[647060]: INFO weewx.engine: Loading station type EcowittHttp (user.ecowitt_http)
weewxd[647060]: INFO user.ecowitt_http: EcowittHttpDriver: version is 0.1.0_test
weewxd[647060]: INFO user.ecowitt_http: unit_system: 17
weewxd[647060]: INFO user.ecowitt_http:      field map is {'appTemp': 'common_list.4.val', 'barometer': 'wh25.rel', 'batteryStatus1': 'wn31.ch1.battery', 'batteryStatus2': 'wn31.ch2.battery', 'batteryStatus3': 'wn31.ch3.battery', 'batteryStatus4': 'wn31.ch4.battery', 'batteryStatus5': 'wn31.ch5.battery', 'batteryStatus6': 'wn31.ch6.battery', 'batteryStatus7': 'wn31.ch7.battery', 'batteryStatus8': 'wn31.ch8.battery', 'co2': 'co2.CO2', 'co2_24h': 'co2.CO2_24H', 'co2_Batt': 'co2.battery', 'co2_Hum': 'co2.humidity', 'co2_Temp': 'co2.temperature', 'co2in': 'wh25.CO2', 'co2in_24h': 'wh25.CO2_24H', 'dateTime': 'datetime', 'daymaxwind': 'common_list.0x19.val', 'depth_ch1': 'ch_lds.1.depth', 'depth_ch2': 'ch_lds.2.depth', 'depth_ch3': 'ch_lds.3.depth', 'depth_ch4': 'ch_lds.4.depth', 'dewpoint': 'common_list.0x03.val', 'extraHumid1': 'ch_aisle.1.humidity', 'extraHumid2': 'ch_aisle.2.humidity', 'extraHumid3': 'ch_aisle.3.humidity', 'extraHumid4': 'ch_aisle.4.humidity', 'extraHumid5': 'ch_aisle.5.humidity', 'extraHumid6': 'ch_aisle.6.humidity', 'extraHumid7': 'ch_aisle.7.humidity', 'extraHumid8': 'ch_aisle.8.humidity', 'extraTemp1': 'ch_aisle.1.temp', 'extraTemp2': 'ch_aisle.2.temp', 'extraTemp3': 'ch_aisle.3.temp', 'extraTemp4': 'ch_aisle.4.temp', 'extraTemp5': 'ch_aisle.5.temp', 'extraTemp6': 'ch_aisle.6.temp', 'extraTemp7': 'ch_aisle.7.temp', 'extraTemp8': 'ch_aisle.8.temp', 'feelslike': 'common_list.3.val', 'heap': 'debug.heap', 'inHumidity': 'wh25.inhumi', 'inTemp': 'wh25.intemp', 'is_raining': 'piezoRain.srain_piezo.val', 'ldsbatt1': 'ch_lds.1.voltage', 'ldsbatt2': 'ch_lds.2.voltage', 'ldsbatt3': 'ch_lds.3.voltage', 'ldsbatt4': 'ch_lds.4.voltage', 'ldsheat_ch1': 'ch_lds.1.heat', 'ldsheat_ch2': 'ch_lds.2.heat', 'ldsheat_ch3': 'ch_lds.3.heat', 'ldsheat_ch4': 'ch_lds.4.heat', 'leafWet1': 'ch_leaf.1.humidity', 'leafWet2': 'ch_leaf.2.humidity', 'leafWet3': 'ch_leaf.3.humidity', 'leafWet4': 'ch_leaf.4.humidity', 'leafWet5': 'ch_leaf.5.humidity', 'leafWet6': 'ch_leaf.6.humidity', 'leafWet7': 'ch_leaf.7.humidity', 'leafWet8': 'ch_leaf.8.humidity', 'leak Batt3': 'wh55.ch3.battery', 'leak_1': 'ch_leak.1.status', 'leak_2': 'ch_leak.2.status', 'leak_3': 'ch_leak.3.status', 'leak_4': 'ch_leak.4.status', 'leak_Batt1': 'wh55.ch1.battery', 'leak_Batt2': 'wh55.ch2.battery', 'leak_Batt4': 'wh55.ch4.battery', 'lightning_Batt': 'wh57.battery', 'lightning_distance': 'lightning.distance', 'lightning_disturber_count': 'lightning.timestamp', 'lightning_strike_count': 'lightning.count', 'outHumidity': 'common_list.0x07.val', 'outTemp': 'common_list.0x02.val', 'p_rain': 'piezoRain.0x0D.val', 'p_rainday': 'piezoRain.0x10.val', 'p_rainhour': 'p_rainhour', 'p_rainmonth': 'piezoRain.0x12.val', 'p_rainrate': 'piezoRain.0x0E.val', 'p_rainweek': 'piezoRain.0x11.val', 'p_rainyear': 'piezoRain.0x13.val', 'pm1_0': 'co2.PM1', 'pm1_24h_co2': 'co2.PM1_24H', 'pm1_24hAQI_co2': 'co2.PM1_24HAQI', 'pm1_RealAQI_co2': 'co2.PM1_RealAQI', 'pm2_5': 'co2.PM25', 'pm4_0': 'co2.PM4', 'pm4_24h_co2': 'co2.PM4_24H', 'pm4_24hAQI_co2': 'co2.PM4_24HAQI', 'pm4_RealAQI_co2': 'co2.PM4_RealAQI', 'pm10_0': 'co2.PM10', 'pm10_24h_co2': 'co2.PM10_24H', 'pm10_24hAQI_co2': 'co2.PM10_24HAQI', 'pm10_RealAQI_co2': 'co2.PM10_RealAQI', 'pm25_1': 'ch_pm25.1.PM25', 'pm25_2': 'ch_pm25.2.PM25', 'pm25_3': 'ch_pm25.3.PM25', 'pm25_4': 'ch_pm25.4.PM25', 'pm25_24h_co2': 'co2.PM25_24H', 'pm25_24hAQI_co2': 'co2.PM25_24HAQI', 'pm25_AQI_24h_ch1': 'ch_pm25.1.PM25_24HAQI', 'pm25_AQI_24h_ch2': 'ch_pm25.2.PM25_24HAQI', 'pm25_AQI_24h_ch3': 'ch_pm25.3.PM25_24HAQI', 'pm25_AQI_24h_ch4': 'ch_pm25.4.PM25_24HAQI', 'pm25_avg_24h_ch1': 'ch_pm25.1.PM25_24H', 'pm25_avg_24h_ch2': 'ch_pm25.2.PM25_24H', 'pm25_avg_24h_ch3': 'ch_pm25.3.PM25_24H', 'pm25_avg_24h_ch4': 'ch_pm25.4.PM25_24H', 'pm25_Batt1': 'wh41.ch1.battery', 'pm25_Batt2': 'wh41.ch2.battery', 'pm25_Batt3': 'wh41.ch3.battery', 'pm25_Batt4': 'wh41.ch4.battery', 'pm25_RealAQI_ch1': 'ch_pm25.1.PM25_RealAQI', 'pm25_RealAQI_ch2': 'ch_pm25.2.PM25_RealAQI', 'pm25_RealAQI_ch3': 'ch_pm25.3.PM25_RealAQI', 'pm25_RealAQI_ch4': 'ch_pm25.4.PM25_RealAQI', 'pm25_RealAQI_co2': 'co2.PM25_RealAQI', 'pressure': 'wh25.abs', 'radiation': 'common_list.0x15.val', 'runtime': 'debug.runtime', 'soilMoist1': 'ch_soil.1.humidity', 'soilMoist2': 'ch_soil.2.humidity', 'soilMoist3': 'ch_soil.3.humidity', 'soilMoist4': 'ch_soil.4.humidity', 'soilMoist5': 'ch_soil.5.humidity', 'soilMoist6': 'ch_soil.6.humidity', 'soilMoist7': 'ch_soil.7.humidity', 'soilMoist8': 'ch_soil.8.humidity', 'soilMoist9': 'ch_soil.9.humidity', 'soilMoist10': 'ch_soil.10.humidity', 'soilMoist11': 'ch_soil.11.humidity', 'soilMoist12': 'ch_soil.12.humidity', 'soilMoist13': 'ch_soil.13.humidity', 'soilMoist14': 'ch_soil.14.humidity', 'soilMoist15': 'ch_soil.15.humidity', 'soilMoist16': 'ch_soil.16.humidity', 'soilMoistBatt1': 'ch_soil.1.voltage', 'soilMoistBatt1s': 'wh51.ch1.battery', 'soilMoistBatt2': 'ch_soil.2.voltage', 'soilMoistBatt2s': 'wh51.ch2.battery', 'soilMoistBatt3': 'ch_soil.3.voltage', 'soilMoistBatt3s': 'wh51.ch3.battery', 'soilMoistBatt4': 'ch_soil.4.voltage', 'soilMoistBatt4s': 'wh51.ch4.battery', 'soilMoistBatt5': 'ch_soil.5.voltage', 'soilMoistBatt5s': 'wh51.ch5.battery', 'soilMoistBatt6': 'ch_soil.6.voltage', 'soilMoistBatt6s': 'wh51.ch6.battery', 'soilMoistBatt7': 'ch_soil.7.voltage', 'soilMoistBatt7s': 'wh51.ch7.battery', 'soilMoistBatt8': 'ch_soil.8.voltage', 'soilMoistBatt8s': 'wh51.ch8.battery', 'soilMoistBatt9': 'ch_soil.9.voltage', 'soilMoistBatt9s': 'wh51.ch9.battery', 'soilMoistBatt10': 'ch_soil.10.voltage', 'soilMoistBatt10s': 'wh51.ch10.battery', 'soilMoistBatt11': 'ch_soil.11.voltage', 'soilMoistBatt11s': 'wh51.ch11.battery', 'soilMoistBatt12': 'ch_soil.12.voltage', 'soilMoistBatt12s': 'wh51.ch12.battery', 'soilMoistBatt13': 'ch_soil.13.voltage', 'soilMoistBatt13s': 'wh51.ch13.battery', 'soilMoistBatt14': 'ch_soil.14.voltage', 'soilMoistBatt14s': 'wh51.ch14.battery', 'soilMoistBatt15': 'ch_soil.15.voltage', 'soilMoistBatt15s': 'wh51.ch15.battery', 'soilMoistBatt16': 'ch_soil.16.voltage', 'soilMoistBatt16s': 'wh51.ch16.battery', 'soilTemp1': 'ch_temp.1.temp', 'soilTemp2': 'ch_temp.2.temp', 'soilTemp3': 'ch_temp.3.temp', 'soilTemp4': 'ch_temp.4.temp', 'soilTemp5': 'ch_temp.5.temp', 'soilTemp6': 'ch_temp.6.temp', 'soilTemp7': 'ch_temp.7.temp', 'soilTemp8': 'ch_temp.8.temp', 'soilTempBatt1': 'ch_temp.1.voltage', 'soilTempBatt1s': 'wn34.ch1.battery', 'soilTempBatt2': 'ch_temp.2.voltage', 'soilTempBatt2s': 'wn34.ch2.battery', 'soilTempBatt3': 'ch_temp.3.voltage', 'soilTempBatt3s': 'wn34.ch3.battery', 'soilTempBatt4': 'ch_temp.4.voltage', 'soilTempBatt4s': 'wn34.ch4.battery', 'soilTempBatt5': 'ch_temp.5.voltage', 'soilTempBatt5s': 'wn34.ch5.battery', 'soilTempBatt6': 'ch_temp.6.voltage', 'soilTempBatt6s': 'wn34.ch6.battery', 'soilTempBatt7': 'ch_temp.7.voltage', 'soilTempBatt7s': 'wn34.ch7.battery', 'soilTempBatt8': 'ch_temp.8.voltage', 'soilTempBatt8s': 'wn34.ch8.battery', 't_rainday': 'rain.0x10.val', 't_rainevent': 'rain.0x0D.val', 't_rainhour': 't_rainhour', 't_rainmonth': 'rain.0x12.val', 't_rainRate': 'rain.0x0E.val', 't_rainweek': 'rain.0x11.val', 't_rainyear': 'rain.0x13.val', 'thi_ch1': 'ch_lds.1.air', 'thi_ch2': 'ch_lds.2.air', 'thi_ch3': 'ch_lds.3.air', 'thi_ch4': 'ch_lds.4.air', 'UV': 'common_list.0x17.val', 'uvradiation': 'common_list.0x16.val', 'vpd': 'common_list.5.val', 'wh25_batt': 'wh25.battery', 'wh25_sig': 'wh25.signal', 'wh26_batt': 'wh26.battery', 'wh26_sig': 'wh26.signal', 'wh41_ch1_sig': 'wh41.ch1.signal', 'wh41_ch2_sig': 'wh41.ch2.signal', 'wh41_ch3_sig': 'wh41.ch3.signal', 'wh41_ch4_sig': 'wh41.ch4.signal', 'wh45_sig': 'co2.signal', 'wh51_ch1_sig': 'wh51.ch1.signal', 'wh51_ch2_sig': 'wh51.ch2.signal', 'wh51_ch3_sig': 'wh51.ch3.signal', 'wh51_ch4_sig': 'wh51.ch4.signal', 'wh51_ch5_sig': 'wh51.ch5.signal', 'wh51_ch6_sig': 'wh51.ch6.signal', 'wh51_ch7_sig': 'wh51.ch7.signal', 'wh51_ch8_sig': 'wh51.ch8.signal', 'wh51_ch9_sig': 'wh51.ch9.signal', 'wh51_ch10_sig': 'wh51.ch10.signal', 'wh51_ch11_sig': 'wh51.ch11.signal', 'wh51_ch12_sig': 'wh51.ch12.signal', 'wh51_ch13_sig': 'wh51.ch13.signal', 'wh51_ch14_sig
weewxd[647060]: INFO user.ecowitt_http:      device IP address is 192.168.0.110
weewxd[647060]: INFO user.ecowitt_http:      poll interval is 20 seconds
weewxd[647060]: INFO user.ecowitt_http:      Max tries is 3 URL retry wait is 2 seconds
weewxd[647060]: INFO user.ecowitt_http:      URL timeout is 3 seconds
weewxd[647060]: INFO user.ecowitt_http:       any debug is set
weewxd[647060]: INFO user.ecowitt_http:      rain debug is not set
weewxd[647060]: INFO user.ecowitt_http:      wind debug is not set
weewxd[647060]: INFO user.ecowitt_http:      loop debug is not set
weewxd[647060]: INFO user.ecowitt_http:   sensors debug is set
weewxd[647060]: INFO user.ecowitt_http:   catchup debug is set
weewxd[647060]: INFO user.ecowitt_http:    parser debug is set
weewxd[647060]: INFO user.ecowitt_http: collector debug is not set
weewxd[647060]: INFO user.ecowitt_http:     cloud debug is not set
weewxd[647060]: INFO user.ecowitt_http:    wn32_indoor: sensor ID decoding will use 'WH26'
weewxd[647060]: INFO user.ecowitt_http:   wn32_outdoor: sensor ID decoding will use 'WH26'
weewxd[647060]: INFO user.ecowitt_http:      device firmware update checks will occur every 86400 seconds
weewxd[647060]: INFO user.ecowitt_http:      available device firmware updates will be logged
weewxd[647060]: INFO user.ecowitt_http:      battery state will not be reported for sensors with no signal data
weewxd[647060]: INFO user.ecowitt_http:      unknown fields will be reported
weewxd[647060]: INFO user.ecowitt_http: catchup source: None
weewxd[647060]: INFO user.ecowitt_http: EcowittHttpCollector startup
weewxd[647060]: INFO weewx.engine: StdConvert target unit is 0x1
weewxd[647060]: INFO weewx.wxservices: StdWXCalculate will use data binding wx_binding
weewxd[647060]: INFO user.GTS: Version 1.1
weewxd[647060]: INFO user.GTS: Local mean time (LMT) UTC offset 0:55:16.533360
weewxd[647060]: INFO user.GTS: PressureCooker True
weewxd[647060]: INFO user.GTS: PressureCooker <user.barometer.PressureCooker object at 0x7fff3d4c9590> 
weewxd[647060]: INFO weewx.engine: Archive will use data binding wx_binding
weewxd[647060]: INFO weewx.engine: Record generation will be attempted in 'hardware'
weewxd[647060]: INFO weewx.engine: Using archive interval of 300 seconds (specified in weewx configuration)
weewxd[647060]: INFO weewx.restx: StationRegistry: Registration not requested.
weewxd[647060]: INFO weewx.restx: Wunderground: Posting not enabled.
weewxd[647060]: INFO weewx.restx: PWSweather: Posting not enabled.
weewxd[647060]: INFO weewx.restx: CWOP: Posting not enabled.
weewxd[647060]: INFO weewx.restx: WOW: Posting not enabled.
weewxd[647060]: INFO weewx.restx: AWEKAS: Posting not enabled.
weewxd[647060]: INFO weewx.engine: 'pyephem' detected, extended almanac data is available
weewxd[647060]: INFO __main__: Starting up weewx version 5.1.0
weewxd[647060]: INFO weewx.engine: Using binding 'wx_binding' to database 'weewx_ecowitt_http.sdb'
weewxd[647060]: INFO weewx.manager: Starting backfill of daily summaries
weewxd[647060]: INFO weewx.manager: Daily summaries up to date
weewxd[647060]: INFO user.ecowitt_http: genArchiveRecords: Using MAC address: 5C:01:3B:46:C3:FF
weewxd[647060]: INFO user.ecowitt_http: Processing history file '202507A.csv' from  GW3000A_V1.0.9 at 192.168.0.110
weewxd[647060]: INFO user.ecowitt_http: Problem with key Time
weewxd[647060]: INFO user.ecowitt_http: Problem with key Timestamp
weewxd[647060]: INFO user.ecowitt_http: Processing history file '202507Allsensors_A.csv' from  GW3000A_V1.0.9 at 192.168.0.110
weewxd[647060]: INFO user.ecowitt_http: Problem with key Time
weewxd[647060]: INFO user.ecowitt_http: Problem with key Timestamp
weewxd[647060]: INFO user.ecowitt_http: no Data field WH35 CH2hum
weewxd[647060]: INFO user.ecowitt_http: no Data field WH35 CH3hum
weewxd[647060]: INFO user.ecowitt_http: no Data field WH35 CH4hum
weewxd[647060]: INFO user.ecowitt_http: no Data field WH35 CH5hum
weewxd[647060]: INFO user.ecowitt_http: no Data field WH35 CH6hum
weewxd[647060]: INFO user.ecowitt_http: no Data field WH35 CH7hum
weewxd[647060]: INFO user.ecowitt_http: no Data field WH35 CH8hum
weewxd[647060]: INFO user.ecowitt_http: no Data field SoilMoisture CH11
weewxd[647060]: INFO user.ecowitt_http: no Data field SoilMoisture CH12
weewxd[647060]: INFO user.ecowitt_http: no Data field SoilMoisture CH13
weewxd[647060]: INFO user.ecowitt_http: no Data field SoilMoisture CH14
weewxd[647060]: INFO user.ecowitt_http: no Data field SoilMoisture CH15
weewxd[647060]: INFO user.ecowitt_http: no Data field SoilMoisture CH16
weewxd[647060]: INFO user.ecowitt_http: no Data field LDS_Air CH2
weewxd[647060]: INFO user.ecowitt_http: no Data field LDS_Depth CH2
weewxd[647060]: INFO user.ecowitt_http: no Data field LDS_Heat CH2
weewxd[647060]: INFO user.ecowitt_http: no Data field LDS_Air CH3
weewxd[647060]: INFO user.ecowitt_http: no Data field LDS_Depth CH3
weewxd[647060]: INFO user.ecowitt_http: no Data field LDS_Heat CH3
weewxd[647060]: INFO user.ecowitt_http: no Data field LDS_Air CH4
weewxd[647060]: INFO user.ecowitt_http: no Data field LDS_Depth CH4
weewxd[647060]: INFO user.ecowitt_http: no Data field LDS_Heat CH4
weewxd[647060]: INFO user.ecowitt_http: Problem with key 
weewxd[647060]: INFO user.ecowitt_http: genArchiveRecords: Yielding archive record 2025-07-03 15:56:00 CEST (1751550960)
weewxd[647060]: INFO user.sunrainduration: Archiv-Record-Interval=300 sec
weewxd[647060]: INFO weewx.engine: Starting main packet loop.
weewxd[647060]: INFO user.ecowitt_http: genArchiveRecords: Using MAC address: 5C:01:3B:46:C3:FF
weewxd[647060]: INFO user.ecowitt_http: Processing history file '202507A.csv' from  GW3000A_V1.0.9 at 192.168.0.110
weewxd[647060]: INFO user.ecowitt_http: Processing history file '202507Allsensors_A.csv' from  GW3000A_V1.0.9 at 192.168.0.110
weewxd[647060]: INFO user.ecowitt_http: genArchiveRecords: Using MAC address: 5C:01:3B:46:C3:9F
weewxd[647060]: INFO user.ecowitt_http: Processing history file '202507A.csv' from  GW3000A_V1.0.9 at 192.168.0.110
weewxd[647060]: INFO user.ecowitt_http: Problem with key Time
weewxd[647060]: INFO user.ecowitt_http: Problem with key Timestamp
weewxd[647060]: INFO user.ecowitt_http: Processing history file '202507Allsensors_A.csv' from  GW3000A_V1.0.9 at 192.168.0.110
new:
weewxd[790259]: INFO user.ecowitt_http: Using 'rain.0x13.val' for rain total
weewxd[790259]: INFO user.ecowitt_http: Using 'piezoRain.0x13.val' for piezo rain total
weewxd[790259]: INFO user.ecowitt_http: skipping rain measurement of 353.3: no last rain
weewxd[790259]: INFO user.ecowitt_http: skipping piezo rain measurement of 345.9: no last rain
weewxd[790259]: INFO user.ecowitt_http: Skipping lightning count of 11: no last count


```
#### New RSSI value:

skin.conf
```
        [[[dayrssi_ws80]]]
            yscale = -100, -40.0, 10
            [[[[wh26_rssi]]]]
             label =wh26 
            [[[[wh69_rssi]]]]
             label =wh69 
            [[[[ws80_rssi]]]]
             label =ws80
            [[[[ws85_rssi]]]]
             label =ws85 
            [[[[ws90_rssi]]]]
             label =ws90 

```
<img width="500" height="180" alt="dayrssi_ws80" src="https://github.com/user-attachments/assets/65e83076-b6f7-4eaa-8270-95e7c57213ce" />

#### New soilad1..16 value:

skin.conf
```
        [[[daysoilMoistAd]]]
            yscale = None, None, 25
            y_label = ""
            [[[[soilad1]]]]
		label = soil1
            [[[[soilad2]]]]
		label = soil2
            [[[[soilad3]]]]
		label = soil3
            [[[[soilad5]]]]
		label = soil5
            [[[[soilad7]]]]
		label = soil7
            [[[[soilad9]]]]
		label = soil9

```
<img width="500" height="180" alt="daysoilMoistAd" src="https://github.com/user-attachments/assets/4be58f6d-f097-42bf-b993-3ff025dc869f" />


## Live data comparison GW3000 original driver V0.1.0a28 with the driver V0.2.5
https://github.com/WernerKr/Ecowitt-or-DAVIS-stations-and-Season-skin/blob/main/ecowitt_http/compare_gw3000_live_data.txt

## Default Mapping:
https://github.com/WernerKr/Ecowitt-or-DAVIS-stations-and-Season-skin/blob/main/ecowitt_http/Ecowitt_http_default_mapping.txt

## WeeWx Fields:
https://github.com/WernerKr/Ecowitt-or-DAVIS-stations-and-Season-skin/blob/main/ecowitt_http/Ecowitt_http_weewx-fields.txt

## Example Data from ecowitt.net:

ecowitt_net_api.txt -> 634.420 Byte !!!

https://github.com/WernerKr/Ecowitt-or-DAVIS-stations-and-Season-skin/blob/main/ecowitt_http/ecowitt_net_api.txt

## Skin with data from Ecowitt_http:
https://www.pc-wetterstation.de/wetter/weewx8/

# Updating the Ecowitt_http driver:

Simply download and unzip the ecowitt_http.zip file, or ecowitt_http.py file and replace the existing file (/etc/weewx/bin/ecowitt_http.py) with it.
After that restart weewx!

# Installation as a WeeWX driver with Skin SeasonsEcowitt

    For WeeWX package installs: 
       #### Install direct from Web do not work! and wget also corrupts the file!
       #### So download it direct as raw file

       weectl extension install weewx-ecowitt_http.zip

    For WeeWX *pip* installs the Python virtual environment must be activated before the extension is installed:
    
        source ~/weewx-venv/bin/activate
        weectl extension install weewx-ecowitt_http.zip

    For WeeWX installs from *git* the Python virtual environment must be activated before the extension is installed:

        source ~/weewx-venv/bin/activate
        python3 ~/weewx/src/weectl.py extension install weewx-ecowitt_http.zip
