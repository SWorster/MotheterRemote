# runs on host computer, generates a command from user interface
import datetime
import os
import socket_testing.configs as configs

path = "MotheterRemote/socket_testing"
filename = "get_command.py"

sensor = configs.sensor
sensor_name = configs.sensor_name
sensor_ip = configs.sensor_ip
sensor_ddns = configs.sensor_ddns


def request_reading() -> None:
    """requests a reading"""
    send("rx", "REQUEST READING")


def request_cal_info() -> None:
    """requests calibration information"""
    send("cx", "REQUEST CALIBRATION INFORMATION")


def request_unit_info() -> None:
    """requests unit information"""
    send("ix", "REQUEST UNIT INFORMATION")


def arm_light_cal() -> None:
    send("zcalAx", "ARM LIGHT CALIBRATION")


def arm_dark_cal() -> None:
    send("zcalBx", "ARM DARK CALIBRATION")


def disarm_cal() -> None:
    send("zcalDx", "DISARM CALIBRATION")


def request_interval_settings() -> None:
    """Sends interval setting request. Prompts two responses: reading w/ serial, and interval setting response"""
    send("Ix", "INTERVAL SETTINGS REQUEST")


def set_interval_report_period() -> None:
    """set interval report period"""

    print(
        "This command sets the interval report period in the RAM by default. This change will not persist through a reboot.\nYou can choose to set this interval in the EEPROM so that the system will boot with this new interval.\nHowever, the EEPROM only has 1 million erase/write cycles, so please test your settings with just RAM before committing to EEPROM."
    )
    boot = parse(
        "To write to EEPROM and RAM, type EEPROM. To write to RAM only (recommended), type anything else and press enter.\nMode: "
    )
    if boot == ("EEPROM"):
        boot = "P"
    else:
        boot = "p"

    interval = parse("Reporting interval (as integer only): ")
    try:
        time = int(interval)
        print(time)
    except:
        print(f"{interval} is not a valid integer.")
        return

    unit = parse("Unit for time value (s=seconds, m=minutes, h=hours): ")
    if "m" in unit:
        print("m")
        time = time * 60
    elif "h" in unit:
        print("h")
        time = time * 3600
    elif "s" not in unit:
        print("Assuming default (seconds)")
    print(time)
    with_zeroes = zero_fill(time, 10)
    send(f"{boot}{with_zeroes}x", "SET INTERVAL REPORT PERIOD")


def set_interval_report_threshold() -> None:
    """set interval report threshold"""
    print(
        "This command sets the interval report threshold in the RAM by default. This change will not persist through a reboot.\nYou can choose to set this interval in the EEPROM so that the system will boot with this new interval.\nHowever, the EEPROM only has 1 million erase/write cycles, so please test your settings with just RAM before committing to EEPROM."
    )
    boot = parse(
        "To write to EEPROM and RAM, type EEPROM. To write to RAM only (recommended), type anything else and press enter.\nMode:"
    )
    if boot == ("EEPROM"):
        boot = "P"
    else:
        boot = "p"

    threshold = parse("Reporting threshold in mag/arcsec^2: ")
    try:
        float(threshold)
    except:
        print(f"{threshold} is not a valid float.")
        return

    with_zeroes = zero_fill_decimal(threshold, 8, 2)
    send(f"{boot}{with_zeroes}x", "SET INTERVAL REPORT THRESHOLD")


def man_cal_set_light_offset() -> None:
    """manually set calibration: light offset"""
    value = parse("Type offset value in mag/arcsec^2 (float): ")
    try:
        float(value)
    except:
        print(f"{value} is not a valid float.")
        return
    hashes = zero_fill_decimal(value, 8, 2)
    send(f"zcal5{hashes}x", "MANUAL CALIBRATION - SET LIGHT OFFSET")


def man_cal_set_light_temperature() -> None:
    """manually set calibration: light temperature"""
    value = parse("Type temperature value in °C (float): ")
    try:
        float(value)
    except:
        print(f"{value} is not a valid float.")
        return
    hashes = zero_fill_decimal(value, 3, 1)
    send(f"zcal6{hashes}x", "MANUAL CALIBRATION - SET LIGHT TEMPERATURE")


def man_cal_set_dark_period() -> None:
    """manually set calibration: dark period"""
    value = parse("Type period value in seconds (float): ")
    try:
        float(value)
    except:
        print(f"{value} is not a valid float.")
        return
    hashes = zero_fill_decimal(value, 7, 3)
    send(f"zcal7{hashes}x", "MANUAL CALIBRATION - SET DARK PERIOD")


def man_cal_set_dark_temperature() -> None:
    """manually set calibration: dark temperature"""
    value = parse("Type temperature value in °C (float): ")
    try:
        float(value)
    except:
        print(f"{value} is not a valid float.")
        return
    hashes = zero_fill_decimal(value, 3, 1)
    send(f"zcal8{hashes}x", "MANUAL CALIBRATION - SET DARK TEMPERATURE")


