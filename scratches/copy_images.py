
import os

from tor.base.utils import Utils
from tor.client import ClientSettings as cs
import tor.TORSettingsLocal as tsl

################################
### copy images from clients ###
################################


ips = []

#positions = []
positions = range(1, 28)
positions = [1]

if len(positions) > 0:
    from tor.base import DBManager

for p in positions:
    ips.append(DBManager.getIPByPosition(p))

path_key = tsl.PATH_TO_SSH_KEY

filename = "copy_images.cmd"
localImageDirectory = os.path.join("D:" + os.sep, "TOR2022", "Pictures", Utils.getFilenameTimestampDay())

cmd_copy_position_ok = r"scp -i {0} pi@{1}:" + cs.IMAGE_DIRECTORY_POSITION + "/ok* " + os.path.join(localImageDirectory, "ok")
cmd_copy_position_wrong = r"scp -i {0} pi@{1}:" + cs.IMAGE_DIRECTORY_POSITION + "/wrong* " + os.path.join(localImageDirectory, "wrong")
cmd_remove_pictures = r'ssh -i {0} pi@{1} "sudo rm -r -f pictures/ok* pictures/wrong*"'

with open(filename, 'w') as f:
    f.write("mkdir " + os.path.join(localImageDirectory, "ok \n"))
    f.write("mkdir " + os.path.join(localImageDirectory, "wrong \n"))
    for ip in ips:
        full_ip = ip
        cmd = cmd_copy_position_ok.format(path_key, full_ip)
        f.write(cmd + "\n")
        cmd = cmd_copy_position_wrong.format(path_key, full_ip)
        f.write(cmd + "\n")
        cmd = cmd_remove_pictures.format(path_key, full_ip)
        f.write(cmd + "\n")