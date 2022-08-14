
from tor.client import ClientSettings as cs
import tor.TORSettingsLocal as tsl

################################
### copy images from clients ###
################################


ips = []

#positions = []
positions = range(1, 28)
positions = [17]

if len(positions) > 0:
    from tor.base import DBManager

for p in positions:
    ips.append(DBManager.getIPByPosition(p))

path_key = tsl.PATH_TO_SSH_KEY

filename = "copy_images.sh"

cmd_copy_position_ok = r"scp -i {0} pi@{1}:" + cs.IMAGE_DIRECTORY_POSITION + "/ok* /home/pi/Sources/PositionVerification/new_images/ok/"
cmd_copy_position_wrong = r"scp -i {0} pi@{1}:" + cs.IMAGE_DIRECTORY_POSITION + "/wrong* /home/pi/Sources/PositionVerification/new_images/wrong/"

with open(filename, 'w') as f:
    for ip in ips:
        full_ip = ip
        cmd = cmd_copy_position_ok.format(path_key, full_ip)
        f.write(cmd + "\n")
        cmd = cmd_copy_position_wrong.format(path_key, full_ip)
        f.write(cmd + "\n")