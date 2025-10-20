
import os

import tor.TORSettingsLocal as tsl

################################
### update source on clients ###
################################

from tor.base import DBManager
clients = DBManager.getAllPossibleClients()

path_key = tsl.PATH_TO_SSH_KEY

cmd_new_shell = "invoke-expression 'cmd /c start powershell -Command {{ {0} }}'"

#### TOR ####
directoryClients = os.path.join(tsl.PATH_TO_TOR_SCRIPTS, "development", "updateClient")
filename = os.path.join(tsl.PATH_TO_TOR_SCRIPTS, "development", "update_tor_all.ps1")
cmd_delete = r'ssh -i {0} pi@{1} "sudo rm -r tor; sudo rm -r scripts; mkdir scripts"'
cmd_copy = r"scp -i {0} -r " + tsl.PATH_TO_TOR_SOURCE + r"/TOR/tor pi@{1}:/home/pi"
cmd_copy_service = r"scp -i {0} -r " + tsl.PATH_TO_TOR_SCRIPTS + r"/client/* pi@{1}:/home/pi/scripts/"
cmd_install = r'ssh -i {0} pi@{1} "sudo cp /home/pi/scripts/TOR*.service /etc/systemd/system/; sudo chmod +x /home/pi/scripts/*.sh"'
cmd_service = r'ssh -i {0} pi@{1} "sudo systemctl daemon-reload; sudo systemctl stop TORStatus; sudo systemctl enable TORStatus --now"'

if not(os.path.exists(directoryClients) and os.path.isdir(directoryClients)):
    os.mkdir(directoryClients)
with (open(filename, 'w') as fAll):
    fAll.write ("$cmdFiles = @(\n")
    for c in clients:
        clientfilename = f"tor_{c.Id}.cmd"
        clientfilenameIP = f"tor_IP_{c.IP[-3:]}.cmd"
        clientfilenamePos = f"tor_Pos_{c.Position}.cmd"
        print(f"write file \"{clientfilename}\"")
        fAll.write(f"\"updateClient\\{clientfilename}\",\n")
        with open(os.path.join(directoryClients, clientfilename), 'w') as f, \
             open(os.path.join(directoryClients, clientfilenameIP), 'w') as fIP, \
             open(os.path.join(directoryClients, clientfilenamePos), 'w') as fPos:
            full_ip = c.IP
            cmd = cmd_delete.format(path_key, full_ip)
            f.write(cmd + "\n")
            fIP.write(cmd + "\n")
            fPos.write(cmd + "\n")
            cmd = cmd_copy.format(path_key, full_ip)
            f.write(cmd + "\n")
            fIP.write(cmd + "\n")
            fPos.write(cmd + "\n")
            cmd = cmd_copy_service.format(path_key, full_ip)
            f.write(cmd + "\n")
            fIP.write(cmd + "\n")
            fPos.write(cmd + "\n")
            cmd = cmd_install.format(path_key, full_ip)
            f.write(cmd + "\n")
            fIP.write(cmd + "\n")
            fPos.write(cmd + "\n")
            cmd = cmd_service.format(path_key, full_ip)
            f.write(cmd + "\n")
            fIP.write(cmd + "\n")
            fPos.write(cmd + "\n")
    fAll.write (")\n")
    fAll.write("foreach ($file in $cmdFiles) {\n")
    fAll.write("Start-Process \"cmd.exe\" -ArgumentList \"/c $file\"\n")
    fAll.write("}\n")

#### TOR-Marlin ####

filename = os.path.join(tsl.PATH_TO_TOR_SCRIPTS, "development", "update_tor_marlin_all.sh")
cmd_delete = r'ssh -i {0} pi@{1} "sudo rm -r /home/pi/tormarlin"'
cmd_mkdir = r'ssh -i {0} pi@{1} "mkdir /home/pi/tormarlin"'
cmd_copy = r"scp -i {0} " + tsl.PATH_TO_TOR_MARLIN_FIRMWARE + r" pi@{1}:/home/pi/tormarlin/"
cmd_flash = r'ssh -i {0} pi@{1} "sudo /home/pi/scripts/flashTORMarlin.sh"'

with open(filename, 'w') as fAll:
    fAll.write ("scripts=(\n")
    for c in clients:
        clientfilename = f"marlin_{c.Id}.cmd"
        print(f"write file \"{clientfilename}\"")
        fAll.write(clientfilename + "\n")
        with open(os.path.join(directoryClients, clientfilename), 'w') as f:
            full_ip = c.IP
            cmd = cmd_delete.format(path_key, full_ip)
            f.write(cmd + "\n")
            cmd = cmd_mkdir.format(path_key, full_ip)
            f.write(cmd + "\n")
            cmd = cmd_copy.format(path_key, full_ip)
            f.write(cmd + "\n")
            cmd = cmd_flash.format(path_key, full_ip)
            f.write(cmd + "\n")
    fAll.write (")\n")
    fAll.write("for script in \"${scripts[@]}\"; do\n")
    fAll.write("bash \"$script\" &\n")
    fAll.write("done\n")
    fAll.write("wait\n")
    fAll.write("echo \"done\"\n")

#### TOR-Marlin ####

filename = os.path.join(tsl.PATH_TO_TOR_SCRIPTS, "development", "update_tor_marlin_all_windows.ps1")
with open(filename, 'w') as fAll:
    fAll.write ("$cmdFiles = @(\n")
    for c in clients:
        clientfilename = f"marlin_win_{c.Id}.ps1"
        print(f"write file \"{clientfilename}\"")
        fAll.write(clientfilename + "\n")
        with open(os.path.join(directoryClients, clientfilename), 'w') as f:
            cmds = ""
            full_ip = c.IP
            cmd = "echo {}".format(full_ip)
            cmds = cmds + cmd + "; "
            cmd = cmd_delete.format(path_key, full_ip)
            cmds = cmds + cmd + "; "
            cmd = cmd_mkdir.format(path_key, full_ip)
            cmds = cmds + cmd + "; "
            cmd = cmd_copy.format(path_key, full_ip)
            cmds = cmds + cmd + "; "
            cmd = cmd_flash.format(path_key, full_ip)
            cmds = cmds + cmd + "; "
            cmd = "sleep 5"
            cmds = cmds + cmd + "; "
            cmd = cmd_new_shell.format(cmds)
            f.write(cmd + "\n")
    fAll.write (")\n")
    fAll.write("foreach ($file in $cmdFiles) {\n")
    fAll.write("Start-Process \"cmd.exe\" -ArgumentList \"/c $file\"\n")
    fAll.write("}\n")
