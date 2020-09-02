
import pandas as pd
import numpy as np
import random
import sys
import os
import math
#import ReadPFB as pfb
import pfio #Hoang's Parflow Read/Write Module
import time
import datetime

from RunParSet import getAllInputRows, pfidbGen, processDataSC,createRunDir


folderName = 'SmallFixedTest'
os.chdir(folderName)
runset = int(sys.argv[1])

# change directory
# first we'll create a single run folder

runset = runset - 1 # the GNU parallel is running a sequence from 1-5 but python wants 0-4, correct here.
print('Running Folder ' + str(runset))
newRunDir = createRunDir(runset)

parameterFN = "ParameterSets_AutoGenPY_" + str(runset) + ".csv"

# get all run parameters
allPar = getAllInputRows(parameterFN)
nsets = len(allPar.index)

os.chdir(newRunDir)

outfn = '../runTimes_' + str(runset) + '.csv'

for currset in range(nsets):
    print('Running Set ' + str(currset))

    # get current parameter set
    runParameters = allPar.iloc[currset]

    # create your pfidb file
    pfidbGen(runParameters)
    #print('PfidbGenerated')

    # run your program
    #os.system("$PARFLOW_DIR/bin/parflow test > parflow.test.log")
    start = time.time()
    os.system("~/parflow/install/bin/parflow test  > parflow.test.log")
    end = time.time()

    # save runtime
    totaltime = end - start
    f = open(outfn,'a')
    testn = runParameters['n']
    f.write(str(testn) + "," + str(totaltime))
    f.write("\n")
    f.close()

    #print('Parflow Run Done')

    # process the data
    #nclm = runParameters['Solver.CLM.RootZoneNZ']
    #totalLayers = runParameters['ComputationalGrid.NZ']
    #runLen = runParameters['TimingInfo.StopTime']
    try:
        processDataSC(runParameters)
    except: 
        print('processing failed for Run '+str(currset))
    #print('Processing Complete')
    #print('Deleting old pfidb file')
    os.system('rm test.pfidb')
    os.system('rm test.out*')

    # delete the directory when all runs have been completed
    #os.chdir('../')
    #os.system('rm -r ' + newRunDir)

