#!/bin/bash

config=$1

dir=`find shed_tools -type d  -regextype posix-egrep -iregex ".*irida_import/.+/irida_import"`
cp $config $dir


#find env.sh file of irida_import
source_file=`find  deps/irida-galaxy-importer/ -name 'env.sh'`

source $source_file
cd $dir
python irida_import.py -c
supervisorctl restart gx:
