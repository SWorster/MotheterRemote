#!/usr/bin/env python

'''
PySQM configuration File.
____________________________

Copyright (c) Mireia Nievas <mnievas[at]ucm[dot]es>

This file is part of PySQM.

PySQM is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

PySQM is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with PySQM.  If not, see <http://www.gnu.org/licenses/>.

____________________________
Notes:

You may need to change the following variables to match your
observatory coordinates, instrumental properties, etc.

Python syntax is mandatory.
____________________________
'''


'''
-------------
SITE location
-------------
'''

_observatory_name = 'MacLeish'
_observatory_latitude  = 42.449183
_observatory_longitude = -72.679909
_observatory_altitude  = 170
_observatory_horizon   = 10  # If Sun is below this altitude, the program will take data

_device_shorttype = 'SQM' # Device STR in the file
_device_type = 'SQM_LU'   # Device type in the Header
_device_id = _device_type + '-' + _observatory_name # Long Device lame
_device_locationname = 'Smith College - MacLeish Field Station'         # Device location in the world
_data_supplier = 'Mariana Abarca / Smith College Biology Department'  # Data supplier (contact)
_device_addr = '/dev/ttyUSB0'  # Default IP address of the ethernet device (if not automatically found)
_measures_to_promediate = 1       # Take the mean of N measures
_delay_between_measures = 2    # Delay between two measures. In seconds.
_cache_measures = 1             # Get X measures before writing on screen/file
_plot_each = 2                 # Call the plot function each X measures.

_use_mysql = False        # Set to True if you want to store data on a MySQL db.
_mysql_host = None        # Host (ip:port / localhost) of the MySQL engine.
_mysql_user = None        # User with write permission on the db.
_mysql_pass = None        # Password for that user.
_mysql_database = None    # Name of the database.
_mysql_dbtable = None     # Name of the table
_mysql_port = None        # Port of the MySQL server.

_local_timezone     = -4     # UTC+1
_computer_timezone  = -4     # UTC
_offset_calibration = -0.11  # magnitude = read_magnitude + offset
_reboot_on_connlost = False  # Reboot if we loose connection

# Monthly (permanent) data
monthly_data_directory = "/tmp/sqm_macleish/"
# Daily (permanent) data
daily_data_directory = monthly_data_directory+"/daily_data/"
limits_nsb = [20.0,16.5] # Limits in Y-axis

# Daily (permanent) graph
daily_graph_directory = monthly_data_directory+"/daily_graphs/"
# Current data, deleted each day.
current_data_directory = monthly_data_directory
# Current graph, deleted each day.
current_graph_directory = monthly_data_directory
# Summary with statistics for the night
summary_data_directory = monthly_data_directory


'''
----------------------------
PySQM data center (OPTIONAL)
----------------------------
'''

# Send the data to the data center
_send_to_datacenter = False


'''
Ploting options
'''
full_plot = True
limits_nsb = [20.0,16.5] # Limits in Y-axis
limits_time   = [17,9] # Hours
limits_sunalt = [-80,5] # Degrees

'''
Email options
'''
_send_data_by_email = False

