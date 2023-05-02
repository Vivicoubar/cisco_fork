# this scripts summarizes all the necessary commands to use the GNN and GMN models to compute the similarity between functions of binaries
# We skip validation, I did it already when training the model beforehand on the same dataset
# and with the same hyper-parameters
# working directory is the root of the git repo
# NOTE: this swript train and test the GNN based model, to do the same thing witht he GMN model, change the model_type to embedding during the training and use the new checkpoint
# when testing the model

## Step 0: ready the model
### build docker images
cd Models/GGSNN-GMN/ &&\
	 docker build --no-cache Preprocessing/ -t gnn-preprocessing &&\
	 docker build --no-cache NeuralNetwork/ -t gnn-neuralnetwork
### train the model (on dataset1)
#### preprocess dataset1 data
docker run --rm \
    -v $(pwd)/../../DBs/Dataset-1/features/training/acfg_disasm_Dataset-1_training:/input \
    -v $(pwd)/Preprocessing/Dataset-1_training:/output \
    -it gnn-preprocessing /code/gnn_preprocessing.py -i /input --training -o /output
#### train model
docker run --rm \
    -v $(pwd)/../../DBs:/input \
    -v $(pwd)/NeuralNetwork:/output \
    -v $(pwd)/Preprocessing:/preprocessing \
    -it gnn-neuralnetwork /code/gnn.py --train --num_epochs 10 \
        --model_type embedding --training_mode pair \  #change model_type to "matching" here for GMN
        --features_type opc --dataset one \
        -c /output/model_checkpoint_$(date +'%Y-%m-%d') \
        -o /output/Dataset-1_training_GGSNN_opc_pair

## Step 1: preprocessing test data
### extract the "features" and "pairs" from the binaries
#### features
python3 IDA_scripts/create_json_for_ACFG_plugin.py -i Binaries/your_dataset/ -o DBs/your_dataset/features/your_dataset.json
python3 IDA_scripts/ANGR_acfg_disasm/cli_acfg_disasm.py -j DBs/your_dataset/features/your_dataset.json -o DBs/your_dataset/features/acfg_disasm/
#### pairs
python3 IDA_scripts/make_pairs_csv.py -i Binaries/your_dataset/ -o DBs/your_dataset/pairs/

### Preprocess your_dataset data (needs the training set preprocessed data - this means the ACFG-disas folder files)
cd Models/GGSNN/ &&\
docker run --rm \
    -v $(pwd)/../../DBs/your_dataset/features/acfg_disasm:/input \
    -v $(pwd)/Preprocessing/Dataset-1_training:/training_data \
    -v $(pwd)/Preprocessing/your_dataset:/output \
    -it gnn-preprocessing /code/gnn_preprocessing.py -i /input -d /training_data/opcodes_dict.json -o /output

## Step 2: infer similarity score with the model
### Use the previously generate checkpoint (step 0 - train model)
docker run --rm \
    -v $(pwd)/../../DBs:/input \
    -v $(pwd)/NeuralNetwork/:/output \
    -v $(pwd)/Preprocessing:/preprocessing \
    -it gnn-neuralnetwork /code/gnn.py --test \
        --model_type embedding --training_mode pair \  # change model_type to "mathcing" if GMN is wanted
        --features_type opc --dataset your_dataset  \ # NOTE: paths are hard-coded in the config.py file. So you will need to edit it and add your dataset name as an option, and the corresponding folder pathes too :o) OR you can call your dataset Dataset-Muaz (replace every occurence in this script of "your_dataset" by "Dataset-Muaz" and if you use the "--dataset muaz" option it should work
        -c /code/model_checkpoint_GGSNN_pair \
        -o /output/your_dataset_testing
