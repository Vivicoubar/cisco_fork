# Preprocess data training
docker run --rm \
    -v $(pwd)/../../DBs/Dataset-adv/features/training/acfg_disasm_Dataset-adv_training:/input \
    -v $(pwd)/Preprocessing/Dataset-adv_training:/output \
     	 -v $(pwd)/Preprocessing/Dataset-1_training:/training_data \
    -it gnn-preprocessing /code/gnn_preprocessing.py -i /input -d /training_data/opcodes_dict.json -o /output

# Preprocess data validation
docker run --rm \
    -v $(pwd)/../../DBs/Dataset-adv/features/validation/acfg_disasm_Dataset-adv_validation:/input \
     	 -v $(pwd)/Preprocessing/Dataset-1_training:/training_data \
    -v $(pwd)/Preprocessing/Dataset-adv_validation:/output \
    -it gnn-preprocessing /code/gnn_preprocessing.py -i /input -d /training_data/opcodes_dict.json -o /output

# Preprocess data testing
docker run --rm \
    -v $(pwd)/../../DBs/Dataset-adv/features/testing/acfg_disasm_Dataset-adv_testing:/input \
     	 -v $(pwd)/Preprocessing/Dataset-1_training:/training_data \
    -v $(pwd)/Preprocessing/Dataset-adv_testing:/output \
    -it gnn-preprocessing /code/gnn_preprocessing.py -i /input -d /training_data/opcodes_dict.json -o /output

# Train GNN

echo "tran gnn press smth"
read input

docker run --rm \
    -v $(pwd)/../../DBs:/input \
    -v $(pwd)/NeuralNetwork:/output \
    -v $(pwd)/Preprocessing:/preprocessing \
    -it gnn-neuralnetwork /code/gnn.py --train --num_epochs 10 \
        --model_type embedding --training_mode pair \
        --features_type opc --dataset adv \
        --restore \
        -c /output/model_checkpoint_GNN_DB-adv \
        -o /output/Dataset-adv_training_GNN_opc_pair

# Train GMN
echo "train gmn press smth"
read input

docker run --rm \
    -v $(pwd)/../../DBs:/input \
    -v $(pwd)/NeuralNetwork:/output \
    -v $(pwd)/Preprocessing:/preprocessing \
    -it gnn-neuralnetwork /code/gnn.py --train --num_epochs 10 \
        --model_type matching --training_mode pair \
        --features_type opc --dataset adv \
        --restore \
        -c /output/model_checkpoint_GMN_DB-adv \
        -o /output/Dataset-adv_training_GMN_opc_pair

