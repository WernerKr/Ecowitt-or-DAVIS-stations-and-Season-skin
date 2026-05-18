#encoding UTF-8
#import datetime

#set $xt = ""
#if $current.stationtype.has_data
  #if not 'EasyWeather' in $current.stationtype.raw
      #if $current.stationtype.raw not in $station.hardware  
          #set $xt = $current.stationtype.raw
      #end if
  #elif $current.model.has_data
        #set $xt = $current.model.raw 
  #end if
#end if

#try
 #set $datex = $datetime.datetime.fromtimestamp($current.dateTime.raw).strftime('%H:%M:%S')
#except
 #set $datex = ""
#end try


<div class="wx-stn-info-container">
    <div class="row">
        <div class="col-sm-1 wx-stn-info-current-obs">
            <span class="obs-header-icon">
                #if $Extras.has_key("forecast_enabled") and $Extras.forecast_enabled == '1' and $current_obs_icon != ""
                <img id="wxicon" src="${relative_url}/images/${current_obs_icon}">
                #end if
            </span>
            <span class="obs-header-outtemp">$current.outTemp</span>
        </div>
        <div class="col-sm-5">
            <div class="wx-stn-name">
		#if $page == "charts"
        <h1>$obs.label.charts_page_header</h1>
		#else if $page == "records"
                <h1>$obs.label.records_page_header</h1>
		#else if $page == "reports"
                <h1>$obs.label.reports_page_header</h1>
		#else if $page == "history"
                <h1>$obs.label.reports_page_header</h1>
		#else if $page == "about"
                <h1>$obs.label.about_page_header</h1>
		#end if
            </div>
        </div>
        <div class="col-sm-5" style="float:right;">
            <div class="wx-stn-info">
                $datex - $station.hardware $xt
                ##$obs.label.powered_by $station.hardware $xt
                ##powered by: $station.hardware $xt
            </div>
            #if $social_html != ""
            <div class="col-sm-10 wx-stn-info-social" style="float:right;">
                $social_html
            </div>
            #end if
        </div>
    </div>
    <div class="clear"></div>
</div>
