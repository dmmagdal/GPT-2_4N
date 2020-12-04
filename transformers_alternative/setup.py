# setup.py
# author: Diego Magdaleno
# Set up all required folders and requirements for using and training
# with huggingface transformers.
# Python 3.7
# Windows/MacOS/Linux


import os
import sys
import subprocess
from download_text import Gutenberg, AO3


def main():
	# Check for the version of Python. The python must be version 3.6+.
	print("Checking for Python version 3.6 or higher...")
	if not sys.version_info.major == 3 and sys.version_info.minor >= 6:
		print("Error: Requires Python 3.6 or higher.")
		exit(1)

	# Send the following command with the subprocess command to
	# determine the path variable set up for python.
	python_commands = []
	command = subprocess.Popen("python3 -V", shell=True, 
								stdout=subprocess.PIPE,
								stderr=subprocess.PIPE)
	command_output, command_error = command.communicate()
	if len(command_error) != 0:
		python_commands = ["python", "pip"]
	else:
		python_commands = ["python3", "pip3"]

	# Install the necessary modules from requirements.txt
	print("Installing required modules...")
	install_command = subprocess.Popen(python_commands[1] +\
										" install -r requirements.txt",
										shell=True, stdout=subprocess.PIPE,
										stderr=subprocess.PIPE)
	install_output, install_error = install_command.communicate()
	print(install_output.decode("utf-8"))
	if len(install_error) != 0:
		print(install_error.decode("utf-8"))

	# Clone the github repository from huggingface for the transformer
	# module.
	print("Cloning huggingface repo for training GPT-2 to transformers folder...")
	repo_command = "git clone https://github.com/huggingface/transformers.git"
	trainer_command = subprocess.Popen(repo_command, shell=True, 
										stdout=subprocess.PIPE,
										stderr=subprocess.PIPE)
	trainer_output, trainer_error = trainer_command.communicate()
	print(trainer_output.decode("utf-8"))
	if len(trainer_error) != 0:
		print(trainer_error.decode("utf-8"))
		print("Failed to clone huggingface repo.")
		exit(1)

	# Download the necessary text files using the text downloader module.
	print("Downloading training texts...")
	valid_input = False
	while not valid_input:
		gut_query = "Do you wish to download training texts from Project Gutenberg?[Y/n] "
		user_input = input(gut_query)
		if user_input.upper() == "Y" or user_input.lower() == "yes":
			gut_obj = Gutenberg()
			gut_obj.download_all_fiction()
			valid_input = True
		elif user_input.upper() == "N" or user_input.lower() == "no":
			valid_input=True
		else:
			print("Input " + user_input + " is not a valid response.")
	valid_input = False
	while not valid_input:
		ao3_query = "Do you wish to download training texts from ArchiveOfOurOwn(AO3)?[Y/n] "
		user_input = input(ao3_query)
		if user_input.upper() == "Y" or user_input.lower() == "yes":
			ao3_obj = AO3()
			ao3_obj.download_from_ao3()
			valid_input = True
		elif user_input.upper() == "N" or user_input.lower() == "no":
			valid_input=True
		else:
			print("Input " + user_input + " is not a valid response.")

	# Notify the user that setup is now complete.
	print("Install is complete. Ready to run GPT-2 Novel Novel Neural Network (GPT-2_4N) Project.")

	# Exit the program.
	exit(0)


if __name__ == '__main__':
	main()