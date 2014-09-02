from __future__ import division  # the result of the division will be always a float
from optparse import OptionParser
import os, gc
from copy import deepcopy

from config.latex_labels import variables_latex, measurements_latex, \
met_systematics_latex, b_tag_bins_latex, fit_variables_latex
from config.variable_binning import bin_edges, variable_bins_ROOT, fit_variable_bin_edges
from config import XSectionConfig
from tools.file_utilities import read_data_from_JSON, make_folder_if_not_exists
from tools.hist_utilities import value_error_tuplelist_to_hist, \
value_tuplelist_to_hist, value_errors_tuplelist_to_graph, graph_to_value_errors_tuplelist
from math import sqrt
# rootpy & matplotlib
from ROOT import kRed, kGreen, kMagenta, kBlue, kBlack
from tools.ROOT_utililities import set_root_defaults
import matplotlib as mpl
from tools.plotting import get_best_max_y
mpl.use( 'agg' )
import rootpy.plotting.root2matplotlib as rplt
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.ticker import MultipleLocator
from config import CMS
from matplotlib import rc
# rc( 'font', **CMS.font )
# rc( 'text', usetex = True )
rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
rc('text', usetex=True)

plt.rc('text', usetex=True)
plt.rc('font', family='sans-serif')
mpl.rc('text', usetex=True)
mpl.rc('font', family='sans-serif')

def read_xsection_measurement_results( category, channel ):
    global path_to_JSON, variable, k_values, met_type
    
    filename = ''
    if category in met_uncertainties and variable == 'HT':
        filename = path_to_JSON + '/xsection_measurement_results/' + channel + '/kv' + str( k_values[channel] ) + '/central/normalised_xsection_' + met_type + '.txt' 
    else:
        filename = path_to_JSON + '/xsection_measurement_results/' + channel + '/kv' + str( k_values[channel] ) + '/' + category + '/normalised_xsection_' + met_type + '.txt'

    if channel == 'combined':
        filename = filename.replace( 'kv' + str( k_values[channel] ), '' )

    normalised_xsection_unfolded = read_data_from_JSON( filename )
        
    h_normalised_xsection = value_error_tuplelist_to_hist( normalised_xsection_unfolded['TTJet_measured'], bin_edges[variable] )
    h_normalised_xsection_unfolded = value_error_tuplelist_to_hist( normalised_xsection_unfolded['TTJet_unfolded'], bin_edges[variable] )
    
    
    histograms_normalised_xsection_different_generators = {'measured':h_normalised_xsection,
                                                           'unfolded':h_normalised_xsection_unfolded}
    
    histograms_normalised_xsection_systematics_shifts = {'measured':h_normalised_xsection,
                                                         'unfolded':h_normalised_xsection_unfolded}
    
    if category == 'central':
        # true distributions
        h_normalised_xsection_MADGRAPH = value_error_tuplelist_to_hist( normalised_xsection_unfolded['MADGRAPH'], bin_edges[variable] )
        h_normalised_xsection_MADGRAPH_ptreweight = value_error_tuplelist_to_hist( normalised_xsection_unfolded['MADGRAPH_ptreweight'], bin_edges[variable] )
        h_normalised_xsection_POWHEG_PYTHIA = value_error_tuplelist_to_hist( normalised_xsection_unfolded['POWHEG_PYTHIA'], bin_edges[variable] )
        h_normalised_xsection_POWHEG_HERWIG = value_error_tuplelist_to_hist( normalised_xsection_unfolded['POWHEG_HERWIG'], bin_edges[variable] )
        h_normalised_xsection_MCATNLO = value_error_tuplelist_to_hist( normalised_xsection_unfolded['MCATNLO'], bin_edges[variable] )
        h_normalised_xsection_mathchingup = value_error_tuplelist_to_hist( normalised_xsection_unfolded['matchingup'], bin_edges[variable] )
        h_normalised_xsection_mathchingdown = value_error_tuplelist_to_hist( normalised_xsection_unfolded['matchingdown'], bin_edges[variable] )
        h_normalised_xsection_scaleup = value_error_tuplelist_to_hist( normalised_xsection_unfolded['scaleup'], bin_edges[variable] )
        h_normalised_xsection_scaledown = value_error_tuplelist_to_hist( normalised_xsection_unfolded['scaledown'], bin_edges[variable] )
        
        histograms_normalised_xsection_different_generators.update( {'MADGRAPH':h_normalised_xsection_MADGRAPH,
                                                                    'MADGRAPH_ptreweight':h_normalised_xsection_MADGRAPH_ptreweight,
                                                                    'POWHEG_PYTHIA':h_normalised_xsection_POWHEG_PYTHIA,
                                                                    'POWHEG_HERWIG':h_normalised_xsection_POWHEG_HERWIG,
                                                                    'MCATNLO':h_normalised_xsection_MCATNLO} )
        
        histograms_normalised_xsection_systematics_shifts.update( {'MADGRAPH':h_normalised_xsection_MADGRAPH,
                                                                  'MADGRAPH_ptreweight':h_normalised_xsection_MADGRAPH_ptreweight,
                                                                  'matchingdown': h_normalised_xsection_mathchingdown,
                                                                  'matchingup': h_normalised_xsection_mathchingup,
                                                                  'scaledown': h_normalised_xsection_scaledown,
                                                                  'scaleup': h_normalised_xsection_scaleup} )
        
        file_template = path_to_JSON + '/xsection_measurement_results/' + channel + '/kv' + str( k_values[channel] ) + '/' + category + '/normalised_xsection_' + met_type
        if channel == 'combined':
            file_template = file_template.replace( 'kv' + str( k_values[channel] ), '' )
