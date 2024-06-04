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

    interval = parse("Reporting interval (integer), default unit seconds\nFor minutes: ####m\nFor hours: ####h")
    time = int(re.search(r'\d+', interval).group())
    if "m" in interval:
        time=time*60
    if "h" in interval:
        time=time*3600

    num=time
    count = 0
    while num>=10:
        num=num%10
        count+=1
    hashes="#"*(10-count)
    send(f"{boot}{hashes}{time}x","SET INTERVAL REPORT PERIOD")

def set_interval_report_threshold():
    boot = parse("Set for immediate use only = i, set for booting and immediate use = b\nMode: ")
    if "b" in boot:
        boot = "T"
    elif "i" in boot:
        boot = "t"
    threshold = float(parse("Reporting threshold in mag/arcsec^2: "))
    hashes=zero_fill_decimal(8,2,threshold)
    send(f"{boot}{hashes}x","SET INTERVAL REPORT THRESHOLD")

def parse_interval_settings(r): # this is the response for Ix, set period, and set threshold
    print("Interval setting response:")
    print("Interval period EEPROM:",ssql(r,2,12))
    print("Interval period RAM:",ssql(r,14,24))
    print("Threshold EEPROM:",ssql(r,26,37))
    print("Threshold RAM:",ssql(r,39,50))

##### MANUAL CALIBRATION #####

def man_cal_set_light_offset():
    value = parse("Type offset value in mag/arcsec^2: ")
    hashes=zero_fill_decimal(8,2,value)
    send(f"zcal5{hashes}x","manual calibration - set light offset")

def man_cal_set_light_temperature():
    value = parse("Type temperature value in °C: ")
    hashes=zero_fill_decimal(8,2,value)
    send(f"zcal6{hashes}x","manual calibration - set light temperature")

def man_cal_set_dark_period():
    value = parse("Type period value in seconds: ")
    hashes=zero_fill_decimal(7,3,value)
    send(f"zcal7{hashes}x","manual calibration - set dark period")

def man_cal_set_dark_temperature():
    value = parse("Type temperature value in °C: ")
    hashes=zero_fill_decimal(8,2,value)
    send(f"zcal8{hashes}x","manual calibration - set dark period")

def parse_manual_cal(r)->bool:
    print("Results of manual calibration:")
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
    send("sx","request internal simulation values")

def parse_simulation_values(r):
    print("Internal simulation values response:")
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
    send(f"S,{count_zeroes},{freq_zeroes},{temp_zeroes}x","simulate internal calculation")

def parse_simulation_calculation(r):
    print("Simulation calculation response:")
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

##### BOOTLOADER COMMANDS #####

# THESE AREN'T DOCUMENTED IN THE MANUAL, SO I'VE MADE THE EXECUTIVE DECISION NOT TO WORK ON THEM

# def reset_microcontroller():
#     send("0x19")#should be hex value 19, not string

# def intel_hex_firmware_upgrade_initiation():
#     send(":")


##### DATA LOGGER COMMANDS #####
def sort_L(r):
    match r[1]:
        case "0":
            parse_ID(r)

def request_ID():
    send("L0x","request report ID")

def parse_ID(r):
    print("Report ID response:")
    print("Manufacturer ID:",ssql(r,3,5))
    print("Device ID:",ssql(r,6,8))

def request_logging_pointer():
    send("L1x","request logging pointer")

def parse_logging_pointer(r):
    print("Logging pointer response:")

def erase_flash_chip(): #no corresponding response
    sure = parse("This action is irreversible. Are you sure you want to erase the entire flash memory? To proceed, type ERASE. To cancel, type anything else.")
    if sure==("ERASE"):
        send("L2x","erase flash chip")
    else:
        print("Request cancelled, flash NOT erased.")

def request_log_one_record():
    send("L3x","request log one record")

def parse_log_one_record(r):
    print("Log one record response:")
    print("Pointer position:",ssql(r,3,8))

def request_return_one_record():
    pointer = parse("Type pointer position of record to return: ")
    pt = zero_fill(10,pointer)
    send(f"L4{pt}x","request return one record")

def parse_return_one_record(r):
    print("Return one record response:")
    print("Date, day of week, time of recording:",ssql(r,3,22))
    print("Reading (mag/arcsec^2):",ssql(r,23,28))
    print("Temperature (°C):",ssql(r,29,36))
    print("Battery voltage ADC valueL:",ssql(r,37,39))

def request_battery_voltage():
    send("L5x","request battery voltage")

def parse_battery_voltage(r):
    print("Battery voltage response:")
    print("Internal voltage ADC:",ssql(r,3,5))
    adc = int(ssql(r,3,5))
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
        send(f"LM{mode}x",f"set logging trigger mode {mode}")
    else:
        print("Invalid mode entered")

def request_logging_trigger_mode():
    send("Lmx","request logging trigger mode")

def parse_logging_trigger_mode(r):
    print("Logging trigger mode response: ",end=" ")
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
    send("LIx","request logging interval settings")

def parse_logging_interval_settings(r):
    print("Logging interval setting response:")
    print("EEPROM interval period (sec):",ssql(r,3,13))
    print("EEPROM interval period (min):",ssql(r,15,25))
    print("RAM interval period (sec):",ssql(r,27,37))
    print("RAM interval period (min):",ssql(r,39,49))
    print("RAM threshold value (mag/arcsec^2):",ssql(r,51,62))

def set_logging_interval_period():
    unit = parse("Type unit for reporting interval (s=seconds m=minutes): ")
    time = parse("Type time value (numeric only): ")
    if time.isNumeric():
        ztime = zero_fill(5,time)
        if "m" in unit:
            send(f"LPM{ztime}x","logging interval reporting period setting minutes")
        elif "s" in unit:
            send(f"LPS{ztime}x","logging interval reporting period setting seconds")
        else:
            print("Invalid mode entry: must be m or s")
    else:
        print("Invalid time format: numeric only, no decimal")

def set_logging_threshold():
    thresh = parse("Type mag/arcsec^2 value: ")
    zthresh = zero_fill_decimal(8,2,thresh)
    send(f"LPT{zthresh}x","logging threshold setting")

def request_clock_data():
    send("Lcx","request clock data")

def set_clock_data():
    data = parse("Type data here (lol finish this later): ")
    send(f"Lc{data}x", "set clock data")

def parse_clock_data(r):
    if r[1]==("C"):
        print("Set command received")
    print("Clock data repsonse:")
    print("Date, day of week, time:",ssql(r,3,21))

def put_unit_to_sleep():
    send("Lsx","put unit to sleep")

def request_alarm_data():
    send("Lax","request alarm data")

def parse_alarm_data(r):
    print("Alarm data response:")
    print("Address 07H, seconds:",ssql(r,3,6))
    print("Address 08H, minutes:",ssql(r,7,10))
    print("Address 09H, hours:",ssql(r,11,14))
    print("Address 0AH, day:",ssql(r,15,18))
    print("Address 0FH, control register:",ssql(r,19,21))

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