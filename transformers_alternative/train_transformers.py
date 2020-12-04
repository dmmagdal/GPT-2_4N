# train_transformers.py
# author: Diego Magdaleno
# Set up everything so that the huggingface transformers GPT-2 model is
# ready to train on the data.
# Sources:
# https://huggingface.co/gpt2?
# http://reyfarhan.com/posts/easy-gpt2-finetuning-huggingface/
# https://huggingface.co/transformers/v2.0.0/examples.html#language-
# model-fine-tuning
# https://github.com/huggingface/transformers/tree/master/examples/
# language-modeling
# https://huggingface.co/transformers/main_classes/pipelines.html#
# transformers.TextGenerationPipeline
# Python 3.7
# Windows/MacOS/Linux


import os
import sys
import string
import subprocess
from datetime import datetime


# Determine the version of python that is running and figure out which python command
# to use for python 3.
# @param: Takes no arguments.
# @return: Returns the python command string for the system.
def get_python_version():
	if not sys.version_info.major == 3 and sys.version_info.minor >= 6:
		print("Error: Requires Python 3.6 or higher.")
		exit(1)

	# Send the following command with the subprocess command to determine the path
	# variable set up for python.
	python_command = ""
	command = subprocess.Popen("python3 -V", shell=True, stdout=subprocess.PIPE,
								stderr=subprocess.PIPE)
	command_output, command_error = command.communicate()
	if len(command_error) != 0:
		python_command = "python"
	else:
		python_command = "python3"

	# Return the python command string.
	return python_command


# Load in the text from AO3. Clean it as necessary and return the text with the
# special delimiter at the end.
# @param: file_name, the name of the text to be read from AO3.
# @return: Returns the cleaned text from the specified file.
def read_AO3_text(file_name):
	# Read in the file.
	file = open("./AO3/" + file_name, "r", encoding="utf-8")
	file_lines = file.readlines()
	file.close()

	# Return an empty string if the text title is not in English (usually a 
	# good indicator that the rest of the text is not in English.
	bad_title_char = 0
	for char in file_name:
		if char not in string.printable:
			bad_title_char += 1
	if bad_title_char // len(file_name) >= 0.5:
		return ""

	# Return an empty string if the text is not in English.
	bad_line_count = 0
	for line in file_lines:
		bad_char_count = 0
		for char in line:
			if char not in string.printable:
				bad_char_count += 1
		if bad_char_count // len(line) >= 0.9:
			bad_line_count += 1
	if bad_line_count // len(file_lines) >= 0.9:
		return ""
	
	# Strip out the text generated at the beginning and end of every AO3 text.
	start_text = "Summary\n"
	end_text = "Afterword\n"
	#end_text = "Chapter End Notes\n"
	start_index = -1
	end_index = -1
	for line_index in range(len(file_lines)):
		if start_text == file_lines[line_index]:
			start_index = line_index
		elif end_text == file_lines[line_index]:
			end_index = line_index

	# Return the resulting text with the special delimiter appended at the end.
	#delimiter = "\n<|endoftext|>\n"
	#return "\n".join(file_lines[start_index + 1:end_index]) + delimiter
	return "\n".join(file_lines[start_index - 2:end_index]) 


# Load in the text from Gutenberg. Clean it as necessary and return the text with the
# special delimiter at the end.
# @param: folder, the subject folder the text is contained in from Gutenberg.
# @param: file_name, the name of the text to be read from Gutenberg.
# @return: Returns the cleaned text from the specified file.
def read_Gutenberg_text(folder, file_name):
	# Read in the file.
	file = open("./Gutenberg/" + folder + "/" + file_name, "r", encoding="utf-8")
	file_lines = file.readlines()
	file.close()

	# Return an empty string if the text is not in English.
	if "Language: English\n" not in file_lines:
		return ""
	
	# Strip out the text generated at the beginning and end of every Project
	# Gutenberg text.
	start_text = "*** START OF THIS PROJECT GUTENBERG EBOOK "
	end_text = "*** END OF THIS PROJECT GUTENBERG EBOOK "
	start_index = -1
	end_index = -1
	for line_index in range(len(file_lines)):
		if start_text in file_lines[line_index]:
			start_index = line_index
		elif end_text in file_lines[line_index]:
			end_index = line_index

	# Return the resulting text with the special delimiter appended at the end.
	#delimiter = "\n<|endoftext|>\n"
	#return "\n".join(file_lines[start_index + 1:end_index]) + delimiter
	return "\n".join(file_lines[start_index + 1:end_index]) 


# Retrieve all the clean text data from AO3 as a string.
# @param: Takes no arguments.
# @return: Returns a compilation of all the text data from AO3.
def load_from_AO3():
	# Retrieve a list of all texts stored in the subfolders. Iterate through each
	# one and extract the cleaned text from each title. Save that cleaned text into
	# the training folder.
	text_files = os.listdir("./AO3/")
	for text in text_files:
		clean_text = read_AO3_text(text)
		if clean_text == "":
			continue
		new_file = open("./training/" + text, "w+", encoding="utf-8")
		new_file.write(clean_text)
		new_file.close()
	
	# Return True. This is more for of a status to whichever function calls this. All
	# operations in this function have been successfully executed.
	return True


