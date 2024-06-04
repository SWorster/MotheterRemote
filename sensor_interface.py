import re

##### SIMPLE READINGS AND INFO REQUESTS #####
def request_reading():
    send("rx","REQUEST READING")

def parse_reading(r):
    print("READING RESULT")
    print("Current light measurement:", ssq(r,2,8))
    print("Frequency:",ssql(r,10,21))
    print("Period (counts):",ssql(r,22,33))
    print("Period (seconds)",ssql(r,35,46))
    print("Temperature:", ssq(r,48,54))
    if len(r)>=63:
        print("Serial number:",ssql(r,55,63))

def request_cal_info():
    send("cx","REQUEST CALIBRATION INFORMATION")

def parse_cal_info(r):
    print("CALIBRATION INFORMATION RESULT")
    print("Light calibration offset:", ssql(r,2,13))
    print("Dark calibraiton period:", ssql(r,15,26))
    print("Temperature during light calibration:", ssq(r,28,34))
    print("Light sensor offset (manufacutrer):", ssql(r,36,47))
    print("Temperature during dark calibration:", ssq(r,49,55))

def request_unit_info():
    send("ix","REQUEST UNIT INFORMATION")

def parse_unit_information(r):
    print("UNIT INFORMATION RESULT")
    print("Protocol number:",ssq(r,2,9))
    print("Model number:",ssq(r,11,18))
    print("Feature number:",ssq(r,20,27))
    print("Serial number:",ssq(r,29,36))

##### ARM/DISARM CALIBRATIONS #####

def send_arm_cal_command():
    mode = parse("a = Arm LIGHT calibration\nb = Arm DARK calibration\nd = DISarm calibration")
    match mode.lower():
        case "a":
            send("zcalAx","ARM LIGHT CALIBRATION")
        case "b":
            send("zcalBx","ARM DARK CALIBRATION")
        case "d":
            send("zcalDx","DISARM CALIBRATION")
        case _:
            print(f"INVALID MODE {mode}, must be a/b/d")

def parse_arm_cal_command(r):
    print("ARM CALIBRATION RESULT")
    match r[1]:
        case "A":
            print("Light calibration",end=" ")
        case "B":
            print("Dark calibration",end=" ")
        case "x":
            print("All calibration modes",end=" ")
        case _:
            print(f"INVALID RESPONSE {r[1]}",end=" ")

    match r[2]:
        case "a":
            print("Armed!")
        case "d":
            print("Disarmed!")
        case _:
            print(f"INVALID RESPONSE {r[2]}",end="")

    match r[3]:
        case "L":
            print("LOCKED. Wait for unlock before calibrating after Arm command, firmware upgrades are disabled.")
        case "U":
            print("UNLOCKED. Calibrate immediately after Arm command, Enable firmware upgrade.")
        case _:
            print(f"INVALID RESPONSE {r[3]}")

##### INTERVALS AND THRESHOLDS #####

def request_interval_settings():
    send("Ix","INTERVAL SETTINGS REQUEST")
    # two responses: reading w/ serial, and interval setting response

def set_interval_report_period():
    print("This command sets the interval report period in the RAM by default.\nThis change will not persist through a reboot.\nYou can choose to set this interval in the EEPROM so that the system will boot with this new interval.\n However, the EEPROM only has 1 million erase/write cycles, so please test your settings with just RAM before committing to EEPROM.")
    boot = parse("To write to EEPROM and RAM, type EEPROM. To write to RAM only (recommended), type anything else and press enter.\nMode:")
    if boot==("EEPROM"):
        boot = "P"
    else:
        boot = "p"

    interval = parse("Reporting interval (as integer only): ")
    value = "".join(re.findall(r'\d+', interval))
    try:
        int(value)
    except:
        print(f"{value} is not a valid integer.")
        return

    unit = parse("Unit for time value - s=seconds, m=minutes, h=hours: ")
    if "m" in unit:
        time=time*60
    elif "h" in unit:
        time=time*3600
    elif "s" not in unit:
        print("Assuming default (seconds)")
    with_zeroes = zero_fill(10,value)
    send(f"{boot}{with_zeroes}{time}x","SET INTERVAL REPORT PERIOD")

