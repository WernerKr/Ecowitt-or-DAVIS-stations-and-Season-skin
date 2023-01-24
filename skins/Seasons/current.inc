## current module for weewx skins
## Copyright Tom Keffer, Matthew Wall
## See LICENSE.txt for your rights
#errorCatcher Echo
#encoding UTF-8

#set $allways_lang = False
#set $use_lang = False
#try
 #if $SKIN_VERSION != '' or $allways_lang == True
  #set $use_lang = True
 #end if
#except
 #pass
#end try

#set $ecowitt_hw = [('GW1000'),
                    ('GW1100'),
                    ('GW2000'),
                    ('WH2650'),
                    ('WH2680'),
                    ('WS1900'),
                    ('WN1980'),
                    ('HP2550'),
                    ('ecowitt-client'),
                    ]

## The list of observations determines which database fields will be shown in
## the summary as well as the order in which they will be displayed.
#set $observ = [('outTemp','#e85d0d','current','1'),
('heatindex','#b44242','current','1'),
('windchill','#4282b4','current','1'),
('dewpoint','#ea4c12','current','1'),
('outHumidity','#82dbf2','current','1'),
 ('appTemp','','current','1'),
 ('appTemp1','','current','1'),
 ('humidex','','current','1'),
 ('humidex1','','current','1'),
 ('outWetbulb','','current','1'),
 ('wetbulb','','current','1'),
('THSW','','current','1'),
('THW','','current','1'),
('barometer','#25ea2f','current','1'),
('pressure','','current','1'),
('cloudbase','','current','1'),
('windSpeed','#0000ff','current','1'),
('windGust','#4282b4','day','1'),
 ('windspdmph_avg10m','','current','1'),
 ('maxdailygust','','current','1'),
 ('windSpeed1','','current','1'),
 ('windDir1','','current','1'),
 ('windSpeed10','','current','1'),
 ('windDir10','','current','1'),
 ('windGustSpeed10','','current','1'),
 ('windGustDir10','','current','1'),
('windrun','','day','1'),
('rain','#72b2c4','current','1'),
('rainRate','#72b2c4','current','1'),
 ('rain15','','current','1'),
 ('rain60','','current','1'),
 ('eventRain','#72b2c4','current','1'),
 ('stormRain','#72b2c4','current','1'),
 ('stormRainlast','','current','1'),
 ('stormStart','','current','1'),
 ('rain_storm_start_at','','current','1'),
 ('rain_storm_last_start_at','','current','1'),
 ('rain_storm_last_end_at','','current','1'),
 ('rain_today','#72b2c4','day','1'),
 ('hourRain','','current','1'),
 ('dayRain','','current','1'),
 ('rain24','','current','1'),
 ('weekRain','','current','1'),
 ('monthRain','','current','1'),
 ('yearRain','','current','1'),
 ('totalRain','','current','1'),
 ('raintotal','#72b2c4','current','1'),
('hail','#72b2c4','current','1'),
('hailRate','#72b2c4','current','1'),
('erain_piezo','#72b2c4','current','1'),
('hrain_piezo','','current','1'),
('drain_piezo','','current','1'),
('wrain_piezo','','current','1'),
('mrain_piezo','','current','1'),
('yrain_piezo','','current','1'),
('snow','','current','1'),
('snowRate','','current','1'),
('snowMoisture','','current','1'),
('snowDepth','','current','1'),
('UV','#E238EC','current','1'),
('ET','#42B4B4','current','1'),
 ('dayET','#42B4B4','current','1'),
 ('monthET','','current','1'),
 ('yearET','','current','1'),
('radiation','#f2a265','current','1'),
 ('maxSolarRad','#f2a265','current','1'),
('luminosity','','current','0'),
('pm25_1','#0e25f2','current','1'),
 ('pm25_avg_24h_ch1','','current','1'),
('pm25_2','#0e25f2','current','1'),
 ('pm25_2','','aqiepa','1'),
 ('pm25_2','','aqieea','1'),
 ('pm25_avg_24h_ch2','','current','1'),
('pm25_3','#0e25f2','current','1'),
 ('pm25_3','','aqiepa','1'),
 ('pm25_3','','aqieea','1'),
 ('pm25_avg_24h_ch3','','current','1'),
