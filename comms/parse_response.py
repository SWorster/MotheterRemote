"""
Runs on host computer, parses messages as they come in. Can be called using sort_response(str), but can't be run as main.
"""


def _parse_reading(r: str) -> str:
    """Parses a single reading of information

    Example request: rx
    Example message: r, 06.70m,0000022921Hz,0000000020c,0000000.000s, 039.4C

    Args:
        r (str): message from unit
    """
    lst = [
        "READING RESULTS",
        f"Light measurement: {_ssq(r, 2, 8)}",
        f"        Frequency: {_ssql(r, 10, 21)}",
        f"  Period (counts): {_ssq(r, 23, 33)}",
        f" Period (seconds): {_ssq(r, 35, 46)}",
        f"      Temperature: {_ssql(r, 48, 54)}",
    ]
    if len(r) >= 63:
        lst.append(f"    Serial number: {_ssq(r, 56, 63)}")
    return "\n".join(lst)


def _parse_cal_info(r: str) -> str:
    """Parses calibration information

    Example request: cx
    Example message: c,00000017.60m,0000000.000s, 039.4C,00000008.71m, 039.4C

    Args:
        r (str): message from unit
    """
    lst = [
        "CALIBRATION INFORMATION",
        f"            Light calibration offset: {_ssql(r, 2, 13)}",
        f"             Dark calibration period: {_ssql(r, 15, 26)}",
        f"Temperature during light calibration: {_ssq(r, 28, 34)}",
        f"  Light sensor offset (manufacturer): {_ssql(r, 36, 47)}",
        f" Temperature during dark calibration: {_ssq(r, 49, 55)}",
    ]
    return "\n".join(lst)


def _parse_unit_information(r: str) -> str:
    """Parses calibration information

    Example request: ix
    Example message: i,00000002,00000003,00000001,00000413

    Args:
        r (str): message from unit
    """
    lst = [
        "UNIT INFORMATION",
        f"Protocol number: {_ssq(r, 2, 9)}",
        f"   Model number: {_ssq(r, 11, 18)}",
        f" Feature number: {_ssq(r, 20, 27)}",
        f"  Serial number: {_ssq(r, 29, 36)}",
    ]
    return "\n".join(lst)


def _parse_arm_cal_command(r: str) -> str:
    """Parses arm calibration commands


    Example request: zcalAx
    Example message: zAaL

    Args:
        r (str): message from unit
    """
    lst = ["ARM CALIBRATION:"]
    match r[1]:
        case "A":
            lst.append("Light calibration ".upper())
        case "B":
            lst.append("Dark calibration ".upper())
        case "x":
            lst.append("All calibration modes ".upper())
        case _:
            lst.append(f"INVALID RESPONSE {r[1]}")

    match r[2]:
        case "a":
            lst[1] = lst[1] + " ARMED!"
        case "d":
            lst[1] = lst[1] + " DISARMED!"
        case _:
            lst[1] = lst[1] + f"INVALID RESPONSE {r[2]}"

    match r[3]:
        case "L":
            lst.append(
                "LOCKED. Wait for unlock before calibrating after Arm command, firmware upgrades are disabled."
            )
        case "U":
            lst.append(
                "UNLOCKED. Calibrate immediately after Arm command, Enable firmware upgrade."
            )
        case _:
            lst.append(f"INVALID RESPONSE {r[3]}")
    return "\n".join(lst)


def _parse_interval_settings(r: str) -> str:
    """Parses interval settings

    This is the response for Ix, set period, and set threshold. Ix will also produce rx responses at the intervals specified, which are not handled here.
    Example request: Ix
    Example request: p0000000360x
    Example message: I,0000000360s,0000000360s,00000017.60m,00000017.60m

    Args:
        r (str): message from unit
    """
    lst = [
        f"INTERVAL SETTINGS",
        f"Interval period EEPROM: {_ssql(r, 2, 12)}",
        f"   Interval period RAM: {_ssql(r, 14, 24)}",
        f"      Threshold EEPROM: {_ssql(r, 26, 37)}",
        f"      Threshold EEPROM: {_ssql(r, 26, 37)}",
        f"         Threshold RAM: {_ssql(r, 39, 50)}",
    ]
    return "\n".join(lst)


