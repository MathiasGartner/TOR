#!/bin/bash

printf "#### flash TOR-Marlin ####\n"
printf "mount usb-STM_SD_Flash_Disk-0\:0-part1 ...\n"
sudo mount /dev/disk/by-id/usb-STM_SD_Flash_Disk-0\:0-part1 /mnt
sudo rm -r /mnt/*
printf "copy firmware.bin ...\n"
sudo cp /home/pi/tormarlin/firmware.bin /mnt/
printf "files on SD card:\n"
ls -l /mnt
sudo umount /mnt
printf "now flashing ...\n"
torenv/bin/python3 -m tor.client.scripts.serialCmd "M997"
sleep 20
printf "mount SD card again ...\n"
sudo mount /dev/disk/by-id/usb-STM_SD_Flash_Disk-0\:0-part1 /mnt
printf "files on SD card (firmware.bin should be deleted):\n"
ls -l /mnt