('pm25_4','#0e25f2','current','1'),
 ('pm25_avg_24h_ch4','','current','1'),
('inTemp','#c95716','current','1'),
('inHumidity','#17c4ef','current','1'),
('inDewpoint','','current','1'),
('extraTemp1','#e85d0d','current','1'),
('extraHumid1','#e85d0d','current','1'),
('extraTemp2','#1a50bc','current','1'),
('extraHumid2','#1a50bc','current','1'),
('extraTemp3','#b44242','current','1'),
('extraHumid3','#b44242','current','1'),
('extraTemp4','#42B4B4','current','1'),
('extraHumid4','#42B4B4','current','1'),
('extraTemp5','#b442b4','current','1'),
('extraHumid5','#b442b4','current','1'),
('extraTemp6','#0000ff','current','1'),
('extraHumid6','#0000ff','current','1'),
('extraTemp7','#f90415','current','1'),
('extraHumid7','#f90415','current','1'),
('extraTemp8','#5127db','current','1'),
('extraHumid8','#5127db','current','1'),
('soilTemp1','#4282b4','current','1'),
('soilTemp2','#b44242','current','1'),
('soilTemp3','#42b442','current','1'),
('soilTemp4','#42b4b4','current','1'),
('soilTemp5','#f90415','current','1'),
('soilTemp6','#5127db','current','1'),
('soilTemp7','#42b4b4','current','1'),
('soilTemp8','#b442b4','current','1'),
('soilMoist1','#e85d0d','current','1'),
('soilMoist2','#1a50bc','current','1'),
('soilMoist3','#b44242','current','1'),
('soilMoist4','#42B4B4','current','1'),
('soilMoist5','#b442b4','current','1'),
('soilMoist6','#0000ff','current','1'),
('soilMoist7','#f90415','current','1'),
('soilMoist8','#5127db','current','1'),
('leafTemp1','#5427db','current','1'),
('leafTemp2','#e85d0d','current','1'),
('leafTemp3','#e85d0d','current','1'),
('leafTemp4','#e85d0d','current','1'),
('leafWet1','#5127db','current','1'),
('leafWet2','#5127db','current','1'),
('leafWet3','#5127db','day','1'),
('leafWet4','#5127db','day','1'),
('leafWet5','#5127db','current','1'),
('leafWet6','#5127db','current','1'),
('leafWet7','#5127db','current','1'),
('leafWet8','#5127db','current','1'),
('leak_1','#006eff','current','1'),
('leak_2','#006eff','current','1'),
('leak_3','#006eff','current','1'),
('leak_4','#006eff','current','1'),
('pb','','day','1'),
('co','','current','1'),
('nh3','','day','1'),
('no2','','day','1'),
('o3','','day','1'),
('so2','','day','1'),
('noise','','current','1'),
 ('lightningcount','','current','1'),
('lightning_strike_count','','day','1'),
('lightning_energy','','current','1'),
('lightning_noise_count','','current','1'),
('ET24','#42B4B4','current','1'),
('GTS','#25ea2f','current','1'),
('GTSdate','#25ea2f','day','2'),
('radiation','','yesterday','1'),
('sunshine_hours','#f2a265','day','1'),
('sunshine_time','#f2a265','day','1'),
('- - - - - - - - - - - - - - - - - - - - -','','current','3'),
('Daten CO2-Sensor','','current','3'),
('co2_Temp','#f20e3c','current','1'),
('co2_Hum','#0e25f2','current','1'),
('co2','#32e5d9','current','1'),
 ('co2_24h','','current','1'),
('pm2_5','#0e25f2','current','1'),
 ('pm2_5_aqi','','current','1'),
 ('pm2_5','','aqiepa','1'),
 ('pm2_5','','aqieea','1'),
 ('pm25_24h_co2','','current','1'),
('pm10_0','#0e25f2','current','1'),
 ('pm10_24h_co2','','current','1'),
