import re


##### SORT RESPONSES #####
def sort_response(r: str) -> None:
    match r[0]:
        case "r":
            parse_reading(r)
        case "c":
            parse_cal_info(r)
        case "z":
            if r[1] == (","):
                pass
            else:
                parse_arm_cal_command(r)
        case "I":
            parse_interval_settings(r)
        case "s":
            parse_simulation_values(r)
        case "S":
            parse_simulation_calculation(r)
        case "L":
            sort_L(r)
        case _:
            pass


##### SIMPLE READINGS AND INFO REQUESTS #####
def request_reading() -> None:
    send("rx", "REQUEST READING")


def parse_reading(r: str) -> None:
    print("READING RESULT")
    print("Current light measurement:", ssq(r, 2, 8))
    print("Frequency:", ssql(r, 10, 21))
    print("Period (counts):", ssql(r, 22, 33))
    print("Period (seconds)", ssql(r, 35, 46))
    print("Temperature:", ssq(r, 48, 54))
    if len(r) >= 63:
        print("Serial number:", ssql(r, 55, 63))


def request_cal_info() -> None:
    send("cx", "REQUEST CALIBRATION INFORMATION")


def parse_cal_info(r: str) -> None:
    print("CALIBRATION INFORMATION RESULT")
    print("Light calibration offset:", ssql(r, 2, 13))
    print("Dark calibration period:", ssql(r, 15, 26))
    print("Temperature during light calibration:", ssq(r, 28, 34))
    print("Light sensor offset (manufacturer):", ssql(r, 36, 47))
    print("Temperature during dark calibration:", ssq(r, 49, 55))


def request_unit_info() -> None:
    send("ix", "REQUEST UNIT INFORMATION")


def parse_unit_information(r: str) -> None:
    print("UNIT INFORMATION RESULT")
    print("Protocol number:", ssq(r, 2, 9))
    print("Model number:", ssq(r, 11, 18))
    print("Feature number:", ssq(r, 20, 27))
    print("Serial number:", ssq(r, 29, 36))


##### ARM/DISARM CALIBRATIONS #####


def send_arm_cal_command() -> None:
    mode = parse(
        "1 = arm light calibration\n2 = arm dark calibration\n3 = disarm calibration\nSelect an option: "
    )
    match mode.lower():
        case "1":
            send("zcalAx", "ARM LIGHT CALIBRATION")
        case "2":
            send("zcalBx", "ARM DARK CALIBRATION")
        case "3":
            send("zcalDx", "DISARM CALIBRATION")
        case _:
            print(f"INVALID MODE {mode}, must be 1/2/3")


def parse_arm_cal_command(r: str) -> None:
    print("ARM CALIBRATION RESULT")
    match r[1]:
        case "A":
            print("Light calibration", end=" ")
        case "B":
            print("Dark calibration", end=" ")
        case "x":
            print("All calibration modes", end=" ")
        case _:
            print(f"INVALID RESPONSE {r[1]}", end=" ")

    match r[2]:
        case "a":
            print("Armed!")
        case "d":
            print("Disarmed!")
        case _:
            print(f"INVALID RESPONSE {r[2]}", end="")

    match r[3]:
        case "L":
            print(
                "LOCKED. Wait for unlock before calibrating after Arm command, firmware upgrades are disabled."
            )
        case "U":
            print(
                "UNLOCKED. Calibrate immediately after Arm command, Enable firmware upgrade."
            )
        case _:
            print(f"INVALID RESPONSE {r[3]}")


##### INTERVALS AND THRESHOLDS #####


def request_interval_settings() -> None:
    send("Ix", "INTERVAL SETTINGS REQUEST")
    # two responses: reading w/ serial, and interval setting response


def set_interval_report_period() -> None:
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
        return

    unit = parse("Unit for time value (s=seconds, m=minutes, h=hours): ")
    if "m" in unit:
        time = time * 60
    elif "h" in unit:
        time = time * 3600
    elif "s" not in unit:
        print("Assuming default (seconds)")
    with_zeroes = zero_fill(value, 10)
    send(f"{boot}{with_zeroes}{time}x", "SET INTERVAL REPORT PERIOD")


def set_interval_report_threshold() -> None:
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
        return

    with_zeroes = zero_fill_decimal(threshold, 8, 2)
    send(f"{boot}{with_zeroes}x", "SET INTERVAL REPORT THRESHOLD")


