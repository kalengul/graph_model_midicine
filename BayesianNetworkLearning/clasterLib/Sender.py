class Sender:
    def __init__(self):
        self.Header = ""
        self.Body = ""
    
    # Добавление параметров для запроса на кластер
    def AddData(self, header, body):
        self.Header = header
        self.Body = body
    
    def Print(self):
        print(f"\n\tHeder: {self.Header} \nBody: {self.Body}")
