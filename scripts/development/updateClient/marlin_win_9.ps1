invoke-expression 'cmd /c start powershell -Command { echo 192.168.1.109; ssh -i C:\Users\Mathias\.ssh\tor pi@192.168.1.109 "sudo rm -r /home/pi/tormarlin"; ssh -i C:\Users\Mathias\.ssh\tor pi@192.168.1.109 "mkdir /home/pi/tormarlin"; scp -i C:\Users\Mathias\.ssh\tor D:\Sources\TOR\resources\TORMarlinFirmware\firmware.bin pi@192.168.1.109:/home/pi/tormarlin/; ssh -i C:\Users\Mathias\.ssh\tor pi@192.168.1.109 "sudo ./scripts/flashTORMarlin.sh"; sleep 5;  }'