# this is the response for Ix, set period, and set threshold
def parse_interval_settings(r: str) -> None:
    print("INTERVAL SETTINGS RESPONSE")
    print("Interval period EEPROM:", ssql(r, 2, 12))
    print("Interval period RAM:", ssql(r, 14, 24))
    print("Threshold EEPROM:", ssql(r, 26, 37))
    print("Threshold RAM:", ssql(r, 39, 50))


##### MANUAL CALIBRATION #####


def man_cal_set_light_offset() -> None:
    value = parse("Type offset value in mag/arcsec^2 (float): ")
    try:
        float(value)
    except:
        print(f"{value} is not a valid float.")
        return
    hashes = zero_fill_decimal(value, 8, 2)
    send(f"zcal5{hashes}x", "MANUAL CALIBRATION - SET LIGHT OFFSET")


def man_cal_set_light_temperature() -> None:
    value = parse("Type temperature value in °C (float): ")
    try:
        float(value)
    except:
        print(f"{value} is not a valid float.")
        return
    hashes = zero_fill_decimal(value, 3, 1)
    send(f"zcal6{hashes}x", "MANUAL CALIBRATION - SET LIGHT TEMPERATURE")


def man_cal_set_dark_period() -> None:
    value = parse("Type period value in seconds (float): ")
    try:
        float(value)
    except:
        print(f"{value} is not a valid float.")
        return
    hashes = zero_fill_decimal(value, 7, 3)
    send(f"zcal7{hashes}x", "MANUAL CALIBRATION - SET DARK PERIOD")


def man_cal_set_dark_temperature() -> None:
    value = parse("Type temperature value in °C (float): ")
    try:
        float(value)
    except:
        print(f"{value} is not a valid float.")
        return
    hashes = zero_fill_decimal(value, 3, 1)
    send(f"zcal8{hashes}x", "MANUAL CALIBRATION - SET DARK TEMPERATURE")


def parse_manual_cal(r: str) -> bool:
    print("MANUAL CALIBRATION RESULTS")
    match r[2]:
        case "5":
            print("Light Magnitude (mag/arcsec^2):", ssql(r, 4, 15))
        case "6":
            print("Light Temperature (°C):", ssql(r, 4, 9))
        case "7":
            print("Dark Period (sec):", ssql(r, 4, 15))
        case "8":
            print("Dark Temperature (°C):", ssql(r, 4, 9))
        case _:
            print("INVALID RESPONSE")
            return False
    return True


##### SIMULATION COMMANDS #####


def request_simulation_values() -> None:
    send("sx", "REQUEST INTERNAL SIMULATION VALUES")


def parse_simulation_values(r: str) -> None:
    print("INTERNAL SIMULATION VALUES RESPONSE")
    print("Number of counts:", ssql(r, 2, 12))
    print("Frequency (Hz):", ssql(r, 14, 24))
    print("Temperature ADC (°C):", ssql(r, 26, 37))


def request_simulation_calculation() -> None:
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


def parse_simulation_calculation(r: str) -> None:
    print("SIMULATION CALCULATION RESPONSE")
    print("Number of counts:", ssql(r, 2, 13))
    print("Frequency (Hz):", ssql(r, 14, 25))
    print("Temperature ADC (°C):", ssql(r, 26, 37))
    print("Calculated mpsas:", ssql(r, 40, 47))
    print("Frequency used for calculation (Hz):", ssql(r, 48, 60))
    print("Counts used for calculation:", ssql(r, 61, 72))
    print("Calculated period from counts:", ssql(r, 73, 85))
    print("Temperature used for calculation (°C):", ssql(r, 86, 92))


##### DATA LOGGER COMMANDS #####
def sort_L(r: str) -> None:
    match r[1]:
        case "0":
            parse_ID(r)
        case "1":
            parse_logging_pointer(r)
        case "3":
            parse_log_one_record(r)
        case "4":
            parse_return_one_record(r)
        case "5":
            parse_battery_voltage(r)
        case "M":
            parse_logging_trigger_mode(r)
        case "I":
            parse_logging_interval_settings(r)
        case "c":
            parse_clock_data(r)
        case "a":
            parse_alarm_data(r)
        case _:
            print(f"INVALID RESPONSE {r}")


def request_ID() -> None:
    send("L0x", "REPORT ID REQUEST")


def parse_ID(r: str) -> None:
    print("REPORT ID RESPONSE")
    print("Manufacturer ID:", ssq(r, 3, 5))
    print("Device ID:", ssq(r, 6, 8))


def request_logging_pointer() -> None:
    send("L1x", "LOGGING POINTER REQUEST")