#         normalised_xsection_unfolded_with_errors = read_data_from_JSON( file_template + '_with_errors.txt' )
        normalised_xsection_unfolded_with_errors_with_systematics_but_without_ttbar_theory = read_data_from_JSON( file_template + '_with_systematics_but_without_ttbar_theory_errors.txt' )
        normalised_xsection_unfolded_with_errors_with_systematics_but_without_generator = read_data_from_JSON( file_template + '_with_systematics_but_without_generator_errors.txt' )

        # a rootpy.Graph with asymmetric errors!
        h_normalised_xsection_with_systematics_but_without_ttbar_theory = value_errors_tuplelist_to_graph( 
                                                                normalised_xsection_unfolded_with_errors_with_systematics_but_without_ttbar_theory['TTJet_measured'],
                                                                bin_edges[variable] )
        h_normalised_xsection_with_systematics_but_without_ttbar_theory_unfolded = value_errors_tuplelist_to_graph( 
                                                                normalised_xsection_unfolded_with_errors_with_systematics_but_without_ttbar_theory['TTJet_unfolded'],
                                                                bin_edges[variable] )
        
        h_normalised_xsection_with_systematics_but_without_generator = value_errors_tuplelist_to_graph( 
                                                                normalised_xsection_unfolded_with_errors_with_systematics_but_without_generator['TTJet_measured'],
                                                                bin_edges[variable] )
        h_normalised_xsection_with_systematics_but_without_generator_unfolded = value_errors_tuplelist_to_graph( 
                                                                normalised_xsection_unfolded_with_errors_with_systematics_but_without_generator['TTJet_unfolded'],
                                                                bin_edges[variable] )
        
        
        histograms_normalised_xsection_different_generators['measured_with_systematics'] = h_normalised_xsection_with_systematics_but_without_ttbar_theory
        histograms_normalised_xsection_different_generators['unfolded_with_systematics'] = h_normalised_xsection_with_systematics_but_without_ttbar_theory_unfolded
        
        histograms_normalised_xsection_systematics_shifts['measured_with_systematics'] = h_normalised_xsection_with_systematics_but_without_generator
        histograms_normalised_xsection_systematics_shifts['unfolded_with_systematics'] = h_normalised_xsection_with_systematics_but_without_generator_unfolded
    
    return histograms_normalised_xsection_different_generators, histograms_normalised_xsection_systematics_shifts

def get_cms_labels( channel, measurement_config ):
    global b_tag_bin
    lepton = 'e'
    if channel == 'electron':
        lepton = 'e + jets'
    elif channel == 'muon':
        lepton = '$\mu$ + jets'
    else:
        lepton = 'e, $\mu$ + jets combined'
#     channel_label = '%s, $\geq$ 4 jets, %s' % ( lepton, b_tag_bins_latex[b_tag_bin] )
    channel_label = lepton
    # template = 'CMS Preliminary, %.1f fb$^{-1}$ (%d TeV), %s'

    label = 'CMS'
    return label
 
