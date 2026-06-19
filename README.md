# 🎬 YouTube Analytics ETL Pipeline

![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=flat&logo=amazon-aws&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=flat&logo=python&logoColor=ffdd54)
![Power Bi](https://img.shields.io/badge/power_bi-F2C811?style=flat&logo=powerbi&logoColor=black)
![YouTube](https://img.shields.io/badge/YouTube-%23FF0000.svg?style=flat&logo=YouTube&logoColor=white)
![Amazon S3](https://img.shields.io/badge/Amazon%20S3-FF9900?style=flat&logo=amazons3&logoColor=white)
![AWS Lambda](https://img.shields.io/badge/AWS%20Lambda-FF9900?style=flat&logo=awslambda&logoColor=white)

> An end-to-end **automated data pipeline** that extracts YouTube trending videos data using the YouTube Data API v3, transforms and cleans it using AWS Lambda, stores it in Amazon S3, catalogs it using AWS Glue, queries it using Amazon Athena, and visualizes insights using **Power BI**.

---

## 📌 Table of Contents

- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Data Model](#data-model)
- [Dashboard](#dashboard)
- [Athena Queries](#athena-queries)
- [How to Run](#how-to-run)
- [Key Learnings](#key-learnings)
- [Author](#author)

---

## 🏗️ Architecture

```
YouTube Data API v3
        ↓
Amazon EventBridge (Scheduled Trigger)
        ↓
AWS Lambda - Extraction
        ↓
Amazon S3 - Raw Bucket (JSON)
        ↓
S3 ObjectPut Trigger (Automatic)
        ↓
AWS Lambda - Transformation
        ↓
Amazon S3 - Transformed Bucket (Parquet)
        ↓
AWS Glue Crawler → Glue Data Catalog
        ↓
Amazon Athena (SQL Queries)
        ↓
Power BI Dashboard (Visualization)
```

---

## ⚙️ Tech Stack

| Service | Purpose |
|---|---|
| **YouTube Data API v3** | Fetch top 50 trending videos in India |
| **AWS Lambda (Python 3.11)** | Serverless extraction & transformation |
| **Amazon S3** | Raw JSON & transformed Parquet storage |
| **AWS Glue Crawler** | Auto schema detection |
| **AWS Glue Data Catalog** | Metadata & schema storage |
| **Amazon Athena** | SQL querying on S3 data |
| **Amazon EventBridge** | Automated pipeline scheduling |
| **Power BI Desktop** | Interactive dashboard & visualization |
| **Pandas & PyArrow** | Data transformation & Parquet conversion |

---

## 📁 Project Structure

```
youtube-etl-pipeline/
├── lambda/
│   ├── extraction.py         # Fetches data from YouTube API → S3 Raw
│   └── transformation.py     # Cleans data → saves as Parquet to S3
├── dashboard/
│   └── youtube_dashboard.jpg # Power BI Dashboard screenshot
└── README.md
```

---

## 📊 Data Model

### Raw Data (JSON)
```
youtube-raw-data-etl/
└── raw/
    └── youtube_trending_YYYYMMDDHHMMSS.json
```

### Transformed Data (Parquet)
```
youtube-transformed-data-etl/
└── transformed/
    ├── videos/
    │   └── videos_data.parquet
    ├── channels/
    │   └── channels_data.parquet
    └── statistics/
        └── statistics_data.parquet
```

---

## 📋 Tables

### 📹 videos
| Column | Type | Description |
|---|---|---|
| video_id | string | Unique YouTube video ID |
| title | string | Video title |
| published_date | string | Date video was published |
| duration | string | Video duration (ISO 8601) |
| definition | string | Video quality (hd/sd) |
| category_id | string | YouTube category ID |

### 📺 channels
| Column | Type | Description |
|---|---|---|
| channel_id | string | Unique YouTube channel ID |
| channel_title | string | Channel name |
| video_id | string | Associated video ID |

### 📊 statistics
| Column | Type | Description |
|---|---|---|
| video_id | string | Unique YouTube video ID |
| views | integer | Total view count |
| likes | integer | Total like count |
| comments | integer | Total comment count |

---

## 📈 Dashboard

![YouTube Analytics Dashboard](dashboard/youtube_dashboard.jpg)

### Visualizations:
| Visual | Type | Description |
|---|---|---|
| **Total Views** | Card | Sum of all video views |
| **Total Likes** | Card | Sum of all video likes |
| **Total Comments** | Card | Sum of all video comments |
| **Top 10 Most Viewed Videos** | Bar Chart | Videos ranked by views |
| **Trending Videos by Category** | Pie Chart | Category distribution |
| **Views, Likes & Comments** | Stacked Column | Engagement metrics per video |
| **Top Channels Performance** | Table | Channels ranked by views |
| **Trending by Published Date** | Line Chart | Publishing date trend |
| **Category Filter** | Slicer | Interactive category filter |

---

## 🔍 Athena Queries

### Top 10 Most Viewed Videos:
```sql
SELECT v.title, s.views, s.likes, s.comments
FROM videos v
JOIN statistics s ON v.video_id = s.video_id
ORDER BY s.views DESC
LIMIT 10;
```

### Top 10 Channels by Views:
```sql
SELECT c.channel_title, SUM(s.views) as total_views
FROM channels c
JOIN statistics s ON c.video_id = s.video_id
GROUP BY c.channel_title
ORDER BY total_views DESC
LIMIT 10;
```

### Videos by Category:
```sql
SELECT v.category_id, COUNT(*) as video_count
FROM videos v
GROUP BY v.category_id
ORDER BY video_count DESC;
```

### Most Liked Videos:
```sql
SELECT v.title, s.likes
FROM videos v
JOIN statistics s ON v.video_id = s.video_id
ORDER BY s.likes DESC
LIMIT 10;
```

---

## 🚀 How to Run

### Prerequisites:
```
✅ AWS Account
✅ YouTube Data API v3 key (Google Cloud Console)
✅ Power BI Desktop (Windows)
✅ Athena ODBC Driver
```

### Step 1 — Get YouTube API Key:
```
→ Go to https://console.cloud.google.com
→ Create new project
→ Enable YouTube Data API v3
→ Create API key credentials
```

### Step 2 — Create S3 Buckets:
```
→ youtube-raw-data-etl      (raw JSON storage)
→ youtube-transformed-data-etl (Parquet storage)
```

### Step 3 — Setup Extraction Lambda:
```
→ Runtime: Python 3.11
→ Add environment variable: YOUTUBE_API_KEY
→ Add IAM role with S3FullAccess
→ Deploy extraction.py code
```

### Step 4 — Setup Transformation Lambda:
```
→ Runtime: Python 3.11
→ Memory: 512MB | Timeout: 1 min
→ Add layer: AWSSDKPandas-Python311
→ Add IAM role with S3FullAccess
→ Deploy transformation.py code
→ Add S3 trigger (ObjectPut on raw bucket)
```

### Step 5 — Setup Glue Crawlers:
```
→ Create 3 crawlers:
   youtube-videos-crawler   → transformed/videos/
   youtube-channels-crawler → transformed/channels/
   youtube-statistics-crawler → transformed/statistics/
→ Output database: youtube_db
→ Add AmazonS3FullAccess to Glue IAM role
→ Run crawlers
```

### Step 6 — Query with Athena:
```
→ Set S3 output location for query results
→ Select database: youtube_db
→ Run SQL queries
```

### Step 7 — Visualize with Power BI:
```
→ Install Athena ODBC driver
→ Connect Power BI to Athena
→ Load videos, channels, statistics tables
→ Create relationships on video_id
→ Build dashboard
```

### Step 8 — Add EventBridge trigger:
```
→ Add trigger to Extraction Lambda
→ Schedule: rate(1 day)
→ Pipeline runs automatically every day! ✅
```

---

## 💡 Key Learnings

- Built a **serverless ETL pipeline** on AWS from scratch
- Implemented **event-driven architecture** using S3 ObjectPut triggers
- Used **AWS Glue** for automatic schema detection
- Queried large datasets using **Amazon Athena** (SQL)
- Converted data to **Parquet format** for efficient storage
- Created **interactive Power BI dashboard** connected to Athena
- Applied **IAM least privilege** concepts for security
- Automated pipeline using **Amazon EventBridge** scheduling

---

## 👩‍💻 Author

**Sruthy G**
- 🎓 B.A. Economics | Cloud Data Analytics Certified (TCCA/ExpertzLab)
- 💼 Big Data Analyst @ GofreeLab Technologies
- 📍 Kerala, India

---

⭐ If you found this project helpful, please give it a star!
