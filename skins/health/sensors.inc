## sensors module for weewx skins
## Copyright Tom Keffer, Matthew Wall
## See LICENSE.txt for your rights

## Modified to work with the DavisHealthAPI extension to display device info

#errorCatcher Echo
#encoding UTF-8

## this is a conditional display of sensor data, including connectivity,
## battery status, and various voltages.  if there are no data available,
## then this degenerates to nothing displayed.

#def get_battery_status($x)
#if $x == 0
<span class="status_ok">OK</span>
#else
<span class="status_low">LOW</span>
#end if
#end def

#set $conns = [ "signalQuality", "rssi", "afc", "txID",
                "signalQuality1", "rssi1", "afc1", "txID1",
                "signalQuality2", "rssi2", "afc2", "txID2",
                "signalQuality3", "rssi3", "afc3", "txID3",
                "signalQuality4", "rssi4", "afc4", "txID4",
                "signalQuality5", "rssi5", "afc5", "txID5",
                "signalQuality6", "rssi6", "afc6", "txID6",
                "signalQuality7", "rssi7", "afc7", "txID7", 
]
#set $battery_statuses = [ "txBatteryFlag", "txBatteryFlag1", "txBatteryFlag2", "txBatteryFlag3", "txBatteryFlag4", "txBatteryFlag5", "txBatteryFlag6", "txBatteryFlag7" ]
#set $max_battery_statuses = 5

#set $transm = [ "packetStreak", "errorPackets", "resynchs",
                "packetStreak1", "errorPackets1", "resynchs1",
                "packetStreak2", "errorPackets2", "resynchs2",
                "packetStreak3", "errorPackets3", "resynchs3",
                "packetStreak4", "errorPackets4", "resynchs4",
                "packetStreak5", "errorPackets5", "resynchs5",
                "packetStreak6", "errorPackets6", "resynchs6",
                "packetStreak7", "errorPackets7", "resynchs7",
]

##

<div id='sensors_widget' class="widget">
  <div class="widget_title">
    Sensor Status Live
    <a class="widget_control"
      onclick="toggle_widget('sensors')">&diams;</a>
  </div>
  <div class="widget_contents">
  <table>

    <tr><th>Connectivity</th><th></th></tr>
 #for $x in $conns
  #if $getattr($current($max_delta=3600,$data_binding='davishealthapi_binding'), $x).has_data
    <tr>
      #if 'signalQuality' in $x
       #set $color = 'blue'
      #else
       #set $color = 'black'
      #end if
      <td class="label"><font color=$color>$obs.label[$x]</font></td>
      #set $xv = $getattr($current($max_delta=3600,$data_binding='davishealthapi_binding'), $x) 
      <td class="data">$xv</td>
    </tr>
  #end if
 #end for

    <tr><th>Power Status</th><th></th></tr>
#if $current($max_delta=3600,$data_binding='davishealthapi_binding').supercapVolt.has_data
    <tr>
      <td class="label">$obs.label.supercapVolt</td>
      <td class="data">$current($max_delta=3600,$data_binding='davishealthapi_binding').supercapVolt.format("%.3f")</td>
    </tr>
    <tr>
      <td class="label">$obs.label.solarVolt</td>
      <td class="data">$current($max_delta=3600,$data_binding='davishealthapi_binding').solarVolt.format("%.3f")</td>
    </tr>
#end if
#if $current($max_delta=3600,$data_binding='davishealthapi_binding').uvVolt.has_data
    <tr>
      <td class="label">$obs.label.uvVolt</td>
      <td class="data">$current($max_delta=3600,$data_binding='davishealthapi_binding').uvVolt.format("%.3f")</td>
    </tr>
#end if
#if $current($max_delta=3600,$data_binding='davishealthapi_binding').txBattery.has_data
    <tr>
      <td class="label">$obs.label.txBattery</td>
      <td class="data">$current($max_delta=3600,$data_binding='davishealthapi_binding').txBattery.format("%.3f")</td>
    </tr>
#end if

#if $current($max_delta=3600,$data_binding='davishealthapi_binding').supercapVolt1.has_data
    <tr>
      <td class="label">$obs.label.supercapVolt1</td>
      <td class="data">$current($max_delta=3600,$data_binding='davishealthapi_binding').supercapVolt1.format("%.3f")</td>
    </tr>
#end if
#if $current($max_delta=3600,$data_binding='davishealthapi_binding').solarVolt1.has_data
    <tr>
      <td class="label">$obs.label.solarVolt1</td>
      <td class="data">$current($max_delta=3600,$data_binding='davishealthapi_binding').solarVolt1.format("%.3f")</td>
    </tr>
