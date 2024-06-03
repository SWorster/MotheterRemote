import re

##### SEND COMMANDS #####
def send_reading_request():
    send("rx")

def send_calibration_information_request():
    send("cx")

def send_unit_information_request():
    send("ix")

def send_arm_light_calibration_command():
    send("zcalAx")

def send_arm_dark_calibration_command():
    send("zcalBx")

def send_disarm_calibration_command():
    send("zcalDx")

def request_interval_settings():
    send("Ix")

def set_period():
    boot = parse("Set for immediate use only = i, set for booting and immediate use = b\nMode: ")
    if boot.contains("b"):
        boot = "P"
    elif boot.contains("i"):
        boot = "p"

    interval = parse("Reporting interval, default unit seconds\nFor minutes: xxxxm\nFor hours: xxxxh")
    time = int(re.search(r'\d+', interval).group())
    if interval.contains("m"):
        time=time*60
    if interval.contains("h"):
        time=time*3600

    num=time
    count = 0
    while num>=10:
        num=num%10
        count+=1
    hashes="#"*(10-count)
    send(f"{boot}{hashes}{time}x")

def set_threshold():
    boot = parse("Set for immediate use only = i, set for booting and immediate use = b\nMode: ")
    if boot.contains("b"):
        boot = "T"
    elif boot.contains("i"):
        boot = "t"
    threshold = float(parse("Reporting threshold in mag/arcsec^2: "))
    hashes=hash_maker(8,2,threshold)
    send(f"{boot}{hashes}x")

def man_cal_set_light_offset():
    value = input("Type offset value in mag/arcsec^2: ")
    hashes=hash_maker(8,2,value)
    send(f"zcal5{hashes}x")

def man_cal_set_light_temperature():
    value = input("Type temperature value in °C: ")
    hashes=hash_maker(8,2,value)
    send(f"zcal6{hashes}x")

def man_cal_set_dark_period():
    value = input("Type period value in seconds: ")
    hashes=hash_maker(7,3,value)
    send(f"zcal7{hashes}x")

def man_cal_set_dark_temperature():
    value = input("Type temperature value in °C: ")
    hashes=hash_maker(8,2,value)
    send(f"zcal8{hashes}x")

def request_internal_simulation_values():
    send("sx")

def simulate_internal_calculation():
    counts = input("Number of simulated counts: ")
    frequency = input("Frequency in Hz: ")
    temp = input("Temperature ADC in °C: ")
    count_zeroes = fill_zeros(10,counts)
    freq_zeroes = fill_zeros(10,frequency)
    temp_zeroes=fill_zeros(10,temp)
    send(f"S,{count_zeroes},{freq_zeroes},{temp_zeroes}x")

##### RESPONSE CASES #####
def sort_response(response):
    match response[0]:
        case "r":
            reading_request(response)
        case "c":
            calibration_information_request(response)
        case "z":
            if response[1].equals(","):
                pass
            else:
                arm_calibration_command(response)
        case "I":
            interval_setting_response(response)
        case "s":
            pass
        case "S":
            simulation_response(response)
        case _:
            pass

##### PARSE COMMANDS #####
def reading_request(response)->bool:
    print("Current light measurement:", response[2:9]) # 2-8
    print("Frequency:",response[10:22]) #10-21
    print("Period (counts):",response[22:34]) #22-33
    print("Period (seconds)",response[35:47])#35-46
    print("Temperature:", response[48-55])#48-54
    if len(response)>=63:
        print("Serial number:",response[55-64])#55-63
    return True

def calibration_information_request(response)->bool:
    print("Light calibration offset:", response[2:14]) # 2-13
    print("Dark calibraiton period:", response[15:27]) #15-26
    print("Temperature during light calibration:", response[28:35])#28-34
    print("Light sensor offset (manufacutrer):", response[36:48])#36-47
    print("Temperature during dark calibration:", response[49:56])#49-55
    return True

