docker run --rm \
	-v $(pwd)/../../DBs:/input \
	-v $(pwd)/NeuralNetwork/:/output \
	-v $(pwd)/Preprocessing:/preprocessing \
	-it gnn-neuralnetwork /code/gnn.py --validate \
		--model_type embedding --training_mode pair \
		--features_type opc --dataset one \
		-c /output/model_checkpoint_2023-02-21 \
		-o /output/Dataset-1_validation
		#-c /code/model_checkpoint_GGSNN_pair \
