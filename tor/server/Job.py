class Job:
    def __init__(self):
        self.ClientId = -1
        self.JobCode = ""
        self.JobParameters = ""
        self.ExecuteAt = None

    def __str__(self):
        return "<Job: (ClientId={}, JobCode={}, JobParameters={}, ExecuteAt={})>".format(self.ClientId, self.JobCode, self.JobParameters, self.ExecuteAt)

class DefaultJobs:
    WAIT = Job()
    WAIT.JobCode = "W"

    RUN = Job()
    RUN.JobCode = "R"

    RUN_AND_WAIT = Job()
    RUN_AND_WAIT.JobCode = "RW"
    # JobParameters: "r w t"
    # run r times, then wait w times for t seconds
    RUN_AND_WAIT.JobParameters = "4 60 6"

    QUIT = Job()
    QUIT.JobCode = "Q"

    SETTINGS = Job()
    SETTINGS.JobCode = "S"

    HOME = Job()
    HOME.JobCode = "H"

    HOME_AND_PICKUP = Job()
    HOME_AND_PICKUP.JobCode = "HH"
