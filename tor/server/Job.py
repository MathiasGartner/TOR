class Job:
    def __init__(self):
        self.JobCode = ""
        self.JobParameters = ""

    def __str__(self):
        return "<Job: (JobCode={}, JobParameters={})>".format(self.JobCode, self.JobParameters)