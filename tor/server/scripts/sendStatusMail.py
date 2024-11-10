
# for registering as a crontab, e.g. hourly updates with:
# 0 * * * * cd /home/pi/TOR && sudo /home/pi/TOR/torenvRP4/bin/python3 -u -m tor.server.scripts.sendStatusMail
# this is done on Raspi4 in <sudo crontab -e>

from tor.base import DBManager
from tor.base import MailManager

try:
    data = DBManager.getResultStatistics("JMAF2022")
    MailManager.sendStatisticMail(data)
except Exception as e:
    print("error sending mail")
    print("{}".format(repr(e)))