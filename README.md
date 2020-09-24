ParFlowMultiRun
=======

*ParFlowMultiRun* is a python package to generate and run a suite of ParFlow simulations useful for sensitivity testing. Currently Parflow Multi Run is developed for Single Column models, but hillslope and basin scale are in Development

#### Development/Contact
+ Lauren Thatch <lmthatch@mines.edu>

Building and Running
--------------------

To install ParFlowMultiRun package, open the terminal/command line and clone the repository with the command

```bash
git clone https://github.com/lmthatch/ParFlowMultiRun.git
```

To run *ParFlowMultiRun*, navigate to the directory with your `SCInput.txt` input file and where you want your *ParFlowMultiRun* Directory.
```
python ParFlowMultiRunDirectory/runScripts/RunPFMultiRun.py
```

**Run the example**
navigate to the *ParFlowMultiRun* directory then examples/PFOnlyEx1/ \
You'll see an already setup simple SCInput.txt file for *ParFlowMultiRun* and an Input folder with the example ParFlow Key Parameter File\
Within this folder execute `python ../../runScripts/RunPFMultiRun.py`


Inputs
--------------------
**File Inputs**
1. **ParflowMultiRun driver file (required):** The main *ParflowMultiRun* input file that includes information on ParFlow input parameters, number of ParFlow simulations, and ParFlow post processing settings. This file must be named `SCInput.txt`.  Refer to the *Settings* section for a complete description of this file.
2. **ParFlow parameter input (required):** Contains ParFlow simulation key values. Values are set as either Constant, Variable, or Calculate. Variable values must include either a min/max range or a list of possible values.
   * *Constant* - These ParFlow keys will be constant for all ParFlow simulations in the ParFlowMultiRun
   * *Variable* - These ParFlow keys will vary for each simulation.
   * *Calculate* - These Parflow keys are dependent on variable parflow key values and will be calculated from these values.
3. **ParFlow Irrigation parameter input (optional):** Input file with ParFlow irrigation Parameters
4. **ParFlow and ParFlow-CLM Input Files (optional):** Parflow Run Input Files (e.g. indicator file, slope files, mannings files, clm driver files etc.)

Outputs
--------------------
***Single Line Files***


Settings
--------------------
The `SCInput.txt` file contains the ParflowMultiRun Parameters.
An example of this file is provided below and other examples are also provided
in the *Examples* folder. Inputs *must* be provided in the oder they appear in the
template shown here.

Here we describe each parameter and what they do:
* **ParFlowMultiRun Run Directory (runfolder):** Working Directory for ParflowMultiRun and all run output and postprocessing
* **Input File Directory (inputfolder):** The directory with all required Parflow Input Data (e.g. CLM driver files, slope files etc.)
* **ParFlow Run Parameter Files (paramfile):** Parameter file to generate ParFlow parameter from
* **Irrigation Parameter File (irrfile):** Irrigation Parameters File, not required, leave empty if not needed
* **Parflow Exectuable Directory (parfDir):** Parflow execuable directory, if blank assumes $PARFLOW_DIR/bin/parflow
* **Number of Simulations to Complete (n):** Total number of random parameter sets to generate and runs
* **Number of Run Folders (runfold):** Number of Folders to Run Parflow in, controls the number of simultaneous runs and total number of files generated
* **Random Seed (rseed):** Random Seed for parameter generation

Post-Processing / File output controls:
* **Save All ParFlow Data:** Saves all parflow output in single file (in `FullRunData/` Folder)
* **Save Total Storage Single Line (saveTotStoSL):** Save all storage values in single line output file (in `SingleLineOutput/` folder)
* **Save Total Storage Recession Curve Fit parameters (saveRecCurve_Total):** Save all total storage recession curve fit statistics to single line file (in `SingleLineOutput/` folder)
* **Save Storage Layer Recession Curve Fit Parameters (saveRecCurve_Layers):** Save  storage recession curve fit statistics for all layers to single line file (in `SingleLineOutput/` folder)
* **Save CLM Totals/Averages (saveCLMSL):** Save total and average statitics for all CLM output data to single line file (in `SingleLineOutput/` folder)
* **Save Storage Statiscs (saveStoStats):** Save storage statitics, including initial, final, and maximum storage for each layer, and hour of maximum storage, to single line file
(in `SingleLineOutput/` folder)

**Example format for the EcoSLIM input file**
```
RainRec_constantSub22   # Run Folder Directory, should be created at start of run.
/home/lmthatch/Documents/PFOnly_Tests/input_files   #input file directory: location of all input files, clm driver files, forcing data, subsurface data
/home/lmthatch/Documents/PFOnly_Tests/input_files/SCInputVariables_PFOnly_ConstantSubSurf_20200916.csv  # file name of parameter file
          # file name with addtional irrigation parameters
          # parflow executable directory
10000     # total number of runs to complete
1         # Number of Folders to Run Parflow in, controls the number of simultaneous runs and total number of files generated
42        # Random Seed
False     # saveAllPFData - Saves ALL Parflow 'raw' output: pressure, saturation, clm (if applicable)
True      # saveTotStoSL - Saves Total Storage at every time point to single line
True      # saveRecCurve_Total -  Total Storage Recession Curve
True      # saveRecCurve_Layers - Layer Recession Curve - outputs each layer to it's own file
False     # saveCLMSL - saves summary data for CLM variables: flux totals or averages depending on variable.
True      # saveStoStats - Saves storage statistics, initial, final, max, hour max...

```
