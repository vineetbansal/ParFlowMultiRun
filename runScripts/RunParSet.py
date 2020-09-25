#Run Parameter Sets
# Gets parameters from parameter file generated by SC_GenerateParamSet.py

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

from ProcessRun import *

############# Functions ##############
# pfidbGen: pfidb generator
# createRunDir: creates parflow run directory for individual run
# getInputRow: get single set of run parameters
# processData: run post processing

# two different overall run behaviors
    # runSet runs a single simulation, in it's own folder
    # runSingleFolder, runs a series of simulations, in sequence, in the same folder.

def pfidbGen(runData):              # generates PFIDB File for Run given input data set
    '''
    creates pfidb file for parflow run
    
    Args:
        runData: Pandas DataFrame with Parflow Keys

    Returns:
        none
    '''

    # clean up run data set
    runData = runData.drop(labels='n') # remove the parameter line file
    runData = runData.astype(str) # convert all data to strings

    # evaluate key and value lengths - these variables are needed for the pfidb file
    keyLengths=[len(i) for i in runData.keys()]
    valueLengths=[len(i) for i in np.array(runData)]

    # open the output file, then first save the number of keys
    outfn = 'test.pfidb'

    with open(outfn,'a') as f: 

        # first write out the number of keys to the pfidb file
        f.write(str(len(runData.keys())))

        # loop through all the keys, add the key length, key, key value length, and key value to the pfidb file
        keyVals = np.array(runData)
        for i in range(len(keyVals)):
            f.write("\n")
            f.write(str(keyLengths[i]))
            f.write("\n")
            f.write(runData.keys()[i])
            f.write("\n")
            if keyVals[i] == 'nan': #nan values should be empty strings
                f.write("0")
                f.write("\n")
            else:
                f.write(str(valueLengths[i]))
                f.write("\n")
                f.write(keyVals[i])

def createPumpFile(pumpVRate, pumpDepth_min, pumpDepth_max, dz, dx, nz):
    '''
    creates parflow pumping file, given pumping rate (m3/hr), pumping depth range, and DZ/NZ
    
    Args:
        pumpVrate: pumping rate in m3/hr (assumes all model configuraiton in m)
        pumpDepth_min: minimum pumping depth (i.e. top of screen)
        pumpDepth_max: maximum pumping depth (i.e bottom of screen)
        dz: parflow domain layer depth (currently only supports constant dz)
        dx: parflow domain lateral cell width (assumes dx == dy)
        nz: Parflow number of vertical layers
    
    Returns:
        none
    
    '''

    # create pumping vector: for single column this is a simple vector the length of NZ
    pumpData = np.zeros(nz)

    # determine which layers will have pumping
    layTop = np.array([i for i in range(dz*(nz-1),-dz,-dz)])
    layBottom = layTop + dz
    layMiddle = (layTop + layBottom)/2.0
    pumpLayers = (layMiddle < pumpDepth_max) & (layMiddle > pumpDepth_min)
    pumpData[pumpLayers] = 1 # select these as the pumping layers, set to 1 for easy multiplication later

    # evalute pumping rate
    nlayers = pumpData.sum()
    pumpDepth = nlayers*dz
    assert pumpDepth == (pumpDepth_max - pumpDepth_min) #sanity check
    pumpRate = pumpVRate/dx/dx/pumpDepth # number of layers does not matter here, only the total depth, because the rate is 1/hr 
    pumpData = pumpData * pumpRate

    # save the file
    outfn = 'test_pump.txt'
    #pfio.pfwrite(pumpData, outfn, 0 , 0 , 0, 1, 1, nz)
    # pfio doesn't seem to like single column? or I"m doing it wrong... very possible
    with open(outfn,"w") as f:
        f.write('1 1 ')
        f.write(str(nz))
        for i in range(nz):
            f.write('\n')
            f.write(str(pumpData[i]))
    # convert text to pfb
    os.system('tclsh /glade/scratch/lmthatch/SCTests/runScripts/ConvertPFB2TXT 0 test_pump.txt test_pump.pfb')

def createRunDir(n): #(clmDir,currTestDir) input parameters ignored for now, assuming we're in the current directory and the clm directory has been copied into this folder
    '''
    create folder for parflow run 
    
    Args:
        n: folder number to create

    Returns:
        none
    '''

    # create run directory
    runDir = 'test' + str(n)
    os.system('mkdir ' + runDir)

    return runDir

def getInputRow(n,paramFile): # gets the input rows needed.
    '''
    get single parameter set from parameter file
    
    Args:
        n: parameter index
        paramFile: filename (string) with parameters for each parflow run
    '''

    allPar = pd.read_csv(paramFile, delimiter=",", header=0) # room for improvement here, may be removed when 'well' parallelized to loop through parameter set
    linePar = allPar.iloc[n]
    return linePar

