ssh -i C:\Users\Mathias\.ssh\tor pi@192.168.1.104 "sudo rm -r /home/pi/tormarlin"
ssh -i C:\Users\Mathias\.ssh\tor pi@192.168.1.104 "mkdir /home/pi/tormarlin"
scp -i C:\Users\Mathias\.ssh\tor D:\Sources\TOR\resources\TORMarlinFirmware\firmware.bin pi@192.168.1.104:/home/pi/tormarlin/
ssh -i C:\Users\Mathias\.ssh\tor pi@192.168.1.104 "sudo ./scripts/flashTORMarlin.sh"
