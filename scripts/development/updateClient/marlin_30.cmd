ssh -i C:\Users\Mathias\.ssh\tor pi@192.168.0.81 "sudo rm -r /home/pi/tormarlin"
ssh -i C:\Users\Mathias\.ssh\tor pi@192.168.0.81 "mkdir /home/pi/tormarlin"
scp -i C:\Users\Mathias\.ssh\tor D:\Sources\TOR\resources\TORMarlinFirmware\firmware.bin pi@192.168.0.81:/home/pi/tormarlin/
ssh -i C:\Users\Mathias\.ssh\tor pi@192.168.0.81 "sudo ./scripts/flashTORMarlin.sh"
