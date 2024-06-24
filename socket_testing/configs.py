client_repo_path = "MotheterRemote/socket_testing"
client_data_path = "/var/tmp/sqm_macleish/"

host_data_path = "data"

sensor = "macleish"
sensor_name = "rp3"
sensor_ip = "131.229.147.51"
sensor_ddns = "macleishmoths.ddns.net"
ddns_over_ip = True
if ddns_over_ip:
    sensor_addr = sensor_ddns
else:
    sensor_addr = sensor_ip

sensor_is_wifi = True
sensor_is_cellular = False


observatory_name = "macleish"
device_type = "SQM-LU"
device_id = device_type + "-" + observatory_name
device_addr = "/dev/ttyUSB0"

debug = True  # whether to raise exceptions if something goes a little sideways

socket_port = 1234
