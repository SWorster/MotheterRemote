#ignore !/usr/bin/env python

'''
PySQM main program
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
'''

import os,sys
import time
import datetime
import argparse # type: ignore


'''
Read input arguments (if any)
'''
import pysqm.settings as settings
InputArguments = settings.ArgParser()
configfilename = InputArguments.config
if not isinstance(configfilename, str):
    configfilename = str(configfilename)

# Load config contents into GlobalConfig
settings.GlobalConfig.read_config_file(configfilename)

# Get the actual config
config = settings.GlobalConfig.config

### Load now the rest of the modules
from pysqm.read import *
import pysqm.plot

'''
This import section is only for software build purposes.
Don't worry if some of these are missing in your setup.
'''

def relaxed_import(themodule:str):
    try: exec('import '+str(themodule))
    except: pass

relaxed_import('socket')
relaxed_import('serial')
relaxed_import('_mysql')
relaxed_import('pysqm.email')


'''
Conditional imports
'''

# If the old format (SQM_LE/SQM_LU) is used, replace _ with -
config.device_type = config.device_type.replace('_','-')

if config.device_type == 'SQM-LE':
    relaxed_import('socket')
elif config.device_type == 'SQM-LU':
    relaxed_import('serial')
if config.use_mysql == True:
    relaxed_import('_mysql')


# Create directories if needed
for directory in [config.monthly_data_directory,config.daily_data_directory,config.current_data_directory]:
    if not os.path.exists(directory):
        os.makedirs(directory)


'''
Select the device to be used based on user input
and start the measures
'''

if config.device_type=='SQM-LU':
    mydevice = SQMLU()
elif config.device_type=='SQM-LE':
    mydevice = SQMLE()
else:
    print(('ERROR. Unknown device type '+str(config.device_type)))
    exit(0)


def loop()->None:
    '''
    Ephem is used to calculate moon position (if above horizon)
    and to determine start-end times of the measures
    '''
    observ = define_ephem_observatory()
    niter = 0
    DaytimePrint=True
    print('Starting readings ...')
    while 1<2:
        ''' The programs works as a daemon '''
        utcdt = mydevice.read_datetime()
        #print (str(mydevice.local_datetime(utcdt))),
        if mydevice.is_nighttime(observ):
            # If we are in a new night, create the new file.
            config.send_to_datacenter = False ### Not enabled by default
            try:
                assert(config.send_to_datacenter == True)
                assert(niter == 0)
                mydevice.save_data_datacenter("NEWFILE")
            except: pass

            StartDateTime = datetime.datetime.now()
            niter += 1

            mydevice.define_filenames()

            timeutc_mean:datetime.datetime
            timelocal_mean:datetime.datetime
            temp_sensor:float
            freq_sensor:float
            ticks_uC:float
            sky_brightness:float
            ''' Get values from the photometer '''
            try:
                timeutc_mean,timelocal_mean,temp_sensor,freq_sensor,ticks_uC,sky_brightness = mydevice.read_photometer(Nmeasures=config.measures_to_promediate,PauseMeasures=10)
            except:
                print('Connection lost')
                if config.reboot_on_connlost == True:
                    time.sleep(600)
                    os.system('reboot.bat')

                time.sleep(1)
                mydevice.reset_device()
                return


            formatted_data = mydevice.format_content(timeutc_mean,timelocal_mean,temp_sensor,freq_sensor,ticks_uC,sky_brightness)

            try:
                assert(config.use_mysql == True)
                mydevice.save_data_mysql(formatted_data)
            except: pass

            try:
                assert(config.send_to_datacenter == True)
                mydevice.save_data_datacenter(formatted_data)
            except: pass

            mydevice.data_cache(formatted_data,number_measures=config.cache_measures,niter=niter)

            if niter%config.plot_each == 0:
                ''' Each X minutes, plot a new graph '''
                try: pysqm.plot.make_plot(send_emails=False,write_stats=False)
                except:
                    print('Warning: Error plotting data.')
                    print((sys.exc_info()))

            if DaytimePrint==False:
                DaytimePrint=True

            MainDeltaSeconds = (datetime.datetime.now()-StartDateTime).total_seconds()
            time.sleep(max(1,config.delay_between_measures-MainDeltaSeconds))

        else:
            ''' Daytime, print info '''
            if DaytimePrint==True:
                utcdt = utcdt.strftime("%Y-%m-%d %H:%M:%S")
                print((utcdt), end=' ')
                print(('. Daytime. Waiting until '+str(mydevice.next_sunset(observ))))
                DaytimePrint=False
            if niter>0:
                mydevice.flush_cache()
                if config.send_data_by_email==True:
                    try: pysqm.plot.make_plot(send_emails=True,write_stats=True)
                    except:
                        print('Warning: Error plotting data / sending email.')
                        print((sys.exc_info()))

                else:
                    try: pysqm.plot.make_plot(send_emails=False,write_stats=True)
                    except:
                        print('Warning: Error plotting data.')
                        print((sys.exc_info()))

                niter = 0

            # Send data that is still in the datacenter buffer
            try:
                assert(config.send_to_datacenter == True)
                mydevice.save_data_datacenter("")
            except: pass

            time.sleep(300)