def request_simulation_values() -> None:
    """get simulation values"""
    send("sx", "REQUEST INTERNAL SIMULATION VALUES")


def request_simulation_calculation() -> None:
    """runs a simulation"""
    counts = parse("Number of simulated counts: ")
    frequency = parse("Frequency in Hz: ")
    temp = parse("Temperature ADC in °C: ")
    count_zeroes = zero_fill(counts, 10)
    freq_zeroes = zero_fill(frequency, 10)
    temp_zeroes = zero_fill(temp, 10)
    send(
        f"S,{count_zeroes},{freq_zeroes},{temp_zeroes}x",
        "SIMULATE INTERNAL CALCULATION",
    )


def request_ID() -> None:
    send("L0x", "REPORT ID REQUEST")


def request_logging_pointer() -> None:
    send("L1x", "LOGGING POINTER REQUEST")


def erase_flash_chip() -> None:
    """erases the flash chip. does not produce a response"""
    sure = parse(
        "This action is irreversible. Are you sure you want to erase the entire flash memory? To proceed, type ERASE. To cancel, type anything else."
    )
    if sure == ("ERASE"):
        send("L2x", "ERASE FLASH CHIP")
    else:
        print("Request cancelled, flash NOT erased.")


def request_log_one_record() -> None:
    send("L3x", "LOG ONE RECORD REQUEST")


def request_return_one_record() -> None:
    pointer = parse("Type pointer position of record to return: ")
    try:
        value = int(pointer)
    except:
        print(f"{pointer} is not a valid integer.")
        return
    if len(pointer) < 10:
        print(f"{pointer} must be between 0 and 9999999999 (ten digits).")
        return
    if value < 0:
        print(f"{pointer} must be between 0 and 9999999999 (ten digits).")
        return
    pt = zero_fill(pointer, 10)
    send(f"L4{pt}x", "RETURN ONE RECORD REQUEST")


def request_battery_voltage() -> None:
    send("L5x", "BATTERY VOLTAGE REQUEST")


def set_logging_trigger_mode() -> None:
    """sets logging trigger mode"""
    print("0 = no automatic logging")
    print("1 = logging granularity in seconds and not powering down")
    print("2 = logging granularity in minutes and powering down between recordings")
    print(
        "3 = logging every 5 minutes on the 1/12th hour, and powering down between recordings"
    )
    print(
        "4 = logging every 10 minutes on the 1/6th hour, and powering down between recordings"
    )
    print(
        "5 = logging every 15 minutes on the 1/4 hour, and powering down between recordings"
    )
    print(
        "6 = logging every 30 minutes on the 1/2 hour, and powering down between recordings"
    )
    print("7 = logging every hour on the hour, and powering down between recordings")
    mode = parse(f"Select mode from above options")
    if 0 <= int(mode) <= 7:
        send(f"LM{mode}x", f"SET LOGGING TRIGGER MODE {mode}")
    else:
        print("Invalid mode entered")


def request_logging_trigger_mode() -> None:
    send("Lmx", "LOGGING TRIGGER MODE REQUEST")


def request_logging_interval_settings() -> None:
    send("LIx", "LOGGING INTERVAL SETTINGS REQUEST")


def set_logging_interval_period() -> None:
    """sets logging interval period"""
    unit = parse("Type unit for reporting interval (s=seconds m=minutes): ")
    time = parse("Type time value (integer only): ")
    try:
        value = int(time)
    except:
        print(f"{time} is not a valid integer.")
        return
    if value > 0 and value < 9999999999:
        zeroes_time = zero_fill(time, 5)
        if "m" in unit:
            send(f"LPM{zeroes_time}x", "SET LOGGING INTERVAL REPORTING PERIOD MINUTES")
        elif "s" in unit:
            send(f"LPS{zeroes_time}x", "SET LOGGING INTERVAL REPORTING PERIOD SECONDS")
        else:
            print("Invalid mode entry: must be m or s")
    else:
        print(f"{value} must be an integer between 0 and 9999999999 (10 digits).")


def set_logging_threshold() -> None:
    """sets logging light measurement threshold"""
    thresh = parse("Type mag/arcsec^2 value: ")
    try:
        float(thresh)
    except:
        print(f"{thresh} is not a valid float.")
        return
    zeroes_thresh = zero_fill_decimal(thresh, 8, 2)
    send(f"LPT{zeroes_thresh}x", "SET LOGGING THRESHOLD")


def request_clock_data() -> None:
    send("Lcx", "CLOCK DATA REQUEST")


