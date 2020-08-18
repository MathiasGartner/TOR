
import tor.TORSettingsLocal as tsl

#######################################
### generate custom client settings ###
#######################################
writeCustomFiles = False

def writeCustomFile(material, settings):
	if writeCustomFiles:
		filename = "../tor/client/CustomClientSettings/{}.py".format(material)
		with open(filename, 'w') as f:
			f.write("import tor.client.ClientSettings as cs" + "\n")
			for s in settings:
				f.write(s + "\n")

material = "orange"
settings = [
    "cs.RAMP_MATERIAL = \"" + material + "\"",
    "cs.RAMP_MATERIAL_HEIGHT = 20",
]
writeCustomFile(material, settings)

material = "moss"
settings = [
    "cs.RAMP_MATERIAL = \"" + material + "\"",
    "cs.RAMP_MATERIAL_HEIGHT = 30",
]
writeCustomFile(material, settings)

material = "coffee"
settings = [
    "cs.RAMP_MATERIAL = \"" + material + "\"",
    "cs.RAMP_MATERIAL_HEIGHT = 30",
]
writeCustomFile(material, settings)

material = "empty"
settings = [
    "cs.RAMP_MATERIAL = \"" + material + "\"",
    "cs.RAMP_MATERIAL_HEIGHT = 0",
]
writeCustomFile(material, settings)


################################
### update source on clients ###
################################

#ips = range(101, 131) #[107]

#ips = [107, 112]
ips = [129,110]
path_key = tsl.PATH_TO_SSH_KEY

#### TOR ####
filename = "update_tor.cmd"
cmd_delete = r'ssh -i {0} pi@{1} "sudo rm -r tor"'
cmd_copy = r"scp -i {0} -r " + tsl.PATH_TO_TOR_SOURCE + r"\TOR\tor pi@{1}:/home/pi"
cmd_delete_service = r'ssh -i {0} pi@{1} "sudo rm -r scripts"'
cmd_copy_service = r"scp -i {0} -r " + tsl.PATH_TO_TOR_SCRIPTS + r"\TOR\scripts pi@{1}:/home/pi"
cmd_copy_service_system = r'ssh -i {0} pi@{1} "sudo cp /home/pi/scripts/TORClient.service /etc/systemd/system/TORClient.service"'
cmd_chmod_marlin = r'ssh -i {0} pi@{1} "sudo chmod +x /home/pi/scripts/flashTORMarlin.sh"'
cmd_chmod_temp = r'ssh -i {0} pi@{1} "sudo chmod +x /home/pi/scripts/temperature.sh"'

with open(filename, 'w') as f:
    for ip in ips:
        full_ip = tsl.CLIENT_IP_NETWORK + "." + str(ip)
        cmd = cmd_delete.format(path_key, full_ip)
        f.write(cmd + "\n")
        cmd = cmd_copy.format(path_key, full_ip)
        f.write(cmd + "\n")
        cmd = cmd_delete_service.format(path_key, full_ip)
        f.write(cmd + "\n")
        cmd = cmd_copy_service.format(path_key, full_ip)
        f.write(cmd + "\n")
        cmd = cmd_copy_service_system.format(path_key, full_ip)
        f.write(cmd + "\n")
        cmd = cmd_chmod_marlin.format(path_key, full_ip)
        f.write(cmd + "\n")
        cmd = cmd_chmod_temp.format(path_key, full_ip)
        f.write(cmd + "\n")

#### TOR-Marlin ####
filename = "update_tor_marlin.cmd"
cmd_delete = r'ssh -i {0} pi@{1} "sudo rm -r /home/pi/tormarlin"'
cmd_mkdir = r'ssh -i {0} pi@{1} "mkdir /home/pi/tormarlin"'
cmd_copy = r"scp -i {0} " + tsl.PATH_TO_TOR_MARLIN_FIRMWARE + r" pi@{1}:/home/pi/tormarlin/"
cmd_flash = r'ssh -i {0} pi@{1} "sudo ./scripts/flashTORMarlin.sh"'

with open(filename, 'w') as f:
    for ip in ips:
        full_ip = tsl.CLIENT_IP_NETWORK + "." + str(ip)
        cmd = cmd_delete.format(path_key, full_ip)
        f.write(cmd + "\n")
        cmd = cmd_mkdir.format(path_key, full_ip)
        f.write(cmd + "\n")
        cmd = cmd_copy.format(path_key, full_ip)
        f.write(cmd + "\n")
        cmd = cmd_flash.format(path_key, full_ip)
        f.write(cmd + "\n")

#### wifi ####
ips = range(100, 135)
filename = "update_wifi.cmd"
cmd_cp = r'scp -i {0} "D:\Dropbox\Uni\AEC\Elektronik\raspi boot files\wpa_supplicant.conf" pi@192.168.0.{1}:/home/pi/wpa_supplicant.conf'
cmd_mv = r'ssh -i {0} pi@192.168.0.{1} "sudo mv /home/pi/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf"'
cmd_reboot = r'ssh -i {0} pi@192.168.0.{1} "sudo reboot"'

with open(filename, 'w') as f:
    for ip in ips:
        full_ip = "" + str(ip)
        cmd = cmd_cp.format(path_key, full_ip)
        f.write(cmd + "\n")
        cmd = cmd_mv.format(path_key, full_ip)
        f.write(cmd + "\n")
        cmd = cmd_reboot.format(path_key, full_ip)
        f.write(cmd + "\n")