invoke-expression 'cmd /c start powershell -Command { echo 192.168.1.106; ssh -i C:\Users\Mathias\.ssh\tor pi@192.168.1.106 "sudo rm -r /home/pi/tormarlin"; ssh -i C:\Users\Mathias\.ssh\tor pi@192.168.1.106 "mkdir /home/pi/tormarlin"; scp -i C:\Users\Mathias\.ssh\tor D:\Sources\TOR\resources\TORMarlinFirmware\firmware.bin pi@192.168.1.106:/home/pi/tormarlin/; ssh -i C:\Users\Mathias\.ssh\tor pi@192.168.1.106 "sudo ./scripts/flashTORMarlin.sh"; sleep 5;  }'