def set_interval_report_threshold():
    print("This command sets the interval report threshold in the RAM by default.\nThis change will not persist through a reboot.\nYou can choose to set this interval in the EEPROM so that the system will boot with this new interval.\n However, the EEPROM only has 1 million erase/write cycles, so please test your settings with just RAM before committing to EEPROM.")
    boot = parse("To write to EEPROM and RAM, type EEPROM. To write to RAM only (recommended), type anything else and press enter.\nMode:")
    if boot==("EEPROM"):
        boot = "P"
    else:
        boot = "p"

    threshold = parse("Reporting threshold in mag/arcsec^2: ")
    value = "".join(re.findall(r'[\d]*[.][\d]+', threshold))
    try:
        float(value)
    except:
        print(f"{value} is not a valid float.")
        return

    with_zeroes=zero_fill_decimal(8,2,threshold)
    send(f"{boot}{with_zeroes}x","SET INTERVAL REPORT THRESHOLD")

def parse_interval_settings(r): # this is the response for Ix, set period, and set threshold
    print("INTERVAL SETTINGS RESPONSE")
    print("Interval period EEPROM:",ssql(r,2,12))
    print("Interval period RAM:",ssql(r,14,24))
    print("Threshold EEPROM:",ssql(r,26,37))
    print("Threshold RAM:",ssql(r,39,50))

##### MANUAL CALIBRATION #####

def man_cal_set_light_offset():
    value = parse("Type offset value in mag/arcsec^2 (float): ")
    try:
        float(value)
    except:
        print(f"{value} is not a valid float.")
        return
    hashes=zero_fill_decimal(8,2,value)
    send(f"zcal5{hashes}x","MANUAL CALIBRATION - SET LIGHT OFFSET")

def man_cal_set_light_temperature():
    value = parse("Type temperature value in °C (float): ")
    try:
        float(value)
    except:
        print(f"{value} is not a valid float.")
        return
    hashes=zero_fill_decimal(3,1,value)
    send(f"zcal6{hashes}x","MANUAL CALIBRATION - SET LIGHT TEMPERATURE")

def man_cal_set_dark_period():
    value = parse("Type period value in seconds (float): ")
    try:
        float(value)
    except:
        print(f"{value} is not a valid float.")
        return
    hashes=zero_fill_decimal(7,3,value)
    send(f"zcal7{hashes}x","MANUAL CALIBRATION - SET DARK PERIOD")

def man_cal_set_dark_temperature():
    value = parse("Type temperature value in °C (float): ")
    try:
        float(value)
    except:
        print(f"{value} is not a valid float.")
        return
    hashes=zero_fill_decimal(3,1,value)
    send(f"zcal8{hashes}x","MANUAL CALIBRATION - SET DARK TEMPERATURE")

def parse_manual_cal(r)->bool:
    print("MANUAL CALIBRATION RESULTS")
    match r[2]:
        case "5":
            print("Light Magnitude (mag/arcsec^2):", ssql(r,4,15))
        case "6":
            print("Light Temperature (°C):", ssql(r,4,9))
        case "7":
            print("Dark Period (sec):", ssql(r,4,15))
        case "8":
            print("Dark Temperature (°C):", ssql(r,4,9))
        case _:
            print("INVALID RESPONSE")
            return False
    return True

##### SIMULATION COMMANDS #####

def request_simulation_values():
    send("sx","REQUEST INTERNAL SIMULATION VALUES")

def parse_simulation_values(r):
    print("INTERNAL SIMULATION VALUES RESPONSE")
    print("Number of counts:",ssql(r,2,12))
    print("Frequency (Hz):",ssql(r,14,24))
    print("Temperature ADC (°C):",ssql(r,26,37))

def request_simulation_calculation():
    counts = parse("Number of simulated counts: ")
    frequency = parse("Frequency in Hz: ")
    temp = parse("Temperature ADC in °C: ")
    count_zeroes = zero_fill(10,counts)
    freq_zeroes = zero_fill(10,frequency)
    temp_zeroes=zero_fill(10,temp)
    send(f"S,{count_zeroes},{freq_zeroes},{temp_zeroes}x","SIMULATE INTERNAL CALCULATION")

def parse_simulation_calculation(r):
    print("SIMULATION CALCULATION RESPONSE")
    print("Number of counts:",ssql(r,2,13))
    print("Frequency (Hz):",ssql(r,14,25))
    print("Temperature ADC (°C):",ssql(r,26,37))
    print("Calculated mpsas:",ssql(r,40,47))
    print("Frequency used for calculation (Hz):",ssql(r,48,60))
    print("Counts used for calculation:",ssql(r,61,72))
    print("Calculated period from counts:",ssql(r,73,85))
    print("Temperature used for calculation (°C):",ssql(r,86,92))

