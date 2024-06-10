# scp rp3@131.229.147.51:/var/tmp/sqm_macleish/daily_data/20240607_120000_SQM-MacLeish.dat /Users/skyeworster/Desktop

import datetime
import os
import argparse

# dict of sensors with rpi names and ips
sensor_default = "macleish primary"
sensor_dict = {
    "not implemented 1": ["rp1", "999.999.999.99"],
    "not implemented 2": ["rp2", "000.0000.000.00"],
    "macleish primary": ["rp3", "131.229.147.51"],
}
names_list = sensor_dict.keys()
string_names_list = ", ".join(names_list)

rpi_name = ""
rpi_ip = ""
target = "."
date = ""
sensor = ""


def user_interface():
    global rpi_name
    global rpi_ip
    global target
    global sensor_dict

    print("Available sensors:", string_names_list)
    sensor_name = input("Name of the sensor setup you're connecting to: ")

    if sensor_name not in names_list:
        print(f"Input not in list of sensors, reverting to default ({sensor_default})")
        sensor_name = sensor_default

    sensor = sensor_dict.get(sensor_name)
    if sensor == None:
        sensor = ["rp3", "131.229.147.51"]
    rpi_name = sensor[0]
    rpi_ip = sensor[1]

    target = input("Type the target destination on your computer (default=root): ")
    if target == "":
        target = "."
    try:
        os.system(f"cd {target}")
        os.system("cd ..")
    except:
        print(f"ERROR: Cannot find directory {target}, defaulting to root")
        target = "."

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
            ui_today()
        case "2":
            ui_give_day()
        case "3":
            ui_since()
        case "4":
            ui_all()
        case _:
            ui_today()


def ui_today():
    print("Getting data for today (or last night)")
    today = datetime.date.today().strftime("%Y%m%d")
    yesterday_raw = datetime.date.today() - datetime.timedelta(days=1)
    yesterday = yesterday_raw.strftime("%Y%m%d")
    command1 = f"scp {rpi_name}@{rpi_ip}:/var/tmp/sqm_macleish/daily_data/{today}_120000_SQM-MacLeish.dat {target}"
    command2 = f"scp {rpi_name}@{rpi_ip}:/var/tmp/sqm_macleish/daily_data/{yesterday}_120000_SQM-MacLeish.dat {target}"
    print(command1)
    print(os.system(command1))
    print(command2)
    print(os.system(command2))


def ui_give_day():
    day = input("To get data from a specific day, type the date in YYYYMMDD format: ")
    command = f"scp {rpi_name}@{rpi_ip}:/var/tmp/sqm_macleish/daily_data/{day}_120000_SQM-MacLeish.dat {target}"
    print(command)
    print(os.system(command))


def ui_since():
    print("Getting data since a specified date")
    since = input(
        "To get data since a specific day, type the date in YYYYMMDD format: "
    )
    start = datetime.datetime(
        year=int(since[0:4]), month=int(since[4:6]), day=int(since[6:8])
    )
    delta = datetime.datetime.today() - start
    print(f"Number of entries: {delta.days}")

    command = f"scp -r {rpi_name}@{rpi_ip}:/var/tmp/sqm_macleish/daily_data {target}"
    print(command)
    print(os.system(command))
    os.chdir("daily_data")
    files = os.listdir()
    for file in files:
        file_date = datetime.datetime(
            year=int(file[0:4]), month=int(file[4:6]), day=int(file[6:8])
        )
        if start > file_date:
            os.remove(file)


def ui_all():
    print("Getting all data")
    command = f"scp -r {rpi_name}@{rpi_ip}:/var/tmp/sqm_macleish/daily_data {target}"
    print(command)
    print(os.system(command))


def all():
    s = sensor_dict.get(sensor)
    if s == None:
        s = ["rp3", "131.229.147.51"]
    rpi_name = sensor[0]
    rpi_ip = sensor[1]


def all_since():
    pass


def give_day():
    pass


def get_today():
    pass


def main():
    # create an argparser
    parser = argparse.ArgumentParser(
        prog="host_get_data",
        description="gets data from remote sensor via ssh/scp",
        epilog=f"List of sensors: {string_names_list}",
    )

    parser.add_argument(
        "-s",
        "--sensor",
        default=sensor_dict.popitem(),
        nargs=1,
        help=f"name of sensor. list of sensors: {string_names_list}",
        type=str,
    )

    parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        default=False,
        help="Get reading from all days ever (yikes)",
    )

    parser.add_argument(
        "-u",
        "-ui",
        "--userinterface",
        action="store_true",
        help="Program runs in user-friendly mode, prompting each input in the command line.",
    )

    parser.add_argument(
        "--allsince",
        action="store",
        help="Get readings from all days since input (inclusive). Takes a date as argument in YYYYMMDD format. For example '--allsince 20241105' for November 5, 2024",
        nargs=1,
    )

    parser.add_argument(
        "--date",
        "--d",
        action="store",
        help="Gets the data for just the date specified. Takes a date as argument in YYYYMMDD format. For example '--allsince 20241105' for November 5, 2024",
        nargs=1,
        type=str,
    )

    parser.add_argument(
        "--t",
        "--target",
        action="store",
        type=str,
        help="Sets where to store files on the host computer. ex.  /Users/username/Desktop",
    )

    args = vars(parser.parse_args())
    print(args)

    if args.get("userinterface"):
        user_interface()  # discards all other presets

    t = args.get("target")
    if t is not None:
        global target
        target = str(t)

    s = args.get("sensor")
    if s is not None:
        global sensor
        sensor = str(s)

    d = args.get("date")
    if d is not None:
        global date
        date = str(d)

    if args.get("all"):
        all()
    elif args.get("allsince"):
        all_since()
    elif args.get("date") is not None:
        give_day()
    else:
        get_today()


main()
