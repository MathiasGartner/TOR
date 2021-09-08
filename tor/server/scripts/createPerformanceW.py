import copy

from tor.base import DBManager
from tor.server.Job import Job

jW = Job()
jW.JobCode = "W"

ids = []
positions = range(1, 28)

for p in positions:
    ids.append(DBManager.getIdByPosition(p))

jobToCreate = jW
jobs = []
for id in ids:
    j = copy.deepcopy(jobToCreate)
    j.ClientId = id
    jobs.append(j)
DBManager.saveJobs(jobs)