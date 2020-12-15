#!/bin/bash
set -eo pipefail
#Entering into a bash shell script to run unit-test cases and generating reports
echo "Coding analysis will be performed shortly..."
python3 -m pip install pylint2junit junitparser; \
#python3 -m pip install --index-url https://nexus.engageska-portugal.pt/repository/pypi/simple ska-logging==0.3.0 lmcbaseclasses==0.7.2 cdm-shared-library==2.0.0 ska-telescope-model==0.1.4 
pwd
# for path in $(find tmc/common  -type f ); do
# 	export TMC_COMMON=$(basename $(dirname $(dirname $path)));
# 	echo +++ linting for $TMC_COMMON;
# 	cd $TMC_COMMON;
# 	python3 -m pip install .;
#   cd ..
# done

python3 -m pip install .;
cd ../
mkdir -p ./build/reports; \
pylint --rcfile=.pylintrc --output-format=parseable  src/tmc | tee ./build/reports/linting.stdout; \
pylint --rcfile=.pylintrc --output-format=pylint2junit.JunitReporter src/tmc > ./build/reports/linting.xml;
