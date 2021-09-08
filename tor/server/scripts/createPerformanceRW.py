import copy

from tor.base import DBManager
from tor.server.Job import Job

jRW = Job()
jRW.JobCode = "RW"
#JobParameters: "r w t"
#run r times, then wait w times for t seconds
jRW.JobParameters = "3 70 6"

ids = []
positions = range(1, 28)

for p in positions:
    ids.append(DBManager.getIdByPosition(p))

jobToCreate = jRW
jobs = []
for id in ids:
    j = copy.deepcopy(jobToCreate)
    j.ClientId = id
    jobs.append(j)
DBManager.saveJobs(jobs)