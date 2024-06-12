##### SIMPLE READINGS AND INFO REQUESTS #####
def parse_reading(r: str) -> None:
    print("READING RESULT")
    print("Current light measurement:", ssq(r, 2, 8))
    print("Frequency:", ssql(r, 10, 21))
    print("Period (counts):", ssql(r, 22, 33))
    print("Period (seconds)", ssql(r, 35, 46))
    print("Temperature:", ssq(r, 48, 54))
    if len(r) >= 63:
        print("Serial number:", ssql(r, 55, 63))


def parse_cal_info(r: str) -> None:
    print("CALIBRATION INFORMATION RESULT")
    print("Light calibration offset:", ssql(r, 2, 13))
    print("Dark calibration period:", ssql(r, 15, 26))
    print("Temperature during light calibration:", ssq(r, 28, 34))
    print("Light sensor offset (manufacturer):", ssql(r, 36, 47))
    print("Temperature during dark calibration:", ssq(r, 49, 55))


def parse_unit_information(r: str) -> None:
    print("UNIT INFORMATION RESULT")
    print("Protocol number:", ssq(r, 2, 9))
    print("Model number:", ssq(r, 11, 18))
    print("Feature number:", ssq(r, 20, 27))
    print("Serial number:", ssq(r, 29, 36))


##### ARM/DISARM CALIBRATIONS #####
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
# this is the response for Ix, set period, and set threshold
def parse_interval_settings(r: str) -> None:
    print("INTERVAL SETTINGS RESPONSE")
    print("Interval period EEPROM:", ssql(r, 2, 12))
    print("Interval period RAM:", ssql(r, 14, 24))
    print("Threshold EEPROM:", ssql(r, 26, 37))
    print("Threshold RAM:", ssql(r, 39, 50))


##### MANUAL CALIBRATION #####
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
def parse_simulation_values(r: str) -> None:
    print("INTERNAL SIMULATION VALUES RESPONSE")
    print("Number of counts:", ssql(r, 2, 12))
    print("Frequency (Hz):", ssql(r, 14, 24))
    print("Temperature ADC (°C):", ssql(r, 26, 37))


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


def parse_ID(r: str) -> None:
    print("REPORT ID RESPONSE")
    print("Manufacturer ID:", ssq(r, 3, 5))
    print("Device ID:", ssq(r, 6, 8))


def parse_logging_pointer(r: str) -> None:
    print("LOGGING POINTER RESPONSE")
    print("Pointer position:", ssq(r, 3, 8))


def parse_log_one_record(r: str) -> None:
    print("LOG ONE RECORD RESPONSE")
    print("Pointer position:", ssq(r, 3, 8))


def parse_return_one_record(r: str) -> None:
    print("RETURN ONE RECORD RESPONSE")
    print("Date, day of week, time of recording:", ssq(r, 3, 22))
    print("Reading (mag/arcsec^2):", ssq(r, 23, 28))
    print("Temperature (°C):", ssq(r, 29, 36))
    print("Battery voltage ADC valueL:", ssq(r, 37, 39))


def parse_battery_voltage(r: str) -> None:
    print("BATTERY VOLTAGE RESPONSE")
    print("Internal voltage ADC:", ssq(r, 3, 5))
    adc = int(ssq(r, 3, 5))
    v = 2.048 + (3.3 * adc) / 256.0
    print("Converted voltage:", v)


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


def parse_logging_interval_settings(r: str) -> None:
    print("LOGGING INTERVAL SETTINGS RESPONSE")
    print("EEPROM interval period (sec):", ssql(r, 3, 13))
    print("EEPROM interval period (min):", ssql(r, 15, 25))
    print("RAM interval period (sec):", ssql(r, 27, 37))
    print("RAM interval period (min):", ssql(r, 39, 49))
    print("RAM threshold value (mag/arcsec^2):", ssql(r, 51, 62))


def parse_clock_data(r: str) -> None:
    if r[1] == ("C"):
        print("Set command received")
    print("CLOCK DATA RESPONSE")
    print("Date, day of week, time:", ssq(r, 3, 21))


def parse_alarm_data(r: str) -> None:
    print("ALARM DATA RESPONSE")
    print("Address 07H, seconds:", ssq(r, 3, 6))
    print("Address 08H, minutes:", ssq(r, 7, 10))
    print("Address 09H, hours:", ssq(r, 11, 14))
    print("Address 0AH, day:", ssq(r, 15, 18))
    print("Address 0FH, control register:", ssq(r, 19, 21))


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


##### DRIVER CODE #####
def main():
    while True:
        response = input()
        sort_response(response)


main()
