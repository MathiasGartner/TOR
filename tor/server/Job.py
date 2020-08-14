class Job:
    def __init__(self):
        self.JobCode = ""
        self.JobParameters = ""
        self.ExecuteAt = None

    def __str__(self):
        return "<Job: (JobCode={}, JobParameters={}, ExecuteAt={})>".format(self.JobCode, self.JobParameters, self.ExecuteAt)