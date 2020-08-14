import copy
from datetime import datetime, timedelta

from tor.base import DBManager
from tor.server.Job import Job

j1 = Job()
j1.ClientId = 22
j1.JobCode = "P"
j1.ExecuteAt = datetime.now() + timedelta(hours=-1) + timedelta(minutes=2)

j2 = copy.deepcopy(j1)
j2.ClientId = 28

DBManager.saveJobs([j1, j2])