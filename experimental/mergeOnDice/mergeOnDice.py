from optparse import OptionParser
from config.summations_8TeV import sample_summations as sample_summations_8TeV
from config.summations_7TeV import sample_summations as sample_summations_7TeV
from config import XSectionConfig
from tools.file_utilities import make_folder_if_not_exists

import os
import subprocess
import time

def checkOptions():
    # A few checks
    if not ( options.run7TeV or options.run8TeV ):
        print 'You need to run on at least 7 or 8 TeV'
        os.sys.exit()
        pass
    
    if not ( options.runQCD or options.runVJets or options.runSingleTop or options.runVJetsSystematics ):
        print 'You need to run on at least one type of sample'
        os.sys.exit()
        pass
    
    if not ( options.runCentral or options.runCategories or options.runVJetsSystematics ):
        print 'You need to run on at least one type of analysis (central or systematics)'
        os.sys.exit()
        pass
    pass

def pickSamples( jobs, options, config, sample_summations, is8TeV ):
    samples = sample_summations.keys()
        
    for sample in samples:
        if options.runQCD and sample.find('QCD')>=0:
            addSamples(jobs, options, sample, is8TeV, config )
        if options.runVJets and sample.find('VJets')>=0 and sample.find('-')<0:
            addSamples(jobs, options, sample, is8TeV, config )
        if options.runSingleTop and sample.find('SingleTop')>=0:
            addSamples(jobs, options, sample, is8TeV, config )
        if options.runVJetsSystematics and sample.find('VJets')>=0 and sample.find('-')>=0:
            addSamples(jobs, options, sample, is8TeV, config )

def addSamples(jobs, options, sample, is8TeV, config ):
    if options.runCentral:
        jobs.append([sample,'central',is8TeV])
        makeOutputDir('central', config)
    if options.runCategories:
        categories = config.categories_and_prefixes.keys()
        for cat in categories:
            jobs.append([sample,cat,is8TeV])
            makeOutputDir(cat, config)

def makeOutputDir(category, config):
    outputPath = config.path_to_files + '/' + category
    outputPath = outputPath.replace("/hdfs/TopQuarkGroup/results/histogramfiles", "/hdfs/tmp/TQG/")
    make_folder_if_not_exists( outputPath )
    os.system('chmod a+w '+outputPath)

def makeCrabConfig(nJobs):
    oldCrabConfig = open('experimental/mergeOnDice/crab.cfg','r')
    newCrabConfig = open('crabConfig.cfg','w')
    
    for line in oldCrabConfig.readlines():
        if line.find('number_of_jobs')>=0:
            newCrabConfig.write('number_of_jobs = %i\n' % nJobs)
        else:
            newCrabConfig.write(line)
        pass
    oldCrabConfig.close()
    newCrabConfig.close()
    pass

def writeJobConfig(jobs):
    oldConfig = open('experimental/mergeOnDice/mergeScript.py','r')
    newConfig = open('mergeScript.py','w')
    
    for line in oldConfig.readlines():
        if line.find('jobs=[]')>=0:
            newConfig.write('jobs = [\n')
            for job in jobs:
                newConfig.write(str(job)+',\n')
                pass
            newConfig.write(']\n')
        else:
            newConfig.write(line)
        pass
    oldConfig.close()
    newConfig.close()
    pass

def submitCrabJob():
    os.system('crab -create -cfg crabConfig.cfg')
    os.system('crab -submit -c mergeOnDiceCrab')
    pass

parser = OptionParser()
parser.add_option('-c',action='store_true',dest='runCentral')
parser.add_option('--cat',action='store_true',dest='runCategories')

parser.add_option('--vsys',action='store_true',dest='runVJetsSystematics')

parser.add_option('-q',action='store_true',dest='runQCD')
parser.add_option('-v',action='store_true',dest='runVJets')
parser.add_option('-s',action='store_true',dest='runSingleTop')

parser.add_option('--run7',action='store_true',dest='run7TeV')
parser.add_option('--run8',action='store_true',dest='run8TeV')
(options, _) = parser.parse_args()

checkOptions()

jobs = []
if options.run7TeV:
    config = XSectionConfig(7)
    pickSamples(jobs, options, config, sample_summations_7TeV, False)

if options.run8TeV:
    config = XSectionConfig(8)
    pickSamples(jobs, options, config, sample_summations_8TeV, True)

nJobs=len(jobs)
print 'Number of jobs :',nJobs

makeCrabConfig(nJobs)

writeJobConfig(jobs)

submitCrabJob()