def parse_logging_pointer(r: str) -> None:
    print("LOGGING POINTER RESPONSE")
    print("Pointer position:", ssq(r, 3, 8))


def erase_flash_chip() -> None:  # no corresponding response
    sure = parse(
        "This action is irreversible. Are you sure you want to erase the entire flash memory? To proceed, type ERASE. To cancel, type anything else."
    )
    if sure == ("ERASE"):
        send("L2x", "ERASE FLASH CHIP")
    else:
        print("Request cancelled, flash NOT erased.")


def request_log_one_record() -> None:
    send("L3x", "LOG ONE RECORD REQUEST")


def parse_log_one_record(r: str) -> None:
    print("LOG ONE RECORD RESPONSE")
    print("Pointer position:", ssq(r, 3, 8))


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


def parse_return_one_record(r: str) -> None:
    print("RETURN ONE RECORD RESPONSE")
    print("Date, day of week, time of recording:", ssq(r, 3, 22))
    print("Reading (mag/arcsec^2):", ssq(r, 23, 28))
    print("Temperature (°C):", ssq(r, 29, 36))
    print("Battery voltage ADC valueL:", ssq(r, 37, 39))


def request_battery_voltage() -> None:
    send("L5x", "BATTERY VOLTAGE REQUEST")


def parse_battery_voltage(r: str) -> None:
    print("BATTERY VOLTAGE RESPONSE")
    print("Internal voltage ADC:", ssq(r, 3, 5))
    adc = int(ssq(r, 3, 5))
    v = 2.048 + (3.3 * adc) / 256.0
    print("Converted voltage:", v)


def set_logging_trigger_mode() -> None:
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


def parse_logging_trigger_mode(r: str) -> None:
    print("LOGGING TRIGGER MODE RESPONSE", end=" ")
    match r[3]:
        case "0":
            print("0 = no automatic logging")
        case "1":
            print("1 = logging granularity in seconds and not powering down")
        case "2":
            print(
                "2 = logging granularity in minutes and powering down between recordings"
            )
        case "3":
            print(
                "3 = logging every 5 minutes on the 1/12th hour, and powering down between recordings"
            )
        case "4":
            print(
                "4 = logging every 10 minutes on the 1/6th hour, and powering down between recordings"
            )
        case "5":
            print(
                "5 = logging every 15 minutes on the 1/4 hour, and powering down between recordings"
            )
        case "6":
            print(
                "6 = logging every 30 minutes on the 1/2 hour, and powering down between recordings"
            )
        case "7":
            print(
                "7 = logging every hour on the hour, and powering down between recordings"
            )
        case _:
            print("INVALID RESPONSE")


def request_logging_interval_settings() -> None:
    send("LIx", "LOGGING INTERVAL SETTINGS REQUEST")


def parse_logging_interval_settings(r: str) -> None:
    print("LOGGING INTERVAL SETTINGS RESPONSE")
    print("EEPROM interval period (sec):", ssql(r, 3, 13))
    print("EEPROM interval period (min):", ssql(r, 15, 25))
    print("RAM interval period (sec):", ssql(r, 27, 37))
    print("RAM interval period (min):", ssql(r, 39, 49))
    print("RAM threshold value (mag/arcsec^2):", ssql(r, 51, 62))


def set_logging_interval_period() -> None:
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
    thresh = parse("Type mag/arcsec^2 value: ")
    try:
        value = float(thresh)
    except:
        print(f"{thresh} is not a valid float.")
        return
    zeroes_thresh = zero_fill_decimal(thresh, 8, 2)
    send(f"LPT{zeroes_thresh}x", "SET LOGGING THRESHOLD")


def request_clock_data() -> None:
    send("Lcx", "CLOCK DATA REQUEST")


def set_clock_data() -> None:
    data = parse("Type data here (lol finish this later): ")
    send(f"Lc{data}x", "SET CLOCK DATA")


def parse_clock_data(r: str) -> None:
    if r[1] == ("C"):
        print("Set command received")
    print("CLOCK DATA RESPONSE")
    print("Date, day of week, time:", ssq(r, 3, 21))


def put_unit_to_sleep() -> None:
    send("Lsx", "PUT UNIT TO SLEEP")


def request_alarm_data() -> None:
    send("Lax", "ALARM DATA REQUEST")


def parse_alarm_data(r: str) -> None:
    print("ALARM DATA RESPONSE")
    print("Address 07H, seconds:", ssq(r, 3, 6))
    print("Address 08H, minutes:", ssq(r, 7, 10))
    print("Address 09H, hours:", ssq(r, 11, 14))
    print("Address 0AH, day:", ssq(r, 15, 18))
    print("Address 0FH, control register:", ssq(r, 19, 21))


