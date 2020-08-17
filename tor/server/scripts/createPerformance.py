import argparse
import copy
from datetime import datetime, timedelta
import time

from tor.base import DBManager
from tor.server.Job import Job

parser = argparse.ArgumentParser()
parser.add_argument("-run", dest="run", action="store_true")
parser.add_argument("-start", dest="start", action="store_true")
parser.add_argument("-wait", dest="wait", action="store_true")
parser.add_argument("-thenwait", dest="thenwait", action="store_true")
parser.add_argument("-id", dest="id", type=int, default=None)
args = parser.parse_args()

jW = Job()
jW.JobCode = "W"

jR = Job()
jR.JobCode = "R"

j1 = Job()
j1.JobCode = "P"
j1.JobParameters = 1
j1.ExecuteAt = datetime.now() + timedelta(hours=-1) + timedelta(minutes=2)

j2 = Job()
j2.JobCode = "P"
j2.JobParameters = 2
j2.ExecuteAt = datetime.now() + timedelta(hours=-1) + timedelta(minutes=1, seconds=20)

jobsToCreate = []

if args.run:
    jobsToCreate.append(jR)
elif args.start:
    jobsToCreate.append(j2)
elif args.wait:
    jobsToCreate.append(jW)

if args.thenwait:
    jobsToCreate.append(jW)

if args.id is not None:
    ids = int(args.id)

#jobsToCreate = [j2, jW]
#ids = [19]

if not isinstance(ids, list):
    ids = [ids]
for jobToCreate in jobsToCreate:
    jobs = []
    for id in ids:
        j = copy.deepcopy(jobToCreate)
        j.ClientId = id
        jobs.append(j)
    DBManager.saveJobs(jobs)
    time.sleep(10)