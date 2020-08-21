#!/bin/bash
#PBS -N PFSC_FIrr
#PBS -A UCSM0009
#PBS -q share
#PBS -l walltime=6:00:00
#PBS -l select=1:ncpus=10

### Set TMPDIR as recommended
setenv TMPDIR /glade/scratch/lmthatch/temp
mkdir -p $TMPDIR

# Load Environment
module load parallel
module load ncarenv/1.3
module load python/3.7.5
ncar_pylib my_npl_clone_20200728

# User Input
#NEWDIR='DiscreteIrr'
#NRUNS=10000
#VARFILE='SCInputVariables_DiscreteIrr_20200805.csv'
#NFOLD=10

#NEWDIR='quicktest5'
#NRUNS=100
#VARFILE='SCInputVariables_Test.csv'
#NFOLD=5

NEWDIR='SCRun_FixedIrrVol'
NRUNS=1000
VARFILE='SCInputVariables_DiscreteIrr_20200805.csv'
NFOLD=10


# create files and directory
python runScripts/SC_GenerateParamSet.py $NRUNS $VARFILE $NEWDIR $NFOLD

# move into new director
cd $NEWDIR

# run runs
parallel python ../runScripts/RunParSet.py {1} ::: $(seq 10)
