# Preprocess data training
docker run --rm \
    -v $(pwd)/../../DBs/Dataset-1/features/training/acfg_disasm_Dataset-1_training:/input \
    -v $(pwd)/Preprocessing/Dataset-1_training:/output \
    -it gnn-preprocessing /code/gnn_preprocessing.py -i /input --training -o /output

# Preprocess data validation
docker run --rm \
    -v $(pwd)/../../DBs/Dataset-1/features/validation/acfg_disasm_Dataset-1_validation:/input \
    -v $(pwd)/Preprocessing/Dataset-1_training:/training_data \
    -v $(pwd)/Preprocessing/Dataset-1_validation:/output \
    -it gnn-preprocessing /code/gnn_preprocessing.py -i /input -d /training_data/opcodes_dict.json -o /output

# Train GNN

docker run --rm \
    -v $(pwd)/../../DBs:/input \
    -v $(pwd)/NeuralNetwork:/output \
    -v $(pwd)/Preprocessing:/preprocessing \
    -it gnn-neuralnetwork /code/gnn.py --train --num_epochs 10 \
        --model_type embedding --training_mode pair \
        --features_type opc --dataset one \
        -c /output/model_checkpoint_GNN_DB3_$(date +'%Y-%m-%d') \
        -o /output/Dataset-1_training_GNN_opc_pair

# Train GMN

docker run --rm \
    -v $(pwd)/../../DBs:/input \
    -v $(pwd)/NeuralNetwork:/output \
    -v $(pwd)/Preprocessing:/preprocessing \
    -it gnn-neuralnetwork /code/gnn.py --train --num_epochs 10 \
        --model_type matching --training_mode pair \
        --features_type opc --dataset one \
        -c /output/model_checkpoint_GMN_DB3_$(date +'%Y-%m-%d') \
        -o /output/Dataset-1_training_GMN_opc_pair

