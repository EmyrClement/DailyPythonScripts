export ORIGDIR=`pwd`
cd ../
. $VO_CMS_SW_DIR/cmsset_default.sh
export SCRAM_ARCH=slc6_amd64_gcc481
cmsrel CMSSW_7_1_3
cd CMSSW_7_1_3/src/
cmsenv
git clone https://github.com/BristolTopGroup/DailyPythonScripts.git
cd DailyPythonScripts
git submodule init && git submodule update
./setup_standalone.sh
export base=`pwd`
export vpython=$base/external/vpython

if [ -d "$vpython" ]; then
        echo "Activating virtual python environment"
        export VIRTUAL_ENV_DISABLE_PROMPT=1
        source $vpython/bin/activate
fi

cd $base
export PYTHONPATH=$PYTHONPATH:`pwd`
export PATH=$PATH:$base/bin


mv $ORIGDIR/mergeScript.py .
python mergeScript.py -j $1

echo 'After running'
pwd
