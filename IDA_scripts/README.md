# The IDA Pro scriptk

This folder contains:
* [one script](run_a2v_test.sh) to run asm2vec on the current binaries in `../Binaries/Dataset-Muaz/bins/`
* several [IDA Pro plugins](#the-ida-pro-plugins) used for the features extraction.

## Files setup before launching `run_a2v_test.sh`

## Requirements

1. Set the `IDA32_PATH` and `IDA_PATH` environment variables with the full path of `idat` and `idat64`. Example:
```bash
export IDA_PATH=/home/user/idapro-7.3/idat64
export IDA32_PATH=/home/user/idapro-7.3/idat
```

2. Install the Python3 [virtualenv](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#installing-virtualenv)

3. Create a new virtualenv and install the required packages
```bash
# create a new "env" environment
python3 -m venv env
# enter the virtual environment
source env/bin/activate

# Install the requirements in the current environment
pip install -r requirements.txt
```

4. (Maybe Optional) Install `Capstone 3.0.4` in the *IDA Pro Python2 environment*:
```bash
pip2 install capstone==3.0.4
```

## Details about the scripts
### Generate the IDBs (IDA databases)

Use the [generate_idbs.py](generate_idbs.py) Python3 script to automatically export the IDBs for the binaries of each dataset:
- **Input**: the flag corresponding to the dataset to process (For us: --muaz)
- **Output**: the corresponding IDBs (in `../IDBs/Dataset-Muaz/` and a log file (`generate_idbs_log.txt`)
- **Performance**: this takes time for big datasets !

---

### IDA FlowChart
**Summary**: it extracts basic information from each function with at least five basic blocks.

- **Input**: the folder with the IDBs (`-i`) and the name of the CSV file in output (`-o`).
- **Output**: one CSV file with all the functions with at least five basic blocks.
- **Performance**: relatively fast.

Example: run the plugin over the IDBs of the Dataset-Muaz (requires the IDBs in the `IDBs/Dataset-Muaz` directory)
```bash
cd IDA_flowchart
python3 cli_flowchart.py -i ../../IDBs/Dataset-Vulnerability -o flowchart_Dataset-Vulnerability.csv
```

---

### Dataset creation Notebook (in `dataset_creation_notebooks/`)
**Summary**: it creates the features files necessary for the acfg-disasm plugin in `../DBs/Dataset-Muaz/`

- **Input**: a .csv file of the pairs of selected functions to compute scores for, and a .txt file with the names of the selected functions
- **Output**: fills the `../DBs/Dataset-Muaz` with the needed test .csv files that describes wich pair of function to process
- **Performance**: relatively fast.

Example: run the plugin for the Dataset-Muaz (requires the `fun_of_interest.txt) and `selected_pairs.csv` files)
```bash
cd dataset_creation_notebooks/
python3 dataset_creation_notebooks/Dataset-Muaz_creation.py dataset_creation_notebooks/fun_of_interest.txt dataset_creation_notebooks/selected_pairs.csv
```

---

### IDA ACFG-disasm
**Summary**: it creates an ACFG with the basic-blocks disassembly for each selected function.

- **Input**: a JSON file with the selected functions (`-j`) and the name of a folder in output (`-o`).
- **Output**: one JSON file (`_acfg_disasm.json`) per IDB.
- **Performance**: this takes time for big datasets !

**Note**: the path of the IDB files in the JSON in input **must be relative** to the `binary_function_similarity` directory. The Python3 script converts the relative path into a full path to correctly load the IDB in IDA Pro.

Example: run the plugin over the functions selected for the Dataset-Muaz test (requires the IDBs in the `IDBs/Dataset-Muaz` directory)
```bash
cd IDA_acfg_disasm
python3 cli_acfg_disasm.py -j ../../DBs/Dataset-Vulnerability/features/selected_Dataset-Muaz.json -o acfg_disasm_Dataset-Muaz
```
