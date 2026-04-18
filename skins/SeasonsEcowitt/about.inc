## about module for weewx skins
## Copyright Tom Keffer, Matthew Wall
## See LICENSE.txt for your rights
## Werner Krenn 2026/04/14

#errorCatcher Echo
#encoding UTF-8


#set $xt5 = ""
#set $xt4 = ""
#set $xt = ""
#if $current.stationtype.has_data
 #if not 'EasyWeather' in $current.stationtype.raw
  #if $current.stationtype.raw not in $station.hardware  
   #set $xt = $current.stationtype.raw
   #set $xt4 = $current.stationtype.raw[7:] 
  #end if
 #elif $current.model.has_data
  #set $xt = $current.model.raw 
  #set $xt5 = $xt
 #end if
#end if


#set $xt1 = ""
#if $current.stationtype.has_data
 #if 'EasyWeather' in $current.stationtype.raw
  #set $xt1 = $current.stationtype.raw
 #end if
#end if

#set $xt3 = ""
#set $xt2 = ""
#try
 #if '_' in $station.hardware
    #set $xt2 = $station.hardware[7:]
 #end if
#except
 #pass
#end try


<div id='about_widget' class="widget">
  <div class="widget_title">
    $gettext("About this station")
    <a class="widget_control"
      onclick="toggle_widget('about')">&diams;</a>
  </div>
  <div class="widget_contents">
  <table>
    <tr>
      <td class="label">$gettext("Hardware")</td>
     #try
       #if $current.apName.has_data
        #set $xt3 = $current.apName
       #end if
     #except
      #pass
     #end try
     #if $xt3 != "" and $xt2 != "" and $xt4 == ""
       <td class="data">$xt3$xt2</td>
     #else
       <td class="data">$station.hardware</td>
     #end if
    </tr>
    #if ( $xt !='' and $xt4 != "" and $xt3 == "") or $xt5 != ""
    <tr>
      <td class="label">      </td>
       <td class="data">$xt</td>
    </tr>
    #end if

    #if $xt1 !=''
    <tr> 
      <td class="label">$gettext("StationType")</td>
      <td class="data">$xt1</td>
    </tr>
    #end if

    ##<tr> 
    ##  <td class="label">$gettext("Station-Hardware")</td>
    ##  <td class="data">$station.hardware</td>
    ##</tr>
    ##<tr> 
    ##  <td class="label">$gettext("Station-type")</td>
    ##  <td class="data">$current.stationtype.raw</td>
    ##</tr>

   #try
     #if $current.apName.has_data and ($xt2 == "" or $station.hardware != $current.stationtype.raw) 
     <tr> 
      <td class="label">$gettext("apName")</td>
      <td class="data">$current.apName$xt4</td>
     </tr>
     #end if
   #except
     #pass
   #end try

   #try
    #if $current.ws_interval.has_data
    <tr>
      #set $xx = "" 
      #try
       #set $x = $current.ws_interval.long_form(format_string="%(minute)d%(minute_label)s, %(second)d%(second_label)s")
      #except
       #set $x = $getattr($current, 'ws_interval').format("%.0f")
       #set $xx = $gettext("Seconds")
      #end try
      <td class="label">$gettext("WS Interval")</td>
      <td class="data">$x $xx</td>
    </tr>
    #end if
   #except
    #pass
   #end try

   #try
    #if $current.upgrade.has_data
    <tr> 
      <td class="label">$gettext("Station Auto upgrade")</td>
      <td class="data">$current.upgrade</td>
    </tr>
    #end if
    #if $current.newVersion.has_data
    <tr> 
      <td class="label">$gettext("Station newVersion")</td>
      <td class="data">$current.newVersion</td>
    </tr>
    #end if
    #if $current.runtime.has_data
    <tr> 
      <td class="label">$gettext("Station uptime")</td>
      <td class="data">$current.runtime.long_form(format_string="%(day)d%(day_label)s, %(hour)d%(hour_label)s, %(minute)d%(minute_label)s")</td>
    </tr>
    #end if
   #if $current.ws90_ver.has_data 
    <tr> 
       <td class="label">$gettext("WS90 Vers")</td>
      <td class="data">$current.ws90_ver.format("%.0f")</td>
    </tr>
    #end if
   #if $current.ws85_ver.has_data 
    <tr> 
       <td class="label">$gettext("WS85 Vers")</td>
      <td class="data">$current.ws85_ver.format("%.0f")</td>
    </tr>
    #end if
   #if $current.pb.has_data 
    <tr> 
       <td class="label">$gettext("Heap")</td>
      <td class="data">$current.pb</td>
    </tr>
    #end if
   #except
    #pass
   #end try
   #try
    #if $current.appUptimeC.has_data
    <tr> 
      <td class="label">$obs.label.appUptimeC</td>
      <td class="data">$current($max_delta=3600).appUptimeC.long_form(format_string="%(day)d%(day_label)s, %(hour)d:%(minute)02d:%(second)02d")</td>
    </tr>
    #end if
   #except
    #pass
   #end try
    <tr>
      <td class="label">$gettext("Latitude")</td>
      <td class="data">$station.latitude[0]&deg; $station.latitude[1]' $station.latitude[2]</td>
    </tr>
    <tr>
      <td class="label">$gettext("Longitude")</td>
      <td class="data">$station.longitude[0]&deg; $station.longitude[1]' $station.longitude[2]</td>
    </tr>
    <tr>
      <td class="label">$pgettext("Geographical", "Altitude")</td>
      <td class="data">$station.altitude</td>
    </tr>
    <tr>
      <td class="label">$gettext("Server uptime")</td>
      <td class="data">$station.os_uptime.long_form</td>
    </tr>
    <tr>
      <td class="label">$gettext("WeeWX uptime")</td>
      <td class="data">$station.uptime.long_form</td>
    </tr>
    <tr>
      <td class="label">$gettext("WeeWX version")</td>
      <td class="data">$station.version</td>
    </tr>
    <tr>
      <td class="label">$gettext("Skin")</td>
      <td class="data">$SKIN_NAME $SKIN_VERSION</td>
    </tr>
  </table>
  </div>

</div>
