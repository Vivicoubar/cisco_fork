set -E
rm -f ../../Results/data/raw_results/Asm2vec/Dataset-Muaz_asm2vec_e10/*
rm -f ../data/Dataset-Muaz/*

docker run --rm -v $(pwd)/../../DBs/Dataset-Muaz/features/acfg_disasm:/input \
								-v $(pwd)/a2v_preprocessing_Dataset-1-training:/training_data \
								-v $(pwd):/output -it asm2vec /code/i2v_preprocessing.py \
								-d -w32 -a2v -i /input -v /training_data/vocabulary.csv -o /output/a2v_preprocessing_Dataset-Muaz-testing

docker run --rm -v $(pwd)/a2v_preprocessing_Dataset-Muaz-testing:/input \
								-v $(pwd)/asm2vec_train_Dataset-1-training:/checkpoint \
								-v $(pwd):/output -it asm2vec /code/i2v.py \
								-d --asm2vec --inference -e10 -w32 --inputdir /input/ -c /checkpoint -o /output/asm2vec_inference_Dataset-Muaz-testing

echo -e "\n *** Results saved in $(pwd)/asm2vec_inference_Dataset-Muaz-testing\n"

cd "../../Results/notebooks/"

echo "working in $(pwd)"

mkdir -p ../data/raw_results/Asm2vec/Dataset-Muaz_asm2vec_e10/
cp "../../Models/Asm2vec/asm2vec_inference_Dataset-Muaz-testing/embeddings.csv" "../data/raw_results/Asm2vec/Dataset-Muaz_asm2vec_e10/"

echo "Converting results..."
python3 Convert_Asm2vec_results.py

echo -e "\n*** Pairs results saved in $(pwd)/../data/Dataset-Muaz/"
cp $(pwd)/../data/Dataset-Muaz/pairs_testing_Dataset-Muaz_asm2vec_e10.csv ~/codemerger/scripts/benchmark/results/pairs_results_Dataset-Muaz_a2v.csv
echo -e "\nResult copied in ~/codemerger/data/inst_insertion_test/results/pairs_results_Dataset-Muaz_a2v.csv"
