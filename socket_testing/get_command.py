# runs on host computer, generates a command from user interface
import argparse

ui = True
from_host = False


def request_reading() -> str:
    """requests a reading"""
    return send("rx", "REQUEST READING")


def request_cal_info() -> str:
    """requests calibration information"""
    return send("cx", "REQUEST CALIBRATION INFORMATION")


def request_unit_info() -> str:
    """requests unit information"""
    return send("ix", "REQUEST UNIT INFORMATION")


def send_arm_cal_command() -> str:
    """Sends an arm calibration command"""
    mode = parse(
        "1 = arm light calibration\n2 = arm dark calibration\n3 = disarm calibration\nSelect an option: "
    )
    match mode.lower():
        case "1":
            return send("zcalAx", "ARM LIGHT CALIBRATION")
        case "2":
            return send("zcalBx", "ARM DARK CALIBRATION")
        case "3":
            return send("zcalDx", "DISARM CALIBRATION")
        case _:
            print(f"INVALID MODE {mode}, must be 1/2/3")
            return ""


def request_interval_settings() -> str:
    """Sends interval setting request. Prompts two responses: reading w/ serial, and interval setting response"""
    return send("Ix", "INTERVAL SETTINGS REQUEST")


def set_interval_report_period() -> str:
    """set interval report period"""
    import re

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
    value = "".join(re.findall(r"\d+", interval))
    try:
        time = int(value)
    except:
        print(f"{value} is not a valid integer.")
        return ""

    unit = parse("Unit for time value (s=seconds, m=minutes, h=hours): ")
    if "m" in unit:
        time = time * 60
    elif "h" in unit:
        time = time * 3600
    elif "s" not in unit:
        print("Assuming default (seconds)")
    with_zeroes = zero_fill(value, 10)
    return send(f"{boot}{with_zeroes}{time}x", "SET INTERVAL REPORT PERIOD")


def set_interval_report_threshold() -> str:
    """set interval report threshold"""
    import re

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
    value = "".join(re.findall(r"[\d]*[.][\d]+", threshold))
    try:
        float(value)
    except:
        print(f"{value} is not a valid float.")
        return ""

    with_zeroes = zero_fill_decimal(threshold, 8, 2)
    return send(f"{boot}{with_zeroes}x", "SET INTERVAL REPORT THRESHOLD")


def man_cal_set_light_offset() -> str:
    """manually set calibration: light offset"""
    value = parse("Type offset value in mag/arcsec^2 (float): ")
    try:
        float(value)
    except:
        print(f"{value} is not a valid float.")
        return ""
    hashes = zero_fill_decimal(value, 8, 2)
    return send(f"zcal5{hashes}x", "MANUAL CALIBRATION - SET LIGHT OFFSET")


def man_cal_set_light_temperature() -> str:
    """manually set calibration: light temperature"""
    value = parse("Type temperature value in °C (float): ")
    try:
        float(value)
    except:
        print(f"{value} is not a valid float.")
        return ""
    hashes = zero_fill_decimal(value, 3, 1)
    return send(f"zcal6{hashes}x", "MANUAL CALIBRATION - SET LIGHT TEMPERATURE")


def man_cal_set_dark_period() -> str:
    """manually set calibration: dark period"""
    value = parse("Type period value in seconds (float): ")
    try:
        float(value)
    except:
        print(f"{value} is not a valid float.")
        return ""
    hashes = zero_fill_decimal(value, 7, 3)
    return send(f"zcal7{hashes}x", "MANUAL CALIBRATION - SET DARK PERIOD")


def man_cal_set_dark_temperature() -> str:
    """manually set calibration: dark temperature"""
    value = parse("Type temperature value in °C (float): ")
    try:
        float(value)
    except:
        print(f"{value} is not a valid float.")
        return ""
    hashes = zero_fill_decimal(value, 3, 1)
    return send(f"zcal8{hashes}x", "MANUAL CALIBRATION - SET DARK TEMPERATURE")


def request_simulation_values() -> str:
    """get simulation values"""
    return send("sx", "REQUEST INTERNAL SIMULATION VALUES")


def request_simulation_calculation() -> str:
    """runs a simulation"""
    counts = parse("Number of simulated counts: ")
    frequency = parse("Frequency in Hz: ")
    temp = parse("Temperature ADC in °C: ")
    count_zeroes = zero_fill(counts, 10)
    freq_zeroes = zero_fill(frequency, 10)
    temp_zeroes = zero_fill(temp, 10)
    return send(
        f"S,{count_zeroes},{freq_zeroes},{temp_zeroes}x",
        "SIMULATE INTERNAL CALCULATION",
    )


def request_ID() -> str:
    return send("L0x", "REPORT ID REQUEST")


