#!/bin/bash

## Prep: put your bins in the "Binaries/Dataset-Muaz/" folder
## Prepare the DBs/Dataset-Muaz/ folder like this:
## Dataset-Muaz/
## |- features/
##    | - acfg_disasm/
## |- pairs/
## Have the GGSNN dockers (Preprocessing and NeuralNetwork) built
## Have the checkpoint of your trained model in Models/GGSNN-GMN/NeuralNetwork/model_checkpoint_XXX/
## Have the training data available in "DBs/Dataset-1/", preprocessed training data in "Models/GGSNN-GMN/Preprocessing/Dataset-1_training/" and "Models/GGSNN-GMN/Preprocessing/Dataset-1_validation/"
### If you have doubts about missing something in the training data folders, try to copy the github' original DBs/Dataset-1/ folder. You can also open the Models/GGSNN-GMN/NeuralNetwork/core/config.py file and look at it.
## Have ANGR installed, and maybe you'll need other python packages, keep your pip at the ready

## Now that you have everything setup let's prepare your binaries, preprocess the data with the trained model using the training dataset opcode_dict, and finally test the model on your dataset.

#--- Preparing the data
echo "Preparing the data"
#### create the json file containing all the fun's ep, needed by cli_acfg_disasm
echo "Running create_json_for_ACFG_plugin"
python3 IDA_scripts/create_json_for_ACFG_plugin.py -i Binaries/Dataset-Muaz/ -o DBs/Dataset-Muaz/features/Dataset-Muaz.json

#### extract the features used by the model (acfg disasm)
echo "Running cli_acfg_disasm"
python3 IDA_scripts/ANGR_acfg_disasm/cli_acfg_disasm.py -j DBs/Dataset-Muaz/features/Dataset-Muaz.json -o DBs/Dataset-Muaz/features/acfg_disasm/

#### make the pairs
echo "Running make_pairs_csv"
python3 IDA_scripts/make_pairs_csv.py -i Binaries/Dataset-Muaz/ -o DBs/Dataset-Muaz/pairs/

#--- Preprocessing the data
cd Models/GGSNN-GMN/
### this uses the training dataset' preprocessed opcode_dict
echo "Running docker to preprocess test data"
docker run --rm \
    -v $(pwd)/../../DBs/Dataset-Muaz/features/acfg_disasm:/input \
    -v $(pwd)/Preprocessing/Dataset-1_training:/training_data \
    -v $(pwd)/Preprocessing/Dataset-Muaz:/output \
    -it gnn-preprocessing /code/gnn_preprocessing.py -i /input -d /training_data/opcodes_dict.json -o /output

#--- Inference with the model (needs the trained model checkpoint, the training dataset data)

echo "Running docker to infer test data"
if [[ "$1" == "GNN" ]]; then
	docker run --rm \
	    -v $(pwd)/../../DBs:/input \
	    -v $(pwd)/NeuralNetwork/:/output \
	    -v $(pwd)/Preprocessing:/preprocessing \
	    -it gnn-neuralnetwork /code/gnn.py --test \
		--model_type embedding --training_mode pair \
		--features_type opc --dataset muaz  \
		-c /code/model_checkpoint_GGSNN_pair \
		-o /output/Dataset-Muaz

elif [[ "$1" == "GMN" ]]; then
	docker run --rm \
	    -v $(pwd)/../../DBs:/input \
	    -v $(pwd)/NeuralNetwork/:/output \
	    -v $(pwd)/Preprocessing:/preprocessing \
	    -it gnn-neuralnetwork /code/gnn.py --test \
		--model_type matching --training_mode pair \
		--features_type opc --dataset muaz  \
		-c /code/model_checkpoint_GMN_pair \
		-o /output/Dataset-Muaz

else
	echo "Error: inference mode not GMN or GNN"
fi