('- - - - - - - - - - - - - - - - - - - - -','','current','0'),
('Daten Air','','current','0'),
('co2_Temp','#f20e3c','current','0'),
('co2_Hum','#0e25f2','current','0'),
('dewpoint1','#ea4c12','current','1'),
('heatindex1','#b44242','current','1'),
('wetbulb1','','current','1'),
('pct_pm_data_last_1_hour','','current','1'),
('pct_pm_data_last_3_hours','','current','1'),
('pct_pm_data_last_24_hours','','current','1'),
('pm1_0','','current','1'),
('pm2_5','#0e25f2','current','0'),
 ('pm2_5_aqi','','current','0'),
 ('pm2_5','#0e25f2','aqiepa','0'),
 ('pm2_5','#0e25f2','aqieea','0'),
 ('pm25_24h_co2','','current','0'),
('pm2_5_nowcast','','current','1'),
('pm_2p5_last_1_hour','','current','1'),
('pm_2p5_last_3_hours','','current','1'),
('pm_2p5_last_24_hours','','current','1'),
('pm10_0','#0e25f2','current','0'),
('pm10_0_nowcast','','current','1'),
('pm_10_last_1_hour','','current','1'),
('pm_10_last_3_hours','','current','1'),
('pm_10_last_24_hours','','current','1'),
('- - - - - - - - - - - - - - - - - - - - -','#E238EC','current','0'),
('Daten VUE','','current','0'),
('outTemp_2','#e85d0d','current','1'),
('outHumidity_2','#82dbf2','current','1'),
('heatindex2','#b44242','current','1'),
('windchill2','#4282b4','current','1'),
('dewpoint2','#ea4c12','current','1'),
('outWetbulb_2','','current','1'),
('THSW_2','','current','1'),
('THW_2','','current','1'),
('UV_2','#E238EC','current','1'),
('radiation_2','#f2a265','current','1'),
('windSpeed_2','#0000ff','current','1'),
 ('windDir_2','#0000ff','current','1'),
('windGust_2','#4282b4','current','1'),
('windGustDir_2','#4282b4','current','1'),
('rain_2','#72b2c4','current','1'),
('rainRate_2','#72b2c4','current','1'),
 ('rain15_2','','current','1'),
 ('rain60_2','','current','1'),
 ('stormRain_2','#72b2c4','current','1'),
 ('stormRainlast_2','','current','1'),
 ('stormStart_2','','current','1'),
 ('rain_storm_start_at_2','#72b2c4','current','1'),
 ('rain_storm_last_start_at_2','#72b2c4','current','1'),
 ('rain_storm_last_end_at_2','#72b2c4','current','1'),
 ('dayRain_2','','current','1'),
 ('rain24_2','','current','1'),
 ('monthRain_2','','current','1'),
 ('yearRain_2','','current','1'),
]


#set $usefontcolor = 1
#set $ecowitt = 0
#for $x in $ecowitt_hw
  #if $x in $station.hardware
        #set $ecowitt = 1
  #end if
#end for
##
#def decHourToHMstr($sh)
 #if $sh != None
  #set $f_sh = float($sh)
  #set $sh_std = int($f_sh)
  #set $sh_min = round(($f_sh-int($f_sh))*60)
  #if $sh_min == 60 
   #set $sh_min = 0
   #set $sh_std = $sh_std + 1 
  #end if 
  #if $sh_min < 10
   <td class="data">$sh_std:0$sh_min Std.</td>
  #else
   <td class="data">$sh_std:$sh_min Std.</td>
  #end if
 #end if
#end def
##
#def compute_pm2_5_aqiepa($xv)
#set $xf = float($xv)
#set $x = int($xf * 10) / 10
  #if $x <= 12.0    ##        Good # Green
     #set $xx = int($x /12.0 * 50)
     #set $color = '#00e400'
  #elif $x <= 35.4 ##         Moderate # Yellow
     #set $xx = int(($x - 12.1) / 23.3 * 49.0 + 51.0)
     #set $color = '#e8e81b'
  #elif $x <= 55.4 ##         Unhealthy for senstive # Orange
     #set $color = '#ff7e00'
     #set $xx =  int(($x - 35.5) / 19.9 * 49.0 + 101.0)
  #elif $x <= 150.4 ##        Unhealthy # Red
     #set $xx =  int(($x - 55.5) / 94.9 * 49.0 + 151.0)
     #set $color = '#ff0000'
  #elif $x <= 250.4 ##        Very Unhealthy # Purple
     #set $xx =  int(($x - 150.5) / 99.9 * 99.0 + 201.0)
     #set $color = '#8f3f97' 
  #elif $x <= 350.4 ##        Hazardous # Maroon
     #set $xx =  int(($x - 250.5) / 99.9 * 99.0 + 301.0)
     #set $color = '#7e0023'
  #else              ##         Hazardous # Maroon
     #set $xx =  int(($x - 350.5) / 149.9 * 99.0 + 401.0)
     #set $color = '#7e0023'
  #end if