def get_lumi_labels( measurement_config ):
    label = '%.1f fb$^{-1}$ (%d TeV) Example Text' % ( measurement_config.new_luminosity / 1000., measurement_config.centre_of_mass_energy )
    return label

def make_plots( histogramsForAllCom, category, output_folder, histname, show_ratio = True, show_before_unfolding = False ):
    global variable, k_values
    
    channel = 'combined'

    if show_ratio:
        gs = gridspec.GridSpec( 2, 2, height_ratios = [5, 1], width_ratios = [1,1] ) 
    else:
        gs = gridspec.GridSpec( 1, 2, width_ratios = [1,1] ) 

    gridIndex = 0

    plt.figure( figsize = CMS.widefigsize, dpi = CMS.dpi, facecolor = CMS.facecolor )

    isLeftMostPlot = True
    isRightMostPlot = False

    for com in [7,8]:

        if show_ratio and ( gridIndex != 0 and gridIndex != 2 ):
            isLeftMostPlot = False
        elif not show_ratio and gridIndex != 0:
            isLeftMostPlot = False
        else:
            isLeftMostPlot = True

        if isLeftMostPlot :
            isRightMostPlot = False
        else:
            isRightMostPlot = True

        measurement_config = XSectionConfig( com )
        histograms = histogramsForAllCom[com]

        # plot with matplotlib
        hist_data = histograms['unfolded']
        if category == 'central':
            hist_data_with_systematics = histograms['unfolded_with_systematics']
        hist_measured = histograms['measured']
        
        hist_data.markersize = 2
        hist_data.marker = 'o'

        if category == 'central':
            hist_data_with_systematics.markersize = 2
            hist_data_with_systematics.marker = 'o'
        
        hist_measured.markersize = 2
        hist_measured.marker = 'o'
        hist_measured.color = 'red'


        if show_ratio:
            axes = plt.subplot( gs[gridIndex] )
        else:
            axes = plt.axes()
            plt.xlabel( '$%s$ [GeV]' % variables_latex[variable], CMS.x_axis_title )

        axes.minorticks_on()
        
        if isLeftMostPlot:
            plt.ylabel( r'$\frac{1}{\sigma}  \frac{d\sigma}{d' + variables_latex[variable] + '} \left[\mathrm{GeV}^{-1}\\right]$', CMS.y_axis_title )
        else :
            plt.setp( axes.get_yticklabels(), visible = False )
        plt.tick_params( **CMS.axis_label_major )
        plt.tick_params( **CMS.axis_label_minor )

        hist_data.visible = True
        if category == 'central':
            hist_data_with_systematics.visible = True
            rplt.errorbar( hist_data_with_systematics, axes = axes, label = 'do_not_show', xerr = None, capsize = 0, elinewidth = 2, zorder = len( histograms ) + 1 )
        rplt.errorbar( hist_data, axes = axes, label = 'do_not_show', xerr = None, capsize = 15, capthick = 3, elinewidth = 2, zorder = len( histograms ) + 2 )
        rplt.errorbar( hist_data, axes = axes, label = 'data', xerr = False, yerr = False, zorder = len( histograms ) + 3 )  # this makes a nicer legend entry
        
        for key, hist in sorted( histograms.iteritems() ):
            if not 'unfolded' in key and not 'measured' in key:
                hist.linewidth = 2
                # setting colours
                if 'POWHEG_PYTHIA' in key or 'matchingdown' in key:
                    hist.linestyle = 'longdashdot'
                    hist.SetLineColor( kBlue )
                elif 'POWHEG_HERWIG' in key or 'scaledown' in key:
                    hist.linestyle = 'dashed'
                    hist.SetLineColor( kGreen )
                elif 'MADGRAPH_ptreweight' in key:
                    hist.linestyle = 'solid'
                    hist.SetLineColor( kBlack )
                elif 'MADGRAPH' in key:
                    hist.linestyle = 'solid'
                    hist.SetLineColor( kRed + 1 )
                elif 'matchingup' in key:
                    hist.linestyle = 'verylongdashdot'
                    hist.linecolor = 'orange'
                elif 'MCATNLO'  in key or 'scaleup' in key:
                    hist.linestyle = 'dotted'
                    hist.SetLineColor( kMagenta + 3 )
                rplt.hist( hist, axes = axes, label = measurements_latex[key], zorder = sorted( histograms, reverse = True ).index( key ) )
                
        handles, labels = axes.get_legend_handles_labels()
        # making data first in the list
        data_label_index = labels.index( 'data' )
        data_handle = handles[data_label_index]
        labels.remove( 'data' )
        handles.remove( data_handle )
        labels.insert( 0, 'unfolded data' )
        handles.insert( 0, data_handle )
        
        new_handles, new_labels = [], []
        for handle, label in zip( handles, labels ):
            if not label == 'do_not_show':
                new_handles.append( handle )
                new_labels.append( label )
        
        legend_location = 'center right'
        if variable == 'MT':
            legend_location = 'center left'
        if isRightMostPlot:
            lg = plt.legend( new_handles, new_labels, numpoints = 1, loc = legend_location, prop = CMS.legend_properties )
            lg.draw_frame(False)
        # plt.title( get_cms_labels( channel, measurement_config ), CMS.title )
        plt.title( get_lumi_labels( measurement_config), CMS.title, loc='right' )

        plt.annotate( 'CMS', xy=(0.85,0.9), xycoords='axes fraction', fontsize='40', fontweight='extra bold')

        if show_ratio:
            plt.setp( axes.get_xticklabels(), visible = False )
            ax1 = plt.subplot( gs[gridIndex+2] )

            ax1.minorticks_on()
            #ax1.grid( True, 'major', linewidth = 1 )
            # setting the x_limits identical to the main plot
            x_limits = axes.get_xlim()
            ax1.set_xlim(x_limits)
            ax1.yaxis.set_major_locator( MultipleLocator( 0.5 ) )
            ax1.yaxis.set_minor_locator( MultipleLocator( 0.1 ) )

            plt.xlabel( '$%s$ [GeV]' % variables_latex[variable], CMS.x_axis_title )
            plt.tick_params( **CMS.axis_label_major )
            plt.tick_params( **CMS.axis_label_minor )

            if isLeftMostPlot:
                plt.ylabel( '$\\frac{\\textrm{theory}}{\\textrm{data}}$', CMS.y_axis_title_small )
                ax1.yaxis.set_label_coords(-0.115, 0.8)
            else:
                ax1.set_yticklabels([])

            #draw a horizontal line at y=1 for data
            plt.axhline(y = 1, color = 'black', linewidth = 1)

            for key, hist in sorted( histograms.iteritems() ):
                if not 'unfolded' in key and not 'measured' in key:
                    ratio = hist.Clone()
                    ratio.Divide( hist_data ) #divide by data
                    rplt.hist( ratio, axes = ax1, label = 'do_not_show' )

            stat_lower = hist_data.Clone()
            stat_upper = hist_data.Clone()
            syst_lower = hist_data.Clone()
            syst_upper = hist_data.Clone()

            # plot error bands on data in the ratio plot
            for bin_i in range( 1, hist_data.GetNbinsX() + 1 ):
                stat_errors = graph_to_value_errors_tuplelist(hist_data)
                stat_lower.SetBinContent( bin_i, 1 - stat_errors[bin_i-1][1]/stat_errors[bin_i-1][0] )
                stat_upper.SetBinContent( bin_i, 1 + stat_errors[bin_i-1][2]/stat_errors[bin_i-1][0] )
                if category == 'central':
                    syst_errors = graph_to_value_errors_tuplelist(hist_data_with_systematics)
                    syst_lower.SetBinContent( bin_i, 1 - syst_errors[bin_i-1][1]/syst_errors[bin_i-1][0] )
                    syst_upper.SetBinContent( bin_i, 1 + syst_errors[bin_i-1][2]/syst_errors[bin_i-1][0] )

            if category == 'central':
                rplt.fill_between( syst_lower, syst_upper, ax1, facecolor = 'yellow', alpha = 0.5 )

            rplt.fill_between( stat_upper, stat_lower, ax1, facecolor = '0.75', alpha = 0.5 )

            # p1 = plt.Rectangle((0, 0), 1, 1, fc="yellow")
            # p2 = plt.Rectangle((0, 0), 1, 1, fc="0.75") 
            # plt.legend([p1, p2], ['Stat. $\\oplus$ Syst.', 'Stat.'], loc = 'upper left', prop = {'size':20})
            ax1.set_ylim( ymin = 0.5, ymax = 1.5 )

        if CMS.tight_layout:
            plt.tight_layout()

        gridIndex += 1

    path = output_folder + 'SideBySide/' + variable + '/' + category
    make_folder_if_not_exists( path )
    for output_format in output_formats:
        filename = path + '/' + histname + '_kv' + str( k_values[channel] ) + '.' + output_format
        if channel == 'combined':
            filename = filename.replace( '_kv' + str( k_values[channel] ), '' )
        plt.savefig( filename )

    del hist_data, hist_measured
    plt.close()
    gc.collect()

