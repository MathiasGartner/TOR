ssh -i C:\Users\Mathias\.ssh\tor pi@192.168.1.123 "sudo rm -r tor; sudo rm -r scripts; mkdir scripts"
scp -i C:\Users\Mathias\.ssh\tor -r D:\Sources/TOR/tor pi@192.168.1.123:/home/pi
scp -i C:\Users\Mathias\.ssh\tor -r D:\Sources/TOR/scripts/client/* pi@192.168.1.123:/home/pi/scripts/
ssh -i C:\Users\Mathias\.ssh\tor pi@192.168.1.123 "sudo cp /home/pi/scripts/TORClient.service /etc/systemd/system/TORClient.service; sudo chmod +x /home/pi/scripts/*.sh"
