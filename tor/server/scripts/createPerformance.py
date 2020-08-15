import copy
from datetime import datetime, timedelta
import time

from tor.base import DBManager
from tor.server.Job import Job

jW = Job()
jW.JobCode = "W"

j1 = Job()
j1.JobCode = "P"
j1.JobParameters = 1
j1.ExecuteAt = datetime.now() + timedelta(hours=-1) + timedelta(minutes=2)

j2 = Job()
j2.JobCode = "P"
j2.JobParameters = 2
j2.ExecuteAt = datetime.now() + timedelta(hours=-1) + timedelta(minutes=1, seconds=20)

ids = [19]
jobsToCreate = [j2, jW]

for jobToCreate in jobsToCreate:
    jobs = []
    for id in ids:
        j = copy.deepcopy(jobToCreate)
        j.ClientId = id
        jobs.append(j)
    DBManager.saveJobs(jobs)
    time.sleep(10)