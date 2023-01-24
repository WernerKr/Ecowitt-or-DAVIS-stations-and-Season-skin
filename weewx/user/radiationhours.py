"""
Adds a new observation field to weewx: [sunshine_hours]

If the radiation observed during an interval of time exceeds 120 W/m2, then the interval is considered sunny,
and [sunshine_hours] is set the length of the time interval.

When [sunshine_hours] is summed over a day, the result is the number of hours during the day when radiation
exceeded 120 W/m2, or 'hours of sunshine'.

The threshold of 120 W/m2 can be overwritten in weewx.conf:

    [RadiationDays]
        min_sunshine = 120

Installation:
    1. Save this file to your user customisations directory (which is often /usr/share/weewx/user)
    2. Enable this service in weewx.conf by adding user.radiationhours.RadiationHours to the process_services list.

        [Engine]

            [[Services]]
                # This section specifies the services that should be run. They are
                # grouped by type, and the order of services within each group
                # determines the order in which the services will be run.
                prep_services = weewx.engine.StdTimeSynch
                process_services = user.radiationhours.RadiationHours, weewx.engine.StdConvert, weewx.engine.StdCalibrate, weewx.engine.StdQC, weewx.wxservices.StdWXCalculate

    3. Add [sunshine_hours] to the database schema so tables include this new observation field.
       In weewx.conf, change the wx_binding schema from schemas.wview.schema to user.radiationhours.schema_with_sunshine_hour

        [DataBindings]

            [[wx_binding]]
                # The database must match one of the sections in [Databases].
                # This is likely to be the only option you would want to change.
                database = archive_sqlite
                # The name of the table within the database
                table_name = archive
                # The manager handles aggregation of data for historical summaries
                manager = weewx.wxmanager.WXDaySummaryManager
                # The schema defines the structure of the database.
                # It is *only* used when the database is created.
                #schema = schemas.wview.schema
                schema = user.radiationhours.schema_with_sunshine_hour

    4. Shutdown Weewx and update your database to bring in the new field.
       wee_database weewx.conf --reconfigure

       Make sure you know what you're doing at this point, you can potentially corrupt/lose your archive data.
       The weewx customization guide covers this in a lot more detail.

    5. Tell Weewx about the units for this new type
        Add this to user/extensions.py:

        #
        # Units for sunshine_days calculated field
        #
        import weewx.units
        weewx.units.obs_group_dict['sunshine_hours'] = 'group_radiation'


        I've cheated here since Weewx doesn't have a unit for hours. So any graphs of sunshine hours will have the
        units W/m2, which I have hidden on the graph by setting the colour of the unit text to the background colour
        of the graph.

    6. Use [sunshine_hours] in your graphs and html template tags.

    Lots more detail on this process can be found here:
        http://www.weewx.com/docs/customizing.htm#Adding_a_new_observation_type

"""


#import schemas.wview_extended
#schema_with_sunshine_hours = schemas.wview_extended.schema + [('sunshine_hours', 'REAL')]

import syslog

import weewx
from weewx.wxengine import StdService

class RadiationHours(StdService):
    def __init__(self, engine, config_dict):
        # Pass the initialization information on to my superclass:
        super(RadiationHours, self).__init__(engine, config_dict)

        # Default threshold value is 120 W/m2
        self.min_sunshine = 120.0

        if 'RadiationDays' in config_dict:
            self.min_sunshine = float(config_dict['RadiationDays'].get('min_sunshine', self.min_sunshine))

        # Start intercepting events:
        self.bind(weewx.NEW_ARCHIVE_RECORD, self.newArchiveRecord)


    def newArchiveRecord(self, event):
        """Gets called on a new archive record event."""

        radiation = event.record.get('radiation')
        if (radiation is not None) and (radiation > self.min_sunshine):
            event.record['sunshine_hours'] = event.record['interval'] / 60.0
        else:
            event.record['sunshine_hours'] = 0.0

        #syslog.syslog(syslog.LOG_DEBUG, "Calculated sunshine_hours = %f, based on radiation = %f, and min_sunshine = %f" %
        #              (event.record['sunshine_hours'], radiation, self.min_sunshine))
