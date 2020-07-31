
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
ips =[107]
path_key = tsl.PATH_TO_SSH_KEY

#### TOR ####
filename = "update_tor.cmd"
cmd_delete = r'ssh -i {0} pi@192.168.0.{1} "sudo rm -r tor"'
cmd_copy = r"scp -i {0} -r " + tsl.PATH_TO_TOR_SOURCE + r"\TOR\tor pi@192.168.0.{1}:/home/pi"
cmd_delete_service = r'ssh -i {0} pi@192.168.0.{1} "sudo rm -r scripts"'
cmd_copy_service = r"scp -i {0} -r " + tsl.PATH_TO_TOR_SCRIPTS + r"\TOR\scripts pi@192.168.0.{1}:/home/pi"
cmd_copy_service_system = r'ssh -i {0} pi@192.168.0.{1} "sudo cp /home/pi/scripts/TORClient.service /etc/systemd/system/TORClient.service"'

with open(filename, 'w') as f:
    for ip in ips:
        full_ip = "" + str(ip)
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

#### TOR-Marlin ####
filename = "update_tor_marlin.cmd"
cmd_delete = r'ssh -i {0} pi@192.168.0.{1} "sudo rm ./tormarlin/firmware.bin"'
cmd_copy = r"scp -i {0} " + tsl.PATH_TO_TOR_MARLIN_FIRMWARE + r" pi@192.168.0.{1}:/home/pi/tormarlin/"
cmd_flash = r'ssh -i {0} pi@192.168.0.{1} "sudo ./scripts/flashTORMarlin.sh"'

with open(filename, 'w') as f:
    for ip in ips:
        full_ip = "" + str(ip)
        cmd = cmd_delete.format(path_key, full_ip)
        f.write(cmd + "\n")
        cmd = cmd_copy.format(path_key, full_ip)
        f.write(cmd + "\n")
        cmd = cmd_flash.format(path_key, full_ip)
        f.write(cmd + "\n")