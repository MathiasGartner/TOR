import datetime

from tor.base import DBManager

startDate = datetime.date(2025, 8, 15)
endDate = datetime.date(2025, 8, 18)

startTime = datetime.time(8, 0)
endTime = datetime.time(19, 0)
slotDuration = datetime.timedelta(minutes=15)
pauseDuration = datetime.timedelta(minutes=30)

day = startDate
while day <= endDate:
    start = datetime.datetime.combine(day, startTime)
    end = datetime.datetime.combine(day, endTime)
    while start + slotDuration <= end:
        DBManager.insertScheduleInterval(start, start + slotDuration)
        start = start + slotDuration + pauseDuration
    day += datetime.timedelta(days=1)