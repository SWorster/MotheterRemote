# ignore !/usr/bin/env python

"""
PySQM plotting program
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
"""

import os, sys


class ArgParser:
    # creates object to parse command-line arguments
    def __init__(self, inputfile=False):
        self.parse_arguments(inputfile)

    # get arguments from command line
    def parse_arguments(self, inputfile: bool) -> None:
        import argparse

        # Return config filename
        self.parser = argparse.ArgumentParser()  # create ArgumentParser object

        # lets user add optional argument for config file location (otherwise, it uses the default). this should be stored in the attribute config
        self.parser.add_argument("-c", "--config", default="config.py", type=str)

        if inputfile:  # true if running plot.py as standalone program
            # adds field for input data file name
            self.parser.add_argument("-i", "--input", default=None, type=str)

        args = self.parser.parse_args()  # parse the command line arguments

        # vars(object) returns the __dict__ writable attributes
        vars(self).update(args.__dict__)  # add the new arguments to the self object

        # BUG squashing attempt by SWW: inserted the next line
        self.config = vars(self).get("config")

    def print_help(self):
        self.parser.print_help()


class ConfigFile:
    def __init__(self, path="config.py"):
        # Guess the selected dir and config filename
        # Should accept:
        # - absolute path (inc. filename)
        # - relative path (inc. filename)
        # - absolute path (exc. filename)
        # - relative path (exc. filename)
        # - shortcuts like ~ . etc
        self.path = path
        # BUG squashing attempt by SWW: uncommented the next line
        # self.config = None

    def read_config_file(self, path: str):
        # Get the absolute path
        abspath = os.path.abspath(path)
        # Is a dir? Then add config.py (default filename)
        if os.path.isdir(abspath):
            abspath += "/config.py"
        # split directory and filename
        directory = os.path.dirname(abspath)
        filename = os.path.basename(abspath)

        old_syspath = sys.path
        sys.path.append(directory)
        import config

        self.config = config


# Create an object (by default empty) accessible from everywhere
# After read_config_file is called, GlobalConfig.config will be accessible
GlobalConfig = ConfigFile()
