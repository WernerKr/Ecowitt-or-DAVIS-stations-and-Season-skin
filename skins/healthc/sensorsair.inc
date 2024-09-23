## sensors module for weewx skins
## Copyright Tom Keffer, Matthew Wall
## See LICENSE.txt for your rights


#errorCatcher Echo
#encoding UTF-8

## this is a conditional display of sensor data, including connectivity,
## battery status, and various voltages.  if there are no data available,
## then this degenerates to nothing displayed.


#if $current($max_delta=3600).rssiA.has_data
<div id='sensorsair_widget' class="widget">
  <div class="widget_title">
    $gettext("Status DAVIS AirLink")
    <a class="widget_control"
      onclick="toggle_widget('sensorsair')">&diams;</a>
  </div>
  <div class="widget_contents">
  <table>

    <tr><th>$gettext("Connectivity Air")</th><th></th></tr>
   <tr>
      <td class="label">$obs.label.rssiA</td>
      <td class="data">$current($max_delta=3600).rssiA</td>
    </tr>

    <tr><th>$gettext("Data Transmission Air")</th><th></th></tr>
    <tr>
      <td class="label">$obs.label.errorPacketsA</td>
      <td class="data">$current($max_delta=3600).errorPacketsA</td>
    </tr>
    <tr>
      <td class="label">$obs.label.rxPacketsA</td>
      <td class="data">$current($max_delta=3600).rxPacketsA</td>
    </tr>
    <tr>
      <td class="label">$obs.label.txPacketsA</td>
      <td class="data">$current($max_delta=3600).txPacketsA</td>
    </tr>
    <tr>
      <td class="label">$obs.label.droppedPacketsA</td>
      <td class="data">$current($max_delta=3600).droppedPacketsA</td>
    </tr>


    <tr>
      <td class="label">$obs.label.localAPIQueriesA</td>
      <td class="data">$current($max_delta=3600).localAPIQueriesA</td>
    </tr>

    <tr>
      <td class="label">$obs.label.iFreeMemChunkA</td>
      <td class="data">$current($max_delta=3600).iFreeMemChunkA</td>
    </tr>
    <tr>
      <td class="label">$obs.label.recordWriteCountA</td>
      <td class="data">$current($max_delta=3600).recordWriteCountA</td>
    </tr>
    <tr>
      <td class="label">$obs.label.iUsedMemA</td>
      <td class="data">$current($max_delta=3600).iUsedMemA</td>
    </tr>
    <tr>
      <td class="label">$obs.label.iFreeMemA</td>
      <td class="data">$current($max_delta=3600).iFreeMemA</td>
    </tr>
    <tr>
      <td class="label">$obs.label.tUsedMemA</td>
      <td class="data">$current($max_delta=3600).tUsedMemA</td>
    </tr>
    <tr>
      <td class="label">$obs.label.tFreeMemA</td>
      <td class="data">$current($max_delta=3600).tFreeMemA</td>
    </tr>
    <tr>
      <td class="label">$obs.label.iFreeMemWatermA</td>
      <td class="data">$current($max_delta=3600).iFreeMemWatermA</td>
    </tr>



    <tr><th>$gettext("Data Information Air")</th><th></th></tr>
    <tr>
      <td class="label">$obs.label.uptimeA</td>
      <td class="data">$current($max_delta=3600).uptimeA.long_form(format_string="%(day)d%(day_label)s, %(hour)d:%(minute)02d:%(second)02d")</td>
    </tr>
    <tr>
      <td class="label">$obs.label.linkUptimeA</td>
      <td class="data">$current($max_delta=3600).linkUptimeA.long_form(format_string="%(day)d%(day_label)s, %(hour)d:%(minute)02d:%(second)02d")</td>
    </tr>
    <tr>
      <td class="label">$obs.label.firmwareVersionA</td>
      <td class="data">$current($max_delta=3600).firmwareVersionA</td>
    </tr>
    <tr>
      <td class="label">$obs.label.bootloaderVersionA</td>
      <td class="data">$current($max_delta=3600).bootloaderVersionA</td>
    </tr>
    <tr>
      <td class="label">$obs.label.healthVersionA</td>
      <td class="data">$current($max_delta=3600).healthVersionA</td>
    </tr>

  </table>
  </div>

</div>
#end if