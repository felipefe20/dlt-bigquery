from googleapiclient.discovery import build
from pprint import pprint 

from datetime import datetime
import pytz

import toml
import dlt
import os 
# Load the date and time of the last comment processed from a file
#try:
#    with open("last_comment.txt", "r") as file:
#        last_comment_time = datetime.fromisoformat(file.read())
#except FileNotFoundError:
#    last_comment_time = datetime.fromtimestamp(0, tz=pytz.UTC)  # If the file doesn't exist, set the last comment time to the Unix epoch

# Make sure last_comment_time is timezone-aware
#if last_comment_time.tzinfo is None or last_comment_time.tzinfo.utcoffset(last_comment_time) is None:
#    last_comment_time = pytz.UTC.localize(last_comment_time)


# Load the secrets from the file
#secrets = toml.load("secrets.toml")

# Get the API key
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
VIDEO_ID = "-Iizd0AkpVI"

youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

comments_data = []
page_token = None

while True:
    request = youtube.commentThreads().list(
        part="snippet",
        videoId=VIDEO_ID,
        textFormat="plainText",
        pageToken=page_token,
        maxResults=100  # Maximum allowed by YouTube API
    )
    response = request.execute()

    if "items" in response:
        for item in response["items"]:
            #comment_time = datetime.fromisoformat(item["snippet"]["topLevelComment"]["snippet"]["publishedAt"].rstrip("Z"))
            #comment_time = comment_time.astimezone(pytz.UTC)  # Make sure the comment time is timezone-aware
            # If the comment was posted after the last comment time, process it
            
            #if comment_time > last_comment_time:
            #pprint(item)
            published_date=item["snippet"]["topLevelComment"]["snippet"]["publishedAt"]
            comment_text = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            author_name = item["snippet"]["topLevelComment"]["snippet"]["authorDisplayName"]
            like_count=item["snippet"]["topLevelComment"]["snippet"]["likeCount"]
            total_reply_count=item["snippet"]["totalReplyCount"]
            video_id=item["snippet"]["videoId"]
            comments_data.append({"author": author_name, 
                            "text": comment_text,
                            "like_count":like_count,
                            "total_reply_count":total_reply_count,
                            "video_id":video_id,
                                "published_date":published_date
                                })
                # Update the last comment time
                #last_comment_time = max(last_comment_time, comment_time)

    if "nextPageToken" in response:
        page_token = response["nextPageToken"]
    else:
        break
# Save the date and time of the last comment processed to a file
#with open("last_comment.txt", "w") as file:
#    file.write(last_comment_time.isoformat())



pipeline = dlt.pipeline(pipeline_name="youtube_comments_pipeline",
        destination='bigquery',
        dataset_name="youtube_comments_data",)

# run the pipeline with default settings, and capture the outcome
info = pipeline.run(comments_data, 
                    table_name="youtube_comments_table", 
                    write_disposition="replace")

# show the outcome
print(info)