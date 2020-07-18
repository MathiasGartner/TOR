class Job:
    def __init__(self):
        self.Code = ""
        self.JobParameters = ""

    def __str__(self):
        return "<Job: (Code={}, JobParameters={})>".format(self.Code, self.JobParameters)