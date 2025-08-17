ssh -i C:\Users\Mathias\.ssh\tor pi@192.168.1.97 "mkdir ~/TOR-Interactive && cd ~/TOR-Interactive && find . -mindepth 1 -maxdepth 1 ! -name dist ! -name node_modules -exec rm -r -- {} +"
scp -i C:\Users\Mathias\.ssh\tor -r D:\Sources\TOR-Interactive\app pi@192.168.1.97:/home/pi/TOR-Interactive/
scp -i C:\Users\Mathias\.ssh\tor -r D:\Sources\TOR-Interactive\public pi@192.168.1.97:/home/pi/TOR-Interactive/
scp -i C:\Users\Mathias\.ssh\tor -r D:\Sources\TOR-Interactive\app.js pi@192.168.1.97:/home/pi/TOR-Interactive/
scp -i C:\Users\Mathias\.ssh\tor -r D:\Sources\TOR-Interactive\config.js pi@192.168.1.97:/home/pi/TOR-Interactive/
scp -i C:\Users\Mathias\.ssh\tor -r D:\Sources\TOR-Interactive\configPrivate.js pi@192.168.1.97:/home/pi/TOR-Interactive/
scp -i C:\Users\Mathias\.ssh\tor -r D:\Sources\TOR-Interactive\mdc.scss pi@192.168.1.97:/home/pi/TOR-Interactive/
scp -i C:\Users\Mathias\.ssh\tor -r D:\Sources\TOR-Interactive\package.json pi@192.168.1.97:/home/pi/TOR-Interactive/
scp -i C:\Users\Mathias\.ssh\tor -r D:\Sources\TOR-Interactive\package-lock.json pi@192.168.1.97:/home/pi/TOR-Interactive/
scp -i C:\Users\Mathias\.ssh\tor -r D:\Sources\TOR-Interactive\webpack.config.js pi@192.168.1.97:/home/pi/TOR-Interactive/
ssh -i C:\Users\Mathias\.ssh\tor pi@192.168.1.97 "sudo systemctl daemon-reload;"
ssh -i C:\Users\Mathias\.ssh\tor pi@192.168.1.97 "sudo systemctl restart TORInteractive;"