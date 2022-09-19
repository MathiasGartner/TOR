
from tor.base import DBManager
from tor.base import MailManager

try:
    data = DBManager.getResultStatistics("JMAF2022")
    MailManager.sendStatisticMail(data)
except Exception as e:
    print("error sending mail")
    print("{}".format(repr(e)))