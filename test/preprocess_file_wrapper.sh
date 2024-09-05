#!/bin/bash
#This wrapper runs the python script for running on a file
#Go to the CMSSW directory and set up the environment
cd /vols/cms/pb4918/L1Scouting/Sep24/Analysis/CMSSW_14_1_0_pre4/src/Preprocess
source /cvmfs/cms.cern.ch/cmsset_default.sh
source /vols/grid/cms/setup.sh
export X509_USER_PROXY=${HOME}/cms.proxy
cmsenv
#Run the python script
python3 test/preprocess_file.py -i $1 -o $2