##### SORT RESPONSES #####
def sort_response(r):
    match r[0]:
        case "r":
            parse_reading(r)
        case "c":
            parse_cal_info(r)
        case "z":
            if r[1]==(","):
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

##### DATA LOGGER COMMANDS #####
def sort_L(r):
    match r[1]:
        case "0":
            parse_ID(r)
        case "1":
            parse_logging_pointer(r)
        case "2":
            erase_flash_chip(r)
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

def request_ID():
    send("L0x","REPORT ID REQUEST")

def parse_ID(r):
    print("REPORT ID RESPONSE")
    print("Manufacturer ID:",ssq(r,3,5))
    print("Device ID:",ssq(r,6,8))

def request_logging_pointer():
    send("L1x","LOGGING POINTER REQUEST")

def parse_logging_pointer(r):
    print("LOGGING POINTER RESPONSE")
    print("Pointer position:",ssq(r,3,8))

def erase_flash_chip(): #no corresponding response
    sure = parse("This action is irreversible. Are you sure you want to erase the entire flash memory? To proceed, type ERASE. To cancel, type anything else.")
    if sure==("ERASE"):
        send("L2x","ERASE FLASH CHIP")
    else:
        print("Request cancelled, flash NOT erased.")

def request_log_one_record():
    send("L3x","LOG ONE RECORD REQUEST")

def parse_log_one_record(r):
    print("LOG ONE RECORD RESPONSE")
    print("Pointer position:",ssq(r,3,8))

def request_return_one_record():
    pointer = parse("Type pointer position of record to return: ")
    try:
        value = int(pointer)
    except:
        print(f"{pointer} is not a valid integer.")
        return
    if len(pointer)<10:
        print(f"{pointer} must be between 0 and 9999999999 (ten digits).")
        return
    if value<0:
        print(f"{pointer} must be between 0 and 9999999999 (ten digits).")
        return
    pt = zero_fill(10,pointer)
    send(f"L4{pt}x","RETURN ONE RECORD REQUEST")

def parse_return_one_record(r):
    print("RETURN ONE RECORD RESPONSE")
    print("Date, day of week, time of recording:",ssq(r,3,22))
    print("Reading (mag/arcsec^2):",ssq(r,23,28))
    print("Temperature (°C):",ssq(r,29,36))
    print("Battery voltage ADC valueL:",ssq(r,37,39))

def request_battery_voltage():
    send("L5x","BATTERY VOLTAGE REQUEST")

def parse_battery_voltage(r):
    print("BATTERY VOLTAGE RESPONSE")
    print("Internal voltage ADC:",ssq(r,3,5))
    adc = int(ssq(r,3,5))
    v = 2.048+(3.3*adc)/256.0
    print("Converted voltage:",v)

def set_logging_trigger_mode():
    print("0 = no automatic logging")
    print("1 = logging granularity in seconds and not powering down")
    print("2 = logging granularity in minutes and powering down between recordings")
    print("3 = logging every 5 minutes on the 1/12th hour, and powering down between recordings")
    print("4 = logging every 10 minutes on the 1/6th hour, and powering down between recordings")
    print("5 = logging every 15 minutes on the 1/4 hour, and powering down between recordings")
    print("6 = logging every 30 minutes on the 1/2 hour, and powering down between recordings")
    print("7 = logging every hour on the hour, and powering down between recordings")
    mode = parse(f"Select mode from above options")
    if 0<=int(mode)<=7:
        send(f"LM{mode}x",f"SET LOGGING TRIGGER MODE {mode}")
    else:
        print("Invalid mode entered")

def request_logging_trigger_mode():
    send("Lmx","LOGGING TRIGGER MODE REQUEST")

def parse_logging_trigger_mode(r):
    print("LOGGING TRIGGER MODE RESPONSE",end=" ")
    match r[3]:
        case "0":
            print("0 = no automatic logging")
        case "1":
            print("1 = logging granularity in seconds and not powering down")
        case "2":
            print("2 = logging granularity in minutes and powering down between recordings")
        case "3":
            print("3 = logging every 5 minutes on the 1/12th hour, and powering down between recordings")
        case "4":
            print("4 = logging every 10 minutes on the 1/6th hour, and powering down between recordings")
        case "5":
            print("5 = logging every 15 minutes on the 1/4 hour, and powering down between recordings")
        case "6":
            print("6 = logging every 30 minutes on the 1/2 hour, and powering down between recordings")
        case "7":
            print("7 = logging every hour on the hour, and powering down between recordings")
        case _:
            print("INVALID RESPONSE")