#end if
#if $current($max_delta=3600,$data_binding='davishealthapi_binding').uvVolt1.has_data
    <tr>
      <td class="label">$obs.label.uvVolt1</td>
      <td class="data">$current($max_delta=3600,$data_binding='davishealthapi_binding').uvVolt1.format("%.3f")</td>
    </tr>
#end if
#if $current($max_delta=3600,$data_binding='davishealthapi_binding').txBattery1.has_data
    <tr>
      <td class="label">$obs.label.txBattery1</td>
      <td class="data">$current($max_delta=3600,$data_binding='davishealthapi_binding').txBattery1.format("%.3f")</td>
    </tr>
#end if
#if $current($max_delta=3600,$data_binding='davishealthapi_binding').txBattery2.has_data
    <tr>
      <td class="label">$obs.label.txBattery2</td>
      <td class="data">$current($max_delta=3600,$data_binding='davishealthapi_binding').txBattery2.format("%.3f")</td>
    </tr>
#end if
#set $count = 0
 #for $x in $battery_statuses
  #set $count = $count + 1  
  #if $getattr($current($max_delta=3600,$data_binding='davishealthapi_binding'), $x).has_data
    <tr>
      <td class="label">$obs.label[$x]</td>
      #set $xv = $getattr($current($max_delta=3600,$data_binding='davishealthapi_binding'), $x) 
      <td class="data">$get_battery_status($xv.raw)</td>
    </tr>
  #else
   #if $count <= $max_battery_statuses
    <tr>
      <td class="label"><font color='red'>$obs.label[$x]</font></td>
      <td class="data"><font color='red'>N/A</font></td>
    </tr>
   #end if
  #end if
 #end for

<tr>
      <td class="label">$obs.label.consoleBattery</td>
      <td class="data">$current($max_delta=3600,$data_binding='davishealthapi_binding').consoleBattery</td>
</tr>
<tr>
      <td class="label">$obs.label.consolePower</td>
      <td class="data">$current($max_delta=3600,$data_binding='davishealthapi_binding').consolePower</td>
</tr>

    <tr><th>Data Transmission</th><th></th></tr>

 #for $x in $transm
  #if $getattr($current($max_delta=3600,$data_binding='davishealthapi_binding'), $x).has_data
    <tr>
      #if 'packetStreak' in $x
       #set $color = 'green'
      #else
       #set $color = 'black'
      #end if
      <td class="label"><font color=$color>$obs.label[$x]</font></td>
      #set $xv = $getattr($current($max_delta=3600,$data_binding='davishealthapi_binding'), $x) 
      <td class="data">$xv</td>
    </tr>
  #end if
 #end for

    <tr>
      <td class="label">$obs.label.rxBytes</td>
      <td class="data">$current($max_delta=3600,$data_binding='davishealthapi_binding').rxBytes</td>
    </tr>
    <tr>
      <td class="label">$obs.label.txBytes</td>
      <td class="data">$current($max_delta=3600,$data_binding='davishealthapi_binding').txBytes</td>
    </tr>

    <tr>
      <td class="label">$obs.label.localAPIQueries</td>
      <td class="data">$current($max_delta=3600,$data_binding='davishealthapi_binding').localAPIQueries</td>
    </tr>

    <tr><th>Data Information Live</th><th></th></tr>
    <tr>
      <td class="label">$obs.label.uptime</td>
      <td class="data">$current($max_delta=3600,$data_binding='davishealthapi_binding').uptime.long_form(format_string="%(day)d%(day_label)s, %(hour)d:%(minute)02d:%(second)02d")</td>
    </tr>
    <tr>
      <td class="label">$obs.label.linkUptime</td>
      <td class="data">$current($max_delta=3600,$data_binding='davishealthapi_binding').linkUptime.long_form(format_string="%(day)d%(day_label)s, %(hour)d:%(minute)02d:%(second)02d")</td>
    </tr>
    <tr>
      <td class="label">$obs.label.firmwareVersion</td>
      <td class="data">$current($max_delta=3600,$data_binding='davishealthapi_binding').firmwareVersion</td>
    </tr>
    <tr>
      <td class="label">$obs.label.bootloaderVersion</td>
      <td class="data">$current($max_delta=3600,$data_binding='davishealthapi_binding').bootloaderVersion</td>
    </tr>
    <tr>
      <td class="label">$obs.label.radioVersion</td>
      <td class="data">$current($max_delta=3600,$data_binding='davishealthapi_binding').radioVersion</td>
    </tr>
    <tr>
      <td class="label">$obs.label.healthVersion</td>
      <td class="data">$current($max_delta=3600,$data_binding='davishealthapi_binding').healthVersion</td>
    </tr>


  </table>
  </div>

</div>
