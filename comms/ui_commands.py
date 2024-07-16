"""
Generates a correctly-formatted command based on user input.
Can be run directly, which will print the output to the terminal.
Can be run from another program using command_menu(), which returns the command to send.
"""

import datetime

# if run as stand-alone program, print to terminal without trying to send
to_terminal = False


def _request_reading() -> str:
    """requests a reading"""
    return _send("rx", "REQUEST READING")


def _request_cal_info() -> str:
    """requests calibration information"""
    return _send("cx", "REQUEST CALIBRATION INFORMATION")


def _request_unit_info() -> str:
    """requests unit information"""
    return _send("ix", "REQUEST UNIT INFORMATION")


def _arm_light_cal() -> str:
    return _send("zcalAx", "ARM LIGHT CALIBRATION")


def _arm_dark_cal() -> str:
    return _send("zcalBx", "ARM DARK CALIBRATION")


def _disarm_cal() -> str:
    return _send("zcalDx", "DISARM CALIBRATION")


def _request_interval_settings() -> str:
    """Sends interval setting request. Prompts two responses: reading w/ serial, and interval setting response"""
    return _send("Ix", "INTERVAL SETTINGS REQUEST")


def _set_interval_report_period() -> str:
    """set interval report period"""
    print(
        "This command sets the interval report period in the RAM by default. This change will not persist through a reboot.\nYou can choose to set this interval in the EEPROM so that the system will boot with this new interval.\nHowever, the EEPROM only has 1 million erase/write cycles, so please test your settings with just RAM before committing to EEPROM."
    )
    boot = _parse(
        "To write to EEPROM and RAM, type EEPROM. To write to RAM only (recommended), type anything else and press enter.\nMode: "
    )
    if boot == ("EEPROM"):
        boot = "P"
    else:
        boot = "p"

    interval = _parse("Reporting interval (as integer only): ")
    try:
        time = int(interval)
        print(time)
    except:
        print(f"{interval} is not a valid integer.")
        return ""

    unit = _parse("Unit for time value (s=seconds, m=minutes, h=hours): ")
    if "m" in unit:
        print("m")
        time = time * 60
    elif "h" in unit:
        print("h")
        time = time * 3600
    elif "s" not in unit:
        print("Assuming default (seconds)")
    print(time)
    with_zeroes = _zero_fill(time, 10)
    return _send(f"{boot}{with_zeroes}x", "SET INTERVAL REPORT PERIOD")


def _set_interval_report_threshold() -> str:
    """set interval report threshold"""
    print(
        "This command sets the interval report threshold in the RAM by default. This change will not persist through a reboot.\nYou can choose to set this interval in the EEPROM so that the system will boot with this new interval.\nHowever, the EEPROM only has 1 million erase/write cycles, so please test your settings with just RAM before committing to EEPROM."
    )
    boot = _parse(
        "To write to EEPROM and RAM, type EEPROM. To write to RAM only (recommended), type anything else and press enter.\nMode:"
    )
    if boot == ("EEPROM"):
        boot = "P"
    else:
        boot = "p"

    threshold = _parse("Reporting threshold in mag/arcsec^2: ")
    try:
        float(threshold)
    except:
        print(f"{threshold} is not a valid float.")
        return ""

    with_zeroes = _zero_fill_decimal(threshold, 8, 2)
    return _send(f"{boot}{with_zeroes}x", "SET INTERVAL REPORT THRESHOLD")


def _man_cal_set_light_offset() -> str:
    """manually set calibration: light offset"""
    value = _parse("Type offset value in mag/arcsec^2 (float): ")
    try:
        float(value)
    except:
        print(f"{value} is not a valid float.")
        return ""
    hashes = _zero_fill_decimal(value, 8, 2)
    return _send(f"zcal5{hashes}x", "MANUAL CALIBRATION - SET LIGHT OFFSET")