def getAllInputRows(paramFile): # gets all input rows
    '''
    get all parameter data sets
    
    Args:
        paramFile: filename (string) with parameters for each parflow run
    '''

    allPar = pd.read_csv(paramFile, delimiter=",", header=0) # room for improvement here, may be removed when 'well' parallelized to loop through parameter set
    #linePar = allPar.iloc[n]
    return allPar

def runSet(parLine, parameterFN, parDict):
    '''
    run set of parflow parameters and process data
    runs in it's own folder

    Args:
        parLine: line in parameter file to read parflow run parameters from
        parameterFN: parameter file name (str) with parameter data
        parDict: ParflowMultiRun input parameters 
    
    Returns:
        none
    '''

    #parameterFN = "ParameterSets_AutoGenPY.csv"
    # create your run directory
    newRunDir = createRunDir(parLine)

    # get your run data
    runParameters = getInputRow(parLine, parameterFN)
    #runParameters['TimingInfo.StopTime'] = 500 
    # navigate to this new folder your created
    os.chdir(newRunDir)

    # create your pfidb file
    pfidbGen(runParameters)

    # run your program
    os.system("$PARFLOW_DIR/bin/parflow test > parflow.test.log")

    # process the data
    processDataSC(runParameters,parDict)

    os.system('rm test.pfidb')

    # delete your folder
    os.chdir('../')
    os.system('rm ' + newRunDir)

    print('parameter set complete: ' + str(parLine))

def runSingleFolder(runset,parDict): 
    '''
    Runs a full set of parameter lines all in sequences within a single run folder

    Args:
        runset: set number of parameter files to run
        parDict: Dictionary w/ ParflowMultiRun Parameters, including processing requirements
    
    Returns:
        none
    '''

    runset = runset - 1 # the GNU parallel is running a sequence from 1-5 but python wants 0-4, correct here.
    print('Running Folder ' + str(runset))
    
    # create run directory
    newRunDir = createRunDir(runset)

    # get all run parameters
    parameterFN = "ParameterSets_AutoGenPY_" + str(runset) + ".csv"
    allPar = getAllInputRows(parameterFN)
    nsets = len(allPar.index) # number of parameter sets in file

    # copy CLM files as needed
    # copy over clm driver files
    print()
    if parDict['clmDir'] != '':
        os.system("cp ../" + parDict['clmDir'] + "/drv_clmin.dat " + newRunDir)
        os.system("cp ../" + parDict['clmDir'] + "/drv_vegm.dat " + newRunDir)
        os.system("cp ../" + parDict['clmDir'] + "/drv_vegp.dat " + newRunDir)

    # move into new run folder
    os.chdir(newRunDir)

    # create file to save run times for each parflow run
    outfn = '../RunTimeData/runTimes_' + str(runset) + '.csv'

    # set parflow run command
    # check if parflow director is set
    if parDict['parfDir'] != '':
        parfcommand = parDict + ' test  > parflow.test.log'
    else:
        parfcommand = "$PARFLOW_DIR/bin/parflow test  > parflow.test.log"

    # loop through all parameter sets
    for currset in range(nsets):
        print('Running Set ' + str(currset))

        # get current parameter set
        runParameters = allPar.iloc[currset]
        testn = runParameters['n']

        # create your pfidb file
        pfidbGen(runParameters)

        # run your parflow
        try: 
            print('Running Parflow')
            start = time.time()
            os.system(parfcommand) # calls parflow run
            end = time.time()
            print('ParFlow Run Complete')

            # save log files for troubleshooting
            os.system('cp parflow.test.log ../'+str(testn) + '_parflow.test.log')
            os.system('cp test.out.kinsol.log ../'+str(testn) + '_test.out.kinsol.log')

            # save runtime
            totaltime = end - start
            with open(outfn,'a') as f:
                f.write(str(testn) + "," + str(totaltime))
                f.write("\n")

            try:
                processDataSC(runParameters,parDict)
            except:
                print('parflow processing failed')
        
        except:
            print('parflow failed and/or parflow processing failed')
        
        os.system('rm test.pfidb')

    # delete the directory when all runs have been completed
    os.chdir('../')
    #os.system('rm -r ' + newRunDir)

def main():
    runset = int(sys.argv[1])

    # default key values
    keys=['saveAllPFData','saveTotStoSL','saveRecCurve_Total', 'saveRecCurve_Layers', 'saveCLMSL', 'saveStoStats']
    defaultVals = [True,True,True,True,True,True]
    defaultDict = dict(zip(keys,defaultVals))

    runSingleFolder(runset,defaultDict)

    # old def main -> When file creation not restricted (no go on Cheyenne)
    # runLine = int(sys.argv[1],"ParameterSets_AutoGenPY.csv")
    # runSet(runLine)

if __name__ == "__main__":

    main() # main is passed the line in the parameter file that you want to pull

