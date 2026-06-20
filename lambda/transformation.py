import json
import boto3
import pandas as pd
import io
import urllib.parse
from datetime import datetime

s3 = boto3.client('s3')

RAW_BUCKET = 'youtube-raw-data-etl'
TRANSFORMED_BUCKET = 'youtube-transformed-data-etl'

def lambda_handler(event, context):
    try:
        # ── 1. Get triggered file from S3 ────────────────────────────
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])

        # ── 2. Read raw JSON ─────────────────────────────────────────
        response = s3.get_object(Bucket=bucket, Key=key)
        data = json.loads(response['Body'].read())

        items = data.get('items', [])

        videos_list = []
        channels_list = []
        statistics_list = []

        # ── 3. Extract data ──────────────────────────────────────────
        for item in items:
            video_id = item.get('id')

            snippet = item.get('snippet', {})
            statistics = item.get('statistics', {})
            content_details = item.get('contentDetails', {})

            videos_list.append({
                'video_id': video_id,
                'title': snippet.get('title'),
                'published_date': snippet.get('publishedAt', '')[:10],
                'duration': content_details.get('duration'),
                'definition': content_details.get('definition'),
                'category_id': snippet.get('categoryId')
            })

            channels_list.append({
                'channel_id': snippet.get('channelId'),
                'channel_title': snippet.get('channelTitle'),
                'video_id': video_id
            })

            statistics_list.append({
                'video_id': video_id,
                'views': int(statistics.get('viewCount', 0)),
                'likes': int(statistics.get('likeCount', 0)),
                'comments': int(statistics.get('commentCount', 0))
            })

        # ── 4. DataFrames ────────────────────────────────────────────
        df_videos = pd.DataFrame(videos_list)
        df_channels = pd.DataFrame(channels_list)
        df_statistics = pd.DataFrame(statistics_list)

        # ── 5. Cleaning ──────────────────────────────────────────────
        df_videos = df_videos.drop_duplicates(subset=['video_id'])
        df_channels = df_channels.drop_duplicates(subset=['channel_id'])
        df_statistics = df_statistics.drop_duplicates(subset=['video_id'])

        df_videos = df_videos.dropna(subset=['video_id', 'title'])
        df_channels = df_channels.dropna(subset=['channel_id'])
        df_statistics = df_statistics.dropna(subset=['video_id'])

        df_statistics['views'] = df_statistics['views'].astype(int)
        df_statistics['likes'] = df_statistics['likes'].astype(int)
        df_statistics['comments'] = df_statistics['comments'].astype(int)

        df_videos.columns = [col.lower() for col in df_videos.columns]
        df_channels.columns = [col.lower() for col in df_channels.columns]
        df_statistics.columns = [col.lower() for col in df_statistics.columns]

        # ── 6. Partition date ────────────────────────────────────────
        today = datetime.now().strftime("%Y-%m-%d")

        # ── 7. Save to S3 ────────────────────────────────────────────

        # Videos
        v_buffer = io.BytesIO()
        df_videos.to_parquet(v_buffer, index=False)
        v_buffer.seek(0)

        s3.put_object(
            Bucket=TRANSFORMED_BUCKET,
            Key=f"transformed/videos/date={today}/videos.parquet",
            Body=v_buffer.getvalue()
        )

        # Channels
        c_buffer = io.BytesIO()
        df_channels.to_parquet(c_buffer, index=False)
        c_buffer.seek(0)

        s3.put_object(
            Bucket=TRANSFORMED_BUCKET,
            Key=f"transformed/channels/date={today}/channels.parquet",
            Body=c_buffer.getvalue()
        )

        # Statistics
        s_buffer = io.BytesIO()
        df_statistics.to_parquet(s_buffer, index=False)
        s_buffer.seek(0)

        s3.put_object(
            Bucket=TRANSFORMED_BUCKET,
            Key=f"transformed/statistics/date={today}/statistics.parquet",
            Body=s_buffer.getvalue()
        )

        print(f" Videos: {len(df_videos)} | Channels: {len(df_channels)} | Statistics: {len(df_statistics)}")

        return {
            'statusCode': 200,
            'body': 'Transformation successful'
        }

    except Exception as e:
        print("ERROR:", str(e))
        raise