def request_logging_pointer() -> str:
    return send("L1x", "LOGGING POINTER REQUEST")


def erase_flash_chip() -> str:
    """erases the flash chip. does not produce a response"""
    sure = parse(
        "This action is irreversible. Are you sure you want to erase the entire flash memory? To proceed, type ERASE. To cancel, type anything else."
    )
    if sure == ("ERASE"):
        return send("L2x", "ERASE FLASH CHIP")
    else:
        print("Request cancelled, flash NOT erased.")
        return ""


def request_log_one_record() -> str:
    return send("L3x", "LOG ONE RECORD REQUEST")


def request_return_one_record() -> str:
    pointer = parse("Type pointer position of record to return: ")
    try:
        value = int(pointer)
    except:
        print(f"{pointer} is not a valid integer.")
        return ""
    if len(pointer) < 10:
        print(f"{pointer} must be between 0 and 9999999999 (ten digits).")
        return ""
    if value < 0:
        print(f"{pointer} must be between 0 and 9999999999 (ten digits).")
        return ""
    pt = zero_fill(pointer, 10)
    return send(f"L4{pt}x", "RETURN ONE RECORD REQUEST")


def request_battery_voltage() -> str:
    return send("L5x", "BATTERY VOLTAGE REQUEST")


def set_logging_trigger_mode() -> str:
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
        return send(f"LM{mode}x", f"SET LOGGING TRIGGER MODE {mode}")
    else:
        print("Invalid mode entered")
        return ""


def request_logging_trigger_mode() -> str:
    return send("Lmx", "LOGGING TRIGGER MODE REQUEST")


def request_logging_interval_settings() -> str:
    return send("LIx", "LOGGING INTERVAL SETTINGS REQUEST")


def set_logging_interval_period() -> str:
    """sets logging interval period"""
    unit = parse("Type unit for reporting interval (s=seconds m=minutes): ")
    time = parse("Type time value (integer only): ")
    try:
        value = int(time)
    except:
        print(f"{time} is not a valid integer.")
        return ""
    if value > 0 and value < 9999999999:
        zeroes_time = zero_fill(time, 5)
        if "m" in unit:
            return send(
                f"LPM{zeroes_time}x", "SET LOGGING INTERVAL REPORTING PERIOD MINUTES"
            )
        elif "s" in unit:
            return send(
                f"LPS{zeroes_time}x", "SET LOGGING INTERVAL REPORTING PERIOD SECONDS"
            )
        else:
            print("Invalid mode entry: must be m or s")
    else:
        print(f"{value} must be an integer between 0 and 9999999999 (10 digits).")
    return ""


def set_logging_threshold() -> str:
    """sets logging light measurement threshold"""
    thresh = parse("Type mag/arcsec^2 value: ")
    try:
        float(thresh)
    except:
        print(f"{thresh} is not a valid float.")
        return ""
    zeroes_thresh = zero_fill_decimal(thresh, 8, 2)
    return send(f"LPT{zeroes_thresh}x", "SET LOGGING THRESHOLD")


def request_clock_data() -> str:
    return send("Lcx", "CLOCK DATA REQUEST")


# TODO figure out date/time I/O
def set_clock_data() -> str:
    data = parse("Type data here (lol finish this later): ")
    return send(f"Lc{data}x", "SET CLOCK DATA")


def put_unit_to_sleep() -> str:
    return send("Lsx", "PUT UNIT TO SLEEP")


def request_alarm_data() -> str:
    return send("Lax", "ALARM DATA REQUEST")


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
    whole = int(value)
    decimal = (float(value) - whole) * pow(10, dec_len)
    num = whole
    count = 0
    while num >= 10:
        num = num % 10
        count += 1
    hashes = "0" * (whole_len - count)
    return f"{hashes}{whole}.{decimal}"


def zero_fill(value: str, length: int) -> str:
    """Pads number with zeroes to the left, to comply with command formatting

    Args:
        value (str): number to pad (string representation of integer)
        length (int): how long to make the string

    Returns:
        str: padded number
    """
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


##### CONNECT TO DEVICE, SOMEHOW #####


def send(command: str, category: str | None = None) -> str:
    if from_host:
        return command

    if not ui:
        print(f"sent command {command}, hypothetically")

    sure = ""
    if category != None:
        sure = parse(
            f"\nDo you wish to send the following {category} command (y/n): {command}   "
        )
    else:
        sure = parse(f"\nDo you wish to send the following command (y/n): {command}   ")

    if "y" in sure:
        print("(simulated) command sent")
        return command
    else:
        print("command NOT sent")
        return ""


