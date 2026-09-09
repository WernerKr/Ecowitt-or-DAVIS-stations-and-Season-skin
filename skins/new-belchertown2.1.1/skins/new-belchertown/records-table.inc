#encoding UTF-8
#import datetime
<section class="records-section-card records-section-card--custom">
    <div class="records-section-card__header">
        <h2 class="records-section-card__title">$obs.label.sunshine_time</h2>
    </div>
    <div class="records-section-card__table">
        <div class="records-section-card__period-header">
            <div class="records-section-card__period-header-spacer" aria-hidden="true"></div>
            <div class="records-section-card__period-header-cell records-section-card__period-header-cell--year">$current.dateTime.format("%Y")</div>
            <div class="records-section-card__period-header-cell records-section-card__period-header-cell--alltime">$obs.label.records_all_time</div>
        </div>
        <div class="records-section-card__body">
            <article class="records-record-card">
                <h3 class="records-record-card__title">$obs.label.records_highest_daily_sunshine</h3>
                <section class="records-record-period records-record-period--year">
                    <div class="records-record-period__label">$current.dateTime.format("%Y")</div>
                    <div class="records-record-period__value"><span class="records-record-period__value-main">$sunniest_day[1] $unit.label.sunshineDur</span></div>
                    <div class="records-record-period__date"><span class="records-record-period__date-line">$datetime.datetime.fromtimestamp($sunniest_day[0]).strftime('%d. %b %Y')</span></div>
                </section>
                <section class="records-record-period records-record-period--alltime">
                    <div class="records-record-period__label">$obs.label.records_all_time</div>
                    <div class="records-record-period__value"><span class="records-record-period__value-main">$at_sunniest_day[1] $unit.label.sunshineDur</span></div>
                    <div class="records-record-period__date"><span class="records-record-period__date-line">$datetime.datetime.fromtimestamp($at_sunniest_day[0]).strftime('%d. %b %Y')</span></div>
                </section>
            </article>
        </div>
        <div class="records-section-card__body">
            <article class="records-record-card">
                <h3 class="records-record-card__title">$obs.label.records_month_high_sunshine</h3>
                <section class="records-record-period records-record-period--year">
                    <div class="records-record-period__label">$current.dateTime.format("%Y")</div>
                    <div class="records-record-period__value"><span class="records-record-period__value-main">$year_sunniest_month[1] $unit.label.sunshineDur</span></div>
                    <div class="records-record-period__date"><span class="records-record-period__date-line">$year_sunniest_month[0]</span></div>
                </section>
                <section class="records-record-period records-record-period--alltime">
                    <div class="records-record-period__label">$obs.label.records_all_time</div>
                    <div class="records-record-period__value"><span class="records-record-period__value-main">$at_sunniest_month[1] $unit.label.sunshineDur</span></div>
                    <div class="records-record-period__date"><span class="records-record-period__date-line">$at_sunniest_month[0]</span></div>
                </section>
            </article>
        </div>
    </div>

</section>
