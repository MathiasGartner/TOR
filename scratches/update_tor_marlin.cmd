ssh -i C:\Users\Mathias\.ssh\tor pi@192.168.0.112 "sudo rm firmware.bin"
scp -i C:\Users\Mathias\.ssh\tor -r D:\Sources\TOR-Marlin\.pio\build\STM32F103RC_btt_512K_USB\firmware.bin pi@192.168.0.112:/home/pi
ssh -i C:\Users\Mathias\.ssh\tor pi@192.168.0.112 "sudo ./flashTORMarlin.sh"
