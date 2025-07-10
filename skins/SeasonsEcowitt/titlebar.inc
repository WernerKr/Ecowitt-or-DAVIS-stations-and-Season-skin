## titlebar for weewx skins
## Copyright Tom Keffer, Matthew Wall
## See LICENSE.txt for your rights
#errorCatcher Echo
#encoding UTF-8
## 2025-07-07 add $station.hardware to header if Ecowitt_http driver

#set $show_rss = $to_bool($DisplayOptions.get('show_rss', True))
#set $show_reports = $to_bool($DisplayOptions.get('show_reports', True))

#set $xt = ''
#set $xx = ''
#if $current.stationtype.has_data
 #if '_' in $current.stationtype.raw
  #set $xt = $current.stationtype.raw
  #set $xx = '-'
 #elif $current.model.has_data
  #set $xt = $current.model.raw
  #set $xx = '-' 
 #end if
#end if

#if $xt == '' and  'V' in $station.hardware
  #set $xt = $station.hardware
  #set $xx = '-'
#end if



<div id="title_bar">
  <div id="title">
    <h1 class="page_title">$station.location $xx $xt</h1>
    <p class="lastupdate">$current.dateTime</p>
  </div>
#if $show_rss
  <div id="rss_link"><a href="rss.xml">RSS</a></div>
#end if
#if $show_reports
  <div id="reports">
    $gettext("Monthly Reports"):
    <select name="reports" onchange="openTabularFile(value)">
      #for $monthYear in $SummaryByMonth
      <option value="$monthYear">$monthYear</option>
      #end for
      <option selected>- $gettext("select month") -</option>
    </select>
    <br/>
    $gettext("Yearly Reports"):
    <select name="reports" onchange="openTabularFile(value)">
      #for $yr in $SummaryByYear
      <option value="$yr">$yr</option>
      #end for
      <option selected>- $gettext("select year") -</option>
    </select>
    <br/>
  </div>
#end if
</div>