<td class="data"><span><font color=$color>$xx AQI EPA</font></span></td>
#end def
##
#def compute_pm2_5_aqieea($xv)
#set $xf = float($xv)
#set $x = int($xf * 10) / 10
  #if $x <= 10.0    ##        Good 	    0..1 < 10
     #set $xx = int($x * 10) / 100
     #set $color = '#50f0e6'
  #elif $x <= 20.0 ##         Moderate        1..2 < 20
     #set $xx = int($x * 10) / 100
     #set $color = '#50ccaa'  
  #elif $x <= 25.0 ##         Unhealthy for senstive  2..3 < 25
     #set $color = '#e8e81b'  ##'#f0e641'
     #set $xx =  int(($x-20)/0.5 + 20 ) / 10
  #elif $x <= 50.0 ##        Unhealthy 	     3..4	< 50
     #set $xx =  int(($x-25)/2.5 + 30 ) / 10
     #set $color = '#ff5050'
  #elif $x <= 75.0 ##        Very Unhealthy    4..5	< 75
     #set $xx =  int(($x-25)/2.5 + 30 ) / 10
     #set $color = '#960032' 
  #else            ##        Hazardous 
     #set $xx =  int(($x/75)*50) / 10
     #set $color = '#7d2181'
  #end if
#if $xx > 5.9
 <td class="data"><span><font color=$color> >5 AQI EEA</font></span></td>
#else
 <td class="data"><span><font color=$color>$xx AQI EEA</font></span></td>
#end if
#end def
##


