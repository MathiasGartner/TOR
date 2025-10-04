
import tor.TORSettingsLocal as tsl

################################
### update source on clients ###
################################

#ips = range(101, 131) #[107]

ips = []
#ips = [107, 112]
#ips = ["192.168.1.110", "192.168.1.127"]
#ips = ["192.168.1.108"]
ips = ["192.168.1.120" ]
#ips = ["192.168.1.102", "192.168.1.107"]
#positions = []
#positions = [1, 2, 3, 4,5, 6, 7, 8, 9]
positions = range(1, 28)
#positions = [10, 11, 12, 13, 14, 15]
#positions = [1, 2, 3]
#positions = [16]
#positions = [25, 19, 9, 20, 4, 13, 27, 1]
#positions = [17]
#positions = []

#from itertools import chain
#positions = chain(range(1, 21), range(23, 28))

if len(positions) > 0:
    from tor.base import DBManager

for p in positions:
    ips.append(DBManager.getIPByPosition(p))

#if len(positions) == 0:
#    ips = [115]


path_key = tsl.PATH_TO_SSH_KEY

cmd_new_shell = "invoke-expression 'cmd /c start powershell -Command {{ {0} }}'"

#### TOR ####
filename = "../../scratches/update_tor.cmd"
cmd_delete = r'ssh -i {0} pi@{1} "sudo rm -r tor; sudo rm -r scripts"'
cmd_copy = r"scp -i {0} -r " + tsl.PATH_TO_TOR_SOURCE + r"/TOR/tor pi@{1}:/home/pi"
#cmd_delete_service = r'ssh -i {0} pi@{1} "sudo rm -r scripts"'
cmd_copy_service = r"scp -i {0} -r " + tsl.PATH_TO_TOR_SCRIPTS + r" pi@{1}:/home/pi"
#cmd_copy_service_system = r'ssh -i {0} pi@{1} "sudo cp /home/pi/scripts/TORClient.service /etc/systemd/system/TORClient.service"'
#cmd_chmod_marlin = r'ssh -i {0} pi@{1} "sudo chmod +x /home/pi/scripts/flashTORMarlin.sh"'
#cmd_chmod_temp = r'ssh -i {0} pi@{1} "sudo chmod +x /home/pi/scripts/temperature.sh"'
cmd_install = r'ssh -i {0} pi@{1} "sudo cp /home/pi/scripts/TORClient.service /etc/systemd/system/TORClient.service; sudo chmod +x /home/pi/scripts/flashTORMarlin.sh; sudo chmod +x /home/pi/scripts/temperature.sh; sudo chmod +x /home/pi/scripts/installPyQt5.sh; sudo chmod +x /home/pi/scripts/enableX11Root.sh"'

with open(filename, 'w') as f:
    for ip in ips:
        #full_ip = tsl.CLIENT_IP_NETWORK + "." + str(ip)
        full_ip = ip
        cmd = cmd_delete.format(path_key, full_ip)
        f.write(cmd + "\n")
        cmd = cmd_copy.format(path_key, full_ip)
        f.write(cmd + "\n")
        #cmd = cmd_delete_service.format(path_key, full_ip)
        #f.write(cmd + "\n")
        cmd = cmd_copy_service.format(path_key, full_ip)
        f.write(cmd + "\n")
        #cmd = cmd_copy_service_system.format(path_key, full_ip)
        #f.write(cmd + "\n")
        #cmd = cmd_chmod_marlin.format(path_key, full_ip)
        #f.write(cmd + "\n")
        #cmd = cmd_chmod_temp.format(path_key, full_ip)
        #f.write(cmd + "\n")
        cmd = cmd_install.format(path_key, full_ip)
        f.write(cmd + "\n")

#### TOR-Marlin ####
filename = "../../scratches/update_tor_marlin.cmd"
cmd_delete = r'ssh -i {0} pi@{1} "sudo rm -r /home/pi/tormarlin"'
cmd_mkdir = r'ssh -i {0} pi@{1} "mkdir /home/pi/tormarlin"'
cmd_copy = r"scp -i {0} " + tsl.PATH_TO_TOR_MARLIN_FIRMWARE + r" pi@{1}:/home/pi/tormarlin/"
cmd_flash = r'ssh -i {0} pi@{1} "sudo /home/pi/scripts/flashTORMarlin.sh"'

with open(filename, 'w') as f:
    for ip in ips:
        #full_ip = tsl.CLIENT_IP_NETWORK + "." + str(ip)
        full_ip = ip
        cmd = cmd_delete.format(path_key, full_ip)
        f.write(cmd + "\n")
        cmd = cmd_mkdir.format(path_key, full_ip)
        f.write(cmd + "\n")
        cmd = cmd_copy.format(path_key, full_ip)
        f.write(cmd + "\n")
        cmd = cmd_flash.format(path_key, full_ip)
        f.write(cmd + "\n")

#### TOR-Marlin ####

filename = "../../scratches/update_tor_marlin_window.ps1"
with open(filename, 'w') as f:
    for ip in ips:
        cmds = ""
        #full_ip = tsl.CLIENT_IP_NETWORK + "." + str(ip)
        full_ip = ip
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

#### wifi ####
ips = range(100, 135)
filename = "../../scratches/update_wifi.cmd"
cmd_cp = r'scp -i {0} "D:\The Transparency of Randomness\Dropbox\Elektronik\raspi boot files\wpa_supplicant.conf" pi@192.168.1.{1}:/home/pi/wpa_supplicant.conf'
cmd_mv = r'ssh -i {0} pi@192.168.1.{1} "sudo mv /home/pi/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf"'
cmd_reboot = r'ssh -i {0} pi@192.168.1.{1} "sudo reboot"'

with open(filename, 'w') as f:
    for ip in ips:
        full_ip = "" + str(ip)
        cmd = cmd_cp.format(path_key, full_ip)
        f.write(cmd + "\n")
        cmd = cmd_mv.format(path_key, full_ip)
        f.write(cmd + "\n")
        cmd = cmd_reboot.format(path_key, full_ip)
        f.write(cmd + "\n")



#######################################
### generate custom client settings ###
#######################################
writeCustomFiles = False

materials = ["Acacia Bohnen","Linsen","Kirschkerne","Eucalyptus","Zimtstangen","Gerstenähren","Kaffeebohnen","Wachtelbohne","Japanischer Schlitzahorn","Strandflieder","Pfeffer","Baumschwamm","Luffa","Platanen","Orangenscheiben","Sternanis","Traubenkerne","Limettenscheiben","Pampasgras","Kork","Palmringe","Lavendel","Apfelscheiben","Air-Fern","Essigbaum","Baumwolle","Palmenblatt","Samtgras","Chilis","Yoga"]

def writeCustomFile(material, settings):
    if writeCustomFiles:
        filename = "../tor/client/CustomClientSettings/{}.py".format(material)
        with open(filename, 'w') as f:
            f.write("import tor.client.ClientSettings as cs" + "\n")
            for s in settings:
                f.write(s + "\n")

for m in materials:
    settings = [
        "cs.RAMP_MATERIAL = \"" + m + "\"",
    ]
    writeCustomFile(m, settings)