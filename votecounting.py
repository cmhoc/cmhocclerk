# Program created by /u/thehowlinggreywolf
#this program will count the votes of the Plebeian Assembly
from __future__ import print_function

import credentials

import praw
from googleapiclient import discovery
import os
from oauth2client import tools
import httplib2

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

#intializations
reddit = praw.Reddit(user_agent='Rome Votes v1.0',  #whatever you wanna call it
                     client_id='beep',  #The string of characters found under the name of the app in reddit
                     client_secret='boop', #Its labeled as secret under the name of the app
                     username='MRomePraefectus-bot',
                     password='****',)

SHEETID = '***'

value_input_option = 'USER_ENTERED'
insert_data_option = 'INSERT_ROWS'

credentials = credentials.get_credentials()

http = credentials.authorize(httplib2.Http())
discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')

service = discovery.build('sheets', 'v4', credentials=credentials, discoveryServiceUrl=discoveryUrl)

# Have we run this code before? If not, create an empty list
if not os.path.isfile("vote_data.txt"):
    vote_data = []
    print('Created List')

# If we have run the code before, load the list of posts we have replied to
else:
    # Read the file into a list and remove any empty values
    with open("vote_data.txt", "r", encoding='utf-8') as f:
        vote_data = f.read()
        vote_data = vote_data.split("\n")
        print('Current data: ', vote_data)

# Have we run this code before? If not, create an empty list
if not os.path.isfile("votes_counted.txt"):
    votes_counted = []
    print('Created List')

# If we have run the code before, load the list of posts we have replied to
else:
     # Read the file into a list and remove any empty values
     with open("votes_counted.txt", "r", encoding='utf-8') as f:
         votes_counted = f.read()
         votes_counted = votes_counted.split("\n")
         print('Current data: ', votes_counted)

votes_for = 0
votes_against = 0
bill = ''
update = False

subreddit = reddit.subreddit('PlebeianVotes')  #the /r/ of the sub you want it to look at
for submission in subreddit.new(limit=1):  #checks only 1 post
    title = submission.title
    bill = title.split(':')
    del bill[1]
    for comment in subreddit.comments(): #actually counting the votes
        if comment.id not in votes_counted:
            if 'Etiam' in comment.body:
                votes_for += 1
                votes_counted.append(comment.id)
            if 'Nullum' in comment.body:
                votes_against += 1
                votes_counted.append(comment.id)


total_votes = votes_for + votes_against
pvotes_for = votes_for / total_votes

if pvotes_for <= 0.5:
    bill_status = 'FAILED'
else:
    bill_status = 'PASSED'


print('Bill: ' + str(bill[0]))
print('Votes For: ' + str(votes_for))
print('Votes Against: ' + str(votes_against))
print('Total Votes: ' + str(total_votes))
print('% of Votes For: ' + str(pvotes_for))
print(bill_status)

# Store the current data into our list
vote_data.append('Bill: ' + str(bill[0]))
vote_data.append('Votes For: ' + str(votes_for))
vote_data.append('Votes Against: ' + str(votes_against))
vote_data.append('Total Votes: ' + str(total_votes))
vote_data.append('% of Votes For: ' + str(pvotes_for))
vote_data.append('Bill Status: ' + bill_status)
vote_data.append('------------------------------------')
if not update:
    update = True

# Write our updated list back to the file
if update:
    with open("vote_data.txt", "w", encoding='utf-8') as f:
        for item in vote_data:
            f.write(item + '\n')
        with open("votes_counted.txt", "w", encoding='utf-8') as f:
            for item in votes_counted:
                f.write(item + '\n')
print('Finished Updating')

spreadsheet_data = [bill, votes_for, votes_against, total_votes, pvotes_for, bill_status]

value_range_body = {                           #All of the data inserted, including a few variables.
    "range": "Plebeian_Votes_2nd_Consuls",     #Note: For some reason the google sheets API can't parse sheets with spaces....
    "majorDimension": "ROWS",                  #Cont. To fix simply change the spaces to underlines.
    "values": [
        [str(bill[0]), votes_for, votes_against, total_votes, pvotes_for, bill_status]
              ]
                   }

request = service.spreadsheets().values().append(spreadsheetId=SHEETID, range='Plebeian_Votes_2nd_Consuls', valueInputOption=value_input_option, insertDataOption=insert_data_option, body=value_range_body)
response = request.execute()
print('Spreadsheet Updated')