
from SC_GenerateParamSet import genParSet
from RunParSet import runSingleFolder
import os

def readInputFile():
    fn = 'SCInput.txt'
    keys=['runFolder','inputDir','parFN','irrFN','totaln','nfold','randomseed','saveAllPFData','saveTotStoSL','saveRecCurve_Total', 'saveRecCurve_Layers', 'saveCLMSL', 'saveStoStats']
    values = []

    # get key values from inputfile
    with open(fn,'r') as f:
        for line in f:
            #print(line)
            currValue = line.split('#')[0]
            currValue = currValue.strip()

            if currValue.isnumeric():
                currValue = int(currValue)
            elif currValue == 'True':
                currValue = True
            elif currValue == 'False':
                currValue = False

            values.append(currValue)

    return dict(zip(keys,values)) #dictionary of key names and values

def createNewRun():

    # get run 'meta' parameters
    inputData = readInputFile()

    # generate run simulation parameters
    genParSet(inputData['totaln'],inputData['parFN'],inputData['runFolder'],inputData['nfold'],inputData['randomseed'])
    
    # move into run directory
    os.chdir(inputData['runFolder'])

    # print out a log file with metaparameters
    outfn = 'runMetaPars.txt'
    with open(outfn,'w') as f:
        f.write(str(inputData))

    # enter parallel code here VVVVVVV
    runSingleFolder(1, inputData) 

def main():
    createNewRun()

if __name__ == "__main__":

    main() # main is passed the line in the parameter file that you want to pull