def request_logging_interval_settings():
    send("LIx","LOGGING INTERVAL SETTINGS REQUEST")

def parse_logging_interval_settings(r):
    print("LOGGING INTERVAL SETTINGS RESPONSE")
    print("EEPROM interval period (sec):",ssql(r,3,13))
    print("EEPROM interval period (min):",ssql(r,15,25))
    print("RAM interval period (sec):",ssql(r,27,37))
    print("RAM interval period (min):",ssql(r,39,49))
    print("RAM threshold value (mag/arcsec^2):",ssql(r,51,62))

def set_logging_interval_period():
    unit = parse("Type unit for reporting interval (s=seconds m=minutes): ")
    time = parse("Type time value (integer only): ")
    try:
        value = int(time)
    except:
        print(f"{value} is not a valid integer.")
        return
    if value>0 and value <9999999999:
        ztime = zero_fill(5,time)
        if "m" in unit:
            send(f"LPM{ztime}x","SET LOGGING INTERVAL REPORTING PERIOD MINUTES")
        elif "s" in unit:
            send(f"LPS{ztime}x","SET LOGGING INTERVAL REPORTING PERIOD SECONDS")
        else:
            print("Invalid mode entry: must be m or s")
    else:
        print(f"{value} must be an integer between 0 and 9999999999 (10 digits).")

def set_logging_threshold():
    thresh = parse("Type mag/arcsec^2 value: ")
    try:
        value = float(thresh)
    except:
        print(f"{value} is not a valid float.")
        return
    zthresh = zero_fill_decimal(8,2,thresh)
    send(f"LPT{zthresh}x","SET LOGGING THRESHOLD")

def request_clock_data():
    send("Lcx","CLOCK DATA REQUEST")

def set_clock_data():
    data = parse("Type data here (lol finish this later): ")
    send(f"Lc{data}x", "SET CLOCK DATA")

def parse_clock_data(r):
    if r[1]==("C"):
        print("Set command received")
    print("CLOCK DATA RESPONSE")
    print("Date, day of week, time:",ssq(r,3,21))

def put_unit_to_sleep():
    send("Lsx","PUT UNIT TO SLEEP")

def request_alarm_data():
    send("Lax","ALARM DATA REQUEST")

def parse_alarm_data(r):
    print("ALARM DATA RESPONSE")
    print("Address 07H, seconds:",ssq(r,3,6))
    print("Address 08H, minutes:",ssq(r,7,10))
    print("Address 09H, hours:",ssq(r,11,14))
    print("Address 0AH, day:",ssq(r,15,18))
    print("Address 0FH, control register:",ssq(r,19,21))


##### BOOTLOADER COMMANDS #####

# THESE AREN'T DOCUMENTED IN THE MANUAL, SO I'VE MADE THE EXECUTIVE DECISION NOT TO WORK ON THEM

# def reset_microcontroller():
#     send("0x19")#should be hex value 19, not string

# def intel_hex_firmware_upgrade_initiation():
#     send(":")


# TODO figure out date/time I/O


##### CONNECT TO DEVICE, SOMEHOW #####

def initialize_connection():
    pass

def ping_device():
    pass

def send(s,exp):
    sure = parse(f"Do you wish to send the following {exp} command (yes/no): {s}")
    if sure == "yes":
        print("(simulated) command sent")
    else:
        print("command NOT sent")

def receive()->str:
    return input("Type possible response code here")






##### UTILITIES #####

def parse(string)->str:
    r = input(string)
    exit_codes = ["exit","quit"]
    for code in exit_codes:
        if code in r:
            print("EXIT CODE DETECTED\nPROGRAM TERMINATING")
            exit(0)

def zero_fill_decimal(whole_len, dec_len, value)->str:
    whole = int(value)
    decimal = int((value-whole)*pow(10,dec_len))
    num = whole
    count = 0
    while num>=10:
        num=num%10
        count+=1
    hashes="0"*(whole_len-count)
    return f"{hashes}{whole}.{decimal}"

def zero_fill(length, value):
    whole = int(value)
    num=whole
    count=0
    while num>=10:
        num=num%10
        count+=1
    zeros = "0"*(length-count)
    return f"{zeros}{value}"

def ssq(s, f, l)->str: # subsequence
    return s[f:l+1] # manual endpoints are all inclusive, and it's easier to adapt in one place than in several dozen.

def ssql(s, f, l)->str: # subsequence with left split to remove 0
    return s[f:l+1].lsplit("0")

##### DRIVER CODE #####

def main():
    #wait for user input, ig
    pass

main()