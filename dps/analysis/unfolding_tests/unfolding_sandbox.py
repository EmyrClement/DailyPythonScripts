'''
    A basic script for manually playing around with the unfolding
    Useful for debugging e.g. with known inputs and outputs
    Currently set up to unfold measured MC and compare to truth MC
'''
from rootpy.io import File

from dps.utils.Unfolding import Unfolding, get_unfold_histogram_tuple
from dps.config.xsection import XSectionConfig
from rootpy import asrootpy
import ROOT as r

def main():

    config = XSectionConfig(13)
    method = 'TUnfold'

    # A few different files for testing different inputs
    file_for_unfolding = File(config.unfolding_central, 'read')
    powheg_herwig_file = File(config.unfolding_powheg_herwig, 'read')

    # for channel in ['combined', 'muon', 'electron']:
    for channel in ['muon']:

        # for variable in config.variables:
        for variable in ['HT']:
        
            print variable
            data = [1924.4735578536986, 25682.269956064225, 29227.654213821887, 32069.328189885615, 32646.642462164164, 28402.32725772858, 27363.846755504605, 21846.973779034615, 17554.106704711914, 13811.932735794782, 10980.524793356657, 8244.573209935426, 7173.377163338661, 4955.374866575003, 3685.5585090100767, 2837.144918859005, 2359.2253744602203, 1603.8065546751022, 1343.20689496994, 976.8266459226609, 812.7188339412212, 477.89672139286995, 314.6792103230953, 304.0482513427734, 699.5895061969758, 205.6797859668732]
            # tau_value = get_tau_value(config, channel, variable)
            # tau_value = 0.000228338590921
            tau_value = 0.000

            h_truth, h_measured, h_response, h_fakes = get_unfold_histogram_tuple(
                inputfile=file_for_unfolding,
                variable=variable,
                channel=channel,
                met_type=config.met_type,
                centre_of_mass=config.centre_of_mass_energy,
                ttbar_xsection=config.ttbar_xsection,
                luminosity=config.luminosity,
                load_fakes=False,
                visiblePS=True,
            )

            measured = asrootpy(h_response.ProjectionX('px',1))
            print 'Measured from response :',list(measured.rebin(2).y())[-2]
            truth = asrootpy(h_response.ProjectionY())
            print 'Truth from response :',list(truth.y())[-1]

            h_truth_ph, h_measured_ph, h_response_ph, h_fakes_ph = get_unfold_histogram_tuple(
                inputfile=powheg_herwig_file,
                variable=variable,
                channel=channel,
                met_type=config.met_type,
                centre_of_mass=config.centre_of_mass_energy,
                ttbar_xsection=config.ttbar_xsection,
                luminosity=config.luminosity,
                load_fakes=False,
                visiblePS=True,
            )

            measured = asrootpy(h_response.ProjectionX('px',1))
            # print 'Measured from response :',list(measured.y())
            # measured.SetBinContent(0,0)
            truth = asrootpy(h_response.ProjectionY())
            # print 'Truth from response :',list(truth.y())
            # print 'Truth underflow : ',truth.GetBinContent(0),truth.GetBinContent(truth.GetNbinsX()+1)

            # measured.SetBinContent(1,0)
            # for i in range(0, len(data)):
            #     measured.SetBinContent(i+1, data[i])

            # for i in range(0, len(data)):
            #     new_measured = 
            
            # Unfold
            print 'Tau :',tau_value
            print 'Measured :',list( measured.y() )
            print measured.GetNbinsX()

            unfolding = Unfolding( measured,
                None, None, h_response, None,
                method=method, tau=tau_value)
            input = asrootpy( unfolding.unfoldObject.GetInput('Input') )
            print input.GetBinContent(0), input.GetBinContent(1)
            # unfolded_data = unfolding.closureTest()

            # print 'Measured :',list( h_measured.y() )
            # h_measured, _ = removeFakes( h_measured, None, h_response)

            # for binx in range(0,h_truth.GetNbinsX()+2):
            #     for biny in range(0,h_truth.GetNbinsX()+2):
            #         print binx, biny,h_response.GetBinContent(binx,biny)
                # print bin,h_truth.GetBinContent(bin)
            # print 'Tau :',tau_value

            unfolded_results = unfolding.unfold()
            # print 'Unfolded :',list( unfolded_results.y() )
            refolded_results = unfolding.refold()
            refolded_results.rebin(2)
            measured.rebin(2)

            print 'Unfolded :',list( unfolded_results.y() )
            print len(list( unfolded_results.y() ))
            print 'Refolded :',list( refolded_results.y() )[-2]

            # print 'Response :',list( h_response.z() )

            chi2 = 0
            # for i in range(1,refolded_results.GetNbinsX()):
            #     print i,measured.GetBinContent(i),measured.GetBinError(i),abs( measured.GetBinContent(i) - refolded_results.GetBinContent(i) )/measured.GetBinError(i)
            #     chi2 += ( measured.GetBinContent(i) - refolded_results.GetBinContent(i) ) ** 2 / measured.GetBinError(i) ** 2

            # print r.TMath.Prob( chi2, len( list( measured.y() ) ))
            pValue = measured.Chi2Test(refolded_results)

            print pValue,1-pValue
            # print unfolding.unfoldObject.GetTau()


def get_tau_value(config, channel, variable):
    if channel == 'electron':
        return config.tau_values_electron[variable]
    if channel == 'muon':
        return config.tau_values_muon[variable]
    if channel == 'combined':
        return config.tau_values_combined[variable]


if __name__ == '__main__':
    # set_root_defaults( msg_ignore_level = 3001 )
    main()
