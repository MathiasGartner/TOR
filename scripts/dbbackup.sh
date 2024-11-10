#!/bin/sh

# for registering as a crontab, e.g. hourly backups with:
# 0 * * * * root /home/pi/dbbackup.sh &>/dev/null
# this is done on Raspi4 in /etc/cron.d/mysql

mkdir -p /home/pi/backup/mysql/$(date +%Y)/$(date +%m)/$(date +%d)
mysqldump -uroot -p'PASSWORD' --all-databases > /home/pi/backup/mysql/$(date +%Y)/$(date +%m)/$(date +%d)/db_$(date +%Y%m%d%H%M%S).sql