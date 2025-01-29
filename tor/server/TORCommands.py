
class TORCommands:
    # r'ssh -i {0} pi@{1} "sudo rm -r tor; sudo rm -r scripts"'
    SERVER_SSH_CONNECTION = "ssh -i \"{0}\" pi@{1}"
    CLIENT_SSH_CONNECTION = "ssh -i \"{0}\" pi@{1}"
    CLIENT_SSH_CONNECTION_X11ROOT = "ssh -X -i \"{0}\" root@{1}"

    SERVER_SERVICE_START = "sudo systemctl daemon-reload; sudo systemctl restart TORServer"
    SERVER_SERVICE_STOP = "sudo systemctl stop TORServer"

    INTERACTIVE_START = "sudo systemctl daemon-reload; sudo systemctl restart TORInteractive"
    INTERACTIVE_STOP = "sudo systemctl stop TORInteractive"

    #CLIENT_PING = "ping -i 0.2 -c 1 {}"
    #CLIENT_PING = "ping -c 1 {}"
    CLIENT_PING = "ping -w 1000 -n 1 {}"

    MSG_CLIENT_SERVICE_START = {"TORCLIENT": "START"}
    MSG_CLIENT_SERVICE_STOP = {"TORCLIENT": "STOP"}

    MSG_CLIENT_TURN_ON_LEDS = {"LED": "ON"}
    MSG_CLIENT_TURN_OFF_LEDS = {"LED": "OFF"}

    CLIENT_START_CALIBRATION = "cd /home/pi/; torenv/bin/python3 -m tor.client.GUI.calibrate"