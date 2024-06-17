# Pretrain
docker run --rm \
    -v $(pwd)/../../DBs/Dataset-1/features/training/acfg_disasm_Dataset-1_training:/input \
    -v $(pwd)/Pretraining/:/output \
    -it safe-pretraining /code/safe_pretraining.py -i /input -o /output/Dataset-1_training

# Preprocess train data
 docker run --rm \
    -v $(pwd)/../../DBs/Dataset-1/features/training/acfg_disasm_Dataset-1_training:/input \
    -v $(pwd)/Pretraining/Dataset-1_training:/instruction_embeddings \
    -v $(pwd)/Preprocessing:/output \
    -it safe-preprocessing /code/safe_preprocessing.py -i /input -o /output/Dataset-1_training

# Preprocess validation data
docker run --rm \
    -v $(pwd)/../../DBs/Dataset-1/features/validation/acfg_disasm_Dataset-1_validation:/input \
    -v $(pwd)/Pretraining/Dataset-1_training:/instruction_embeddings \
    -v $(pwd)/Preprocessing:/output \
    -it safe-preprocessing /code/safe_preprocessing.py -i /input -o /output/Dataset-1_validation

# Train
docker run --rm \
    -v $(pwd)/../../DBs:/input \
    -v $(pwd)/Pretraining/Dataset-1_training:/instruction_embeddings \
    -v $(pwd)/Preprocessing:/preprocessing \
    -v $(pwd)/NeuralNetwork/:/output \
    -it safe-neuralnetwork /code/safe_nn.py \
        --train \
        --num_epochs 5 \
        --dataset one \
        -c /output/model_checkpoint_$(date +'%Y-%m-%d') \
        -o /output/Dataset-1_training