##### BOOTLOADER COMMANDS #####

# THESE AREN'T DOCUMENTED IN THE MANUAL, SO I'VE MADE THE EXECUTIVE DECISION NOT TO WORK ON THEM

# def reset_microcontroller():
#     send("0x19")#should be hex value 19, not string

# def intel_hex_firmware_upgrade_initiation():
#     send(":")


# TODO figure out date/time I/O


##### UTILITIES #####


def parse(text: str) -> str:
    r = input(text)
    exit_codes = ["exit", "quit"]
    for code in exit_codes:
        if code in r:
            print("EXIT CODE DETECTED\nPROGRAM TERMINATING")
            exit(0)
    return r


def zero_fill_decimal(value: str, whole_len: int, dec_len: int) -> str:
    whole = int(value)
    decimal = (int(value) - whole) * pow(10, dec_len)
    num = whole
    count = 0
    while num >= 10:
        num = num % 10
        count += 1
    hashes = "0" * (whole_len - count)
    return f"{hashes}{whole}.{decimal}"


def zero_fill(value: str, length: int) -> str:
    difference = length - len(value)
    if difference < 0:
        return "INCOMPATIBLE"
    elif difference == 0:
        return value
    zeroes = "0" * difference
    return f"{zeroes}{value}"


def ssq(s: str, first: int, last: int) -> str:  # subsequence
    output = s[first : last + 1]  # manual endpoints are all inclusive
    return output  # and it's easier to adapt in one place than in several dozen.


def ssql(
    s: str, first: int, last: int
) -> str:  # subsequence with left split to remove 0
    output = s[first : last + 1]
    return output.lstrip("0")


##### CONNECT TO DEVICE, SOMEHOW #####


def initialize_connection():
    pass


def ping_device():
    pass


def send(command: str, category: str) -> None:
    sure = parse(
        f"\nDo you wish to send the following {category} command (y/n): {command}   "
    )
    if "y" in sure:
        print("(simulated) command sent")
    else:
        print("command NOT sent")


def receive() -> str:
    return input("Type possible response code here")


##### SELECT SEND #####
def command_menu() -> None:
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
                    request_reading()
                case "2":
                    request_cal_info()
                case "3":
                    request_unit_info()
                case _:
                    print(f"{cat1} is not a valid selection.")
        case "2":
            send_arm_cal_command()
        case "3":
            print(
                "Commands:\n1 = request interval settings\n2 = set interval report period\n3 = set interval report threshold"
            )
            cat3 = parse(f"Select a command: ")
            match cat3:
                case "1":
                    request_interval_settings()
                case "2":
                    set_interval_report_period()
                case "3":
                    set_interval_report_threshold()
                case _:
                    print(f"{cat3} is not a valid selection.")
        case "4":
            print(
                "Commands:\n1 = set light offset\n2 = set light temperature\n3 = set dark period\n4 = set dark temperature"
            )
            cat4 = parse(f"Select a command: ")
            match cat4:
                case "1":
                    man_cal_set_light_offset()
                case "2":
                    man_cal_set_light_temperature()
                case "3":
                    man_cal_set_dark_period()
                case "4":
                    man_cal_set_dark_temperature()
                case _:
                    print(f"{cat4} is not a valid selection.")
        case "5":
            print(
                "Commands:\n1 = request simulation values\n2 = request simulation calculation"
            )
            cat5 = parse(f"Select a command: ")
            match cat5:
                case "1":
                    request_simulation_values()
                case "2":
                    request_simulation_calculation()
                case _:
                    print(f"{cat5} is not a valid selection.")
        case "6":
            print(
                "Commands:\n1 = request logging pointer\n2 = request logging one record\n3 = request return one record\n4 = set logging trigger mode\n5 = request logging trigger mode\n6 = request logging interval settings\n7 = set logging interval period\n8 = set logging threshold"
            )
            cat6 = parse(f"Select a command: ")
            match cat6:
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
                    print(f"{cat6} is not a valid selection.")
        case "7":
            print(
                "Commands:\n1 = request ID\n2 = erase flash chip\n3 = request battery voltage\n4 = request clock data\n5 = set clock data\n6 = put unit to sleep\n7 = request alarm data"
            )
            cat7 = parse(f"Select a command: ")
            match cat7:
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
                    print(f"{cat7} is not a valid selection.")
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


##### DRIVER CODE #####


def main():
    while True:
        command_menu()


main()
