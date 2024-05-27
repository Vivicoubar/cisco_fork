docker run --rm \
	-v $(pwd)/../../DBs:/input \
	-v $(pwd)/NeuralNetwork:/output \
	-v $(pwd)/Preprocessing:/preprocessing \
	-it gnn-neuralnetwork /code/gnn.py --train --num_epoch 16 \
		--model_type embedding --training_mode pair \
		--features_type nofeatures --dataset one \
		-c /output/model_checkpoint_GNN_nofeatures_$(date +'%Y-%m-%d') \
		-o /output/Dataset-1_training_GNN_nofeatures_pair
