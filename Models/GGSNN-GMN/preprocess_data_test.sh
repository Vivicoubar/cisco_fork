docker run --rm \
       -v $(pwd)/../../DBs/Dataset-Muaz/features/acfg_disasm:/input \
       -v $(pwd)/Preprocessing/Dataset-1_training:/training_data \
       -v $(pwd)/Preprocessing/Dataset-Muaz:/output \
       -it gnn-preprocessing /code/gnn_preprocessing.py -i /input -d /training_data/opcodes_dict.json -o /output
