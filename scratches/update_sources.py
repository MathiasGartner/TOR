ips = [101, 102, 104]

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