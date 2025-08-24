import datetime

from tor.base import DBManager

startDate = datetime.date(2025, 8, 24)
endDate = datetime.date(2025, 8, 24)

# INFO: Database timezone is UTC
#       Database 08:00 is Austria 10:00
startTime = datetime.time(10, 25)
endTime = datetime.time(10, 27)
slotDuration = datetime.timedelta(minutes=2)
pauseDuration = datetime.timedelta(minutes=10)

day = startDate
while day <= endDate:
    start = datetime.datetime.combine(day, startTime)
    end = datetime.datetime.combine(day, endTime)
    while start + slotDuration <= end:
        DBManager.insertScheduleInterval(start, start + slotDuration)
        start = start + slotDuration + pauseDuration
    day += datetime.timedelta(days=1)
