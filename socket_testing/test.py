import os

path = "MotheterRemote/socket_testing"
filename = "get_command.py"
name = "rp3"
ip = "131.229.147.51"
command = "rx"
s = f"ssh {name}@{ip} 'python3 {path}/{filename} {command}'"
print(s)

os.system(f"ssh {name}@{ip} 'python3 {path}/{filename} {command}'")