<div id='current_widget' class="widget">
  <div class="widget_title">
    #if not $use_lang
      Current Conditions
    #else 
      $gettext("Current Conditions")
    #end if
    <a class="widget_control"
      onclick="toggle_widget('current')">&diams;</a>
  </div>

  <div class="widget_contents">
  <table>
    <tbody>

 #for $x in $observ
   #if $x[2] == 'day'
     #set $xt = getattr($day, $x[0])
   #elif $x[2] == 'yesterday'
     #set $xt = getattr($yesterday, $x[0])
   #elif $x[2] == 'aqiepa' or $x[2] == 'aqieea' 
     #set $xt = getattr($current, $x[0])
   #else
     #set $xt = getattr($current, $x[0])
   #end if 
  
   #if ($xt.has_data and $x[3] == '1') or $x[3] == '2' or $x[3] == '3'
    #if $usefontcolor == 1
      #set $color = $x[1]
      #if $color == ''
        #set $color = 'black'
      #end if 
    #else
      #set $color = 'black'
    #end if
    #if $x[3] == '3'
      <tr>
        <td class="label"><font color=$color><b>$x[0]</b></font></td>
        <td class="data"><font color=$color> </font></td>
      </tr>
    #elif $x[0] == 'barometer'
      <tr>
        <td class="label"><font color=$color>$obs.label[$x[0]]</font></td>
        <td class="data">$current.barometer ($trend.barometer.formatted)</td>
      </tr>
    #elif $x[0] == 'pressure'
      <tr>
        <td class="label"><font color=$color>$obs.label[$x[0]]</font></td>
        <td class="data">$current.pressure ($trend.pressure.formatted)</td>
      </tr>
    #elif $x[0] == 'windSpeed'
      <tr>
        <td class="label"><font color=$color>$obs.label[$x[0]]</font></td>
        <td class="data">$current.windSpeed $current.windDir.ordinal_compass ($current.windDir)</td>
      </tr>
    #elif $x[0] == 'windGust'
      <tr>
        <td class="label"><font color=$color>$obs.label[$x[0]]</font></td>
        <td class="data">$current.windGust $current.windGustDir.ordinal_compass ($current.windGustDir)</td>
      </tr>
    #elif $x[0] == 'windrun'
      <tr>
        <td class="label"><font color=$color>$obs.label[$x[0]]</font></td>
        <td class="data">$day.windrun.sum</td>
      </tr>
    #elif $x[0] == 'windspdmph_avg10m'
      <tr>
        <td class="label"><font color=$color>$obs.label[$x[0]]</font></td>
        <td class="data">$current.windspdmph_avg10m $current.winddir_avg10m.ordinal_compass ($current.winddir_avg10m)</td>
      </tr>
    #elif $x[0] == 'rain_today'
      <tr>
        <td class="label"><font color=$color>$obs.label[$x[0]]</font></td>
        <td class="data">$day.rain.sum</td>
      </tr>
    #elif 'soilMoist' in $x[0] 
      <tr>
        <td class="label"><span><font color=$color>$obs.label[$x[0]]</font></span></td>
        #if $ecowitt == 1
          #set $xv = $getattr($current, $x[0])
          <td class="data">$xv.format("%.0f", add_label=False)%</td>
        #else
          <td class="data">$getattr($current, $x[0])</td>
        #end if
      </tr>
    #elif 'leafWet' in $x[0] 
      <tr>
        <td class="label"><span><font color=$color>$obs.label[$x[0]]</font></span></td>
        #if $ecowitt == 1
          #set $xv = $getattr($current, $x[0])
          <td class="data">$xv.format("%.0f", add_label=False)%</td>
        #else
          <td class="data">$getattr($current, $x[0])</td>
        #end if
      </tr>
    #elif 'leak_' in $x[0] 
      <tr>
        <td class="label"><span><font color=$color>$obs.label[$x[0]]</font></span></td>
          #set $xv = $getattr($current, $x[0])
          <td class="data">$xv.format("%.2f")</td>
      </tr>
    #elif $x[0] == 'lightningcount'
      <tr>
        <td class="label"><span><font color=$color>$obs.label[$x[0]]</font></span></td>
          <td class="data">$current.lightningcount.format("%.0f")</td>
      </tr>
    #elif $x[0] == 'lightning_strike_count'
      <tr>
        <td class="label"><span><font color=$color>$obs.label[$x[0]]</font></span></td>
        <td class="data">$current.lightning_strike_count</td>
      </tr>
      <tr>
        <td class="label">$obs.label.lightning_distance</td>
        <td class="data">$current.lightning_distance km</td>
      </tr>
      <tr>
        <td class="label">$obs.label.lightning_disturber_count</td>
        #if $current.lightning_disturber_count.raw == 0
         <td class="data">N/A</td> 
        #else
         <td class="data">$current.lightning_disturber_count</td>
        #end if
      </tr>
    #elif $x[0] == 'GTSdate'
      <tr>
        <td class="label"><span><font color=$color>$obs.label[$x[0]]</font></span></td>
          <td class="data">$day.GTSdate.last.format("%d.%m.%Y")</td>
      </tr>
    #elif 'sunshine_' in $x[0] 
      <tr>
        <td class="label"><span><font color=$color>$obs.label[$x[0]]</font></span></td>
          #set $xv = $xt.sum.raw
          $decHourToHMstr($xv)
	   ##<td class="data">$day.sunshine_hours.sum.format("%.3f", add_label=False) Std.</td>
      </tr>
    #elif $x[0] == 'radiation' and $x[2] == 'yesterday'
      <tr>
        <td class="label"><span><font color=$color>$obs.label.energy_integral</font></span></td>
          <td class="data">$yesterday.radiation.energy_integral.kilowatt_hour_per_meter_squared</td>
      </tr>
    #elif $x[2] == 'aqiepa'
      <tr>
        <td class="label"><span><font color=$color>$obs.label[$x[0]]</font></span></td>
        #set $xv = $xt.raw
        $compute_pm2_5_aqiepa($xv)
      </tr>
    #elif $x[2] == 'aqieea'
      <tr>
        <td class="label"><span><font color=$color>$obs.label[$x[0]]</font></span></td>
        #set $xv = $xt.raw
        $compute_pm2_5_aqieea($xv)
      </tr>
    #else
      <tr>
        <td class="label"><font color=$color>$obs.label[$x[0]]</font></td>
        <td class="data">$xt</td>
      </tr>
    #end if
  #end if
#end for
##

    </tbody>
  </table>
  </div>

</div>
