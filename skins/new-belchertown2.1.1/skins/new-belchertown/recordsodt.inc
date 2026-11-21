#errorCatcher Echo
#encoding UTF-8
#import datetime
#try
 #set $otd_date = $datetime.datetime.fromtimestamp($current.dateTime.raw).strftime('%d. %B')
#except
 #set $otd_date = datetime.datetime.today().strftime('%d. %B')
#end try


#set $this_year = datetime.date.fromtimestamp($current.dateTime.raw).year
#set $full = "time_records_page_full_date"
#set $date = "time_records_page_month_day_year"

        <main class="content">
            <article class="weewx records" itemscope itemtype="https://schema.org/CreativeWork">

                #set $otd = $on_this_day
                #if len($otd) > 1
                <section class="rec-section rec-otd" id="on-this-day">
                    <h4 style="text-align: center;"><i class="fa fa-calendar" aria-hidden="true"></i> $obs.label.records_on_this_day $otd_date </h4>
                    <div class="rec-otd-rows">
                        #for $d in reversed($otd)
                        <div class="rec-otd-row#if $d.today then ' is-today' else ''#">
                            <span class="rec-otd-year">$d.year#if $d.today then '<small>' + $obs.label.records_so_far + '</small>' else ''#</span>
                            <span class="rec-otd-low#if $d.coldest then ' is-record' else ''#"#if $d.coldest then ' title="' + $obs.label.records_coldest + '"' else ''#>$d.low</span>
                            <span class="rec-otd-bar"><span style="left: ${d.bar_left}%; width: ${d.bar_width}%"></span></span>
                            <span class="rec-otd-high#if $d.warmest then ' is-record' else ''#"#if $d.warmest then ' title="' + $obs.label.records_warmest + '"' else ''#>$d.high</span>
                            <span class="rec-otd-rain#if $d.wettest then ' is-record' else ''#"#if $d.wettest then ' title="' + $obs.label.records_wettest + '"' else ''#>#if $d.rain is not None then $d.rain else ''#</span>
                        </div>
                        #end for
                    </div>
                </section>
                #end if

            </article>
        </main>
 
