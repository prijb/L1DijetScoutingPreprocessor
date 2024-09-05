## Preprocessor for L1 Scouting Ntuples
This repository preprocesses ntuples from L1 Scouting MC/Data produced by the L1ScoutingNtuplizer.

# Running on a file
```preprocess_file.py``` is the main script which takes an input and output file (specificed by ```--input``` and ```--output``` respectively), and gets binned dijet mass histograms over a mass range of 150-700 GeV. The output file, along with the histograms, also stores the number of events processed. 

An example of running this script on MC is
```
python3 test/preprocess_file.py -i davs://gfe02.grid.hep.ph.ic.ac.uk:2880/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/ppradeep/L1Scouting/QCD_PT-30to50_TuneCP5_13p6TeV_pythia8/QCD_PT-30to50_regressed_leading/240821_124954/0000/output_1.root -o /vols/cms/pb4918/L1Scouting/Sep24/Analysis/CMSSW_14_1_0_pre4/src/Preprocess/output/output_processed.root
```
# Running on a dataset
To run on a dataset, we use ```preprocess_dataset.py```. This takes an input and output dataset directory (not file) ```--input``` and ```--output``` and uses the input location to find the first ```-n``` files to process on. The list of files, along with their respective output locations are stored in a ```preprocess_args.txt``` file also generated on execution. Then, this script generates a condor submission file which runs the main script on each file. To run on HTCondor, we use a wrapper script called ```preprocess_file_wrapper.sh``` which runs ```preprocess_file.py``` on each node. The dataset has options for running on the grid or locally

Examples of dataset submissions are:
Running over all MC files of a given local dataset
```
python3 test/preprocess_dataset.py -i /vols/cms/pb4918/StoreNTuple/L1Scouting/QCDProdwReco/QCD_30to50 -o /vols/cms/pb4918/L1Scouting/Sep24/Analysis/CMSSW_14_1_0_pre4/src/Preprocess/output/QCD_30to50 -n -1
```
Running over all MC files of a given dataset stored pn the grid
```
python3 test/preprocess_dataset.py -i store/user/ppradeep/L1Scouting/QCD_PT-30to50_TuneCP5_13p6TeV_pythia8/QCD_PT-30to50_regressed_leading/240821_124954/0000 -o /vols/cms/pb4918/L1Scouting/Sep24/Analysis/CMSSW_14_1_0_pre4/src/Preprocess/output/QCD_30to50 -g True -n 20
```
