#
#    Copyright (c) 2026 Tom Keffer <tkeffer@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

"""Search list extension to calculate when an SQL statement last evaluted true, or how long since it evaluated true.

Example:

    <p>It last rained at $time_at('rain>0') ($time_since('rain>0') ago).</p>

would result in

    <p>It last rained 20 June 2020 (81 days, 1 hour, 35 minutes ago).</p>

"""
from weewx.cheetahgenerator import SearchList

from weewx.units import ValueTuple, ValueHelper

VERSION = "0.4"


class TimeSince(SearchList):
    def get_extension_list(self, timespan, db_lookup):
        def time_since(expression, data_binding=None):
            """Time since a sql expression evaluted true"""
            db_manager = db_lookup(data_binding=data_binding)
            sql_stmt = "SELECT dateTime FROM %s WHERE %s AND dateTime <= %d ORDER BY dateTime DESC LIMIT 1" \
                       % (db_manager.table_name, expression, timespan.stop)

            row = db_manager.getSql(sql_stmt)
            val = timespan.stop - row[0] if row else None
            vt = ValueTuple(val, 'second', 'group_deltatime')
            vh = ValueHelper(vt,
                             context='month',
                             formatter=self.generator.formatter,
                             converter=self.generator.converter)
            return vh

        def time_at(expression, data_binding=None):
            """When an sql expression evaluated true"""
            db_manager = db_lookup(data_binding=data_binding)
            sql_stmt = "SELECT dateTime FROM %s WHERE %s AND dateTime <= %d ORDER BY dateTime DESC LIMIT 1" \
                       % (db_manager.table_name, expression, timespan.stop)

            row = db_manager.getSql(sql_stmt)
            val = row[0] if row else None
            vt = ValueTuple(val, 'unix_epoch', 'group_time')
            vh = ValueHelper(vt,
                             formatter=self.generator.formatter,
                             converter=self.generator.converter)
            return vh

        return [{
            'time_since': time_since,
            'time_at': time_at,
        }]
