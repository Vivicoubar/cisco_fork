# NOTE: I separated those two steps so that you can launch the
# ./generate_acfg_features_from_idbs.sh script when you already have the IDBs
# to save time

## generate IDBs
python3 generate_idbs.py --muaz

## generate the acfg features from the IDBs, using the sleected_pairs.csv and fun_of_interest.txt
./generate_acfg_features_from_idbs.sh

## run asm2vec

PWD=$pwd

cd "../Models/Asm2vec/"
./testing_script.sh

cd $PWD
echo "Done"
