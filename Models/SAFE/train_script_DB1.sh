# Pretrain
docker run --rm \
    -v $(pwd)/../../DBs/Dataset-adv/features/training/acfg_disasm_Dataset-adv_training:/input \
    -v $(pwd)/Pretraining/:/output \
    -it safe-pretraining /code/safe_pretraining.py -i /input -o /output/Dataset-adv_training

# Preprocess train data
 docker run --rm \
    -v $(pwd)/../../DBs/Dataset-adv/features/training/acfg_disasm_Dataset-adv_training:/input \
    -v $(pwd)/Pretraining/Dataset-adv_training:/instruction_embeddings \
    -v $(pwd)/Preprocessing:/output \
    -it safe-preprocessing /code/safe_preprocessing.py -i /input -o /output/Dataset-adv_training

# Preprocess validation data
docker run --rm \
    -v $(pwd)/../../DBs/Dataset-adv/features/validation/acfg_disasm_Dataset-adv_validation:/input \
    -v $(pwd)/Pretraining/Dataset-adv_training:/instruction_embeddings \
    -v $(pwd)/Preprocessing:/output \
    -it safe-preprocessing /code/safe_preprocessing.py -i /input -o /output/Dataset-adv_validation

# Preprocess test data (?)
 docker run --rm \
    -v $(pwd)/../../DBs/Dataset-adv/features/testing/acfg_disasm_Dataset-adv_testing:/input \
    -v $(pwd)/Pretesting/Dataset-adv_testing:/instruction_embeddings \
    -v $(pwd)/Preprocessing:/output \
    -it safe-preprocessing /code/safe_preprocessing.py -i /input -o /output/Dataset-adv_testing

echo "Waiting for input to train..;"
read input

# Train
docker run --rm -v $(pwd)/../../DBs:/input -v $(pwd)/Pretraining/Dataset-1_training:/instruction_embeddings -v $(pwd)/Preprocessing:/preprocessing -v $(pwd)/NeuralNetwork/:/output -it safe-neuralnetwork /code/safe_nn.py --train --num_epochs 5 --dataset adv --restore -c /output/model_checkpoint_adv -o /output/Dataset-adv_training
