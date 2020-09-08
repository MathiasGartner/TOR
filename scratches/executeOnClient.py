
import argparse

import tor.TORSettingsLocal as tsl

from tor.base import DBManager

parser = argparse.ArgumentParser()
parser.add_argument("-cmd", dest="cmd")
args = parser.parse_args()


ips = []
poses = []
#positions = [1, 2, 3, 4, 5, 6, 7, 8, 9]
positions = range(1, 28)
#positions = [1, 2, 3]
#positions = [18]
#positions = [3, 6, 17, 22, 27]
#positions = [3]

from itertools import chain
#positions = chain(range(1, 22), range(23, 28))
#positions = chain(range(1, 21), range(23, 28))

for p in positions:
    ips.append(DBManager.getIPByPosition(p))
    poses.append(p)

#if len(positions) == 0:
#    ips = [115]

path_key = tsl.PATH_TO_SSH_KEY

filename = "executeOnClient.cmd"

cmd_ssh = r'ssh -i {0} pi@{1} "{2}"'
cmd_scp_get = r"scp -i {0} -r pi@{1}:/home/pi/{2} {3}"
cmd_startService = "sudo systemctl daemon-reload; sudo systemctl restart TORClient"
cmd_stopService = "sudo systemctl daemon-reload; sudo systemctl stop TORClient"
cmd_removeImages = "sudo rm -r fail/*; sudo rm -r found/*;"
cmd_copyImages = "sudo rm -r fail/*; sudo rm -r found/*;"

if args.cmd != "":
    cmd = args.cmd


with open(filename, 'w') as f:
    for ip, pos in zip(ips, poses):
        #full_ip = tsl.CLIENT_IP_NETWORK + "." + str(ip)
        full_ip = ip
        cmd = cmd_ssh.format(path_key, full_ip, cmd_startService)
        #cmd = cmd_ssh.format(path_key, full_ip, cmd_stopService)
        #cmd = cmd_ssh.format(path_key, full_ip, cmd_removeImages)
        f.write(cmd + "\n")
        copyFiles = False
        if copyFiles:
            cmd = "mkdir " + tsl.DIRECTORY_TEST_IMAGES_DATE + str(pos)
            f.write(cmd + "\n")
            cmd = cmd_scp_get.format(path_key, full_ip, "found", tsl.DIRECTORY_TEST_IMAGES_DATE + str(pos) + "\\" + "found")
            f.write(cmd + "\n")
            cmd = cmd_scp_get.format(path_key, full_ip, "fail", tsl.DIRECTORY_TEST_IMAGES_DATE + str(pos) + "\\" + "fail")
            f.write(cmd + "\n")