class StatusCommunication:
    def __init__(self):
        self.Status = ""
        self.timeDelayStatus = 0
        self.threadAgentCount = 0

    def Set(self, status):
        self.Status = status

    def Print(self):
        print(f"-----------------------\nStatus: {self.Status} \ntimeDelayStatus: {self.timeDelayStatus} \nthreadAgentCount: {self.threadAgentCount}-----------------------\n")