if __name__ == '__main__':
    set_root_defaults()
    parser = OptionParser()
    parser.add_option( "-p", "--path", dest = "path", default = 'data/',
                  help = "set path to JSON files" )
    parser.add_option( "-o", "--output_folder", dest = "output_folder", default = 'plots/',
                  help = "set path to save plots" )
    parser.add_option( "-v", "--variable", dest = "variable", default = 'MET',
                  help = "set variable to plot (MET, HT, ST, MT)" )
    parser.add_option( "-m", "--metType", dest = "metType", default = 'type1',
                      help = "set MET type used in the analysis of MET, ST or MT" )
    parser.add_option( "-b", "--bjetbin", dest = "bjetbin", default = '2m',
                  help = "set b-jet multiplicity for analysis. Options: exclusive: 0-3, inclusive (N or more): 0m, 1m, 2m, 3m, 4m" )
    parser.add_option( "-a", "--additional-plots", action = "store_true", dest = "additional_plots",
                      help = "creates a set of plots for each systematic (in addition to central result)." )
    
    output_formats = ['png', 'pdf']
    ( options, args ) = parser.parse_args()

    histograms_generators = {}
    histograms_systematics = {}
    for com in [7,8]:
        
        measurement_config = XSectionConfig( com )
        # caching of variables for shorter access
        translate_options = measurement_config.translate_options
        ttbar_theory_systematic_prefix = measurement_config.ttbar_theory_systematic_prefix
        vjets_theory_systematic_prefix = measurement_config.vjets_theory_systematic_prefix
        met_systematics_suffixes = measurement_config.met_systematics_suffixes
        
        variable = options.variable
        output_folder = options.output_folder
        if not output_folder.endswith( '/' ):
            output_folder += '/'
        k_values = {
                    'combined' : 'None'
                    }
        met_type = translate_options[options.metType]
        b_tag_bin = translate_options[options.bjetbin]
        path_to_JSON = options.path + '/' + str( measurement_config.centre_of_mass_energy ) + 'TeV/' + variable + '/'
        
        categories = deepcopy( measurement_config.categories_and_prefixes.keys() )
        ttbar_generator_systematics = [ttbar_theory_systematic_prefix + systematic for systematic in measurement_config.generator_systematics]
        vjets_generator_systematics = [vjets_theory_systematic_prefix + systematic for systematic in measurement_config.generator_systematics]
        categories.extend( ttbar_generator_systematics )
        categories.extend( vjets_generator_systematics )
        
        # all MET uncertainties except JES as this is already included
        met_uncertainties = [met_type + suffix for suffix in met_systematics_suffixes if not 'JetEn' in suffix and not 'JetRes' in suffix]
        
        all_measurements = deepcopy( categories )
        all_measurements.extend( met_uncertainties )
        for channel in ['combined']:
            for category in all_measurements:
                if not category == 'central':
                    continue
                # setting up systematic MET for JES up/down samples for reading fit templates
                met_type = translate_options[options.metType]

                # change back to original MET type
                met_type = translate_options[options.metType]
                if met_type == 'PFMET':
                    met_type = 'patMETsPFlow'
                
                histograms_normalised_xsection_different_generators, histograms_normalised_xsection_systematics_shifts = read_xsection_measurement_results( category, channel )
                histograms_generators[com] = histograms_normalised_xsection_different_generators
                histograms_systematics[com] = histograms_normalised_xsection_systematics_shifts
                # make_plots( histograms_normalised_xsection_different_generators, category, output_folder, 'normalised_xsection_' + channel + '_different_generators' )
                # make_plots( histograms_normalised_xsection_systematics_shifts, category, output_folder, 'normalised_xsection_' + channel + '_systematics_shifts' )

    make_plots( histograms_generators, 'central', output_folder, 'normalised_xsection_' + channel + '_different_generators' )
    # make_plots( histograms_systematics, category, output_folder, 'normalised_xsection_' + channel + '_systematics_shifts' )