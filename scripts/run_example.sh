#!/bin/bash
sh test_genspeech.sh 
cd ..
python utils/prepend_files.py --prepend_with "resources/" --dataset "resources/test_genspeech.csv"
python pipeline.py --root_node_id "Load DF" --graph_config_path "config/example.json"