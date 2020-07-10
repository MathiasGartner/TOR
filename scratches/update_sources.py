
#######################################
### generate custom client settings ###
#######################################

def writeCustomFile(material, settings):
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



################################
### update source on clients ###
################################

ips = [102]

path_key = r"C:\Users\Mathias\.ssh\tor"
cmd_delete = r'ssh -i {0} pi@192.168.0.{1} "rm -r tor"'
cmd_copy = r"scp -i {0} -r D:\Sources\TOR\tor pi@192.168.0.{1}:/home/pi"

filename = "update_tor.cmd"

with open(filename, 'w') as f:
    for ip in ips:
        full_ip = "" + str(ip)
        cmd = cmd_delete.format(path_key, full_ip)
        f.write(cmd + "\n")
        cmd = cmd_copy.format(path_key, full_ip)
        f.write(cmd + "\n")