import os


# command = "COMMAND"
# # os.system(f"echo {command} | nc 131.229.147.51 12345")
# os.chdir("sensor_interface")
# os.system("nc -lv 12345 | python3 get_command.py")
# 131.229.152.158

os.system("nc 131.229.147.51 12345")
while True:
    inp = input()
    print(f"Got input {inp}")
