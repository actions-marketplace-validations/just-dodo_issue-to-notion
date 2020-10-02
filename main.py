import sys
import os
import json
from notion.client import NotionClient
from notion.block import PageBlock, BookmarkBlock
from md2notion.upload import upload, convert, uploadBlock

# Get data from github environment
path = os.environ.get("GITHUB_EVENT_PATH")
token = os.environ.get("NOTION_TOKEN")
database_url = os.environ.get("DATABASE_URL")

# Get the event string from github
with open(path,"r") as f:
    github_event_str = f.read()

# Convert event string to json
github_event_json = json.loads(github_event_str)

# Set card title, body and link
action_type = github_event_json["action"]
card_number = github_event_json["issue"]["number"]
card_title = github_event_json["issue"]["title"]
card_link = github_event_json["issue"]["html_url"]

# Login and go into collection
client = NotionClient(token_v2=token)
cv = client.get_collection_view(database_url)

# Check action type
if action_type == "opened":

    # Add row to notion collection
    row = cv.collection.add_row()
    row.name = card_title
    row.ID = card_number
    row.state = 'open'

    # Add Bookmark for issue
    row.children.add_new(BookmarkBlock, title=card_title, link=card_link)
    upload_body_with_markdown(row)
else:
    row = cv.collection.get_rows(ID=card_number)[0]

    if action_type == "edited":
        clear_page(row)
        row.children.add_new(BookmarkBlock, title=card_title, link=card_link)
        upload_body_with_markdown(row)
        
    elif action_type == "closed":
        row.state = 'closed'

    elif action_type == "deleted":
        pass
    # TODO
    elif action_type == "reopened":
        row.state = 'open'

    elif action_type == "labeled" or action_type == "unlabeled":
        pass
    # TODO


def upload_body_with_markdown(row):
    
    body = github_event_json["issue"]["body"]
        
    # Make markdown file from issue body
    f= open("body.md","w+")
    f.write(body)
    f.close()

    # Upload issue body markdown file to row
    with open("body.md", "r", encoding="utf-8") as mdFile:
        upload(mdFile,row)

def clear_page(row):
    for child in row.children:
        child.remove()