# runs on host computer, parses messages as they come in


def parse_reading(r: str) -> None:
    """Parses a single reading of information

    Example request: rx
    Example message: r, 06.70m,0000022921Hz,0000000020c,0000000.000s, 039.4C

    Args:
        r (str): message from unit
    """
    result_lst = [
        "READING RESULTS",
        f"Light measurement: {ssq(r, 2, 8)}",
        f"        Frequency: {ssql(r, 10, 21)}",
        f"  Period (counts): {ssql(r, 23, 33)}",
        f" Period (seconds): {ssql(r, 35, 46)}",
        f"      Temperature: {ssq(r, 48, 54)}",
    ]
    if len(r) >= 63:
        result_lst.append(f"            Serial number: {ssq(r, 56, 63)}")
    result = "\n".join(result_lst)
    print(result)


def parse_cal_info(r: str) -> None:
    """Parses calibration information

    Example request: cx
    Example message: c,00000017.60m,0000000.000s, 039.4C,00000008.71m, 039.4C

    Args:
        r (str): message from unit
    """
    result_lst = [
        "CALIBRATION INFORMATION",
        f"            Light calibration offset: {ssql(r, 2, 13)}",
        f"             Dark calibration period: {ssql(r, 15, 26)}",
        f"Temperature during light calibration: {ssq(r, 28, 34)}",
        f"  Light sensor offset (manufacturer): {ssql(r, 36, 47)}",
        f" Temperature during dark calibration: {ssq(r, 49, 55)}",
    ]
    result = "\n".join(result_lst)
    print(result)


def parse_unit_information(r: str) -> None:
    """Parses calibration information

    Example request: ix
    Example message: i,00000002,00000003,00000001,00000413

    Args:
        r (str): message from unit
    """
    result_lst = [
        "UNIT INFORMATION",
        f"Protocol number: {ssq(r, 2, 9)}",
        f"   Model number: {ssq(r, 11, 18)}",
        f" Feature number: {ssq(r, 20, 27)}",
        f"  Serial number: {ssq(r, 29, 36)}",
    ]
    result = "\n".join(result_lst)
    print(result)


def parse_arm_cal_command(r: str) -> None:
    """Parses arm calibration commands

    Example request: zcalAx
    Example message: zAaL

    Args:
        r (str): message from unit
    """
    print("ARM CALIBRATION:")
    match r[1]:
        case "A":
            print("Light calibration ".upper(), end="")
        case "B":
            print("Dark calibration ".upper(), end="")
        case "x":
            print("All calibration modes ".upper(), end="")
        case _:
            print(f"INVALID RESPONSE {r[1]}", end="")

    match r[2]:
        case "a":
            print("Armed!".upper())
        case "d":
            print("Disarmed!".upper())
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


def parse_interval_settings(r: str) -> None:
    """Parses interval settings

    This is the response for Ix, set period, and set threshold. Ix will also produce rx responses at the intervals specified, which are not handled here.
    Example request: Ix
    Example request: p0000000360x
    Example message: I,0000000360s,0000000360s,00000017.60m,00000017.60m

    Args:
        r (str): message from unit
    """
    result_lst = [
        f"INTERVAL SETTINGS",
        f"Interval period EEPROM: {ssql(r, 2, 12)}",
        f"   Interval period RAM: {ssql(r, 14, 24)}",
        f"      Threshold EEPROM: {ssql(r, 26, 37)}",
        f"      Threshold EEPROM: {ssql(r, 26, 37)}",
        f"         Threshold RAM: {ssql(r, 39, 50)}",
    ]
    result = "\n".join(result_lst)
    print(result)


def parse_manual_cal(r: str) -> bool:
    """Parses manual calibration results

    Example request: zcal500000017.60x
    Example message: z,5,00000017.60m

    Args:
        r (str): message from unit
    """
    print("MANUAL CALIBRATION RESULTS")
    match r[2]:
        case "5":
            print("Light Magnitude:", ssql(r, 4, 15))
        case "6":
            print("Light Temperature:", ssql(r, 4, 9))
        case "7":
            print("Dark Period:", ssql(r, 4, 15))
        case "8":
            print("Dark Temperature:", ssql(r, 4, 9))
        case _:
            print("INVALID RESPONSE")
            return False
    return True


def parse_simulation_values(r: str) -> None:
    """Parses internal values

    Example request: sx
    Example message: s,0000000360c,0000000360f,0000000360t

    Args:
        r (str): message from unit
    """
    result_lst = [
        "INTERNAL SIMULATION VALUES",
        f"          Number of counts: {ssql(r, 2, 12)}",
        f"            Frequency (Hz): {ssql(r, 14, 24)}",
        f"           Temperature ADC: {ssql(r, 26, 37)}",
    ]
    print("\n".join(result_lst))


def parse_simulation_calculation(r: str) -> None:
    """Parses simulation calculation results

    Example request: S,0000000360,0000000360,0000000360x
    Example message: S,0000094000c,0000000000f,0000000245t,r, 18.04m,0000000000Hz,0000094000c,0000000.204s, 029.0C

    Args:
        r (str): message from unit
    """
    result_lst = [
        "SIMULATION VALUES",
        f"Number of counts: {ssql(r, 2, 12)}",
        f"  Frequency (Hz): {ssq(r, 14, 23)}",
        f" Temperature ADC: {ssql(r, 26, 36)}",
        "CALCULATED READINGS",
        f"Light measurement: {ssql(r, 40, 46)}",
        f"        Frequency: {ssq(r, 48, 59)}",
        f"  Period (counts): {ssql(r, 61, 71)}",
        f" Period (seconds): {ssql(r, 73, 84)}",
        f"      Temperature: {ssql(r, 86, 91)}",
    ]
    print("\n".join(result_lst))


