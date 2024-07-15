# this will be interesting. possibly even fun. but definitely interesting.

import datetime
import os
import argparse

# Constants
MIN_YEAR = 2000
MAX_YEAR = int(datetime.date.today().strftime("%Y"))

# dict of sensors with rpi names and ips
sensor_dict = {
    "test1": ["rp1", "999.999.999.99"],
    "test2": ["rp2", "000.0000.000.00"],
    "macleish": ["rp3", "131.229.147.51"],
}
sensor_default = "macleish"
string_names_list = ", ".join(sensor_dict.keys())

# globals
sensor = sensor_default
rpi_name = ""
rpi_ip = ""
target = "."
date = datetime.datetime.today() - datetime.timedelta(days=1)
force = False


def parse_date(d: str) -> datetime.datetime | None:
    """Converts a string date in YYYYMMDD format to a datetime object

    Args:
        d (str): date to be converted, in format YYYYMMDD

    Returns:
        datetime.datetime | None: corresponding datetime object, or None if not possible
    """
    try:
        formatted = datetime.datetime.strptime(d, "%Y%m%d")
        return formatted
    except Exception:
        return


def parse_date_default(d: str) -> datetime.datetime:
    """Converts a string date in YYYYMMDD format to a datetime object

    Args:
        d (str): date to be converted, in format YYYYMMDD

    Returns:
        datetime.datetime: corresponding datetime object, or datetime for today if not possible
    """
    day = parse_date(d)
    if day == None:
        day = datetime.datetime.today() - datetime.timedelta(days=1)
    return day


def user_interface() -> None:
    """User-friendly interface. Prompts user for each field."""
    print("Available sensors:", string_names_list)
    s = input("Name of the sensor setup you're connecting to: ")
    set_sensor(s)

    t = input("Type the target destination on your computer (default=root): ")
    set_target(t, True)

    print(
        "Modes of operation:",
        "\n1 = get only today's data",
        "\n2 = get data from a specific date",
        "\n3 = get data for all days since a specific date",
        "\n4 = get all data",
    )
    mode = input("Type operating mode: ")
    match mode:
        case "1":
            get_today()
        case "2":
            ui_give_day()
        case "3":
            ui_all_since()
        case "4":
            get_all()
        case _:
            get_today()


def get_today() -> None:
    """Sends command to retrieve today's (last night's) reading.

    Note that readings are dated by which day they started on, so last night's reading is under yesterday's date even though it finished this morning.
    """
    yesterday = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime(
        "%Y%m%d"
    )
    command = f"scp {rpi_name}@{rpi_ip}:/var/tmp/sqm_macleish/daily_data/{yesterday}_120000_SQM-MacLeish.dat {target}"
    print(command)
    os.system(command)


def give_day() -> None:
    """Sends command to retrieve the specified day's reading.

    Note that readings are dated by which day they started on, so last night's reading is under yesterday's date even though it finished this morning.
    """
    d = date.strftime("%Y%m%d")
    command = f"scp {rpi_name}@{rpi_ip}:/var/tmp/sqm_macleish/daily_data/{d}_120000_SQM-MacLeish.dat {target}"
    print(command)
    os.system(command)


def ui_give_day() -> None:
    """Takes a date from the user, then gets reading from that date."""
    day = input("To get data from a specific day, type the date in YYYYMMDD format: ")
    set_date(day)
    give_day()


def better_all_since() -> None:
    """Sends command to retrieve all readings taken on or before the specified date.

    Note that readings are dated by which day they started on, so last night's reading is under yesterday's date even though it finished this morning.
    """
    start = date
    today = datetime.datetime.today()
    dates = [start + datetime.timedelta(n) for n in range(int((today - start).days))]
    for d in dates:
        d_str = d.strftime("%Y%m%d")
        command = f"scp {rpi_name}@{rpi_ip}:/var/tmp/sqm_macleish/daily_data/{d_str}_120000_SQM-MacLeish.dat {target}"
        print(command)
        os.system(command)


def ui_all_since() -> None:
    """Takes date from user, then gets all readings on or after that date."""
    since = input(
        "To get data since a specific day, type the date in YYYYMMDD format: "
    )
    set_date(since)
    better_all_since()


def get_all() -> None:
    """Sends a command to retrieve all readings."""
    print("Getting all data")
    command = f"scp -r {rpi_name}@{rpi_ip}:/var/tmp/sqm_macleish/daily_data {target}"
    print(command)
    os.system(command)


def set_date(d: str | list[str] | None) -> None:
    """Sets the date from a string

    Args:
        d (str | list[str] | None): date to set, or None if no input from command line
    """
    global date
    if isinstance(d, list):
        d = d[0]
    if d == None or d == "":  # no date entered, default today
        return
    day = parse_date_default(d)
    date = day


