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
save_folder_name="${date_value}_${model}_${new_model_name}"

# Run the encode program on the specified folder containing the training text
# data.
if [[ "${python_command}" -eq "python" ]]; then
	python encode.py --model_name=$model $folder_name $output_name
else
	python3 encode.py --model_name=$model $folder_name $output_name
fi

# Wait until the encoding file is created before moving on.
encoded_files=$(ls | grep *.npz)
while [[ ${#encoded_files} -eq 0 ]]; do
	encoded_files=$(ls | grep *.npz)
done
sleep 5

# Run the train program on the resulting npz output file.
if [[ "${python_command}" -eq "python" ]]; then
	python train.py --model_name $model --dataset $output_name --run_name $save_folder_name
else
	python3 train.py --model_name $model --dataset $output_name --run_name $save_folder_name
fi

# Wait until the training program is done before moving on.
#echo $?
sleep 5

# Clean up the /src folder and copy the model over to the /models folder.
rm $output_name
mkdir "./models/${save_folder_name}"
cp -a "./checkpoint/${save_folder_name}/." "./models/${save_folder_name}"
#cp -a "./checkpoint/run1/." "./models/${save_folder_name}"
cp "./models/${model}/encoder.json" "./models/${save_folder_name}/encoder.json"
cp "./models/${model}/hparams.json" "./models/${save_folder_name}/hparams.json"
cp "./models/${model}/vocab.bpe" "./models/${save_folder_name}/vocab.bpe"
#rm -r "./checkpoint/"
#rm -r "./samples/"