def _man_cal_set_light_temperature() -> str:
    """manually set calibration: light temperature"""
    value = _parse("Type temperature value in °C (float): ")
    try:
        float(value)
    except:
        print(f"{value} is not a valid float.")
        return ""
    hashes = _zero_fill_decimal(value, 3, 1)
    return _send(f"zcal6{hashes}x", "MANUAL CALIBRATION - SET LIGHT TEMPERATURE")


def _man_cal_set_dark_period() -> str:
    """manually set calibration: dark period"""
    value = _parse("Type period value in seconds (float): ")
    try:
        float(value)
    except:
        print(f"{value} is not a valid float.")
        return ""
    hashes = _zero_fill_decimal(value, 7, 3)
    return _send(f"zcal7{hashes}x", "MANUAL CALIBRATION - SET DARK PERIOD")


def _man_cal_set_dark_temperature() -> str:
    """manually set calibration: dark temperature"""
    value = _parse("Type temperature value in °C (float): ")
    try:
        float(value)
    except:
        print(f"{value} is not a valid float.")
        return ""
    hashes = _zero_fill_decimal(value, 3, 1)
    return _send(f"zcal8{hashes}x", "MANUAL CALIBRATION - SET DARK TEMPERATURE")


def _request_simulation_values() -> str:
    """get simulation values"""
    return _send("sx", "REQUEST INTERNAL SIMULATION VALUES")


def _request_simulation_calculation() -> str:
    """runs a simulation"""
    counts = _parse("Number of simulated counts: ")
    frequency = _parse("Frequency in Hz: ")
    temp = _parse("Temperature ADC in °C: ")
    count_zeroes = _zero_fill(counts, 10)
    freq_zeroes = _zero_fill(frequency, 10)
    temp_zeroes = _zero_fill(temp, 10)
    return _send(
        f"S,{count_zeroes},{freq_zeroes},{temp_zeroes}x",
        "SIMULATE INTERNAL CALCULATION",
    )


def _request_ID() -> str:
    return _send("L0x", "REPORT ID REQUEST")


def _request_logging_pointer() -> str:
    return _send("L1x", "LOGGING POINTER REQUEST")


def _erase_flash_chip() -> str:
    """erases the flash chip. does not produce a response"""
    sure = _parse(
        "This action is irreversible. Are you sure you want to erase the entire flash memory? To proceed, type ERASE. To cancel, type anything else."
    )
    if sure == ("ERASE"):
        return _send("L2x", "ERASE FLASH CHIP")
    else:
        print("Request cancelled, flash NOT erased.")
        return ""


def _request_log_one_record() -> str:
    return _send("L3x", "LOG ONE RECORD REQUEST")


def _request_return_one_record() -> str:
    pointer = _parse("Type pointer position of record to return: ")
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
    pt = _zero_fill(pointer, 10)
    return _send(f"L4{pt}x", "RETURN ONE RECORD REQUEST")


def _request_battery_voltage() -> str:
    return _send("L5x", "BATTERY VOLTAGE REQUEST")


def _set_logging_trigger_mode() -> str:
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
    mode = _parse(f"Select mode from above options")
    if 0 <= int(mode) <= 7:
        return _send(f"LM{mode}x", f"SET LOGGING TRIGGER MODE {mode}")
    else:
        print("Invalid mode entered")
        return ""


def _request_logging_trigger_mode() -> str:
    return _send("Lmx", "LOGGING TRIGGER MODE REQUEST")


def _request_logging_interval_settings() -> str:
    return _send("LIx", "LOGGING INTERVAL SETTINGS REQUEST")


def _set_logging_interval_period() -> str:
    """sets logging interval period"""
    unit = _parse("Type unit for reporting interval (s=seconds m=minutes): ")
    time = _parse("Type time value (integer only): ")
    try:
        value = int(time)
    except:
        print(f"{time} is not a valid integer.")
        return ""
    if value > 0 and value < 9999999999:
        zeroes_time = _zero_fill(time, 5)
        if "m" in unit:
            return _send(
                f"LPM{zeroes_time}x", "SET LOGGING INTERVAL REPORTING PERIOD MINUTES"
            )
        elif "s" in unit:
            return _send(
                f"LPS{zeroes_time}x", "SET LOGGING INTERVAL REPORTING PERIOD SECONDS"
            )
        else:
            print("Invalid mode entry: must be m or s")
    else:
        print(f"{value} must be an integer between 0 and 9999999999 (10 digits).")
    return ""


