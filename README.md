## Driver Ecowittcustom
   This driver fully supports all currently available data from Ecowitt Wi-Fi consoles and/or gateways.
   
   It supports both the Ecowitt Protocol and the Wunderground Protocol
```
Revision History
   Jan 2024:
       - supports soilad1 - soilad16 and heap (as pb)
   May/June 2024:
      - Support Co2in, PM1, PM4
      - WS85
   Jan-Mar 2025:
       - all data from FOSHKplugin
       - vpd
       - LDS01 - LDS04 (WH54)
   Aug 2025:
       - Support for WS6210
       - Support for WN38 (bgt, wbgt)
   
   26 Sep 2025            v0.1.6
      - "kPa" = "%.3f" -> VPD
      - wbgtcat

   30 Dec 2025            v0.1.7
      - bgt, wbgt, bgtbatt, wn38_sig, wn38_rssi, lightning_distance = group_distance 

```
![Ecowitt_ecowitt](https://github.com/user-attachments/assets/bbc8312e-f51c-4e47-aebf-d29fb8353d73)
![Ecowitt_wunderground](https://github.com/user-attachments/assets/333c1192-edc7-41c6-9ecf-50521fa526fb)


If you also use Oliver's FOSHKplugin, and the corresponding Wi-Fi station also provides the signals, 
or the gateways always provide the signals, the Ecowitt Custom function in the Ecowitt protocol sends 
the data to the FOSHKplugin, and FOSHKplugin forwards the data to the Ecowittcustom driver for WeeWx.

This provides the functionality of the GW1000 driver with all newer data (e.g. inbuilt WS3910 CO2 sensor, LDS sensor WH54, VPD) 
that is no longer provided by the Ecowitt API (last Telnet v1.7.0 - 2024.05.27 [WH46]).
```
Ecowitt protocol:
  - Ecowitt Gateways GW1000, GW1100, GW1200, GW2000, GW3000, WS38xx, WS39xx, WS6210, WS1900, WN1980, WN1900, WH2650 
  - Ecowitt wifi consoles HP2560, HP2550, HP3500, WS39xx, WS38xx, WN1980, WN1900, WS1900
``` 
All mapping and unit assignments are done in the Ecowittcustom driver

The wview_extended database schema has been extended for Ecowitt data and is provided as wview_ecowitt schema.

Script files (add_ecowitt_data_v5.sh, add_ecowitt_allsignaldata_v5.sh, add_ecowitt_to_wview_extended_database.sh) 
are provided to extend an existing database accordingly.

The rain from the piezo sensors (WS85, WS90) is recorded as hail or hailRate!
This allows you to compare both data if a WH40 rain sensor is also present.

If you want the signal values (0-4) provided by the FOSHKplugin to be expressed as percentages, 
you can do so in the weewx.conf file in the section
```
[StdCalibrate]
[[Corrections]]
ws90_sig = ws90_sig * 25 if ws90_sig is not None else None
ws85_sig = ws85_sig * 25 if ws85_sig is not None else None
wh54_ch1_sig = wh54_ch1_sig * 25 if wh54_ch1_sig is not None else None
```
This will then be automatically taken into account in the SeasonsEcowitt skin (sensors.inc).

FOSHKplugin:
https://foshkplugin.phantasoft.de/files/generic-FOSHKplugin-0.0.10Beta.zip

Settings for FOSHKplugin to forward the ecowitt data to weewx 
foshkplugin.conf
Ecowitt protocol:
  - Ecowitt Gateways GW1000, GW1100, GW1200, GW2000, GW3000, WS38xx, WS39xx, WS6210, WS1900, WN1980, WN1900, WH2650 
  - Ecowitt wifi consoles HP2560, HP2550, HP3500, WS39xx, WS38xx, WN1980, WN1900, WS1900 
``` 
** FOSHKplugin ADD_More - not GW1000!
= radcompensation,newVersion,upgrade,rainFallPriority,rainGain,piezo,rstRainDay,rstRainWeek,rstRainYear,rain1_gain,rain2_gain,rain3_gain,rain4_gain,rain5_gain

** FOSHKplugin ADD_RSSI - not GW1000!
``` 
```
[Config]
LB_IP = 192.168.0.93
LBH_PORT = 8083            # this port is set at customized server (gateway/station)

[Weatherstation]
WS_IP = 192.168.0.86      # IP Ecowitt Gateway/Station
WS_PORT = 45000
WS_INTERVAL = 16

[Export]
EVAL_VALUES = True
ADD_ITEMS = 
OUT_TEMP = 
OUT_HUM = 
OUT_TIME = False
FIX_LIGHTNING = True
UDP_MINMAX = False
ADD_SPREAD = False
ADD_SIGNAL = True		all Gateways support this (*sig)
ADD_DEWPT = False
ADD_MORE = True		not all Gateways support this (see **)
ADD_RSSI = True      you get also the rssi value from the supported Gateways and Stations (like WS3910, WS6210)
ADD_VPD = False

[Forward-1]
FWD_ENABLE = True
FWD_CMT = Weewx Ecowittcustom 86
FWD_URL = http://192.168.0.93:8572/data/report/
FWD_INTERVAL = 
FWD_IGNORE = 
FWD_OPTION = blacklist=False
FWD_TYPE = EW
FWD_SID = 
FWD_PWD = 
FWD_STATUS = False
FWD_MQTTCYCLE = 0
FWD_EXEC = 
```


## Skin SeasonsEcowitt or SeasonsDavis too
Based on the new structure of the Seasons skin (sensor management in array) I have the Seasons Skin
extended accordingly so that all possible sensor data of the Ecowitt stations/devices are displayed.
There is also the option of displaying the air quality index for AQI EPA (US) or AQI EEA (EU).
It currently contains all database values from the weewx_extended database schema
and now Ecowitt database schema weewx_ecowitt and loop values of
Ecowitt (Ecowittcustom: ecowitt-client) or GW1000 driver, VantagePro, Davis Weatherlink Live, Davis AirLink
In order to get all data from the Ecowitt stations/devices, you have to use my 
Ecowittcustom driver
or GW1000 driver.
```
My array offers these possibilities:
  at current.inc example for outside temperature:
  ('outTemp', '#e85d0d', 'current', '1')
  or
  ('outTemp','#e85d0d','day','1')
  (1:value, 2:labelcolor, ''=black, 3:current or day or yesterday or aqiepa or aqieea or trend or deltatime or wx_binding?, 4:'1')
  3: = current -> default
  3: = day -> show avages of the day
  3: = yesterday -> show avages of the last day
  3: = 3:yesterday -> at 1:radiation  -> radiation.energy_integral.kilowatt_hour_per_meter_squared for yesterday and day
  3: = trend -> show additonal to value the 24hr trend or 3 hr trend (barometer)
  3: = deltatime -> for sunShineDur or rainDur or hailDur
  3: = 'wx_binding?' -> example: 'wx_binding3, WS90' Data are from the Database settings 'wx_binding3' and here additional to the label is ' WS90' added
  3: = 'daywx_bindig?' or 'trendwx_bindging?' are also allowed. example: 'daywx_binding3, Ultrasonic'
  3: = aqiepa -> computes pm2_5 Air quality Index EPA
  3: = aqieea -> computes pm2_5 Air quality Index EEA
  4: = 1 show, 4: = 0 don't show, although values are available, 4: = 3 Textinformation or Separation

at hilo.inc and statistics.inc
  observ-Array -> (1:value, 2:labelcolor, ''=black, 3:''=min&max or max or sum or wx_binding?, 4:don't show, although values are available = 0)
  ('outTemp', '#e85d0d', '', '1'),
  1: value
  2: label color, if '' = black
  3: which evaluation , '' (= empty = min and max), or sum, or only max
  3: ='wx_binding?' or 'sumwx_binding?' or 'maxwx_binding?' or 'minwx_binding?' or 'avgwx_binding?' or 'maxwx_binding?, Text' or ...
  -> example: 'wx_binding3, WS90' or 'maxwx_binding3, WS90' Data are from the Database settings 'wx_binding3' and here additional to the label is ' WS90' added
  4: show if available, if 0 never show (e.g. for indoor temperature)
  labelcolor can be general disabled -> #set $usefontcolor = 0


In addition, the skin also takes into account that the Ecowitt stations / devices use the unit "%" for the soil moisture values
  and not "cb" as specified centrally in Weewx
  In general, a label color can be used with
  #set $usefontcolor = 0
  be switched off
  The order in the array is also the display position. 
```
Files for this
  weewx/skins/SeasonsEcowitt or weewx/skins/SeasonsDavis
 
Example for the skin:

- WeatherLinkLiveUDP: 	https://www.pc-wetterstation.de/wetter/weewx
- Ecowittcustom & FOSHKplugin (GW3000): https://www.pc-wetterstation.de/wetter/weewx1
- Ecowittcustom & FOSHKplugin (HP2550): 	https://www.pc-wetterstation.de/wetter/weewx2
- VantagePro: https://www.pc-wetterstation.de/wetter/weewx3
- Ecowittcustom & GW1000 & FOSHKplugin (GW2000):  https://www.pc-wetterstation.de/wetter/weewx4
- Ecowittcustom & GW1000 & FOSHKplugin (GW2000):  https://www.pc-wetterstation.de/wetter/weewx5


#### Calculation of the sunshine duration and now too rain duration:

Which, however, was modified by me weewx/user/sunrainduration.py
and the configuration is done via the weewx.conf and this entry:
```
Code:
[RadiationDays]
    min_sunshine = 120     	# Entry of extension radiationhours.py, if is installed (= limit value)
    sunshine_coeff = 0.8   	# Factor from which value sunshine is counted - the higher the later
    sunshine_min = 18     	# below this value (W/m²), sunshine is not taken into account.
    sunshine_loop = 1      # use for sunshine loop packet (or archive: sunshine_loop = 0)
    rainDur_loop = 0       # use for rain duration loop packet - default is not       
    hailDur_loop = 0       # use for piezo-rain duration loop packet - default is not
    sunshine_log = 0       # should not be logged when sunshine is recorded
    rainDur_log = 0        # no logging for rain duration
    hailDur_log = 0        # no logging for piezo-rain duration
``` 

#################################################

May 2025: 
Under [Accumulator] all "*.sig" removed, as not necessary

In sensors.inc the assignment of the signals (0..4) to percentage values ??(in the weewx.conf) is now automatically recognized and displayed correctly.

Only Ecowittcustom (former Interceptor): 

Jan 2024:
 - supports soilad1 - soilad16 and heap
 - If you will track the heap values - I use the unused value "pb" from the extended database for this

 So add this in the weeewx.conf file to
``` 
[StdCalibrate]
    [[Corrections]]
      pb = heap if heap is not None else None 
``` 

  
weewx-ecowittcustom.zip 
 - V4: sudo wee_extension --install=weewx-ecowittcustom.zip
 - V5: sudo weectl extension install weewx-ecowittcustom.zip

 or
 - V4: sudo wee_extension --install=/%path_where_file_located%/weewx-???.zip
to install.

Both use a new database schema:

wview_ecowitt.py

An existing database can also be expanded with these shell scripts:
  -> is very likely the easiest way

Version 5
- add_ecowitt_data_v5.sh
- add_ecowitt_allsignaldata_v5.sh

Version 4
- add_ecowitt_to_wview_database.sh
- add_ecowitt_to_wview_extended_database.sh

  The new data fields are added to the existing database and the old ones
  Data are retained.
  If you don't work with the standard configuration (/etc/weewx/weewx.conf), you have to
  adjust the --config=/etc/weewx/weewx.conf entry accordingly.

#################################################

In weewx.conf you can/should use the existing entry (only useful with a completely new installation) for 
``` 
Code:
[DataBindings]
     [[wx_binding]]
        schema = schemas.wview.schema
        schema_new = schemas.wview_ecowitt.schema # -> is entered in this way by the installation!
# Change to
        #schema = schemas.wview.schema
        schema = schemas.wview_ecowitt.schema

# Now there are more database schemas are available:
 - wview_ecowittrssi.py            # with the rssi fields
 - wview_ecowittrssisoilad.py      # with the rssi and soilad fields

Possibly also the database name from weewx.sdb to weewx_ecowitt.sdb
to change.
Code:
[Databases]
     # A SQLite database is simply a single file
     [[archive_sqlite]]
         database_name = weewx.sdb
         database_type = SQLite
         database_name_new = weewx_ecowitt.sdb
         database_name_new = weewx_ecowittrssi.sdb
     change to
         # database_name = weewx.sdb
         database_type = SQLite
         database_name = weewx_ecowitt.sdb       # or database_name = weewx_ecowittrssi.sdb

Since the installation routine does not change any existing entries, one must in weewx.conf
adapt a few entries

Signal assignment with GW1000 driver (the Ecowittcustom driver can evaluate the signals with the FOSHKplugin )

But if you use FOSHKplugin, the ecowittcustorm driver can also evalute the signals and all
this other data (and more), which are only available from the ecowitt_http driver
or from the old gateway GW1000  with the gw1000 driver
The weewx-ecowittcustom.zip installation routine adds these entries to weewx.conf:
[StdCalibrate]
    [[Corrections]]
        #rxCheckPercent = ws80_sig * 25 if ws80_sig is not None else None
        #rxCheckPercent = wh24_sig * 25 if wh24_sig is not None else None
        #rxCheckPercent = wh25_sig * 25 if wh25_sig is not None else None
        #rxCheckPercent = wh65_sig * 25 if wh65_sig is not None else None
        #rxCheckPercent = wh68_sig * 25 if wh68_sig is not None else None
        #signal1 = wh24_sig * 25 if wh24_sig is not None else None
        #signal2 = wh31_ch1_sig * 25 if wh31_ch1_sig is not None else None
        #signal3 = wh34_ch1_sig * 25 if wh34_ch1_sig is not None else None
        #signal4 = wh40_sig * 25 if wh40_sig is not None else None
        #signal5 = wh45_sig * 25 if wh45_sig is not None else None
        #signal6 = wh57_sig * 25 if wh57_sig is not None else None
        #signal7 = wh51_ch1_sig * 25 if wh51_ch1_sig is not None else None
        #signal8 = wh35_ch1_sig * 25 if wh35_ch1_sig is not None else None

        ws90_sig = ws90_sig * 25 if ws90_sig is not None else None
        ws85_sig = ws85_sig * 25 if ws85_sig is not None else None
        wh54_ch1_sig = wh54_ch1_sig * 25 if wh54_ch1_sig is not None else None

       hail = p_rain if p_rain is not None else None
       hailRate = p_rainrate if p_rainrate is not None else None
    
       pb = heap if heap is not None else None

       wh85_sig = ws85_sig if ws85_sig is not None else None
       ws85_sig = ws85_sig * 25 if ws85_sig is not None else None 

      lightning_distance_save = lightning_distance if lightning_distance is not None else None
      lightning_distance = lightning_distance if lightning_strike_count > 0 else None

      wh31_ch1_sig = wh31_ch1_sig *25 if wh31_ch1_sig is not None else None
      wh31_ch2_sig = wh31_ch2_sig *25 if wh31_ch2_sig is not None else None
      wh31_ch3_sig = wh31_ch3_sig *25 if wh31_ch3_sig is not None else None
      wh31_ch4_sig = wh31_ch4_sig *25 if wh31_ch4_sig is not None else None
      wh31_ch5_sig = wh31_ch5_sig *25 if wh31_ch5_sig is not None else None
      wh31_ch6_sig = wh31_ch6_sig *25 if wh31_ch6_sig is not None else None
      wh31_ch7_sig = wh31_ch7_sig *25 if wh31_ch7_sig is not None else None
      wh31_ch8_sig = wh31_ch8_sig *25 if wh31_ch8_sig is not None else None

      wn34_ch1_sig = wn34_ch1_sig *25 if wn34_ch1_sig is not None else None
      wn34_ch2_sig = wn34_ch2_sig *25 if wn34_ch2_sig is not None else None
      wn34_ch3_sig = wn34_ch3_sig *25 if wn34_ch3_sig is not None else None
      wn34_ch4_sig = wn34_ch4_sig *25 if wn34_ch4_sig is not None else None
      wn34_ch5_sig = wn34_ch5_sig *25 if wn34_ch5_sig is not None else None
      wn34_ch6_sig = wn34_ch6_sig *25 if wn34_ch6_sig is not None else None
      wn34_ch7_sig = wn34_ch7_sig *25 if wn34_ch7_sig is not None else None
      wn34_ch8_sig = wn34_ch8_sig *25 if wn34_ch8_sig is not None else None

      wh51_ch1_sig = wh51_ch1_sig *25 if wh51_ch1_sig is not None else None
      wh51_ch2_sig = wh51_ch2_sig *25 if wh51_ch2_sig is not None else None
      wh51_ch3_sig = wh51_ch3_sig *25 if wh51_ch3_sig is not None else None
      wh51_ch4_sig = wh51_ch4_sig *25 if wh51_ch4_sig is not None else None
      wh51_ch5_sig = wh51_ch5_sig *25 if wh51_ch5_sig is not None else None
      wh51_ch6_sig = wh51_ch6_sig *25 if wh51_ch6_sig is not None else None
      wh51_ch7_sig = wh51_ch7_sig *25 if wh51_ch7_sig is not None else None
      wh51_ch8_sig = wh51_ch8_sig *25 if wh51_ch8_sig is not None else None
      wh51_ch9_sig = wh51_ch9_sig *25 if wh51_ch9_sig is not None else None
      wh51_ch10_sig = wh51_ch10_sig *25 if wh51_ch10_sig is not None else None
   
So are not active and is an example:
Here everyone can choose for themselves which signals should be assigned to which Ecowitt sensor sig.
signal 1..8 belongs to the database values, with the assignment they are also recorded for evaluation.

Code:
[Station]

# Set to type of station hardware. There must be a corresponding stanza
# in this file with a 'driver' parameter indicating the driver to be used.
  station_type = Ecowittcustom		# with Ecowittcustom driver
  #station_type = GW1000			# with GW1000 driver

[[SeasonsReport]]
  skin = Seasons
  enable = false
  HTML_ROOT = /var/www/html/weewx/old

[[SeasonsEcowitt]]
  skin = SeasonsEcowitt
  enable = true
  lang =en
  # lang = de
  HTML_ROOT = /var/www/html/weewx

[StdWXCalculate]
  [[WXXTypes]]
    [[[maxSolarRad]]]
      algorithm = rs
      atc = 0.9
      
  [[Calculations]]
        pressure = prefer_hardware
        altimeter = prefer_hardware
        appTemp = prefer_hardware
        barometer = prefer_hardware
        cloudbase = prefer_hardware
        dewpoint = prefer_hardware
        ET = prefer_hardware
        heatindex = software
        humidex = prefer_hardware
        inDewpoint = prefer_hardware
        maxSolarRad = prefer_hardware
        rainRate = prefer_hardware
        windchill = software
        windrun = prefer_hardware
        
        GTS = software, archive
        GTSdate = software, archive
        utcoffsetLMT = software, archive
        dayET = prefer_hardware, archive
        ET24 = prefer_hardware, archive
        yearGDD = software, archive
        seasonGDD = software, archive

        outVaporP = software, loop
        outSVP    = software, loop
        outMixingRatio = software, loop
        outEquiTemp = software, loop
        outThetaE = software, loop
        outHumAbs = software, loop
        boilingTemp = software, loop
 
[Engine]
    # The following section specifies which services should be run and in what order.
    # Using the GW1000 as data-service,  if you whish both drivers
    # added user.sunrainduration.SunshineDuration for calculation sunshinehours
    # addet user.GTS.GTSService for calculation dayET, ET24, GTS, GTSdate and other
    [[Services]]
        data_services = user.gw1000.Gw1000Service
        # or data_services = ,
        process_services = weewx.engine.StdConvert, weewx.engine.StdCalibrate, weewx.engine.StdQC, weewx.wxservices.StdWXCalculate, user.sunrainduration.SunshineDuration
        xtype_services = weewx.wxxtypes.StdWXXTypes, weewx.wxxtypes.StdPressureCooker, weewx.wxxtypes.StdRainRater, weewx.wxxtypes.StdDelta, user.GTS.GTSService

##############################################################################
[Ecowittcustom]
    # This section is for the network traffic ecowittcustom driver.
    # The driver to use:
    driver = user.ecowittcustom
    device_type = ecowitt-client
    port = 8083         # example direct from Custom function station/gateway
    #port = 8572        # example if you use FOSHKplugin (FWD_URL = http://192.168.0.93:8572/data/report/)
    iface = eth0
    #iface = wlan0 

  [[sensor_map_extensions]]
   # mappings now in the ecowittcustom.py driver
   #  outTempBatteryStatus = wh26batt

##############################################################################

# Options for extension 'ecowitt-client' = ecowittcustom (or gw1000 too) 
[Accumulator]
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