def unit_information_request(response):
    print("Protocol number:",response[2:10]) #2-9
    print("Model number:",response[11:19]) #11-18
    print("Feature number:",response[20:28]) #20-27
    print("Serial number:",response[29:37]) #29-36

def arm_calibration_command(response):
    match response[1]:
        case "A":
            print("Light calibration")
        case "B":
            print("Dark calibration")
        case "x":
            print("All calibration modes")
        case _:
            print("INVALID RESPONSE")

    match response[2]:
        case "a":
            print("Armed")
        case "d":
            print("Disarmed")

    match response[3]:
        case "L":
            print("LOCKED. Wait for unlock before calibrating after Arm command, firmware upgrades are disabled.")
        case "U":
            print("UNLOCKED. Calibrate immediately after Arm command, Enable firmware upgrade.")


def parse_manually_set_calibration(response)->bool:
    print("Manual Set Light Calibration Offset")
    match response[2]:
        case "5":
            print("Light Magnitude (mag/arcsec^2):", response[4-16])#4-15
        case "6":
            print("Light Temperature (°C):", response[4-10])#4-9
        case "7":
            print("Dark Period (sec):", response[4-16])#4-15
        case "8":
            print("Dark Temperature (°C):", response[4-10])#4-9
        case _:
            print("INVALID RESPONSE")
            return False
    return True

def interval_setting_response(response):
    print("Interval setting response")
    print("Interval period EEPROM:",response[2:13])#2-12
    print("Interval period RAM:",response[14:25])#14-24
    print("Threshold EEPROM:",response[26:38])#26-37
    print("Threshold RAM:",response[39:51])#39-50

def internal_simulation_values(response):
    print("Internal simulation values")
    print("Number of counts:",response[2:13])#2-12
    print("Frequency (Hz):",response[14:25])#14-24
    print("Temperature ADC (°C):",response[26:38])#26-37

def simulation_response(response):
    print("Simulation response")
    print("Number of counts:",response[2:13])#2-12
    print("Frequency (Hz):",response[13:23])#13-22
    print("Temperature ADC (°C):",response[24:34])#24-33

##### UNSORTED COMMANDS #####

def reset_microcontroller():
    pass

def intel_hex_firmware_upgrade_initiation():
    pass

def request_reading_internal_variables():
    pass



##### DATA LOGGER COMMANDS #####
def report_ID():
    pass

def report_logging_pointer():
    pass

def erase_flash_chip():
    pass

def log_one_record():
    pass

def return_one_record():
    pass

def get_battery_voltage():
    pass

def set_logging_trigger_mode():
    pass

def get_logging_trigger_mode():
    pass

def logging_interval_settings_requested():
    pass

def logging_interval_period_set():
    pass

def logging_threshold_set():
    pass

def get_clock_data():
    pass

def set_clock_data():
    pass

def put_unit_to_sleep():
    pass

def get_alarm_data():
    pass

##### CONNECT TO DEVICE, SOMEHOW #####

def initialize_connection():
    pass

def ping_device():
    pass

def send(str):
    pass

def receive()->str:
    pass


##### UTILITIES #####

def parse(string):
    response = input(string)
    exit_codes = ["exit","quit"]
    for code in exit_codes:
        if response.contains(code):
            print("EXIT CODE DETECTED\nPROGRAM TERMINATING")
            exit(0)

def hash_maker(whole_len, dec_len, value)->str:
    whole = int(value)
    decimal = int((value-whole)*pow(10,dec_len))
    num = whole
    count = 0
    while num>=10:
        num=num%10
        count+=1
    hashes="#"*(whole_len-count)
    return f"{hashes}{whole}.{decimal}"

def fill_zeros(length, value):
    whole = int(value)
    num=whole
    count=0
    while num>=10:
        num=num%10
        count+=1
    zeros = "0"*(length-count)
    return f"{zeros}{value}"

##### DRIVER CODE #####

def main():
    #wait for user input, ig
    pass

main()