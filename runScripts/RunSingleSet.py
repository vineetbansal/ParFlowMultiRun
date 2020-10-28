import sys
import os

from RunPFMultiRun import readInputFile
from RunParSet import runSingleFolder

currDir = os.getcwd()

# get run settings
os.chdir('../')
inputData = readInputFile()

os.chdir(currDir)
# get set to run from command line
runset = int(sys.argv[1])

# run set
runSingleFolder(runset, inputData) 