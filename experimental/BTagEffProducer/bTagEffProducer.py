from rootpy.tree import Tree, TreeChain
from rootpy.plotting import Hist2D, Canvas
from rootpy.io import root_open
from rootpy.interactive import wait
from optparse import OptionParser


fileNames = {
             '8TeV' : {
                    'TTJets' : '/storage/TopQuarkGroup/mc/8TeV/BLT/NoBTag/TTJets_MassiveBinDECAY_TuneZ2star_8TeV-madgraph-tauola/TTJets_nTuple_53X_mc_merged.root',
                    'WJets' : 'WJets8TeV',
                },
             '7TeV' : {
                    'TTJets' : '/storage/TopQuarkGroup/mc/7TeV/v11/NoSkimUnfolding/BLT/NoBTag/TTJets_MSDecays_central_TuneZ2_7TeV-madgraph-tauola/TTJets_nTuple_53X_mc_merged.root',
                     'WJets' : 'WJets8TeV',
               }
             }

channels = [
            'ePlusJets',
            'muPlusJets',
            ]

treeName = {
            'ePlusJets' : 'rootTupleTreeEPlusJets/ePlusJetsTree_noBTag',
            'muPlusJets' : 'rootTupleTreeMuPlusJets/muPlusJetsTree_noBTag',
            }

jetCollection = {
            'ePlusJets' : 'cleanedJetsPFlowEPlusJets',
            'muPlusJets' : 'cleanedJetsPFlowMuPlusJets',
                 }

# Bin edges that match SFb in 2012
ptBinEdges = [20, 30, 40, 50, 60, 70, 80, 100, 120, 160, 210, 260, 320, 400, 500, 600,800]
etaBinEdges = [0,2.4]

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
def main():
    
    parser = OptionParser()
    parser.add_option('--is7TeV', action='store_true', dest='is7TeVData', default=False )
    parser.add_option('-s', '--sample', dest='sample', default='TTJets')
    parser.add_option('-d', '--debug', action='store_true', dest='debug', default=False)

    (options, _) = parser.parse_args()
    
    inputFile = 'crap.root'
    if options.is7TeVData:
        inputFile = fileNames['7TeV'][options.sample]
    else:
        inputFile = fileNames['8TeV'][options.sample]
    
    outputFile = 'crapout.toot'
    if options.is7TeVData:
        outputFile = 'bTagEfficiencies_'+options.sample+'_7TeV.root'
    else:
        outputFile = 'bTagEfficiencies_'+options.sample+'_8TeV.root'

    with root_open(inputFile, 'read') as f, root_open(outputFile, 'recreate') as out:
        for channel in channels:
            
            f.cd()
            tree = f.Get(treeName[channel])
        
            # Useful for getting list of branches
            #     vars = [branch.GetName() for branch in tree.GetListOfBranches()]
            
            # Derive pt variable from tree
            jetPt='sqrt('+jetCollection[channel]+'.Px*'+jetCollection[channel]+'.Px+'+jetCollection[channel]+'.Py*'+jetCollection[channel]+'.Py)'
            jetEta='-1.0*log(tan(atan(sqrt('+jetCollection[channel]+'.Px*'+jetCollection[channel]+'.Px+'+jetCollection[channel]+'.Py*'+jetCollection[channel]+'.Py)/'+jetCollection[channel]+'.Pz/2)))'
            
            # Parton criteria
            bPartonCriteria = 'abs('+jetCollection[channel]+'.PartonFlavour)==5'
            cPartonCriteria = 'abs('+jetCollection[channel]+'.PartonFlavour)==4'
            lightPartonCriteria = '( abs('+jetCollection[channel]+'.PartonFlavour)!=5 && abs('+jetCollection[channel]+'.PartonFlavour)!=4 )'
            
            # B tag criteria
            bTagCriteria = jetCollection[channel]+'.CombinedSecondaryVertexBJetTag>0.679'
            
            # B hists
            h_bAll = Hist2D(etaBinEdges,ptBinEdges,name='h_bAll_'+channel)
            h_bPass = Hist2D(etaBinEdges,ptBinEdges,name='h_bPass_'+channel)
            
            # C hists
            h_cAll = Hist2D(etaBinEdges,ptBinEdges,name='h_cAll_'+channel)
            h_cPass = Hist2D(etaBinEdges,ptBinEdges,name='h_cPass_'+channel)
            
            # Light hists
            h_lAll = Hist2D(etaBinEdges,ptBinEdges,name='h_lAll_'+channel)
            h_lPass = Hist2D(etaBinEdges,ptBinEdges,name='h_lPass_'+channel)
            
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
            
            h_cPass.Divide(h_cPass,h_cAll,1.,1.,'B')
            h_cPass.Draw('COLZ')
            printEfficienciesToScreen(h_cPass)
            
            h_lPass.Divide(h_lPass,h_lAll,1.,1.,'B')
            h_lPass.Draw('COLZ')
            printEfficienciesToScreen(h_lPass)
            
            # Output to file
            print 'Writing output'
            out.cd()
            h_bPass.Write()
            h_cPass.Write()
            h_lPass.Write()
            print 'Done'
            pass
        pass
    pass

if __name__ == '__main__':
    main()