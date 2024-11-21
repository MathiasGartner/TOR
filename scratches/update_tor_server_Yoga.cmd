ssh -i C:\Users\Mathias\.ssh\tor pi@192.168.1.97 "sudo rm -r ~/TOR/tor; sudo rm -r ~/TOR/scripts; sudo rm -r ~/TOR/scratches; sudo rm -r ~/TOR/db"
scp -i C:\Users\Mathias\.ssh\tor -r D:\Sources\TOR\tor pi@192.168.1.97:/home/pi/TOR
scp -i C:\Users\Mathias\.ssh\tor -r D:\Sources\TOR\scripts pi@192.168.1.97:/home/pi/TOR
scp -i C:\Users\Mathias\.ssh\tor -r D:\Sources\TOR\scratches pi@192.168.1.97:/home/pi/TOR
scp -i C:\Users\Mathias\.ssh\tor -r D:\Sources\TOR\db pi@192.168.1.97:/home/pi/TOR
scp -i C:\Users\Mathias\.ssh\tor -r D:\Sources\TOR\position_verification\model\position_verification*.tflite pi@192.168.1.97:/home/pi/TOR/position_verification
ssh -i C:\Users\Mathias\.ssh\tor pi@192.168.1.97 "sudo cp /home/pi/TOR/scripts/TORServer.service /etc/systemd/system/TORServer.service;"
ssh -i C:\Users\Mathias\.ssh\tor pi@192.168.1.97 "sudo systemctl daemon-reload;"
