import os
import requests
import pandas as pd
import pickle
import time
from dotenv import load_dotenv

# Retrieve API Authorization Token
def auth():
    load_dotenv()
    return os.getenv('BEARER_TOKEN')

# GET request to Twitter API
def get_tweet(tweetId: str, headers: dict, params: dict):
    url = f'https://api.twitter.com/2/tweets/{tweetId}'
    response = requests.get(url, headers = headers, params = params)
    if response.status_code not in (200, 429):
        raise Exception(response.status_code, response.text)
    return response.json()

# Initialize inputs for the API call
bearer_token = auth()
headers = {"Authorization": f'Bearer {bearer_token}'}

# Fetches only the text of the target tweet, no metadata
params = {'tweet.fields': 'text'}

# Import #1
# dirname = os.path.dirname(__file__)
# notes = pd.read_csv(dirname + '/data/notes-00000.tsv', sep='\t', header=0)

# # Initialize target columns of dataframe
# notes['tweetText'] = ""
# notes['apiErrors'] = ""
# notes['apiCalled'] = bool(False)

# Import #2
dirname = os.path.dirname(__file__)
notes = pd.read_csv(dirname + '/../data/notes-with-tweet-text.csv', header=0)

# # Import #3 
# dirname = os.path.dirname(__file__)
# notes = pd.read_pickle(dirname + '/../data/notes-with-tweet-text.pkl', header=0)

deh = get_tweet("1380905193781380000", headers, params)
print(deh)

# # Fetch and store the text of every Tweet in notes
# for idx, row in notes[notes['apiCalled'] == False].iterrows():
#     print(row['tweetId'])
#     response = get_tweet(row['tweetId'], headers, params)
    
#     # Sleep while rate limit is reached
#     while 'title' in response.keys() and response['title'] == 'Too Many Requests':
#         print('sleeping')
#         notes.to_pickle(dirname + '/../data/notes-with-tweet-text.pkl')
#         time.sleep(900)
#         response = get_tweet(row['tweetId'], headers, params)
        
#     # Store errors in one column
#     if 'errors' in response.keys():
#         print('failed')
#         print(response)
#         notes.loc[idx, 'apiErrors'] = response['errors']
    
#     # Store text in another column
#     if 'data' in response.keys():
#         print('success')
#         notes.loc[idx, 'tweetText'] = response['data']['text']
    
#     # Mark the row as called
#     notes.loc[idx, 'apiCalled'] = True

#     break

# notes.to_pickle(dirname + '/../data/notes-with-tweet-text.pkl')