##### SELECT SEND #####
def command_menu() -> str:
    """User interface command menu"""
    print(
        "\nCategories:\n1 = simple readings and info requests\n2 = arm/disarm calibrations\n3 = interval and threshold settings\n4 = manual calibration\n5 = simulation commands\n6 = data logging commands\n7 = data logging utilities\n8 = bootloader commands (not yet implemented)"
    )
    cat = parse(f"Select a category: ")
    print("")
    match cat:
        case "1":
            print(
                "Commands:\n1 = request reading\n2 = request calibration information\n3 = request unit information"
            )
            cat1 = parse(f"Select a command: ")
            match cat1:
                case "1":
                    return request_reading()
                case "2":
                    return request_cal_info()
                case "3":
                    return request_unit_info()
                case _:
                    print(f"{cat1} is not a valid selection.")
                    return ""
        case "2":
            return send_arm_cal_command()
        case "3":
            print(
                "Commands:\n1 = request interval settings\n2 = set interval report period\n3 = set interval report threshold"
            )
            cat3 = parse(f"Select a command: ")
            match cat3:
                case "1":
                    return request_interval_settings()
                case "2":
                    return set_interval_report_period()
                case "3":
                    return set_interval_report_threshold()
                case _:
                    print(f"{cat3} is not a valid selection.")
                    return ""
        case "4":
            print(
                "Commands:\n1 = set light offset\n2 = set light temperature\n3 = set dark period\n4 = set dark temperature"
            )
            cat4 = parse(f"Select a command: ")
            match cat4:
                case "1":
                    return man_cal_set_light_offset()
                case "2":
                    return man_cal_set_light_temperature()
                case "3":
                    return man_cal_set_dark_period()
                case "4":
                    return man_cal_set_dark_temperature()
                case _:
                    print(f"{cat4} is not a valid selection.")
                    return ""
        case "5":
            print(
                "Commands:\n1 = request simulation values\n2 = request simulation calculation"
            )
            cat5 = parse(f"Select a command: ")
            match cat5:
                case "1":
                    return request_simulation_values()
                case "2":
                    return request_simulation_calculation()
                case _:
                    print(f"{cat5} is not a valid selection.")
                    return ""
        case "6":
            print(
                "Commands:\n1 = request logging pointer\n2 = request logging one record\n3 = request return one record\n4 = set logging trigger mode\n5 = request logging trigger mode\n6 = request logging interval settings\n7 = set logging interval period\n8 = set logging threshold"
            )
            cat6 = parse(f"Select a command: ")
            match cat6:
                case "1":
                    return request_logging_pointer()
                case "2":
                    return request_log_one_record()
                case "3":
                    return request_return_one_record()
                case "4":
                    return set_logging_trigger_mode()
                case "5":
                    return request_logging_trigger_mode()
                case "6":
                    return request_logging_interval_settings()
                case "7":
                    return set_logging_interval_period()
                case "8":
                    return set_logging_threshold()
                case _:
                    print(f"{cat6} is not a valid selection.")
                    return ""
        case "7":
            print(
                "Commands:\n1 = request ID\n2 = erase flash chip\n3 = request battery voltage\n4 = request clock data\n5 = set clock data\n6 = put unit to sleep\n7 = request alarm data"
            )
            cat7 = parse(f"Select a command: ")
            match cat7:
                case "1":
                    return request_ID()
                case "2":
                    return erase_flash_chip()
                case "3":
                    return request_battery_voltage()
                case "4":
                    return request_clock_data()
                case "5":
                    return set_clock_data()
                case "6":
                    return put_unit_to_sleep()
                case "7":
                    return request_alarm_data()
                case _:
                    print(f"{cat7} is not a valid selection.")
                    return ""
        case "8":
            print("BOOTLOADER COMMANDS ARE NOT YET IMPLEMENTED")
        case "0":
            print("Welcome to the secret debugging command menu!")
            print(
                "Commands:\n1 = parse\n2 = zero fill\n3 = zero fill decimal\n4 =  subsequence\n5 = subsequence left strip"
            )
            cat0 = parse(f"Select a command: ")
            match cat0:
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
                    print(f"{cat0} is not a valid choice.")
        case _:
            print(f"{cat} is not a valid choice.")
    return ""


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="get_command.py",
        description="Sends a command to the raspberry pi",
        epilog=f"If no argument given, runs user interface",
    )

    parser.add_argument(
        "command",
        nargs="?",
        type=str,
        help=f"To send a command you've already made, just give it as an argument",
    )

    args = vars(parser.parse_args())
    command = args.get("command")

    if command == None:  # no input, use user interface
        command_menu()
    else:  # send given command
        send(command)


def from_socket(command: str) -> None:
    global ui
    ui = False
    print("yippee this worked")
    send(command)


def command_from_host() -> str:
    global from_host
    from_host = True
    return command_menu()