def _parse_manual_cal(r: str) -> str:
    """Parses manual calibration results

    Example request: zcal500000017.60x
    Example message: z,5,00000017.60m

    Args:
        r (str): message from unit
    """
    lst = ["MANUAL CALIBRATION RESULTS"]
    match r[2]:
        case "5":
            lst.append(f"Light Magnitude: {_ssql(r, 4, 15)}")
        case "6":
            lst.append(f"Light Temperature: {_ssql(r, 4, 9)}")
        case "7":
            lst.append(f"Dark Period: {_ssql(r, 4, 15)}")
        case "8":
            lst.append(f"Dark Temperature: {_ssql(r, 4, 9)}")
        case _:
            lst.append("INVALID RESPONSE")
    return "\n".join(lst)


def _parse_simulation_values(r: str) -> str:
    """Parses internal values

    Example request: sx
    Example message: s,0000000360c,0000000360f,0000000360t

    Args:
        r (str): message from unit
    """
    lst = [
        "INTERNAL SIMULATION VALUES",
        f"          Number of counts: {_ssql(r, 2, 12)}",
        f"            Frequency (Hz): {_ssql(r, 14, 24)}",
        f"           Temperature ADC: {_ssql(r, 26, 37)}",
    ]
    return "\n".join(lst)


def _parse_simulation_calculation(r: str) -> str:
    """Parses simulation calculation results

    Example request: S,0000000360,0000000360,0000000360x
    Example message: S,0000094000c,0000000000f,0000000245t,r, 18.04m,0000000000Hz,0000094000c,0000000.204s, 029.0C

    Args:
        r (str): message from unit
    """
    lst = [
        "SIMULATION VALUES",
        f"Number of counts: {_ssql(r, 2, 12)}",
        f"  Frequency (Hz): {_ssq(r, 14, 23)}",
        f" Temperature ADC: {_ssql(r, 26, 36)}",
        "CALCULATED READINGS",
        f"Light measurement: {_ssql(r, 40, 46)}",
        f"        Frequency: {_ssq(r, 48, 59)}",
        f"  Period (counts): {_ssql(r, 61, 71)}",
        f" Period (seconds): {_ssql(r, 73, 84)}",
        f"      Temperature: {_ssql(r, 86, 91)}",
    ]
    return "\n".join(lst)


##### DATA LOGGER COMMANDS #####
def _sort_L(r: str) -> str:
    """Hands response to corresponding parser

    Args:
        r (str): message from unit
    """
    match r[1]:
        case "0":
            return _parse_ID(r)
        case "1":
            return _parse_logging_pointer(r)
        case "3":
            return _parse_log_one_record(r)
        case "4":
            return _parse_return_one_record(r)
        case "5":
            return _parse_battery_voltage(r)
        case "M":
            return _parse_logging_trigger_mode(r)
        case "I":
            return _parse_logging_interval_settings(r)
        case "c":
            return _parse_clock_data(r)
        case "C":
            return _parse_clock_data(r)
        case "a":
            return _parse_alarm_data(r)
        case _:
            return f"INVALID RESPONSE {r}"


def _parse_ID(r: str) -> str:
    """Parses ID response

    Example request: L0x
    Example message: L0,000,000

    Args:
        r (str): message from unit
    """
    lst = [
        "REPORT ID",
        f"Manufacturer ID: {_ssq(r, 3, 5)}",
        f"      Device ID: {_ssq(r, 7, 9)}",
    ]
    return "\n".join(lst)


def _parse_logging_pointer(r: str) -> str:
    """Parses logging pointer

    Example request: L1x
    Example message: L1,000000

    Args:
        r (str): message from unit
    """
    return f"LOGGING POINTER\nPointer position: {_ssq(r, 3, 8)}"


def _parse_log_one_record(r: str) -> str:
    """Parses logging record response

    Example request: L3x
    Example message: L3,000000

    Args:
        r (str): message from unit
    """
    return f"LOG ONE RECORD RESPONSE\nPointer position: {_ssq(r, 3, 8)}"


def _parse_return_one_record(r: str) -> str:
    """Parses record result

    Example request: L40000000000x
    Example message: L4,11-01-06 5 11:51:00,10.44, 023.8C,234

    Args:
        r (str): message from unit
    """
    lst = [
        "RETURN ONE RECORD RESPONSE",
        f"               Date: {_ssq(r,3,10)}",
        f"        Day of week: {r[12]}",
        f"               Time: {_ssq(r,14,21)}",
        f"  Light measurement: {_ssq(r, 23, 27)}",
        f"        Temperature: {_ssq(r, 29, 35)}",
        f"Battery voltage ADC: {_ssq(r, 37, 39)}",
    ]
    return "\n".join(lst)


