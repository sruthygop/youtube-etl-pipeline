import json
import boto3
import urllib.request
import os
from datetime import datetime

s3 = boto3.client('s3')

API_KEY    = os.environ['YOUTUBE_API_KEY']
RAW_BUCKET = 'youtube-raw-data-etl'  # hardcoded

def get_trending_videos():
    url = (
        f"https://www.googleapis.com/youtube/v3/videos"
        f"?part=snippet,contentDetails,statistics"
        f"&chart=mostPopular"
        f"&regionCode=IN"
        f"&maxResults=50"
        f"&key={API_KEY}"
    )

    req = urllib.request.Request(url)
    response = urllib.request.urlopen(req)
    data = json.loads(response.read())
    return data

def lambda_handler(event, context):
    try:
        data = get_trending_videos()

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        s3.put_object(
            Bucket=RAW_BUCKET,
            Key=f"raw/youtube_trending_{timestamp}.json",
            Body=json.dumps(data)
        )

        print(f"✅ Raw data saved → {len(data.get('items', []))} videos")
        return {
            "statusCode": 200,
            "body": "Data extracted successfully"
        }

    except Exception as e:
        print("ERROR:", str(e))
        raise
