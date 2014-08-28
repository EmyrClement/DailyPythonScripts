from optparse import OptionParser
from config.summations_8TeV import sample_summations as sample_summations_8TeV
from config.summations_7TeV import sample_summations as sample_summations_7TeV
from config import XSectionConfig
from tools.file_utilities import make_folder_if_not_exists

from tools.file_utilities import merge_ROOT_files
import os
import subprocess
import time

jobs=[]

# parser = OptionParser()
# parser.add_option('-s','--sample',type='string',dest='sample')
# parser.add_option('-c','--category',type='string',dest='category',default='central')
# parser.add_option('--is8TeV',action="store_true", dest="is8TeV")
# (options, _) = parser.parse_args()
# sample = options.sample
# category = options.sample

parser = OptionParser()
parser.add_option('-j','--job_number',type='int',dest='jobNumber',default=0)
(options, _) = parser.parse_args()
job = jobs[options.jobNumber]
sample = job[0]
category = job[1]
is8TeV = job[2]

config = 0
sample_summations = 0
if is8TeV:
	config = XSectionConfig(8)
	sample_summations = sample_summations_8TeV
else:
	config = XSectionConfig(7)
	sample_summations = sample_summations_7TeV



input_samples = sample_summations[sample]

# Check output path
finalOutputPath = config.path_to_files + '/' + category
finalOutputPath = finalOutputPath.replace("/hdfs/TopQuarkGroup/results/histogramfiles", "/hdfs/tmp/TQG/")
#Make folder for category (e.g. central, BJet_up, LightJet_up, etc....)
make_folder_if_not_exists( finalOutputPath )

print 'Merging ',sample,category
# Generator systematics
if sample in ['VJets-matchingup',
              'VJets-matchingdown', 'VJets-scaleup',
              'VJets-scaledown']: #
	input_files = [config.central_general_template % input_sample for input_sample in input_samples]
	input_files = ' '.join(input_files)
	output_file = config.central_general_template % sample
	output_file = output_file.split('/')[-1]
	# command = 'hadd -f%d %s %s' %(7, output_file, input_files)
	command = 'touch '+output_file
	os.system(command)
	# Copy output to hdfs
	print 'Moving output'
	copyCommand = 'mv '+output_file+' '+finalOutputPath
	# os.system(copyCommand)
elif sample in ['QCD_Electron', 'QCD_Muon', 'VJets',
                          'SingleTop']: #
	print 'Merging ',sample,category
	input_files = [config.general_category_templates[category] % input_sample for input_sample in input_samples]
	input_files = ' '.join(input_files)
	output_file = config.general_category_templates[category] % sample
	output_file = output_file.split('/')[-1]
	print input_files
	print output_file
	# command = 'hadd -f%d %s %s' %(7, output_file, input_files)
	command = 'touch '+output_file
	os.system(command)
	# Copy output to hdfs
	print 'Moving output'
	copyCommand = 'mv '+output_file+' '+finalOutputPath
	os.system(copyCommand)