# Retrieve all the clean text data from Project Gutenberg as a string.
# @param: Takes no arguments.
# @return: Returns a compilation of all the text data from Project Gutenberg.
def load_from_Gutenberg():
	# Retrieve a list of all subfolders (specific fiction genres) in the project
	# Gutenberg folder. Iterate through each one.
	gutenberg_folders = os.listdir("./Gutenberg/")
	for folder in gutenberg_folders:
		# Retrieve a list of all texts stored in the subfolders. Iterate through each
		# one and extract the cleaned text from each title. Save that cleaned text into
		# the training folder.
		text_files = os.listdir("./Gutenberg/" + folder + "/")
		for text in text_files:
			clean_text = read_Gutenberg_text(folder, text)
			if clean_text == "":
				continue
			new_file = open("./training/" + text, "w+", encoding="utf-8")
			new_file.write(clean_text)
			new_file.close()
	
	# Return True. This is more for of a status to whichever function calls this. All
	# operations in this function have been successfully executed.
	return True


# Load all the training text from the sources list to memory, clean it, and save it
# to a file.
# @param: model_name, the unique model name to save the compiled training texts under.
# @param: sources, the list of valid sources that contain the individual training texts.
# @return: Returns a boolean as to whether the text was successfully loaded
def load_text_to_memory(model_name, sources):
	# Iterate through the list of sources. Clean the text data from each and save it to
	# the training folder.
	for source in sources:
		if source == "AO3":
			source_status = load_from_AO3()
			if not source_status:
				print("Error: There was an error in cleaning the texts from AO3.")
				return source_status
		elif source == "Gutenberg":
			source_status = load_from_Gutenberg()
			if not source_status:
				print("Error: There was an error in cleaning the texts from Gutenberg.")
				return source_status

	# Iterate through the training texts in the training folder. Store
	# all text to a single string and write that to a file, each text
	# separated by a delimiter.
	delimiter = "\n<|endoftext|>\n"
	for text_title in os.listdir("./training"):
		file = open("./training/" + text_title, "r", encoding="utf-8")
		master_file = open(model_name + "_training_text.txt", "a+", encoding="utf-8")
		master_file.write(file.read() + delimiter)
		file.close()
		master_file.close()

	# Return True. This is more for of a status to whichever function calls this. All
	# operations in this function have been successfully executed.
	return True


def main():
	# Check the version of python running.
	python_command = get_python_version()

	# Check for all the required directories (transformers repository
	# from huggingface.
	if not os.path.exists("transformers"):
		print("Error: Missing huggingface repository. Run setup.py or git clone" +\
				"https://github.com/huggingface/transformers.git to retrieve the" +\
				" repository.")
		exit(1)

	# Check for all the desired directories (AO3 and Gutenberg).
	valid_sources = ["AO3", "Gutenberg"]

	# Copy the model from the OpenAI repository to the n-sheppard repository under the
	# src/models folder. Rename it based on the date, model, and name given by the user.
	# This will be referred to as the unique model name.
	user_name = ""
	valid_name_input = False
	while not valid_name_input:
		user_name = input("Enter a name for this model: ")
		if user_name != "":
			valid_name_input = True
		else:
			print("Entered an invalid save name for this model.")
	today = datetime.now().strftime("%Y-%m-%d")
	unique_model_name = today + "_" + user_name

	# Iterate through the training data, cleaning and removing and unecessary text as
	# well as inserting the special delimiter. Combine all texts into one. Save the
	# combined texts as unique model name + "_training_text.txt".
	print("Creating training text file(s) (this may take a few minutes)...")
	if not os.path.exists("./training"):
		os.mkdir("./training")
	status = load_text_to_memory(unique_model_name, valid_sources)
	if not status:
		print("Error: Failed to create training text file.")
		exit(1)

	# Run the training program under the language-modeling folder in
	# the examples directory from the transformers repository.
	print("Training huggingface model (this may take a few hours)...")
	os.chdir("./transformers/examples/language-modeling")
	training_file_path = "../../../" + unique_model_name +\
							"_training_text.txt"
	training_command = python_command + " run_clm.py" +\
						" --model_name_or_path gpt2 --train_file " +\
						training_file_path + " --do_train" +\
						" --output_dir /tmp/test-clm/" +\
						unique_model_name
	train_command = subprocess.Popen(training_command, shell=True,
										stdout=subprocess.PIPE,
										stderr=subprocess.PIPE)
	training_output, training_error = train_command.communicate()
	print(training_output.decode("utf-8"))
	print(training_error.decode("utf-8"))
	if len(training_error) != 0:
		exit(1)

	# Delete the training text.
	print("Cleaning directories...")
	os.chdir("../../..")
	os.remove(unique_model_name + "_training_text.txt")
	for text in os.listdir("./training"):
		os.remove("./training/" + text)

	# Exit the program.
	print("Training is completed successfully.")
	exit(0)


if __name__ == '__main__':
	main()