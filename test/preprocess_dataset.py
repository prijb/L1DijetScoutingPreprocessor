#This code runs preprocess_file.py over a whole dataset using HTCondor
import os
import argparse

#Argument parser
parser = argparse.ArgumentParser(description='Preprocess L1 Scouting Dataset')
parser.add_argument('--input', '-i', type=str, help='Input dataset path')
parser.add_argument('--output', '-o', type=str, help='Output dataset path')
parser.add_argument('--nfiles', '-n', default=-1, type=int, help='Number of files to process')
parser.add_argument('--grid', '-g', default=False, type=bool, help='Dataset is on the grid')

args = parser.parse_args()

dataset_input = args.input
#If grid, add prefix
if args.grid:
    prefix = "davs://gfe02.grid.hep.ph.ic.ac.uk:2880/pnfs/hep.ph.ic.ac.uk/data/cms/"
    #prefix = "root://gfe02.grid.hep.ph.ic.ac.uk/pnfs/hep.ph.ic.ac.uk/data/cms/"
    dataset_input = prefix + dataset_input
    
#Check if the dataset path exists
#if not os.path.exists(dataset_input):
#    print("Input dataset path does not exist")
#    exit()

#Make a directory for the output path
os.makedirs(args.output, exist_ok=True)

#Make a directory for condor submission 
os.makedirs("condor_submission", exist_ok=True)

#Make a directory for condor logs
os.makedirs("condor_submission/logs", exist_ok=True)

#Make the input arguments file for the condor job
with open("condor_submission/preprocess_args.txt", "w") as f:
    #Count the number of files in the dataset
    files = None
    if args.grid == True:
        files = os.popen(f"gfal-ls {dataset_input}").read().strip().split("\n")
    else:
        files = os.popen(f"ls {dataset_input}").read().strip().split("\n")
    #Only retain .root files
    files_filtered = [file for file in files if "root" in file]
    n_files_dataset = len(files_filtered)

    #Number of files to process
    n_files_to_process = args.nfiles
    if(args.nfiles > n_files_dataset):
        n_files_to_process = n_files_dataset
    elif(args.nfiles < 0):
        n_files_to_process = n_files_dataset
    else:
        n_files_to_process = args.nfiles
    
    #Now write the input arguments for the job submission
    for i in range(n_files_to_process):
        f.write(f"{dataset_input}/{files_filtered[i]} {args.output}/processed_{files_filtered[i]}\n")


#Create the HTCondor submit file
submit_file_content = f"""
universe = vanilla
executable = /vols/cms/pb4918/L1Scouting/Sep24/Analysis/CMSSW_14_1_0_pre4/src/Preprocess/test/preprocess_file_wrapper.sh
arguments = $(infile) $(outfile)
output = condor_submission/logs/preprocess_$(Cluster)_$(Process).out
error = condor_submission/logs/preprocess_$(Cluster)_$(Process).err
log = condor_submission/logs/preprocess_$(Cluster)_$(Process).log
request_cpus = 1
request_memory = 1GB
use_x509userproxy = true
+MaxRuntime = 3600
queue infile, outfile from condor_submission/preprocess_args.txt
"""

with open("condor_submission/preprocess.submit", "w") as f:
    f.write(submit_file_content)

#Delete exist log files
os.system("rm condor_submission/logs/*")

# Run the condor job
os.system("condor_submit condor_submission/preprocess.submit")

# Remove the condor submission file
os.system("rm condor_submission/preprocess.submit")
        