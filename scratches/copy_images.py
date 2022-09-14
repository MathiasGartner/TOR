
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
#positions = [22, 23, 24, 25, 26, 27]
#positions = [25]

if len(positions) > 0:
    from tor.base import DBManager

for p in positions:
    ips.append(DBManager.getIPByPosition(p))

path_key = tsl.PATH_TO_SSH_KEY

# INFO: set local directories
#localImageDirectory_magnet = os.path.join("D:" + os.sep, "TOR2022", "Pictures", "magnet_{}".format(Utils.getFilenameTimestampDay()))
#localImageDirectory_dice = os.path.join("D:" + os.sep, "TOR2022", "Pictures", "dice_{}".format(Utils.getFilenameTimestampDay()))
localImageDirectory_magnet = os.path.join("/home/tor", "TORPictures", "magnet_{}".format(Utils.getFilenameTimestampDay()))
localImageDirectory_dice = os.path.join("/home/tor", "TORPictures", "dice_{}".format(Utils.getFilenameTimestampDay()))

filename_magnet = "copy_images_magnet.cmd"
filename_dice = "copy_images_dice.cmd"

cmd_copy_position_ok = r"scp -i {0} pi@{1}:" + cs.IMAGE_DIRECTORY_POSITION + "/ok* " + os.path.join(localImageDirectory_magnet, "ok")
cmd_copy_position_wrong = r"scp -i {0} pi@{1}:" + cs.IMAGE_DIRECTORY_POSITION + "/wrong* " + os.path.join(localImageDirectory_magnet, "wrong")
cmd_remove_pictures_magnet = r'ssh -i {0} pi@{1} "sudo rm -r -f ' + cs.IMAGE_DIRECTORY_POSITION + '/ok* ' + cs.IMAGE_DIRECTORY_POSITION + '/wrong*"'

cmd_copy_dice_found = r"scp -i {0} pi@{1}:" + cs.IMAGE_DIRECTORY_DICE + "/found/* " + os.path.join(localImageDirectory_dice, "found")
cmd_copy_dice_fail = r"scp -i {0} pi@{1}:" + cs.IMAGE_DIRECTORY_DICE + "/fail/* " + os.path.join(localImageDirectory_dice, "fail")
cmd_remove_pictures_dice = r'ssh -i {0} pi@{1} "sudo rm -r -f ' + cs.IMAGE_DIRECTORY_DICE + '/found/* ' + cs.IMAGE_DIRECTORY_DICE + '/fail/*"'

with open(filename_magnet, 'w') as f:
    f.write("mkdir " + localImageDirectory_magnet + "\n")
    f.write("mkdir " + os.path.join(localImageDirectory_magnet, "ok") + "\n")
    f.write("mkdir " + os.path.join(localImageDirectory_magnet, "wrong") + "\n")
    for ip in ips:
        full_ip = ip
        cmd = cmd_copy_position_ok.format(path_key, full_ip)
        f.write(cmd + "\n")
        cmd = cmd_copy_position_wrong.format(path_key, full_ip)
        f.write(cmd + "\n")
        cmd = cmd_remove_pictures_magnet.format(path_key, full_ip)
        f.write(cmd + "\n")

with open(filename_dice, 'w') as f:
    f.write("mkdir " + localImageDirectory_dice + "\n")
    f.write("mkdir " + os.path.join(localImageDirectory_dice, "found") + "\n")
    f.write("mkdir " + os.path.join(localImageDirectory_dice, "fail") + "\n")
    for ip in ips:
        full_ip = ip
        cmd = cmd_copy_dice_found.format(path_key, full_ip)
        f.write(cmd + "\n")
        cmd = cmd_copy_dice_fail.format(path_key, full_ip)
        f.write(cmd + "\n")
        cmd = cmd_remove_pictures_dice.format(path_key, full_ip)
        f.write(cmd + "\n")