def set_force(f: bool | list[bool] | None) -> None:
    """Sets force flag. Determines whether to create the target directory if it doesn't already exist.

    Args:
        f (bool | list[bool] | None): whether to force creation of directory, or None if no input from command line
    """
    if isinstance(f, list):
        f = f[0]
    if f is not None:
        global force
        force = f


def set_target(t: str | list[str] | None, ui: bool = False) -> None:
    """Sets target. This is where the files will be saved. Must be reachable from current working directory.

    Args:
        t (str | list[str] | None): target folder, or None if no input from command line
        ui (bool, optional): True if this was called through the user interface Defaults to False.
    """
    global target
    if isinstance(t, list):
        t = t[0]
    if t == None or t == "":  # no input, use default
        return
    if os.path.isdir(t):  # path exists, so use it
        target = str(t)
        return
    if ui:  # path doesn't exist, ask user for force flag
        resp = input("This directory does not exist. Would you like to create it? Y/N ")
        if resp == "Y":
            set_force(True)
    if force:  # force creation
        print(f"Creating directory {t}")
        os.makedirs(t)
        if os.path.isdir(t):
            target = t
    else:  # use current working directory
        print(
            f"{t} is not a valid target. Using current working directory {os.getcwd()}"
        )


def set_sensor_default() -> None:
    """Sets the sensor to the default. Should only be used from within set_sensor()"""
    global sensor, rpi_name, rpi_ip
    print("USING DEFAULT SENSOR")
    sensor = sensor_default
    info = sensor_dict.get(sensor)
    print("info", info)
    if info == None:  # default info not in dictionary
        print(
            "Default sensor not found! Fix this error by modifying host_get_data.py and adding the RPi info to sensor_dict."
        )
        exit()
    rpi_name = info[0]
    rpi_ip = info[1]


def set_sensor(s: str | list[str] | None) -> None:
    """Sets the sensor to get readings from. More accurately, this is which RPi we're getting readings from, but I'm too lazy to change "sensor" to "rpi" everywhere.

    Args:
        s (str | list[str] | None): the sensor to use, or None if no input from command line
    """
    global sensor
    global rpi_name
    global rpi_ip
    if isinstance(s, list):
        s = s[0]
    print("s", s)
    if s == None or s == "":  # no input given
        set_sensor_default()
        return

    info = sensor_dict.get(s)  # get corresponding name and ip
    print("info1", info)
    if info == None:  # no match, use default
        print("here")
        set_sensor_default()
        return

    sensor = s  # set globals
    rpi_name = info[0]
    rpi_ip = info[1]


def main() -> None:
    """Parses command line arguments and determines which operation to perform."""
    # create an argparser
    parser = argparse.ArgumentParser(
        prog="host_get_data",
        description="Gets data from remote sensor via ssh/scp. For user-friendly mode, run with -u.",
        epilog=f"List of sensors: {string_names_list}",
    )

    parser.add_argument(
        "-all",
        "-a",
        action="store_true",
        help="Gets all existing readings. If a date is supplied with --d, gets all readings since that date (inclusive).",
    )

    parser.add_argument(
        "-userinterface",
        "-u",
        action="store_true",
        help="Program runs in user-friendly mode, prompting each input in the command line.",
    )

    parser.add_argument(
        "-force",
        "-f",
        action="store_true",
        help="If target directory does not exist, forces creation of target directory. Otherwise, current working directory will be used.",
    )

    parser.add_argument(
        "--sensor",
        "--s",
        nargs=1,
        type=str,
        help=f"Name of sensor (default={sensor_default}). List of sensors: {string_names_list}",
    )

    parser.add_argument(
        "--date",
        "--d",
        nargs=1,
        type=str,
        help="Gets readings for specified date. If -a or -all is supplied, gets all readings since this date (inclusive). Takes a date as argument in YYYYMMDD format. For example: '-a --d 20241105' for November 5, 2024.",
    )

    parser.add_argument(
        "--target",
        "--t",
        nargs=1,
        type=str,
        help="Sets where to store files on the host computer (uses current working directory by default). ex. /Users/username/MotheterRemote",
    )

    args = vars(parser.parse_args())
    print(args)

    if args.get("userinterface"):
        user_interface()  # ignores all other presets
        exit("program ended")

    # set global variables
    set_force(args.get("force"))
    set_sensor(args.get("sensor"))
    set_date(args.get("date"))
    set_target(args.get("target"))

    # decide which operation to perform
    if args.get("all"):
        if args.get("date") is not None:
            better_all_since()  # date given, do all since
        else:
            get_all()
    elif args.get("date") is not None:  # date given
        give_day()
    else:  # no mode-related args
        get_today()


main()
