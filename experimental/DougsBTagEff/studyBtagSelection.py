
from ROOT import TFile, TChain, TH1F
from collections import OrderedDict
import os

# Prepare output TFile, and output directory
# Returns a TFile
def prepareOutputFiles() :

	file = TFile("BTagEfficiency.root", "RECREATE")
	if not os.path.exists('plots'):
		os.makedirs('plots')

	return file

# Prepare location of input files and trees
# Returns a dictionary of 'channel name' : TChain for this channel
def prepareInputFiles():
	input_file = "/hdfs/TopQuarkGroup/run2/atOutput/13TeV/25ns/TTJets_PowhegPythia8_tree.root"

	E_inputTree = "TTbar_plus_X_analysis/EPlusJets/Ref selection NoBSelection/BTagEfficiencies/Jets"
	E_Chain = TChain(E_inputTree)
	E_Chain.Add(input_file)

	Mu_inputTree = "TTbar_plus_X_analysis/MuPlusJets/Ref selection NoBSelection/BTagEfficiencies/Jets"
	Mu_Chain = TChain(Mu_inputTree)
	Mu_Chain.Add(input_file)

	setBranchStatus( [ E_Chain, Mu_Chain ] )

	return 	{ 'Electron' : E_Chain, 'Muon' : Mu_Chain }

# Set the status of branches in the trees
# Only turn on the branches you will be reading
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

	# Open the output file
	outputFile = prepareOutputFiles()
	# Get the input trees/chains
	channelsAndChains = prepareInputFiles()

	# Loop over the two channels
	for channel, chain in channelsAndChains.iteritems():

		print channel,'channel'

		eventCounter=0

		# Histogram to store the results
		resultsHistogram = TH1F( 'results', 'results', 2, 0, 2)

		# Loop over the events in this chain
		for event in chain:
			eventCounter=eventCounter+1
			if eventCounter % 10000 == 0: print "Processing ",eventCounter, "th event"
			if eventCounter > 100000 : break

			# Counter for the number of medium b tagged jets in this event
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

				# Only consider jets with pt > 25 GeV
				if (pt[JetIndex] < 25): continue;

				if isMedium[JetIndex] : numberOfMediumJets += 1

			resultsHistogram.Fill( 'Total', 1 )
			if numberOfMediumJets >= 2 : 
				resultsHistogram.Fill( '2Medium', 1 )

		resultsHistogram.Draw()
		raw_input('Press anything to continue...')


if __name__ == '__main__':
	main()
