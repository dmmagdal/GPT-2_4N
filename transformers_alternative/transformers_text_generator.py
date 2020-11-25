# transformers_text_generator.py
# author: Diego Magdaleno
# This program utilises the GPT-2 program stored in the hugging face
# transformers module for text generation and specialized training.
# Sources: https://huggingface.co/gpt2?text=Good+morning+my+friends.
# +My+name+is+Albert+Einstien.+Today+we+will+be+
# Python 3.7
# Windows/MacOS/Linux


import json
from transformers import pipeline, set_seed


def main():
    # Initialize a generator from the pipeline, specifying GPT-2 for
    # the model.
    generator = pipeline("text-generation", model="gpt2")

    # Set the seed value (for repeatability).
    set_seed(42)

    # Generate text samples.
    raw_text = "The children were chanting again. I'm pretty sure most" +\
                " teenagers do not have as much practice with ritual" +\
                " chanting as Sammy does. Even back when ritual chanting" +\
                " was a normal thing on this continent, it was mostly for" +\
                " adults. Yet there they go, Sammy and her latest pack of" +\
                " idiot friends, wearing silly outfits and chanting in a" +\
                " graveyard. They started at midnight, which was silly, the" +\
                " best time to start is a little past eleven, because then" +\
                " by midnight you've got a good rhythm going.\nBut Sammy" +\
                " had never once taken up with sensible cultists. No, it" +\
                " was always idiot children just smart enough to hit on" +\
                " something that works, and plenty stupid enough to dive" +\
                " headfirst into the worst kinds of trouble."
    #raw_text = input("model input>>>")
    #sample_list = generator("Hello, I am a language model,", max_length=30, num_return_sequences=5)
    #sample_list = generator(raw_text, max_length=512, num_return_sequences=5)
    sample_list = generator(raw_text, max_length=512, num_return_sequences=3)
    
    # Print out the samples.
    print(json.dumps(sample_list, indent=4))
    with open('sample_output.json', 'w+') as json_file:
        json.dump(sample_list, json_file, indent=4)

    # Exit the program.
    exit(0)


if __name__ == '__main__':
    main()
