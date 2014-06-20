from rootpy.tree import Tree, TreeChain
from rootpy.plotting import Hist2D, Canvas
from rootpy.io import root_open
from rootpy.interactive import wait

inputFileDir = '/storage/TopQuarkGroup/mc/8TeV/LeptonPlus3JetsSkim/TTJets_MassiveBinDECAY_TuneZ2star_8TeV-madgraph-tauola/nTuple_v10_Summer12_DR53X-PU_S10_START53_V7C-v1_LeptonPlus3Jets/'
inputFiles = [
              inputFileDir+'TTJets_nTuple_53X_mc_merged.root',
#               inputFileDir+'/TTJets_nTuple_53X_mc_merged_001.root',
#               inputFileDir+'/TTJets_nTuple_53X_mc_merged_002.root',
#             inputFileDir+'/TTJets_nTuple_53X_mc_merged_003.root',
#             inputFileDir+'/TTJets_nTuple_53X_mc_merged_004.root',
#             inputFileDir+'/TTJets_nTuple_53X_mc_merged_005.root',
#             inputFileDir+'/TTJets_nTuple_53X_mc_merged_006.root',
#             inputFileDir+'/TTJets_nTuple_53X_mc_merged_007.root',
#             inputFileDir+'/TTJets_nTuple_53X_mc_merged_008.root',
#             inputFileDir+'/TTJets_nTuple_53X_mc_merged_009.root'
              ]

# Bin edges that match SFb in 2012
ptBinEdges = [20, 30, 40, 50, 60, 70, 80, 100, 120, 160, 210, 260, 320, 400, 500, 600,800]
etaBinEdges = [0,2.4]

# Bin edges from example code....
# ptBinEdges = ptBinEdges
# etaBinEdges = etaBinEdges


# Derive pt variable from tree
jetPt='sqrt(goodPatJetsPFlow.Px*goodPatJetsPFlow.Px+goodPatJetsPFlow.Py*goodPatJetsPFlow.Py)'
jetEta='-1.0*log(tan(atan(sqrt(goodPatJetsPFlow.Px*goodPatJetsPFlow.Px+goodPatJetsPFlow.Py*goodPatJetsPFlow.Py)/goodPatJetsPFlow.Pz/2)))'

def printEfficienciesToScreen( hist ):
    for xbin in range(1,hist.GetNbinsX() + 1):
        for ybin in range(1,hist.GetNbinsY() + 1):    
            print 'Efficiency in bin : ',hist.GetXaxis().GetBinCenter(xbin),',',hist.GetYaxis().GetBinCenter(ybin)
            print hist.GetBinContent(xbin,ybin),'+/-',hist.GetBinError(xbin,ybin)
            pass
        pass
    pass

#===============================================================================
# Main code
#===============================================================================
# with root_open(inputFile, 'read') as f:
#     tree = f.Get('rootTupleTree/tree')

tree = TreeChain('rootTupleTree/tree', inputFiles)
# Useful for getting list of branches
#     vars = [branch.GetName() for branch in tree.GetListOfBranches()]

# Parton criteria
bPartonCriteria = 'abs(goodPatJetsPFlow.PartonFlavour)==5'
cPartonCriteria = 'abs(goodPatJetsPFlow.PartonFlavour)==4'
lightPartonCriteria = '( abs(goodPatJetsPFlow.PartonFlavour)!=5 && abs(goodPatJetsPFlow.PartonFlavour)!=4 )'

# B tag criteria
bTagCriteria = 'goodPatJetsPFlow.CombinedSecondaryVertexBJetTag>0.679'

# B hists
h_bAll = Hist2D(etaBinEdges,ptBinEdges,name='h_bAll')
h_bPass = Hist2D(etaBinEdges,ptBinEdges,name='h_bPass')

# C hists
h_cAll = Hist2D(etaBinEdges,ptBinEdges,name='h_cAll')
h_cPass = Hist2D(etaBinEdges,ptBinEdges,name='h_cPass')

# Light hists
h_lAll = Hist2D(etaBinEdges,ptBinEdges,name='h_lAll')
h_lPass = Hist2D(etaBinEdges,ptBinEdges,name='h_lPass')

# Read trees
# B partons
tree.Draw(jetEta+':'+jetPt,bPartonCriteria, hist=h_bAll)
tree.Draw(jetEta+':'+jetPt,bPartonCriteria+'&&'+bTagCriteria, hist=h_bPass)

# C partons
tree.Draw(jetEta+':'+jetPt,cPartonCriteria, hist=h_cAll)
tree.Draw(jetEta+':'+jetPt,cPartonCriteria+'&&'+bTagCriteria, hist=h_cPass)

# Light partons
tree.Draw(jetEta+':'+jetPt,lightPartonCriteria, hist=h_lAll)
tree.Draw(jetEta+':'+jetPt,lightPartonCriteria+'&&'+bTagCriteria, hist=h_lPass)
    
# Make efficiency histograms
h_bPass.Divide(h_bPass,h_bAll,1.,1.,'B')
h_bPass.Draw('COLZ')
printEfficienciesToScreen(h_bPass)
raw_input('...')

h_cPass.Divide(h_cPass,h_cAll,1.,1.,'B')
h_cPass.Draw('COLZ')
printEfficienciesToScreen(h_cPass)
raw_input('...')

h_lPass.Divide(h_lPass,h_lAll,1.,1.,'B')
h_lPass.Draw('COLZ')
printEfficienciesToScreen(h_lPass)
raw_input('...')

# Output to file
print 'Writing output'
outputFile = root_open('bJetEfficienies.root','Recreate')
h_bPass.Write()
h_cPass.Write()
h_lPass.Write()
outputFile.Close()
print 'Done'
pass