def _set_logging_threshold() -> str:
    """sets logging light measurement threshold"""
    thresh = _parse("Type mag/arcsec^2 value: ")
    try:
        float(thresh)
    except:
        print(f"{thresh} is not a valid float.")
        return ""
    zeroes_thresh = _zero_fill_decimal(thresh, 8, 2)
    return _send(f"LPT{zeroes_thresh}x", "SET LOGGING THRESHOLD")


def _request_clock_data() -> str:
    return _send("Lcx", "CLOCK DATA REQUEST")


def _set_clock_data() -> str:
    date_str = _parse("Type date in YYYYMMDD format: ")
    time_str = _parse("Type time in HHMMSS format: ")

    date = ""
    try:
        date = datetime.datetime.strptime(f"{date_str}{time_str}", "%Y%m%d%H%M%S")

    except Exception:
        print("Incorrectly formatted date, using today's date")
        date = datetime.datetime.today()

    dt = date.strftime("%Y-%m-%d %w %H:%M:%S")
    return _send(f"Lc{dt}x", "SET CLOCK DATA")


def _put_unit_to_sleep() -> str:
    return _send("Lsx", "PUT UNIT TO SLEEP")


def _request_alarm_data() -> str:
    return _send("Lax", "ALARM DATA REQUEST")


def _parse(text: str) -> str:
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


def _zero_fill_decimal(value: str, whole_len: int, dec_len: int) -> str:
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


def _zero_fill(value: str | int, length: int) -> str:
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


def _ssq(s: str, first: int, last: int) -> str:
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


def _ssql(s: str, first: int, last: int) -> str:
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


def _send(command: str, category: str | None = None) -> str:
    """sends the command

    Args:
        command (str): the command to send
        category (str | None, optional): the type of command. Defaults to None.

    Returns:
        str: the command to send
    """
    # if run as stand-alone, don't do sending behavior
    if to_terminal:
        return command
    if category == None:
        category = " "
    else:
        category = f" {category} "

    sure = _parse(
        f"\nDo you wish to send the following{category}command (y/n): {command}   "
    )
    if "y" not in sure:
        print("command NOT sent")
        exit()  # stop execution

    print(f"sending command {command}")
    return command


def _select_reading_type() -> str:
    print(
        "Commands:\n\
        1 = request reading\n\
        2 = request calibration information\n\
        3 = request unit information"
    )
    resp = _parse(f"Select a command: ")
    match resp:
        case "1":
            return _request_reading()
        case "2":
            return _request_cal_info()
        case "3":
            return _request_unit_info()
        case _:
            print(f"{resp} is not a valid selection.")
            return ""


def _select_arm_cal_command() -> str:
    """Sends an arm calibration command"""
    mode = _parse(
        "1 = arm light calibration\n\
        2 = arm dark calibration\n\
        3 = disarm calibration\n\
        Select an option: "
    )
    match mode.lower():
        case "1":
            return _arm_light_cal()
        case "2":
            return _arm_dark_cal()
        case "3":
            return _disarm_cal()
        case _:
            print(f"INVALID MODE {mode}, must be 1/2/3")
            return ""


def _select_int_thresh() -> str:
    print(
        "Commands:\n\
        1 = request interval settings\n\
        2 = set interval report period\n\
        3 = set interval report threshold"
    )
    resp = _parse(f"Select a command: ")
    match resp:
        case "1":
            return _request_interval_settings()
        case "2":
            return _set_interval_report_period()
        case "3":
            return _set_interval_report_threshold()
        case _:
            print(f"{resp} is not a valid selection.")
            return ""