# TODO figure out date/time I/O
def set_clock_data() -> None:
    date_str = parse("Type date in YYYYMMDD format: ")
    time_str = parse("Type time in HHMMSS format: ")

    date = ""
    try:
        date = datetime.datetime.strptime(f"{date_str}{time_str}", "%Y%m%d%H%M%S")

    except Exception:
        print("Incorrectly formatted date, using today's date")
        date = datetime.datetime.today()

    dt = date.strftime("%Y-%m-%d %w %H:%M:%S")
    send(f"Lc{dt}x", "SET CLOCK DATA")


def put_unit_to_sleep() -> None:
    send("Lsx", "PUT UNIT TO SLEEP")


def request_alarm_data() -> None:
    send("Lax", "ALARM DATA REQUEST")


def parse(text: str) -> str:
    """Allows quick exit from user interface. Checks if user typed a trigger word, halting execution if one is found. Otherwise, simply passes input string.

    Args:
        text (str): input string to check

    Returns:
        str: input string
    """
    r = input(text)
    exit_codes = ["exit", "quit"]
    for code in exit_codes:
        if code in r:
            print("EXIT CODE DETECTED\nPROGRAM TERMINATING")
            exit(0)
    return r


def zero_fill_decimal(value: str, whole_len: int, dec_len: int) -> str:
    """Pads string representation of float with zeroes to left and right to comply with command formatting

    Args:
        value (str): number to pad (string representation of integer)
        whole_len (int): length to make integer portion
        dec_len (int): length to make decimal portion

    Returns:
        str: padded number
    """
    if "." in value:  # if decimal
        # int_str, dec_str = value.split(".")[1]
        dec_str = ("%.2f" % float(value)).split(".")[1]
        int_str = value.split(".")[0]
        print(int_str, dec_str)
    else:
        int_str = int(value)
        dec_str = "0" * dec_len

    num = round(float(value))
    count = 0
    while num >= 10:
        num = num % 10
        count += 1
    hashes = "0" * (whole_len - count)
    return f"{hashes}{int_str}.{dec_str}"


def zero_fill(value: str | int, length: int) -> str:
    """Pads number with zeroes to the left, to comply with command formatting

    Args:
        value (str): number to pad (string representation of integer)
        length (int): how long to make the string

    Returns:
        str: padded number
    """
    if isinstance(value, int):
        value = str(value)

    difference = length - len(value)
    if difference < 0:
        return "INCOMPATIBLE"
    elif difference == 0:
        return value
    zeroes = "0" * difference
    return f"{zeroes}{value}"


def ssq(s: str, first: int, last: int) -> str:
    """Get subsequence of string with inclusive endpoints. Most interval values in the manual are listed this way, so this makes things much easier to code. Also strips whitespace for nicer printing.

    Args:
        s (str): string to subsequence
        first (int): start index (inclusive)
        last (int): end index (inclusive)

    Returns:
        str: subsequence, with whitespace stripped
    """
    output = s[first : last + 1]
    return output


def ssql(s: str, first: int, last: int) -> str:
    """Get subsequence of string with inclusive endpoints. Strips all leading zeroes on left. Also strips whitespace for nicer printing.

    Args:
        s (str): string to subsequence
        first (int): start index (inclusive)
        last (int): end index (inclusive)

    Returns:
        str: subsequence, with whitespace and left zeros stripped
    """
    output = s[first : last + 1]
    return output.lstrip("0")


def send(command: str, category: str | None = None) -> str:
    """sends the command

    Args:
        command (str): the command to send
        category (str | None, optional): the type of command. Defaults to None.

    Returns:
        str: _description_
    """
    if category == None:
        category = " "
    else:
        category = f" {category} "

    sure = parse(
        f"\nDo you wish to send the following{category}command (y/n): {command}   "
    )
    if "y" not in sure:
        print("command NOT sent")
        exit()  # stop execution

    print(f"sending command {command}")
    return command


def select_reading_type() -> None:
    print(
        "Commands:\n\
        1 = request reading\n\
        2 = request calibration information\n\
        3 = request unit information"
    )
    resp = parse(f"Select a command: ")
    match resp:
        case "1":
            request_reading()
        case "2":
            request_cal_info()
        case "3":
            request_unit_info()
        case _:
            print(f"{resp} is not a valid selection.")


def select_arm_cal_command() -> None:
    """Sends an arm calibration command"""
    mode = parse(
        "1 = arm light calibration\n\
        2 = arm dark calibration\n\
        3 = disarm calibration\n\
        Select an option: "
    )
    match mode.lower():
        case "1":
            arm_light_cal()
        case "2":
            arm_dark_cal()
        case "3":
            disarm_cal()
        case _:
            print(f"INVALID MODE {mode}, must be 1/2/3")


