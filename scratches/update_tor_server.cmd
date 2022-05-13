ssh -i ~/.ssh/tor pi@192.168.1.97 "sudo rm -r ~/TOR/tor; sudo rm -r ~/TOR/scripts; sudo rm -r ~/TOR/scratches; sudo rm -r ~/TOR/db"
scp -i ~/.ssh/tor -r ~/Sources/TOR/tor pi@192.168.1.97:/home/pi/TOR
scp -i ~/.ssh/tor -r ~/Sources/TOR/scripts pi@192.168.1.97:/home/pi/TOR
scp -i ~/.ssh/tor -r ~/Sources/TOR/scratches pi@192.168.1.97:/home/pi/TOR
scp -i ~/.ssh/tor -r ~/Sources/TOR/db pi@192.168.1.97:/home/pi/TOR
ssh -i ~/.ssh/tor pi@192.168.1.97 "sudo cp /home/pi/TOR/scripts/TORServer.service /etc/systemd/system/TORServer.service;"
ssh -i ~/.ssh/tor pi@192.168.1.97 "sudo systemctl daemon-reload;"