##### DATA LOGGER COMMANDS #####
def sort_L(r: str) -> None:
    """Hands response to corresponding parser

    Args:
        r (str): message from unit
    """
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
        case "C":
            parse_clock_data(r)
        case "a":
            parse_alarm_data(r)
        case _:
            print(f"INVALID RESPONSE {r}")


def parse_ID(r: str) -> None:
    """Parses ID response

    Example request: L0x
    Example message: L0,000,000

    Args:
        r (str): message from unit
    """
    print("REPORT ID")
    print("Manufacturer ID:", ssq(r, 3, 5))
    print("      Device ID:", ssq(r, 7, 9))


def parse_logging_pointer(r: str) -> None:
    """Parses logging pointer

    Example request: L1x
    Example message: L1,000000

    Args:
        r (str): message from unit
    """
    print("LOGGING POINTER")
    print("Pointer position:", ssq(r, 3, 8))


def parse_log_one_record(r: str) -> None:
    """Parses logging record response

    Example request: L3x
    Example message: L3,000000

    Args:
        r (str): message from unit
    """
    print("LOG ONE RECORD RESPONSE")
    print("Pointer position:", ssq(r, 3, 8))


def parse_return_one_record(r: str) -> None:
    """Parses record result

    Example request: L40000000000x
    Example message: L4,11-01-06 5 11:51:00,10.44, 023.8C,234

    Args:
        r (str): message from unit
    """
    result_lst = [
        "RETURN ONE RECORD RESPONSE",
        f"               Date: {ssq(r,3,10)}",
        f"        Day of week: {r[12]}",
        f"               Time: {ssq(r,14,21)}",
        f"  Light measurement: {ssq(r, 23, 27)}",
        f"        Temperature: {ssq(r, 29, 35)}",
        f"Battery voltage ADC: {ssq(r, 37, 39)}",
    ]
    print("\n".join(result_lst))


def parse_battery_voltage(r: str) -> None:
    """Parses battery voltage

    Example request: L5x
    Example message: L5,238

    Args:
        r (str): message from unit
    """
    print("BATTERY VOLTAGE")
    print("Internal voltage ADC:", ssq(r, 3, 5))
    adc = int(ssq(r, 3, 5))
    v = 2.048 + (3.3 * adc) / 256.0
    print("Converted voltage:", v)


def parse_logging_trigger_mode(r: str) -> None:
    """Parses logging trigger responses

    Sent when trigger modes are read or set (LMx and LM_x commands)
    Example request: LMx
    Example message: LM,0

    Args:
        r (str): message from unit
    """
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
    """Parses logging interval

    Sent when intervals are read or set (LIx and LI_x commands)
    Example request: LIx
    Example message: LI,0000000360s,0000000005m,0000000121s,0000000004m,00000017.60m

    Args:
        r (str): message from unit
    """
    result_lst = [
        "LOGGING INTERVAL SETTINGS",
        f"EEPROM interval period (sec): {ssql(r, 3, 13)}",
        f"EEPROM interval period (min): {ssql(r, 15, 25)}",
        f"   RAM interval period (sec): {ssql(r, 27, 37)}",
        f"   RAM interval period (min): {ssql(r, 39, 49)}",
        f"   RAM light threshold value: {ssql(r, 51, 62)}",
    ]
    print("\n".join(result_lst))


def parse_clock_data(r: str) -> None:
    """Parses clock data

    Send when intervals are read or set (LCx and Lcx commands)
    Example request: LCx
    Example message: Lc,11-01-06 5 11:51:00
    Example message: LC,11-01-06 5 11:51:00

    Args:
        r (str): message from unit
    """
    print("CLOCK DATA RESPONSE")
    if r[1] == ("C"):
        print("Set command received")
    result_lst = [
        f"       Date: {ssq(r,3,10)}",
        f"Day of week: {r[12]}",
        f"       Time: {ssq(r,14,21)}",
    ]
    print("\n".join(result_lst))


def parse_alarm_data(r: str) -> None:
    """Parses alarm data

    Example request: Lax
    Example message: La,000,128,128,128,001

    Args:
        r (str): message from unit
    """
    result_lst = [
        "ALARM DATA RESPONSE",
        f"         Address 07H seconds: {ssq(r, 3, 5)}",
        f"         Address 08H minutes: {ssq(r, 7, 9)}",
        f"           Address 09H hours: {ssq(r,11,13)}",
        f"             Address 0AH day: {ssq(r,15,17)}",
        f"Address 0FH control register: {ssq(r,19,20)}",
    ]
    print("\n".join(result_lst))


##### UTILITIES #####
def ssq(s: str, first: int, last: int) -> str:
    """Get subsequence of string with inclusive endpoints. Most interval values in the manual are listed this way, so this makes things much easier to code. Also strips whitespace for nicer printing.

    Args:
        s (str): string to subsequence
        first (int): start index (inclusive)
        last (int): end index (inclusive)

    Returns:
        str: subsequence, with whitespace stripped
    """
    output = s[first : last + 1].strip()
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
    return output.lstrip("0").strip()


def sort_response(r: str) -> None:
    """Sorts all messages from machine to the corresponding parser

    Args:
        r (str): message from sensor unit
    """
    match r[0]:
        case "r":
            parse_reading(r)
        case "c":
            parse_cal_info(r)
        case "z":
            if r[1] == (","):
                parse_manual_cal(r)
            else:
                parse_arm_cal_command(r)
        case "i":
            parse_unit_information(r)
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
