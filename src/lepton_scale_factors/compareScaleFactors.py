from rootpy.io import File, root_open
from math import sqrt
from rootpy.plotting import Hist2D, Canvas
from ROOT import gStyle, Long


# Trigger
# doId = False
# sergeysSFFileName = '/storage/ec6821/DailyPythonScripts/CMSSW_6_0_0/src/DailyPythonScripts/plots/2011/muon/scaleFactors_muon_trigger.root'
# pogSFFileName = '/storage/ec6821/NTupleProduction/SynchEx/CMSSW_6_0_0/src/BristolAnalysis/Tools/data/MuonEfficiencies_SF_2011_53X_DataMC.root'

# ID/iso
doId = True
sergeysSFFileName = '/storage/ec6821/DailyPythonScripts/CMSSW_6_0_0/src/DailyPythonScripts/plots/2011/muon/scaleFactors_muon_id_iso.root'
pogSFFileName = '/storage/ec6821/NTupleProduction/SynchEx/CMSSW_6_0_0/src/BristolAnalysis/Tools/data/MuonEfficiencies_SF_2011_53X_DataMC.root'

with root_open(sergeysSFFileName) as sfSergeyFile, root_open(pogSFFileName) as sfPogFile:
	h_sfSergey = sfSergeyFile.Get( 'scaleFactors' )
	if doId:
		h_sfPog = sfPogFile.Get('SF_2011_TIGHT_ISO_PT25_PtrgL_eta_pt_PLOT')
	else:
		h_sfPog = sfPogFile.Get('SF_2011_HLT_TisoMu24eta2p1_IsoMu24_eta2p1_charge_eta_pt_PLOT')

	print h_sfPog.GetNbinsX(), h_sfPog.GetNbinsY(), h_sfPog.GetNbinsZ()
	print h_sfPog.GetXaxis().GetBinLowEdge(1),h_sfPog.GetXaxis().GetBinUpEdge(h_sfPog.GetNbinsX())
	print h_sfPog.GetYaxis().GetBinLowEdge(1),h_sfPog.GetYaxis().GetBinUpEdge(h_sfPog.GetNbinsY())
	print h_sfPog.GetZaxis().GetBinLowEdge(1),h_sfPog.GetZaxis().GetBinUpEdge(h_sfPog.GetNbinsZ())

	print h_sfSergey.GetNbinsX(), h_sfSergey.GetNbinsY(), h_sfSergey.GetNbinsZ()
	print h_sfSergey.GetXaxis().GetBinLowEdge(1),h_sfSergey.GetXaxis().GetBinUpEdge(h_sfSergey.GetNbinsX())
	print h_sfSergey.GetYaxis().GetBinLowEdge(1),h_sfSergey.GetYaxis().GetBinUpEdge(h_sfSergey.GetNbinsY())
	print h_sfSergey.GetZaxis().GetBinLowEdge(1),h_sfSergey.GetZaxis().GetBinUpEdge(h_sfSergey.GetNbinsZ())

	h = Hist2D( 42, -2.1, 2.1, 75, 25, 100 )

	for pt in range(25,100):
		for eta in range(-21,21):
			fEta = float(eta)/10
			sfSergey = h_sfSergey.GetBinContent( h_sfSergey.FindBin( pt, fEta ) )
			sfSergeyError = h_sfSergey.GetBinError( h_sfSergey.FindBin( pt, fEta ) )

			if doId:
				sfPOG = h_sfPog.GetBinContent( h_sfPog.FindBin( fEta, pt ) )
				sfPOGError = h_sfPog.GetBinError( h_sfPog.FindBin( fEta, pt ) )
			else:
				sfPOG = (h_sfPog.GetBinContent( h_sfPog.FindBin( 1, fEta, pt ) ) + h_sfPog.GetBinContent( h_sfPog.FindBin( -1, fEta, pt ) ) ) / 2
				sfPOGError = sqrt(h_sfPog.GetBinError( h_sfPog.FindBin( 1, fEta, pt ) )**2 + h_sfPog.GetBinError( h_sfPog.FindBin( -1, fEta, pt ) )**2 )

			difference = abs( (sfSergey - sfPOG) )
			errorOnDifference = sqrt( sfPOGError**2 + sfSergeyError**2 )
			# print pt, eta, sfSergey, sfPOG

			bin = h.FindBin( fEta, pt )

			if fEta >= 0.7 and fEta < 0.8:
				print fEta, pt, sfSergey, sfPOG, difference / errorOnDifference

			if errorOnDifference != 0:
				# if fEta >= 0 and fEta < 0.3:
				# 	print 'Filling ',bin,'with',difference / errorOnDifference
				# 	x = 0
				# 	y = 0
				# 	z = 0
				# 	h.GetBinXYZ(bin, Long(x), Long(y), Long(z))
				# 	print x,y

				h.SetBinContent( bin, difference / errorOnDifference )
			else:
				print 'ZERO',pt, fEta,
				h.SetBinContent( bin, 0 )


			# if errorOnDifference != 0 :
			# 	if difference / errorOnDifference > 10: 
			# 		print difference / errorOnDifference
			# 		# print 'PANIC'
			# 		print pt, fEta, sfSergey, sfPOG, sfSergeyError, sfPOGError, difference, errorOnDifference, difference / errorOnDifference
			# else: 
			# 	print 'ZERO ERROR'
			# 	print pt, eta, sfSergey, sfPOG, sfSergeyError, sfPOGError,

	canvas = Canvas(width=700, height=500)
	# h.GetZaxis().SetRangeUser(0,20)
	h.Draw('COLZ')
	raw_input('Waiting...')
