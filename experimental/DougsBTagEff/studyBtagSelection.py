
import ROOT 
# from ROOT import gROOT, gPad, gStyle, TChain, TFile, TTree, TMath, TH1, TH1F, TH2F, TCanvas, TPad, TAxis, TLegend, TLatex
from ROOT import TFile, TChain, TGraph
# from array import array
# import math
import os
# ROOT.gROOT.SetBatch(True)

# Prepare output TFile, and output directory
# Returns a TFile
def prepareOutputFiles() :

	file = TFile("BTagEfficiency.root", "RECREATE")
	if not os.path.exists('plots'):
		os.makedirs('plots')

	return file

def prepareInputFiles():
	input_file = "/hdfs/TopQuarkGroup/run2/atOutput/13TeV/25ns/TTJets_PowhegPythia8_tree.root"

	E_inputTree = "TTbar_plus_X_analysis/EPlusJets/Ref selection NoBSelection/BTagEfficiencies/Jets"
	E_Chain = TChain(E_inputTree)
	E_Chain.Add(input_file)

	Mu_inputTree = "TTbar_plus_X_analysis/MuPlusJets/Ref selection NoBSelection/BTagEfficiencies/Jets"
	Mu_Chain = TChain(Mu_inputTree)
	Mu_Chain.Add(input_file)

	setBranchStatus( [ E_Chain, Mu_Chain ] )

	return E_Chain, Mu_Chain

def setBranchStatus(chains):
	for chain in chains:
		chain.SetBranchStatus("*",0)
		chain.SetBranchStatus("pt",1)
		chain.SetBranchStatus("eta",1)
		chain.SetBranchStatus("CSV",1)
		chain.SetBranchStatus("partonFlavour",1)
		chain.SetBranchStatus("isLoose",1)
		chain.SetBranchStatus("isMedium",1)
		chain.SetBranchStatus("isTight",1)
		chain.SetBranchStatus("NJets",1)
		chain.SetBranchStatus("EventWeight",1)
		chain.SetBranchStatus("PUWeight",1)
		chain.SetBranchStatus("ElectronEfficiencyCorrection",1)
		chain.SetBranchStatus("MuonEfficiencyCorrection",1)
def main():


	outputFile = prepareOutputFiles()

	E_Chain, Mu_Chain = prepareInputFiles()

	channelsAndChains = { 'Electron' : E_Chain,
							'Muon'   : Mu_Chain }


	for channel, chain in channelsAndChains.iteritems():

		print channel,'channel'

		totalNumberOfEvents=0
		numberOfEventsWithTwoMediumBTags = 0

		eventCounters = {
		'Total' : 0,
		'2Medium' : 0
		}

		for event in chain:
			totalNumberOfEvents=totalNumberOfEvents+1
			if totalNumberOfEvents==10000: print totalNumberOfEvents, "th Event"
			if totalNumberOfEvents > 20000 : break


			numberOfMediumJets = 0

			# Read variables for this event
			NJets = event.__getattr__("NJets")
			pt = event.__getattr__("pt")
			eta = event.__getattr__("eta")
			CSV = event.__getattr__("CSV")
			partonFlavour = event.__getattr__("partonFlavour")
			isLoose = event.__getattr__("isLoose")
			isMedium = event.__getattr__("isMedium")
			isTight = event.__getattr__("isTight")
			eventWeight = event.__getattr__("EventWeight")
			puWeight = event.__getattr__("PUWeight")
			electronWeight = event.__getattr__("ElectronEfficiencyCorrection")
			weight = eventWeight * puWeight * electronWeight

			# Loop over jets and count how many are b tagged
			for JetIndex in range (0,int(NJets)):

				if (pt[JetIndex] < 25): continue;

				if isMedium[JetIndex] : numberOfMediumJets += 1

			eventCounters['Total'] += 1
			if numberOfMediumJets >= 2 : eventCounters['2Medium'] += 1

		resultsGraph = TGraph( len( eventCounters )+1 )
		pointCounter = 1
		for counter,number in eventCounters.iteritems():
			print pointCounter, counter, number
			resultsGraph.SetPoint(pointCounter, pointCounter, number)
			resultsGraph.GetXaxis().SetBinLabel(pointCounter, counter)
			pointCounter += 1

		resultsGraph.Draw('AP')
		raw_input()

	# bQuarkJets_BTags_Hist.Write()

	# # Easy access to .pngs 
	# bQuarkJetCanvas = TCanvas("bQuarkJet","bQuarkJet", 0, 0, 800, 600)
	# bQuarkJets_BTags_Hist.SetTitle("bQuarkJet BTag Efficiencies; pt; eta")
	# bQuarkJets_BTags_Hist.Draw("colz text e")
	# bQuarkJetCanvas.Update()
	# bQuarkJetCanvas.SaveAs("plots/bQuarkJet_BTagEfficiency.png")



if __name__ == '__main__':
	main()
