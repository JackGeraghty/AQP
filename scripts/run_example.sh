#!/bin/bash
sh get_quickstart_genspeech.sh 
python prepend_files.py --prepend_with "resources/" --dataset "../resources/quickstart_genspeech.csv"
if [ $? -eq 0 ]
then
    cd ..
    python pipeline.py --root_node_id "Load DF" --graph_config_path "config/example.json"
else
    echo "Prepend files exitted with error code 1, not running pipeline"
fi