import urllib.request
import json
import os
import datetime
from unidecode import unidecode
import csv

# CHANGE THESE SETTINGS!
saveDirectory = '/path/to/parent/directory/'
boardLetter = 'pol'

print(f"The current working directory is {saveDirectory}")

# Create a folder for the board if it doesn't exist
path = os.path.join(saveDirectory, boardLetter)
print(f"Attempting to create directory for board at {path}")
os.makedirs(path, exist_ok=True)
print(f"Directory for board {path} {'already exists' if os.path.exists(path) else 'created successfully'}")

# Get the 4chan board catalog JSON file and open it
url = f"https://a.4cdn.org/{boardLetter}/catalog.json"
response = urllib.request.urlopen(url)
threadCatalog = json.loads(response.read())

print("BEGINNING 4CHAN FRONT PAGE SCRAPE")
print(f"Current board: {boardLetter}")

downloadCounter = 0

# Only look at the front page
frontPage = threadCatalog[0]['threads']

# Create a file to list all threads we've analyzed
allThreadFile = os.path.join(path, f"frontPage-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.csv")
with open(allThreadFile, mode='w', newline='', encoding='utf-8') as thread_file:
    thread_writer = csv.writer(thread_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
    thread_writer.writerow(["timeStamp", "lastScraped", "posterID", "name", "postID", "subjectText", "commentText"])

print("Now parsing front page threads...")
# There are always 20 threads on the front page. So we'll loop through and read each one
for i, thread in enumerate(frontPage[:20]):
    threadNumber = thread['no']
    print(f"STARTING NEW THREAD - #{threadNumber}")
    
    subjectText = thread.get('sub', "No Subject Text Provided")
    commentText = thread.get('com', "No Comment Text Provided")
    posterID = thread.get('id', "No ID")
    name = thread.get('name', "Anonymous")
    
    with open(allThreadFile, mode='a', newline='', encoding='utf-8') as thread_file:
        thread_writer = csv.writer(thread_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        thread_writer.writerow([thread['now'], datetime.datetime.now(), posterID, name, threadNumber, subjectText, commentText])
    
    # Create a new directory for the thread
    threadPath = os.path.join(path, f"{threadNumber} - {thread['semantic_url']}")
    print(f"Attempting to create directory for thread {threadPath}")
    os.makedirs(threadPath, exist_ok=True)
    print(f"Directory for thread {threadPath} {'already exists' if os.path.exists(threadPath) else 'created successfully'}")
    
    # Create a CSV file for the individual thread
    with open(os.path.join(threadPath, "thread.csv"), mode='w', newline='', encoding='utf-8') as thread_file:
        thread_writer = csv.writer(thread_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        thread_writer.writerow(["timeStamp", "posterID", "name", "postID", "subjectText", "commentText", "filename"])
    
    # Get the individual thread JSON file from 4chan and open it
    threadUrl = f"https://a.4cdn.org/{boardLetter}/thread/{threadNumber}.json"
    response = urllib.request.urlopen(threadUrl)
    individualThread = json.loads(response.read())
    
    # Loop through every post in this thread
    for post in individualThread['posts']:
        timeStamp = post.get('now', "")
        name = post.get('name', "Anonymous")
        posterID = post.get('id', "No ID")
        postID = post.get('no', "")
        subjectText = post.get('sub', "No Subject Text Provided")
        commentText = post.get('com', "No Comment Text Provided")
        
        filename = "No File Posted"
        if 'tim' in post:
            OGfilename = unidecode(post.get('filename', ""))
            renamedFile = str(post['tim'])
            fileExtension = str(post['ext'])
            filename = f"{OGfilename} - {renamedFile}{fileExtension}"
            try:
                postFileUrl = f"https://i.4cdn.org/{boardLetter}/{renamedFile}{fileExtension}"
                postFilePath = os.path.join(threadPath, filename)
                urllib.request.urlretrieve(postFileUrl, postFilePath)
                downloadCounter += 1
            except Exception as e:
                print(f"File Download Error: {e}")
                filename += " - Download Error"
        
        with open(os.path.join(threadPath, "thread.csv"), mode='a', newline='', encoding='utf-8') as thread_file:
            thread_writer = csv.writer(thread_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
            thread_writer.writerow([timeStamp, posterID, name, postID, subjectText, commentText, filename])

print(f"Front Page Scrape Completed - {downloadCounter} files downloaded")
