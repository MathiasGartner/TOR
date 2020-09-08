import argparse
import copy
from datetime import datetime, timedelta
import time

from tor.base import DBManager
from tor.server.Job import Job
import tor.TORSettings as ts

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

jQ = Job()
jQ.JobCode = "Q"

jS = Job()
jS.JobCode = "S"

jH = Job()
jH.JobCode = "H"

jHH = Job()
jHH.JobCode = "HH"

j1 = Job()
j1.JobCode = "P"
j1.JobParameters = 1
j1.ExecuteAt = datetime.now() + timedelta(hours=-1) + timedelta(seconds=10)

j2 = Job()
j2.JobCode = "P"
j2.JobParameters = 2
j2.ExecuteAt = datetime.now() + timedelta(hours=-1) + timedelta(minutes=1, seconds=20)

j3 = Job()
j3.JobCode = "P"
j3.JobParameters = 3
j3.ExecuteAt = datetime.now() + timedelta(hours=-1) + timedelta(seconds=20)

j4 = Job()
j4.JobCode = "P"
j4.JobParameters = 4
j4.ExecuteAt = datetime.now() + timedelta(hours=-1) + timedelta(seconds=20)

j5 = Job()
j5.JobCode = "P"
j5.JobParameters = 5
j5.ExecuteAt = datetime.now() + timedelta(hours=-1) + timedelta(seconds=20)

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

jobsToCreate = [jW]
#jobsToCreate = [jH, jW]
#ids = [15]4

ids = []
#positions = [1, 2, 3, 4, 5, 6, 7, 8, 9]
positions = range(1, 28)
#positions = [1, 2, 3]
#positions = [16]
#positions = [4, 5, 6]
#positions = [1]

#from itertools import chain
#positions = chain(range(1, 22), range(23, 28))
#positions = chain(range(1, 21), range(23, 28))

for p in positions:
    ids.append(DBManager.getIdByPosition(p))

#if len(positions) == 0:
#    ids = [15]

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