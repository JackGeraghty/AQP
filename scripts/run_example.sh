#!/bin/bash
sh get_quickstart_genspeech.sh 
cd ..
python utils/prepend_files.py --prepend_with "resources/" --dataset "resources/quickstart_genspeech.csv"
python pipeline.py --root_node_id "Load DF" --graph_config_path "config/example.json"