class Job:
    def __init__(self):
        self.ClientId = -1
        self.JobCode = ""
        self.JobParameters = ""
        self.ExecuteAt = None

    def __str__(self):
        return "<Job: (ClientId={}, JobCode={}, JobParameters={}, ExecuteAt={})>".format(self.ClientId, self.JobCode, self.JobParameters, self.ExecuteAt)