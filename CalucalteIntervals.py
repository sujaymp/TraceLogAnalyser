import csv
from datetime import datetime
import sys

keys =[]
keys.append("Start Calling - Dashboard API")                    #0
keys.append("End Calling - ValidateHttpGetScope")               #1
keys.append("Start Calling - Configuration DB")                 #2
keys.append("End Calling - Configuration DB")                   #3
keys.append("Start Calling - TimeSeries API")                   #4
keys.append("End Calling - TimeSeries API")                     #5
keys.append("Start Calling - Construct Trend Data response")    #6
keys.append("End Calling - Construct Trend Data response")      #7
keys.append("End Calling - Dashboard API")                      #8


class AppInsightLog:
    
    def __init__(self,fileName):
        self.__content = []
        self.__file= fileName
        self.__timestamps = []
        self.__batches = {}
        with open(fileName, newline='') as csvfile:
            logreader = csv.reader(csvfile, delimiter=',')
            for line in logreader:
                self.__content.append(line)
            count = 0    
            for row in self.__content:
                for key in keys:
                    if key in row[1]:
                        timestamp = datetime.strptime(row[1][11:37],'%m/%d/%Y %I:%M:%S.%f %p')                       
                        self.__timestamps.append((key,timestamp))
        self.Content =self.__content
        self.TS =self.__timestamps
               
    def Seggregate(self):
        count = 0
        index = 0
        while(index<len(self.__timestamps)-1):
            self.__batches[count] = []
            if index+37 > len(self.__timestamps):
                max = len(self.__timestamps)-1
            else:
                max = index+37
            for i in range(index,max):
                self.__batches[count].append(self.__timestamps[i])
            index +=37
            count += 1
        self.UpdateOrder()
            
    def Fix0to3(self, batch):
        fi=batch[0]
        se=batch[1]
        th=batch[2]        
        for index in range(0,3):
            if batch[index][0] == keys[0]:
                fi = batch[index]
            elif batch[index][0] == keys[1]:
                se = batch[index]
            elif batch[index][0] == keys[2]:
                th = batch[index]            
        batch[0]=fi
        batch[1]=se
        batch[2]=th

    def Fix4(self, batch):        
        for index in range(4,len(batch)-4):            
            cur = batch[index]            
            fi=si=se=fo =''
            if cur[0] == keys[4]:
                for j in range(index+1,index+5):                    
                    if batch[j][0] == keys[5]:
                        fi = batch[j]
                    elif batch[j][0] == keys[6]:
                        si = batch[j]
                    elif batch[j][0] == keys[7]:
                        se = batch[j]
                    elif batch[j][0] == keys[4]:
                        fo = batch[j]
                    elif batch[j][0] == keys[8]:
                        fo = batch[j] 
                batch[index+1] = fi
                batch[index+2] = si
                batch[index+3] = se
                batch[index+4] = fo
                              
    def FixTheOrder(self, batch):                        
##        print("------------------")        
##        self.PrintBatch(batch)
        self.Fix0to3(batch)
        self.Fix4(batch)
##        self.PrintBatch(batch)
        
    def UpdateOrder(self):        
        if self.__batches:
            batchno=1
            self.__rows=[]
            for key in self.__batches.keys():                
                self.FixTheOrder(self.__batches[key])                

    def GetIntervals(self, batch):
        values = []
        for i in range(0,len(batch)-1):
            values.append((batch[i+1][0],batch[i+1][1]-batch[i][1]))
        values.append(("total", batch[len(batch)-2][1] - batch[0][1]))
        return values
    
    def CalcIntervalsInRows(self):
        if self.__batches:
            batchno=1
            self.__rows=[]
            for key in self.__batches.keys():
                batch = self.__batches[key]
                values = self.GetIntervals(batch)
                row = str(batchno);
                batchno+=1
                for value in values:
                    row+=", " + str(value[1])
                self.__rows.append(row)
            
    def CalcIntervalsWithLabels(self):
        if self.__batches:
            batchno=1
            self.__lines=[]
            for key in self.__batches.keys():
                batch = self.__batches[key]
                values = self.GetIntervals(batch)
                self.__lines.append("batch" + str(batchno)+", ")
                print("batch " + str(batchno))
                batchno+=1
                for value in values:                    
                    self.__lines.append(value[0].ljust(45) +"," + str(value[1]))

    def WriteToFileAsRows(self):
        fh = open(self.__file+ "_intervals_rows.csv", "w")
        fh.writelines('\n'.join(self.__rows))
        fh.close()

    def WriteToFileWithLabels(self):
        fh = open(self.__file+ "intervals_with_labels.csv", "w")
        fh.writelines('\n'.join(self.__lines))
        fh.close()

    def PrintBatch(self,batch):        
        for index in range(0,len(batch)):
            if batch[index][0] == keys[0]:
                print('0 - '+ batch[index][0].ljust(50) + str(batch[index][1]))
            elif batch[index][0] == keys[1]:
                print('1- '+ batch[index][0].ljust(50)  + str(batch[index][1]))
            elif batch[index][0] == keys[2]:
                print('2- '+ batch[index][0].ljust(50)  + str(batch[index][1]))
            elif batch[index][0] == keys[3]:
                print('3- '+ batch[index][0].ljust(50)  + str(batch[index][1]))
            elif batch[index][0] == keys[4]:
                print("4- "+ batch[index][0].ljust(50)  + str(batch[index][1]))
            elif batch[index][0] == keys[5]:
                print("5- "+ batch[index][0].ljust(50)  + str(batch[index][1]))
            elif batch[index][0] == keys[6]:
                print("6- "+ batch[index][0].ljust(50)  + str(batch[index][1]))
            elif batch[index][0] == keys[7]:
                print("7- "+ batch[index][0].ljust(50)  + str(batch[index][1]))
            elif batch[index][0] == keys[8]:
                print("8- "+ batch[index][0].ljust(50)  + str(batch[index][1]))            
        print("------------------")
    
    def PrintContent(self):
        for item in self.__timestamps:                                        
            print(item[0].ljust(45) + ": " +str(item[1]) )

    def PrintBatches(self):
        for key in self.__batches.keys():
            print(key)
            for item in self.__batches[key]:
                print(item[0].ljust(45) + ": " +str(item[1]) )
                
fileName = sys.argv[1]
log = AppInsightLog(fileName)
print(fileName)
log.Seggregate()
log.CalcIntervalsWithLabels()
log.WriteToFileWithLabels()
log.CalcIntervalsInRows()
log.WriteToFileAsRows()





    


        
