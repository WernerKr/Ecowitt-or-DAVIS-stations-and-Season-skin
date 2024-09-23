## sensors module for weewx skins
## Copyright Tom Keffer, Matthew Wall
## See LICENSE.txt for your rights

## Modified to work with the DavisHealthAPI extension to display device info

#errorCatcher Echo
#encoding UTF-8

## this is a conditional display of sensor data, including connectivity,
## battery status, and various voltages.  if there are no data available,
## then this degenerates to nothing displayed.


#if $current($max_delta=3600,$data_binding='davishealthapi_binding').rssiA.has_data
<div id='sensorsair_widget' class="widget">
  <div class="widget_title">
    Status DAVIS AirLink
    <a class="widget_control"
      onclick="toggle_widget('sensorsair')">&diams;</a>
  </div>
  <div class="widget_contents">
  <table>

    <tr><th>Connectivity Air</th><th></th></tr>
   <tr>
      <td class="label">$obs.label.rssiA</td>
      <td class="data">$current($max_delta=3600,$data_binding='davishealthapi_binding').rssiA</td>
    </tr>

    <tr><th>Data Transmission Air</th><th></th></tr>
    <tr>
      <td class="label">$obs.label.errorPacketsA</td>
      <td class="data">$current($max_delta=3600,$data_binding='davishealthapi_binding').errorPacketsA</td>
    </tr>
    <tr>
      <td class="label">$obs.label.rxPacketsA</td>
      <td class="data">$current($max_delta=3600,$data_binding='davishealthapi_binding').rxPacketsA</td>
    </tr>
    <tr>
      <td class="label">$obs.label.txPacketsA</td>
      <td class="data">$current($max_delta=3600,$data_binding='davishealthapi_binding').txPacketsA</td>
    </tr>
    <tr>
      <td class="label">$obs.label.droppedPacketsA</td>
      <td class="data">$current($max_delta=3600,$data_binding='davishealthapi_binding').droppedPacketsA</td>
    </tr>


    <tr>
      <td class="label">$obs.label.localAPIQueriesA</td>
      <td class="data">$current($max_delta=3600,$data_binding='davishealthapi_binding').localAPIQueriesA</td>
    </tr>

    <tr>
      <td class="label">$obs.label.iFreeMemChunkA</td>
      <td class="data">$current($max_delta=3600,$data_binding='davishealthapi_binding').iFreeMemChunkA</td>
    </tr>
    <tr>
      <td class="label">$obs.label.recordWriteCountA</td>
      <td class="data">$current($max_delta=3600,$data_binding='davishealthapi_binding').recordWriteCountA</td>
    </tr>
    <tr>
      <td class="label">$obs.label.iUsedMemA</td>
      <td class="data">$current($max_delta=3600,$data_binding='davishealthapi_binding').iUsedMemA</td>
    </tr>
    <tr>
      <td class="label">$obs.label.iFreeMemA</td>
      <td class="data">$current($max_delta=3600,$data_binding='davishealthapi_binding').iFreeMemA</td>
    </tr>
    <tr>
      <td class="label">$obs.label.tUsedMemA</td>
      <td class="data">$current($max_delta=3600,$data_binding='davishealthapi_binding').tUsedMemA</td>
    </tr>
    <tr>
      <td class="label">$obs.label.tFreeMemA</td>
      <td class="data">$current($max_delta=3600,$data_binding='davishealthapi_binding').tFreeMemA</td>
    </tr>
    <tr>
      <td class="label">$obs.label.iFreeMemWatermA</td>
      <td class="data">$current($max_delta=3600,$data_binding='davishealthapi_binding').iFreeMemWatermA</td>
    </tr>



    <tr><th>Data Information Air</th><th></th></tr>
    <tr>
      <td class="label">$obs.label.uptimeA</td>
      <td class="data">$current($max_delta=3600,$data_binding='davishealthapi_binding').uptimeA.long_form(format_string="%(day)d%(day_label)s, %(hour)d:%(minute)02d:%(second)02d")</td>
    </tr>
    <tr>
      <td class="label">$obs.label.linkUptimeA</td>
      <td class="data">$current($max_delta=3600,$data_binding='davishealthapi_binding').linkUptimeA.long_form(format_string="%(day)d%(day_label)s, %(hour)d:%(minute)02d:%(second)02d")</td>
    </tr>
    <tr>
      <td class="label">$obs.label.firmwareVersionA</td>
      <td class="data">$current($max_delta=3600,$data_binding='davishealthapi_binding').firmwareVersionA</td>
    </tr>
    <tr>
      <td class="label">$obs.label.bootloaderVersionA</td>
      <td class="data">$current($max_delta=3600,$data_binding='davishealthapi_binding').bootloaderVersionA</td>
    </tr>
    <tr>
      <td class="label">$obs.label.healthVersionA</td>
      <td class="data">$current($max_delta=3600,$data_binding='davishealthapi_binding').healthVersionA</td>
    </tr>

  </table>
  </div>

</div>
#end if