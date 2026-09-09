#encoding UTF-8
#import datetime
#from datetime import timedelta


<section class="records-section-card records-section-card--custom">
  #set $Time = "%H:%M"
  #set $d = $current.dateTime.format("%H:%M")
    <div class="records-section-card__header">
        <h2 class="records-section-card__title">$obs.label.records_average_hourly</h2>
    </div>
    <div class="records-section-card__table">
        <div class="records-section-cardavg__period-header">
            <div class="records-section-cardavg__period-header-cell records-section-cardavg__period-header-cell">$obs.label.records_time</div>
            <div class="records-section-cardavg__period-header-cell records-section-cardavg__period-header-cell">$obs.label.outTemp</div>
            <div class="records-section-cardavg__period-header-cell records-section-cardavg__period-header-cell">$obs.label.outHumidity</div>
            <div class="records-section-cardavg__period-header-cell records-section-cardavg__period-header-cell">$obs.label.barometer</div>
            <div class="records-section-cardavg__period-header-cell records-section-cardavg__period-header-cell">$obs.label.rain</div>
            <div class="records-section-cardavg__period-header-cell records-section-cardavg__period-header-cell">$obs.label.windSpeed</div>
            <div class="records-section-cardavg__period-header-cell records-section-cardavg__period-header-cell">$obs.label.records_sun_records</div>
        </div>
  #for $hour in $day.hours
    #if ($hour.dateTime.format($Time) < $d)
        <div class="records-section-card__body">
            <article class="records-record-card">
                <h3 class="records-record-card__hour">$hour.dateTime.format($Time)</h3>
                <section class="records-record-period records-record-period--yesterday"">
                    <div class="records-record-period__label">$obs.label.snapshot_period_day</div>
                    <div class="records-record-period__value"><span class="records-record-period__value-main">$hour.outTemp.avg</span></div>
                </section>
                <section class="records-record-period records-record-period--yesterday">
                    <div class="records-record-period__label">$obs.label.snapshot_period_yesterday</div>
                    <div class="records-record-period__value"><span class="records-record-period__value-main">$hour.outHumidity.avg</span></div>
                </section>
                <section class="records-record-period records-record-period--week">
                    <div class="records-record-period__label">$obs.label.snapshot_period_7days</div>
                    <div class="records-record-period__value"><span class="records-record-period__value-main">$hour.barometer.avg</span></div>
                </section>
                <section class="records-record-period records-record-period--month">
                    <div class="records-record-period__label">$obs.label.snapshot_period_month</div>
                    <div class="records-record-period__value"><span class="records-record-period__value-main">$hour.rain.sum.format("%.1f")</span></div>
                </section>
                <section class="records-record-period records-record-period--year">
                    <div class="records-record-period__label">$current.dateTime.format("%Y")</div>
                    <div class="records-record-period__value"><span class="records-record-period__value-main_nb">$hour.windSpeed.avg / $hour.windDir.avg.ordinal_compass</span></div>
                </section>
                <section class="records-record-period records-record-period--year">
                    <div class="records-record-period__label">$obs.label.records_all_time</div>
                    <div class="records-record-period__value"><span class="records-record-period__value-main">$hour.radiation.avg</span></div>
                </section>
            </article>
        </div>
    #end if
  #end for
    <br>
        <div class="records-section-card__body">
            <article class="records-record-card">
                <h4 class="records-record-card__title">$obs.label.records_averages_from_today</h4>
                <section class="records-record-period records-record-period--yesterday"">
                    <div class="records-record-period__label">$obs.label.snapshot_period_day</div>
                    <div class="records-record-period__value"><span class="records-record-period__value-main">$day.outTemp.avg</span></div>
                </section>
                <section class="records-record-period records-record-period--yesterday">
                    <div class="records-record-period__label">$obs.label.snapshot_period_yesterday</div>
                    <div class="records-record-period__value"><span class="records-record-period__value-main">$day.outHumidity.avg</span></div>
                </section>
                <section class="records-record-period records-record-period--week">
                    <div class="records-record-period__label">$obs.label.snapshot_period_7days</div>
                    <div class="records-record-period__value"><span class="records-record-period__value-main">$day.barometer.avg</span></div>
                </section>
                <section class="records-record-period records-record-period--month">
                    <div class="records-record-period__label">$obs.label.snapshot_period_month</div>
                    <div class="records-record-period__value"><span class="records-record-period__value-main"><div><font size="2">$obs.label.records_total $obs.label.snapshot_period_today</font></div><div>$day.rain.sum.format("%.1f")</span></div>
                </section>
                <section class="records-record-period records-record-period--year">
                    <div class="records-record-period__label">$current.dateTime.format("%Y")</div>
                    <div class="records-record-period__value"><span class="records-record-period__value-main"><font size="2"><div>$obs.label.windGustDir</div></font><div>$day.wind.gustdir.ordinal_compass</div></span></div>
                </section>
                <section class="records-record-period records-record-period--year">
                    <div class="records-record-period__label">$obs.label.records_all_time</div>
                    <div class="records-record-period__value"><span class="records-record-period__value-main">$day.radiation.avg</span></div>
                </section>
            </article>
        </div>

    <br>
        <div class="records-section-card__body">
            <article class="records-record-card">
                <h4 class="records-record-card__title">$obs.label.records_averages_from_yesterday</h4>
                <section class="records-record-period records-record-period--yesterday"">
                    <div class="records-record-period__label">$obs.label.snapshot_period_day</div>
                    <div class="records-record-period__value"><span class="records-record-period__value-main">$yesterday.outTemp.avg</span></div>
                </section>
                <section class="records-record-period records-record-period--yesterday">
                    <div class="records-record-period__label">$obs.label.snapshot_period_yesterday</div>
                    <div class="records-record-period__value"><span class="records-record-period__value-main">$yesterday.outHumidity.avg</span></div>
                </section>
                <section class="records-record-period records-record-period--week">
                    <div class="records-record-period__label">$obs.label.snapshot_period_7days</div>
                    <div class="records-record-period__value"><span class="records-record-period__value-main">$yesterday.barometer.avg</span></div>
                </section>
                <section class="records-record-period records-record-period--month">
                    <div class="records-record-period__label">$obs.label.snapshot_period_month</div>
                    <div class="records-record-period__value"><span class="records-record-period__value-main"><div><font size="2">$obs.label.records_total $obs.label.snapshot_period_yesterday</font></div><div>$yesterday.rain.sum.format("%.1f")</span></div>
                </section>
                <section class="records-record-period records-record-period--year">
                    <div class="records-record-period__label">$current.dateTime.format("%Y")</div>
                    <div class="records-record-period__value"><span class="records-record-period__value-main"><font size="2"><div>$obs.label.windGustDir</div></font><div>$yesterday.wind.gustdir.ordinal_compass</div></span></div>
                </section>
                <section class="records-record-period records-record-period--year">
                    <div class="records-record-period__label">$obs.label.records_all_time</div>
                    <div class="records-record-period__value"><span class="records-record-period__value-main">$yesterday.radiation.avg</span></div>
                </section>
            </article>
        </div>

    <br>
        <div class="records-section-card__body">
            <article class="records-record-card">
                <h4 class="records-record-card__title">$obs.label.records_average_values $current.dateTime.format("%B %Y")</h4>
                <section class="records-record-period records-record-period--yesterday"">
                    <div class="records-record-period__label">$obs.label.snapshot_period_day</div>
                    <div class="records-record-period__value"><span class="records-record-period__value-main">$month.outTemp.avg</span></div>
                </section>
                <section class="records-record-period records-record-period--yesterday">
                    <div class="records-record-period__label">$obs.label.snapshot_period_yesterday</div>
                    <div class="records-record-period__value"><span class="records-record-period__value-main">$month.outHumidity.avg</span></div>
                </section>
                <section class="records-record-period records-record-period--week">
                    <div class="records-record-period__label">$obs.label.snapshot_period_7days</div>
                    <div class="records-record-period__value"><span class="records-record-period__value-main">$month.barometer.avg</span></div>
                </section>
                <section class="records-record-period records-record-period--month">
                    <div class="records-record-period__label">$obs.label.snapshot_period_month</div>
                    <div class="records-record-period__value"><span class="records-record-period__value-main"><div><font size="2">$obs.label.records_total_rainfall</font></div><div>$month.rain.sum.format("%.1f")</span></div>
                </section>
                <section class="records-record-period records-record-period--year">
                    <div class="records-record-period__label">$current.dateTime.format("%Y")</div>
                    <div class="records-record-period__value"><span class="records-record-period__value-main"><font size="2"><div>$obs.label.windGustDir</div></font><div>$month.wind.gustdir.ordinal_compass</div></span></div>
                </section>
                <section class="records-record-period records-record-period--year">
                    <div class="records-record-period__label">$obs.label.records_all_time</div>
                    <div class="records-record-period__value"><span class="records-record-period__value-main">$month.radiation.avg</span></div>
                </section>
            </article>
        </div>




    </div>
</section>