def _parse_battery_voltage(r: str) -> str:
    """Parses battery voltage

    Example request: L5x
    Example message: L5,238

    Args:
        r (str): message from unit
    """
    adc = int(_ssq(r, 3, 5))
    v = 2.048 + (3.3 * adc) / 256.0
    lst = ["BATTERY VOLTAGE", f"Internal voltage ADC: {adc}", f"Converted voltage: {v}"]
    return "\n".join(lst)


def _parse_logging_trigger_mode(r: str) -> str:
    """Parses logging trigger responses

    Sent when trigger modes are read or set (LMx and LM_x commands)
    Example request: LMx
    Example message: LM,0

    Args:
        r (str): message from unit
    """
    lst = ["LOGGING TRIGGER MODE RESPONSE"]
    match r[3]:
        case "0":
            lst.append("0 = no automatic logging")
        case "1":
            lst.append("1 = logging granularity in seconds and not powering down")
        case "2":
            lst.append(
                "2 = logging granularity in minutes and powering down between recordings"
            )
        case "3":
            lst.append(
                "3 = logging every 5 minutes on the 1/12th hour, and powering down between recordings"
            )
        case "4":
            lst.append(
                "4 = logging every 10 minutes on the 1/6th hour, and powering down between recordings"
            )
        case "5":
            lst.append(
                "5 = logging every 15 minutes on the 1/4 hour, and powering down between recordings"
            )
        case "6":
            lst.append(
                "6 = logging every 30 minutes on the 1/2 hour, and powering down between recordings"
            )
        case "7":
            lst.append(
                "7 = logging every hour on the hour, and powering down between recordings"
            )
        case _:
            lst.append("INVALID RESPONSE")
    return " ".join(lst)


def _parse_logging_interval_settings(r: str) -> str:
    """Parses logging interval

    Sent when intervals are read or set (LIx and LI_x commands)
    Example request: LIx
    Example message: LI,0000000360s,0000000005m,0000000121s,0000000004m,00000017.60m

    Args:
        r (str): message from unit
    """
    lst = [
        "LOGGING INTERVAL SETTINGS",
        f"EEPROM interval period (sec): {_ssql(r, 3, 13)}",
        f"EEPROM interval period (min): {_ssql(r, 15, 25)}",
        f"   RAM interval period (sec): {_ssql(r, 27, 37)}",
        f"   RAM interval period (min): {_ssql(r, 39, 49)}",
        f"   RAM light threshold value: {_ssql(r, 51, 62)}",
    ]
    return "\n".join(lst)


def _parse_clock_data(r: str) -> str:
    """Parses clock data

    Send when intervals are read or set (LCx and Lcx commands)
    Example request: LCx
    Example message: Lc,11-01-06 5 11:51:00
    Example message: LC,11-01-06 5 11:51:00

    Args:
        r (str): message from unit
    """
    head = "CLOCK DATA RESPONSE"
    if r[1] == ("C"):
        head = head + "\nSet command received"
    lst = [
        head,
        f"       Date: {_ssq(r,3,10)}",
        f"Day of week: {r[12]}",
        f"       Time: {_ssq(r,14,21)}",
    ]
    return "\n".join(lst)


def _parse_alarm_data(r: str) -> str:
    """Parses alarm data

    Example request: Lax
    Example message: La,000,128,128,128,001

    Args:
        r (str): message from unit
    """
    lst = [
        "ALARM DATA RESPONSE",
        f"         Address 07H seconds: {_ssq(r, 3, 5)}",
        f"         Address 08H minutes: {_ssq(r, 7, 9)}",
        f"           Address 09H hours: {_ssq(r,11,13)}",
        f"             Address 0AH day: {_ssq(r,15,17)}",
        f"Address 0FH control register: {_ssq(r,19,20)}",
    ]
    return "\n".join(lst)


##### UTILITIES #####
def _ssq(s: str, first: int, last: int) -> str:
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
    return output.lstrip("0").strip()


def sort_response(r: str) -> str:
    """Sorts all messages from machine to the corresponding parser

    Args:
        r (str): message from sensor unit
    """
    if r == "":
        return ""
    match r[0]:
        case "r":
            return _parse_reading(r)
        case "c":
            return _parse_cal_info(r)
        case "z":
            if r[1] == (","):
                return _parse_manual_cal(r)
            else:
                return _parse_arm_cal_command(r)
        case "i":
            return _parse_unit_information(r)
        case "I":
            return _parse_interval_settings(r)
        case "s":
            return _parse_simulation_values(r)
        case "S":
            return _parse_simulation_calculation(r)
        case "L":
            return _sort_L(r)
        case _:
            return r
