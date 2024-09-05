#Python RDF script to preprocess L1 Scouting ntuples
import ROOT
import time
import argparse

#Argument parser
parser = argparse.ArgumentParser(description='Preprocess L1 Scouting ntuples')
parser.add_argument('--input', '-i', type=str, help='Input file path')
parser.add_argument('--output', '-o', type=str, help='Output file path')

args = parser.parse_args()

#File input
#fname = "/vols/cms/pb4918/StoreNTuple/L1Scouting/QCDProdwReco/QCD_15to7000/output_1.root"
#Data file: davs://gfe02.grid.hep.ph.ic.ac.uk:2880/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/ppradeep/L1Scouting/L1ScoutingSelection/run383996_dijet/240903_120147/0000/output_1.root
fname = args.input
oname = args.output

#Change " .root" to "_hist.root"
oname_hist = oname.replace(".root", "_hist.root")

#Start processing
start = time.time()

#Multithreading option
#ROOT.ROOT.EnableImplicitMT(8)

#Preprocess function call
ROOT.gInterpreter.Declare("""
    using Vbool = ROOT::RVec<bool>;
    using Vint = ROOT::RVec<int>;
    using Vfloat = ROOT::RVec<float>;

    auto preprocess(ROOT::RDF::RNode df){
        

        //Trigger filter 
        auto df_trig = df.Filter("nJet > 1")
        .Filter("(Jet_pt[0] > 30)&&(std::abs(Jet_eta[0]) < 1.5)")
        .Filter("(Jet_pt[1] > 30)&&(std::abs(Jet_eta[1]) < 1.5)");

        return df_trig;
    }

    auto getDijetMass(Vfloat Jet_pt, Vfloat Jet_eta, Vfloat Jet_phi){
        float mjj = -1;
        if(Jet_pt.size() > 1){
            ROOT::Math::PtEtaPhiMVector jet1(Jet_pt[0], Jet_eta[0], Jet_phi[0], 0);
            ROOT::Math::PtEtaPhiMVector jet2(Jet_pt[1], Jet_eta[1], Jet_phi[1], 0);
            mjj = (jet1 + jet2).M();
        }

        return mjj;
    }
                          
    auto getDijetDPhi(Vfloat Jet_phi){
        float dijet_dphi = -1;
        if(Jet_phi.size() > 1){
           float dphi = std::abs(TVector2::Phi_mpi_pi(Jet_phi[0] - Jet_phi[1]));               
        }
        return dijet_dphi;
    }
                          
    auto getDijetDR(Vfloat Jet_eta, Vfloat Jet_phi){
        float dijet_dr = -1;
        if(Jet_eta.size() > 1){
            float deta = Jet_eta[0] - Jet_eta[1];
            float dphi = TVector2::Phi_mpi_pi(Jet_phi[0] - Jet_phi[1]);
            dijet_dr = std::sqrt(deta*deta + dphi*dphi);
        }
        return dijet_dr;
    }
""")



#Input data
data = ROOT.TChain()
data.Add("{}/scNtuplizer/Events".format(fname))

df = ROOT.RDataFrame(data)

#Get number of events
n_entries = df.Count().GetValue()

#Event selection
df = df.Filter("nJet > 1").Filter("(Jet_pt[0] > 30)&&(std::abs(Jet_eta[0]) < 1.5)").Filter("(Jet_pt[1] > 30)&&(std::abs(Jet_eta[1]) < 1.5)")
#Event vetoes
df = df.Filter("Sum(Jet_pt == 1023.5)==0", "Saturated jet veto")
df = df.Filter("Sum(EGamma_pt == 255)==0", "Saturated EGamma veto")

#Define quantities
df = df.Define("mjj", "getDijetMass(Jet_pt, Jet_eta, Jet_phi)")
df = df.Define("deta", "std::abs(Jet_eta[0] - Jet_eta[1])").Define("dphi", "getDijetDPhi(Jet_phi)").Define("dr", "getDijetDR(Jet_eta, Jet_phi)")
#Further event selections
df = df.Filter("dr > 0.4", "Overlapping jet veto")
#Define control regions
df = df.Define("region_sig", "deta < 1.0")
df = df.Define("region_bkg_1", "deta > 1.0 && deta < 1.5")
df = df.Define("region_bkg_2", "deta > 1.5 && deta < 2.5")

#Make histograms
h_mjj = df.Histo1D(("h_mjj", "m_{{jj}}", 110, 150, 700), "mjj")
h_mjj_sig = df.Filter("region_sig").Histo1D(("h_mjj_sig", "m_{{jj}}", 110, 150, 700), "mjj")
h_mjj_bkg_1 = df.Filter("region_bkg_1").Histo1D(("h_mjj_bkg_1", "m_{{jj}}", 110, 150, 700), "mjj")
h_mjj_bkg_2 = df.Filter("region_bkg_2").Histo1D(("h_mjj_bkg_2", "m_{{jj}}", 110, 150, 700), "mjj")
h_deta = df.Histo1D(("h_deta", "#Delta#eta_{{jj}}", 50, 0, 3.0), "deta")

#Save histograms
f = ROOT.TFile("{}".format(oname_hist), "RECREATE")
#Store the number of events
n_entries_param = ROOT.TParameter(float)("n_entries", n_entries)
n_entries_param.Write()
h_mjj.Write()
h_mjj_sig.Write()
h_mjj_bkg_1.Write()
h_mjj_bkg_2.Write()
h_deta.Write()
f.Close()

#Save a snapshot of the data with the regions specifed
df.Snapshot("Events", "{}".format(oname), ["mjj", "region_sig", "region_bkg_1", "region_bkg_2"])


#End processing
end = time.time()
print("Time taken: {:.2f} seconds".format(end-start))



