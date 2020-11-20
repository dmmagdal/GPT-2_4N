#!/bin/bash
# train_models.sh
# author: Diego Magdaleno
# Runs the console commands to encode and train the data for the GPT-2 model.

# Load in the arguments.
model=$1
folder_name=$2
python_command=$3
new_model_name=$4

# Create encoded npz output file name.
date_value=$(echo $(date '+%Y-%m-%d'))
output_name="${date_value}_${model}_${new_model_name}.npz"

# Run the encode program on the specified folder containing the training text
# data.
if [[ "${python_command}" -eq "python" ]]; then
	python encode.py --model_name=$model $folder_name $output_name
else
	python3 encode.py --model_name=$model $folder_name $output_name
fi

# Run the train program on the resulting npz output file.
if [[ "${python_command}" -eq "python" ]]; then
	python train.py --model_name $model --dataset $output_name
else
	python3 train.py --model_name $model --dataset $output_name
fi
