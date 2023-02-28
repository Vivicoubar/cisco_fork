docker run --rm \
	-v $(pwd)/../../DBs:/input \
	-v $(pwd)/NeuralNetwork:/output \
	-v $(pwd)/Preprocessing:/preprocessing \
	-it gnn-neuralnetwork /code/gnn.py --train --num_epoch 16 \
		--model_type matching --training_mode pair \
		--features_type opc --dataset one \
		-c /output/model_checkpoint_GMN_$(date +'%Y-%m-%d') \
		-o /output/Dataset-1_training_GMN_opc_pair
