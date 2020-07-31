#!/bin/bash

printf "#### flash TOR-Marlin ####"
printf "mount usb-STM_SD_Flash_Disk-0\:0-part1 ..."
sudo mount /dev/disk/by-id/usb-STM_SD_Flash_Disk-0\:0-part1 /mnt
printf "copy firmware.bin ..."
sudo cp /home/pi/firmware.bin /mnt/
printf "files on SD card:"
ls /mnt
printf "now flashing ..."
torenv/bin/python3 -m tor.client.scripts.serialCmd "M997"
sleep 10
printf "mount SD card again ..."
sudo mount /dev/disk/by-id/usb-STM_SD_Flash_Disk-0\:0-part1 /mnt
printf "files on SD card (firmware.bin should be deleted):"
ls /mnt