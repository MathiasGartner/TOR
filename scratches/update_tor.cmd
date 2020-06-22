ssh -i C:\Users\Mathias\.ssh\tor pi@192.168.0.101 "rm -r tor"
scp -i C:\Users\Mathias\.ssh\tor -r D:\Sources\TOR\tor pi@192.168.0.101:/home/pi
ssh -i C:\Users\Mathias\.ssh\tor pi@192.168.0.102 "rm -r tor"
scp -i C:\Users\Mathias\.ssh\tor -r D:\Sources\TOR\tor pi@192.168.0.102:/home/pi
ssh -i C:\Users\Mathias\.ssh\tor pi@192.168.0.104 "rm -r tor"
scp -i C:\Users\Mathias\.ssh\tor -r D:\Sources\TOR\tor pi@192.168.0.104:/home/pi
