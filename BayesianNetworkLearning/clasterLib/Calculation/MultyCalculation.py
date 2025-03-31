class MultyCalculation:
    def __init__(self, calculationList=None):
        self.calculationList = []
        if(calculationList!=None):
            self.calculationList = calculationList.copy()
    
    def Add(self, calculation):
        self.calculationList.append(calculation)

    def TypeOf(self):
        return "MultyCalculation"
    
    def GetJSON():
        return 
