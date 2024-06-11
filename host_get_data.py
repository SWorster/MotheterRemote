# scp rp3@131.229.147.51:/var/tmp/sqm_macleish/daily_data/20240607_120000_SQM-MacLeish.dat /Users/skyeworster/Desktop

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

sensor = sensor_default
rpi_name = ""
rpi_ip = ""
target = "."
date = datetime.datetime.today() - datetime.timedelta(days=1)
force = False


def parse_date(d: str) -> datetime.datetime | None:
    try:
        formatted = datetime.datetime.strptime(d, "%Y%m%d")
        return formatted
    except Exception:
        return


def parse_date_default(d: str) -> datetime.datetime:
    day = parse_date(d)
    if day == None:
        day = datetime.datetime.today() - datetime.timedelta(days=1)
    return day


def user_interface() -> None:

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


def get_today():
    yesterday = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime(
        "%Y%m%d"
    )
    command = f"scp {rpi_name}@{rpi_ip}:/var/tmp/sqm_macleish/daily_data/{yesterday}_120000_SQM-MacLeish.dat {target}"
    print(command)
    os.system(command)


def give_day():
    d = date.strftime("%Y%m%d")
    command = f"scp {rpi_name}@{rpi_ip}:/var/tmp/sqm_macleish/daily_data/{d}_120000_SQM-MacLeish.dat {target}"
    print(command)
    os.system(command)


def ui_give_day() -> None:
    day = input("To get data from a specific day, type the date in YYYYMMDD format: ")
    set_date(day)
    give_day()


def all_since() -> None:
    # This is horrendously inefficient, as it copies all files then deletes the ones that weren't asked for.
    # It's also dangerous, because it will overwrite any other daily_data folder in the target directory.
    start = date
    command = f"scp -r {rpi_name}@{rpi_ip}:/var/tmp/sqm_macleish/daily_data {target}"
    print(command)
    os.system(command)

    print("PRINT THIS PLEASE", os.listdir())
    print("target", target)
    if not os.path.isdir(f"{target}/daily_data"):
        print(
            f"Something went wrong! daily_data wasn't properly copied to target location {target}/daily_data"
        )
        print(os.listdir())
        exit()
    os.chdir(f"{target}/daily_data")
    files = os.listdir()
    for file in files:
        file_date = parse_date(file[0:8])
        if isinstance(file_date, datetime.datetime):
            if start > file_date:
                os.remove(file)


def ui_all_since() -> None:
    since = input(
        "To get data since a specific day, type the date in YYYYMMDD format: "
    )
    set_date(since)
    all_since()


def get_all() -> None:
    print("Getting all data")
    command = f"scp -r {rpi_name}@{rpi_ip}:/var/tmp/sqm_macleish/daily_data {target}"
    print(command)
    os.system(command)


def set_date(d: str | None) -> None:
    global date
    if isinstance(d, str):
        day = parse_date(d)
        if day != None:
            date = day

    print("Invalid date entered. Setting date to yesterday.")
    date = datetime.datetime.today() - datetime.timedelta(days=1)


def set_force(f: bool | None) -> None:
    if f is not None:
        global force
        force = f


def set_target(t: str | None, ui: bool) -> None:
    global target
    if t == None or t == "":
        return
    if os.path.isdir(t):
        target = str(t)
        return
    if ui:
        resp = input("This directory does not exist. Would you like to create it? Y/N ")
        if resp == "Y":
            set_force(True)
    if force:
        print(f"Creating directory {t}")
        os.makedirs(t)
        if os.path.isdir(t):
            target = t
    else:
        print(
            f"{t} is not a valid target. Using current working directory {os.getcwd()}"
        )


def set_sensor(s: str | None):
    global sensor
    global rpi_name
    global rpi_ip

    if s is not None:  # if input was given
        sensor = s
        if s == "":  # ui pressed enter
            sensor = sensor_default
        sensor_info = sensor_dict.get(sensor)  # get corresponding name and ip
        if sensor_info != None:  # sensor is valid
            rpi_name = sensor_info[0]  # set info
            rpi_ip = sensor_info[1]
            return
        print(f"Input not in list of sensors, reverting to default ({sensor_default})")

    # no input given, or input was invalid
    sensor = sensor_default
    sensor_info = sensor_dict.get(sensor)

    if sensor_info != None:  # if it does exist by this point
        rpi_name = sensor_info[0]  # set info
        rpi_ip = sensor_info[1]
    else:
        print(
            "Default sensor not found! Fix this error by modifying host_get_data.py and adding the RPi info to sensor_dict."
        )
        exit()


def main() -> None:
    # create an argparser
    parser = argparse.ArgumentParser(
        prog="host_get_data",
        description="Gets data from remote sensor via ssh/scp. For user-friendly mode, run with -u.",
        epilog=f"List of sensors: {string_names_list}",
    )

    parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="Gets all existing readings. If a date is supplied with --d, gets all readings since that date (inclusive)",
    )

    parser.add_argument(
        "-u",
        "-ui",
        "--userinterface",
        action="store_true",
        help="Program runs in user-friendly mode, prompting each input in the command line.",
    )

    parser.add_argument(
        "-s",
        "--sensor",
        nargs=1,
        type=str,
        help=f"Name of sensor (default={sensor_default}). List of sensors: {string_names_list}",
    )

    parser.add_argument(
        "--date",
        "--d",
        action="store",
        nargs=1,
        type=str,
        help="Gets readings for specified date. If --a/--all is supplied, gets all readings since this date (inclusive). Takes a date as argument in YYYYMMDD format. For example '--allsince 20241105' for November 5, 2024",
    )

    parser.add_argument(
        "--t",
        "--target",
        action="store",
        type=str,
        help="Sets where to store files on the host computer (uses current working directory by default). ex. /Users/username/Desktop",
        nargs=1,
    )

    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="If target directory does not exist, forces creation of target directory. Otherwise, current working directory will be used.",
    )

    args = vars(parser.parse_args())
    print(args)

    if args.get("userinterface"):
        user_interface()  # ignores all other presets
        exit("program ended")

    set_force(args.get("force"))
    set_sensor(args.get("sensor"))
    set_date(args.get("date"))
    set_target(args.get("target"), False)

    if args.get("all"):
        if args.get("date") is not None:
            all_since()  # date given, do all since
        else:
            get_all()
    elif args.get("date") is not None:  # date given
        give_day()
    else:  # no mode-related args
        get_today()


main()


# if __name__ != "__main__":
#     user_interface()
# else:
#     main()


# os.system("ssh rp3@131.229.147.51") # user will need to enter password
# from subprocess import run
# output = run("pwd", capture_output=True).stdout ???
# file_list = os.listdir()
# # scp user@remote:'/path1/file1 /path2/file2 /path3/file3' /localPath
