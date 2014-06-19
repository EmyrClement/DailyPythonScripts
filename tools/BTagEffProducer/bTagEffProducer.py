from rootpy.tree import Tree
from rootpy.plotting import Hist2D, Canvas
from rootpy.io import root_open
from rootpy.interactive import wait

inputFile = '/storage/TopQuarkGroup/mc/8TeV/LeptonPlus3JetsSkim/TTJets_MassiveBinDECAY_TuneZ2star_8TeV-madgraph-tauola/nTuple_v10_Summer12_DR53X-PU_S10_START53_V7C-v1_LeptonPlus3Jets/TTJets_nTuple_53X_mc_merged_001.root'


#===============================================================================
# Main code
#===============================================================================
with root_open(inputFile, 'read') as f:
    
    tree = f.Get('rootTupleTree/tree')
    
    vars = [branch.GetName() for branch in tree.GetListOfBranches()]
    
    # Partong criteria
    bPartonCriteria = 'abs(goodPatJetsPFlow.PartonFlavour)==5'
    cPartonCriteria = 'abs(goodPatJetsPFlow.PartonFlavour)==4'
    lightPartonCriteria = '( abs(goodPatJetsPFlow.PartonFlavour)!=5 && abs(goodPatJetsPFlow.PartonFlavour)!=4 )'
    
    # B tag criteria
    bTagCriteria = 'goodPatJetsPFlow.CombinedSecondaryVertexBJetTag>0.679'
    
    # B hists
    h_bAll = Hist2D(6,0,3,5,0,1000,name='h_bAll')
    h_bPass = Hist2D(6,0,3,5,0,1000,name='h_bPass')

    # C hists
    h_cAll = Hist2D(6,0,3,5,0,1000,name='h_cAll')
    h_cPass = Hist2D(6,0,3,5,0,1000,name='h_cPass')
    
    # Light hists
    h_lAll = Hist2D(6,0,3,5,0,1000,name='h_lAll')
    h_lPass = Hist2D(6,0,3,5,0,1000,name='h_lPass')
    
    # Read trees
    # B partons
    tree.Draw('abs(goodPatJetsPFlow.GenJet.Eta):goodPatJetsPFlow.GenJet.Pt',bPartonCriteria, hist=h_bAll)
    tree.Draw('abs(goodPatJetsPFlow.GenJet.Eta):goodPatJetsPFlow.GenJet.Pt',bPartonCriteria+'&&'+bTagCriteria, hist=h_bPass)
    
    # C partons
    tree.Draw('abs(goodPatJetsPFlow.GenJet.Eta):goodPatJetsPFlow.GenJet.Pt',cPartonCriteria, hist=h_cAll)
    tree.Draw('abs(goodPatJetsPFlow.GenJet.Eta):goodPatJetsPFlow.GenJet.Pt',cPartonCriteria+'&&'+bTagCriteria, hist=h_cPass)

    # Light partons
    tree.Draw('abs(goodPatJetsPFlow.GenJet.Eta):goodPatJetsPFlow.GenJet.Pt',lightPartonCriteria, hist=h_lAll)
    tree.Draw('abs(goodPatJetsPFlow.GenJet.Eta):goodPatJetsPFlow.GenJet.Pt',lightPartonCriteria+'&&'+bTagCriteria, hist=h_lPass)
        
    # Make efficiency histograms
    h_bPass.Divide(h_bAll)
    h_bPass.Draw('COLZ')
    raw_input('...')
    
    h_cPass.Divide(h_cAll)
    h_cPass.Draw('COLZ')
    raw_input('...')

    h_lPass.Divide(h_lAll)
    h_lPass.Draw('COLZ')
    raw_input('...')    
    pass