def select_int_thresh() -> None:
    print(
        "Commands:\n\
        1 = request interval settings\n\
        2 = set interval report period\n\
        3 = set interval report threshold"
    )
    resp = parse(f"Select a command: ")
    match resp:
        case "1":
            request_interval_settings()
        case "2":
            set_interval_report_period()
        case "3":
            set_interval_report_threshold()
        case _:
            print(f"{resp} is not a valid selection.")


def manual_calibrations() -> None:
    print(
        "Commands:\n\
        1 = set light offset\n\
        2 = set light temperature\n\
        3 = set dark period\n\
        4 = set dark temperature"
    )
    resp = parse(f"Select a command: ")
    match resp:
        case "1":
            man_cal_set_light_offset()
        case "2":
            man_cal_set_light_temperature()
        case "3":
            man_cal_set_dark_period()
        case "4":
            man_cal_set_dark_temperature()
        case _:
            print(f"{resp} is not a valid selection.")


def simulation_commands() -> None:
    print(
        "Commands:\n\
        1 = request simulation values\n\
        2 = request simulation calculation"
    )
    resp = parse(f"Select a command: ")
    match resp:
        case "1":
            request_simulation_values()
        case "2":
            request_simulation_calculation()
        case _:
            print(f"{resp} is not a valid selection.")


def logging_commands() -> None:
    print(
        "Commands:\n\
        1 = request logging pointer\n\
        2 = request logging one record\n\
        3 = request return one record\n\
        4 = set logging trigger mode\n\
        5 = request logging trigger mode\n\
        6 = request logging interval settings\n\
        7 = set logging interval period\n\
        8 = set logging threshold"
    )
    resp = parse(f"Select a command: ")
    match resp:
        case "1":
            request_logging_pointer()
        case "2":
            request_log_one_record()
        case "3":
            request_return_one_record()
        case "4":
            set_logging_trigger_mode()
        case "5":
            request_logging_trigger_mode()
        case "6":
            request_logging_interval_settings()
        case "7":
            set_logging_interval_period()
        case "8":
            set_logging_threshold()
        case _:
            print(f"{resp} is not a valid selection.")


def logging_settings() -> None:
    print(
        "Commands:\n\
        1 = request ID\n\
        2 = erase flash chip\n\
        3 = request battery voltage\n\
        4 = request clock data\n\
        5 = set clock data\n\
        6 = put unit to sleep\n\
        7 = request alarm data"
    )
    resp = parse(f"Select a command: ")
    match resp:
        case "1":
            request_ID()
        case "2":
            erase_flash_chip()
        case "3":
            request_battery_voltage()
        case "4":
            request_clock_data()
        case "5":
            set_clock_data()
        case "6":
            put_unit_to_sleep()
        case "7":
            request_alarm_data()
        case _:
            print(f"{resp} is not a valid selection.")


def debugging() -> None:
    print(
        "Welcome to the secret debugging command menu!\
        Commands:\n\
        1 = parse\n\
        2 = zero fill\n\
        3 = zero fill decimal\n\
        4 = subsequence\n\
        5 = subsequence left strip"
    )
    resp = parse(f"Select a command: ")
    match resp:
        case "1":
            parse("Write something to get parsed: ")
        case "2":
            string = parse("Write something to get converted: ")
            length = int(parse("Length of end string: "))
            print(zero_fill(string, length))
        case "3":
            string = parse("Write something to get converted: ")
            before = int(parse("Numbers before decimal: "))
            after = int(parse("Numbers after decimal: "))
            print(zero_fill_decimal(string, before, after))
        case "4":
            string = parse("Write something to take a subsequence of: ")
            start = int(parse("start (inclusive): "))
            end = int(parse("end (inclusive): "))
            print(ssq(string, start, end))
        case "5":
            string = parse("Write something with lots of zeroes to the left: ")
            start = int(parse("start (inclusive): "))
            end = int(parse("end (inclusive): "))
            print(ssql(string, start, end))
        case _:
            print(f"{resp} is not a valid choice.")


def main() -> None:
    """User interface command menu"""

    print(
        "\nCategories:\n\
        1 = simple readings and info requests\n\
        2 = arm/disarm calibrations\n\
        3 = interval and threshold settings\n\
        4 = manual calibration\n\
        5 = simulation commands\n\
        6 = data logging commands\n\
        7 = data logging utilities\n\
        8 = bootloader commands (not yet implemented)"
    )
    resp = parse(f"Select a category: ")
    print("")
    match resp:
        case "1":
            select_reading_type()
        case "2":
            select_arm_cal_command()
        case "3":
            select_int_thresh()
        case "4":
            manual_calibrations()
        case "5":
            simulation_commands()
        case "6":
            logging_commands()
        case "7":
            logging_settings()
        case "8":
            print("BOOTLOADER COMMANDS ARE NOT YET IMPLEMENTED")
        case "0":
            debugging()
        case _:
            print(f"{resp} is not a valid choice.")


main()
