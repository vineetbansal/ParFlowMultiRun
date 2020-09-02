
# Converted from 'SC_GenerateParameterSets.R'

def genParSet(n,inputFile,testDir,numFiles):

   import pandas as pd
   import numpy as np
   import random
   import sys
   import os

   ###################################
   ##     CREATE PARAMETER SETS     ##
   ###################################

   # load csv file of keys and values
   inputVarDF=pd.read_csv(inputFile, delimiter=',')
   inputVarDF.columns = ['KeyName', 'SCValue', 'inputType', 'set', 'MinRange', 'MaxRange']

   ##### Variable Variables ####
   # evaluate variable variables
   varVars = inputVarDF[inputVarDF['set'] == 'Variable']
   varNames = np.unique(varVars['SCValue']) # some variables may be set together, so read unique names

   # create parameter data sets
   parDataSets={'n': list(range(0,n))}
   parDF=pd.DataFrame(parDataSets)

   print(inputVarDF.head())

   for var in varNames:
      print(var)
      varIdx = varVars[varVars['SCValue']==var]
      if varIdx['inputType'].iat[0] =='double': 
         varmin = int(float(varIdx['MinRange'].iat[0])*1000*n)
         varmax = int(float(varIdx['MaxRange'].iat[0])*1000*n)
         varValues = np.array(random.sample(range(varmin,varmax),n))/(1000*n)
      elif varIdx['inputType'].iat[0] =='integer':
         varmin = int(varIdx['MinRange'].iat[0])
         varmax = int(varIdx['MaxRange'].iat[0])
         intRange = [format(x, '01d') for x in range(varmin,varmax)]
         varValues = np.array(random.choices(intRange,k=n))
         varValues = varValues.astype(int)
      else:
         varPos = varIdx['MinRange'].iat[0].split(sep=" ")
         varValues = np.array(random.choices(varPos,k=n))
      for name in varIdx['KeyName']:
         parDF[name]=varValues


   ##### Constant Variables ####
   # add on constant variables
   # grab constant variables, these won't need to be changed, can be read straight in
   constantVars = inputVarDF[inputVarDF['set'] == 'Constant']
   constantKeys = constantVars['KeyName']

   for key in constantKeys:
      #print(key)
      keyRow = constantVars[constantVars['KeyName']==key]
      keyValue = keyRow['SCValue'].iat[0]
      parDF[key] = [keyValue] * n


   ##### Calculate Variables ####
   # calculate variables
   calcVars = inputVarDF[inputVarDF['set'] == 'Calculate']

   ##### Irrigation Variables ####
   if 'Solver.CLM.IrrigationStartTime' in inputVarDF.KeyName.values:
      # randomly generate volumes, durrations, and timings
      irrVols = [2.5,5,10]
      irrDurrs = [1,2.5,5,10]
      irrTiming = ['morn','day','eve','night']

      irrVolValues = np.array(random.choices(irrVols,k=n))
      irrDurrValues = np.array(random.choices(irrDurrs,k=n))
      irrTimingValues = np.array(random.choices(irrTiming,k=n))

      # convert to irrigation start and stop times
      irrTimingDF = pd.read_csv('SC_IrrigationTiming_20200813.csv')
      irrStart = []
      irrEnd = []

      for i in range(len(irrDurrValues)):
         dfsub = irrTimingDF[(irrTimingDF['durration'] == irrDurrValues[i]) & (irrTimingDF['timing'] == irrTimingValues[i])] 
         irrStart.append(dfsub['start'].iloc[0])
         irrEnd.append(dfsub['end'].iloc[0])

      parDF['Solver.CLM.IrrigationStartTime'] = irrStart
      parDF['Solver.CLM.IrrigationStopTime'] = irrEnd
      irrRate = irrVolValues/irrDurrValues/3600
      parDF['Solver.CLM.IrrigationRate'] = irrRate
   
   # make sure clm soil layer not greater than the number of layers
   # first check if these variables exist
   if (('Solver.CLM.SoiLayer' in inputVarDF.KeyName.values) & ('Solver.CLM.RootZoneNZ' in inputVarDF.KeyName.values)):
      clmLayDif = parDF['Solver.CLM.SoiLayer'] - parDF['Solver.CLM.RootZoneNZ'] #check difference between soilLayer and RootZoneNZ 
      #parDF['Solver.CLM.SoiLayer'][clmLayDif > 0] = parDF['Solver.CLM.RootZoneNZ'][clmLayDif > 0] # if soilLayer > RootZoneNZ then replace with the RootZoneNZ
      parDF['Solver.CLM.SoiLayer'] = [parDF['Solver.CLM.SoiLayer'][i] if clmLayDif[i] < 0 else parDF['Solver.CLM.RootZoneNZ'][i] for i in range(len(parDF))]

   # calculate variables
   for i in range(len(calcVars)):
      currRow = calcVars.iloc[i,:]
      allargs = currRow.SCValue.split(" ")
      op = allargs[0]
      firstArg = allargs[1]

      # check if first argument is a string or a number
      try:
         firstValue = int(firstArg)
         parValue = pd.Series(np.repeat(firstValue,n))
      except:
         parValue = parDF[firstArg]

         # check variable type & convert
         vartype = inputVarDF[inputVarDF['KeyName']==firstArg].inputType
         if vartype.iat[0] == 'double':
            parValue = parValue.astype('float')

         else:
            parValue = parValue.astype('int')


      for j in range(len(allargs)-2):
          currarg = allargs[j + 2]
         
          currValue = parDF[currarg]

          # check variable type & convert
          vartype = inputVarDF[inputVarDF['KeyName']==currarg].inputType
          if vartype.iat[0] == 'double':
              currValue = currValue.astype('float')
          else:
              currValue = currValue.astype('int')

          if op == 'divide':
              parValue = parValue.divide(currValue)
          elif op == 'multiply':
              parValue = parValue.multiply(currValue)
          elif op == 'add':
              parValue = parValue.add(currValue)
          elif op == 'subtract':
              parValue = parValue.subtract(currValue)
      parDF[currRow.KeyName] = parValue 

   # create new test directory
   os.system('mkdir ' + testDir)
   os.system('mkdir ' + testDir + '/FullRunData')
   os.system('mkdir ' + testDir + '/SingleLineOutput')
   os.system('mkdir ' + testDir + '/RunTimeData')
   os.system('mkdir ' + testDir + '/TotalStorageData')
   os.system('cp -r clm_input/ ' + testDir)

   # write out parameter data set variables to number of files
   print(n)
   print(numFiles)
   numFiles = int(numFiles)

   if numFiles == 1:
      outfn = testDir + '/ParameterSets_AutoGenPY.csv'
      parDF.to_csv(outfn,index=False)
   else:
      filesPerOutF = n/numFiles
      for nf in range(numFiles):

         # cut the out parameter set
         fileStart = nf * filesPerOutF
         fileEnd = (nf+1) * filesPerOutF - 1
         parDF_sub = parDF.loc[fileStart:fileEnd,:]

         # save the data
         outfn = testDir + '/ParameterSets_AutoGenPY_' + str(nf) + '.csv'
         parDF_sub.to_csv(outfn,index=False)


def main():
    import sys
    n = int(sys.argv[1])
    inputFile = sys.argv[2]
    testDir =sys.argv[3]
    nfiles = sys.argv[4]
    genParSet(n,inputFile,testDir,nfiles)

if __name__ == "__main__":

    main() # main will take in command line input for genParSet parameters

