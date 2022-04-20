import os
import requests
import pandas as pd
import numpy as np
import pickle
import openai
from transformers import GPT2TokenizerFast 
from dotenv import load_dotenv
from sklearn.model_selection import train_test_split

# Import Labeled Tweets
dirname = os.path.dirname(__file__)
df = pd.read_csv(dirname + '/../data/notes-with-tweet-text.csv', header=0)

# Generate tokenizer-friendly labels
df['classification'].replace({'MISINFORMED_OR_POTENTIALLY_MISLEADING': "False",
                              'NOT_MISLEADING': "True"}, inplace=True)

# Filter out notes without tweet text
df = df[df['tweetText'].notnull()]

# Filter out non-unique tweets
df['uniqueTweet'] = ~df['tweetText'].duplicated(keep=False)
df = df[df['uniqueTweet']]

# Build Training and Test Sets
x = df['tweetText'].values
y = df['classification'].values
metadata = df['noteId'].values
x_train, x_test, y_train, y_test, meta_train, meta_test = train_test_split(x, y, metadata, test_size=0.70, random_state=42)

# Build JSON training file
file_df = pd.DataFrame()
file_df['text'] = x_train
file_df['label'] = y_train
file_df['metadata'] = meta_train.astype(str)
file_df.to_json(dirname + '/../data/train-gpt3.json', orient='records', lines=True)

# Configure OpenAI API connection
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# # Delete existing file (if necessary)
# openai.File.delete('file-tRA4imBhtj0pSVKBfLrbNzQl')

# # Upload training data to OpenAI API
# # TODO: only upload if no files are uploaded
# openai.File.create(
#   file=open(dirname + '/../data/train-gpt3.json'),
#   purpose='classifications'
# )

# # Check that file was uploaded correctly
# print(openai.File.list())

# Initalize tokenizer and labels_tokens
tokenizer = GPT2TokenizerFast.from_pretrained('gpt2')
labels = ['True', 'False']
labels_tokens = {label: tokenizer.encode(" " + label) for label in labels}
first_token_to_label = {tokens[0]: label for label, tokens in labels_tokens.items()}


# Function for GPT3 classification query
def classify_gpt(text, labels):
    # POST Request
    response = openai.Classification.create(
        file="file-9ygjJEkq44BZY8WS5PiP1dNw",
        query=text,
        search_model="babbage", 
        model="babbage", 
        labels=labels,
        max_examples=100,
        logprobs=4
    )

    # Pull logprobs from response
    top_logprobs = response["completion"]["choices"][0]["logprobs"]["top_logprobs"][0]

    # Generate dict of token probabilities
    token_probs = {
        tokenizer.encode(token)[0]: np.exp(logp) 
        for token, logp in top_logprobs.items()
    }

    # Generate dict of label probabilities
    label_probs = {
        first_token_to_label[token]: prob 
        for token, prob in token_probs.items()
        if token in first_token_to_label
    }

    # Fill in the probability for the special "Unknown" label.
    if sum(label_probs.values()) < 1.0:
        label_probs["Unknown"] = 1.0 - sum(label_probs.values())
    
    return label_probs


test = pd.DataFrame()
test['noteId'] = meta_test
test['tweetText'] = x_test
test['humanLabel'] = y_test
test['gptTrue'] = test['gptFalse'] = test['gptUnknown'] = None

for i in range(len(x_test)):
    print(f'{i} of {len(x_test)}')
    label_probs = classify_gpt(x_test[i], labels)
    test.loc[i, 'gptTrue'] = label_probs['True']
    test.loc[i, 'gptFalse'] = label_probs['False']
    test.loc[i, 'gptUnknown'] = label_probs['Unknown']

    if i % 100 == 0:
        test.to_csv(dirname + '/../data/test-gpt3.csv', index=False)


    











# logit_bias = {str(first_token): 100 for first_token in first_token_to_label}

# # Query the /classification endpoint with logit_bias
# result = openai.Classification.create(
#     file="file-hRsoFZ4J3dNoiTeudHesgPoh",
#     query="movie is very good",
#     search_model="ada",
#     model="curie",
#     max_examples=10,
#     logit_bias=logit_bias,
# )