def _manual_calibrations() -> str:
    print(
        "Commands:\n\
        1 = set light offset\n\
        2 = set light temperature\n\
        3 = set dark period\n\
        4 = set dark temperature"
    )
    resp = _parse(f"Select a command: ")
    match resp:
        case "1":
            return _man_cal_set_light_offset()
        case "2":
            return _man_cal_set_light_temperature()
        case "3":
            return _man_cal_set_dark_period()
        case "4":
            return _man_cal_set_dark_temperature()
        case _:
            print(f"{resp} is not a valid selection.")
            return ""


def _simulation_commands() -> str:
    print(
        "Commands:\n\
        1 = request simulation values\n\
        2 = request simulation calculation"
    )
    resp = _parse(f"Select a command: ")
    match resp:
        case "1":
            return _request_simulation_values()
        case "2":
            return _request_simulation_calculation()
        case _:
            print(f"{resp} is not a valid selection.")
            return ""


def _logging_commands() -> str:
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
    resp = _parse(f"Select a command: ")
    match resp:
        case "1":
            return _request_logging_pointer()
        case "2":
            return _request_log_one_record()
        case "3":
            return _request_return_one_record()
        case "4":
            return _set_logging_trigger_mode()
        case "5":
            return _request_logging_trigger_mode()
        case "6":
            return _request_logging_interval_settings()
        case "7":
            return _set_logging_interval_period()
        case "8":
            return _set_logging_threshold()
        case _:
            print(f"{resp} is not a valid selection.")
            return ""


def _logging_settings() -> str:
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
    resp = _parse(f"Select a command: ")
    match resp:
        case "1":
            return _request_ID()
        case "2":
            return _erase_flash_chip()
        case "3":
            return _request_battery_voltage()
        case "4":
            return _request_clock_data()
        case "5":
            return _set_clock_data()
        case "6":
            return _put_unit_to_sleep()
        case "7":
            return _request_alarm_data()
        case _:
            print(f"{resp} is not a valid selection.")
            return ""


def _debugging() -> str:
    print(
        "Welcome to the secret debugging command menu!\n\
        Commands:\n\
        1 = parse\n\
        2 = zero fill\n\
        3 = zero fill decimal\n\
        4 = subsequence\n\
        5 = subsequence left strip"
    )
    resp = _parse(f"Select a command: ")
    match resp:
        case "1":
            _parse("Write something to get parsed: ")
        case "2":
            string = _parse("Write something to get converted: ")
            length = int(_parse("Length of end string: "))
            print(_zero_fill(string, length))
        case "3":
            string = _parse("Write something to get converted: ")
            before = int(_parse("Numbers before decimal: "))
            after = int(_parse("Numbers after decimal: "))
            print(_zero_fill_decimal(string, before, after))
        case "4":
            string = _parse("Write something to take a subsequence of: ")
            start = int(_parse("start (inclusive): "))
            end = int(_parse("end (inclusive): "))
            print(_ssq(string, start, end))
        case "5":
            string = _parse("Write something with lots of zeroes to the left: ")
            start = int(_parse("start (inclusive): "))
            end = int(_parse("end (inclusive): "))
            print(_ssql(string, start, end))
        case _:
            print(f"{resp} is not a valid choice.")
    return ""


def command_menu() -> str:
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
        8 = bootloader commands (not yet implemented)\n\
        9 = exit user interface"
    )
    resp = _parse(f"Select a category: ")
    print("")
    match resp:
        case "1":
            return _select_reading_type()
        case "2":
            return _select_arm_cal_command()
        case "3":
            return _select_int_thresh()
        case "4":
            return _manual_calibrations()
        case "5":
            return _simulation_commands()
        case "6":
            return _logging_commands()
        case "7":
            return _logging_settings()
        case "8":
            print("BOOTLOADER COMMANDS ARE NOT YET IMPLEMENTED")
        case "9":
            return "exit"
        case "0":
            return _debugging()
        case _:
            print(f"{resp} is not a valid choice.")
    return ""


def main() -> None:
    """Does all UI behavior without sending the command, instead printing it to the terminal."""
    global to_terminal
    to_terminal = True
    print(command_menu())


if __name__ == "__main__":
    main()
