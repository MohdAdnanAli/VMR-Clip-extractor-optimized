import sqlite3
import pandas as pd
from sentence_transformers import SentenceTransformer, util
import whisper
import imagehash
from PIL import Image
import requests
import io
import yt_dlp  # For downloading clip snippets
from sklearn.linear_model import LinearRegression
import datetime
import math
import os
import json  # Assume API fetches return JSON

# Setup
NICHE_KEYWORDS = ["gaming", "memes"]  # Your niche
DB_FILE = "clip_history.db"
EXCEL_FILE = "clip_selections.xlsx"
MODEL = SentenceTransformer('all-MiniLM-L6-v2')
WHISPER_MODEL = whisper.load_model("tiny")
WEIGHTS = {'views': 0.4, 'velocity': 0.3, 'engagement': 0.2, 'relevance': 0.1}  # Initial; updated weekly

# Init DB
conn = sqlite3.connect(DB_FILE)
conn.execute('''CREATE TABLE IF NOT EXISTS history (video_id TEXT PRIMARY KEY, hash TEXT)''')
conn.execute('''CREATE TABLE IF NOT EXISTS performance (video_id TEXT, source TEXT, length FLOAT, topic TEXT, rpm FLOAT)''')
conn.close()

def fetch_trending_clips(platform='youtube', limit=100):
    # Placeholder: Use actual API/Selenium to fetch trending shorts
    # Example: returns list of dicts {'id': str, 'title': str, 'views': int, 'views_last_24h': int, 'likes': int, 'comments': int, 'shares': int,
    # 'age_hours': float, 'growth_6h': float, 'transcript': str (fetch via API), 'thumbnail_url': str, 'url': str}
    return []  # Implement real fetch

def calculate_virality(views_last_24h, likes, comments, shares, views):
    if views == 0: return 0
    return math.log10(views_last_24h + 1) * ((likes + comments + shares) / views)

def calculate_relevance(title_transcript, niche_keywords):
    niche_emb = MODEL.encode(' '.join(niche_keywords))
    clip_emb = MODEL.encode(title_transcript)
    return util.cos_sim(niche_emb, clip_emb)[0][0].item()

def velocity_filter(growth_6h):
    return growth_6h >= 3.0  # 300%

def deduplicate(video_id, thumbnail_url):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM history WHERE video_id=?", (video_id,))
    if c.fetchone(): return True
    try:
        img = Image.open(io.BytesIO(requests.get(thumbnail_url).content))
        phash = str(imagehash.phash(img))
        c.execute("SELECT * FROM history WHERE hash=?", (phash,))
        if c.fetchone(): return True
        c.execute("INSERT INTO history VALUES (?, ?)", (video_id, phash))
        conn.commit()
    except: pass
    conn.close()
    return False

def reactability_check(clip_url):
    try:
        with yt_dlp.YoutubeDL({'quiet': True, 'format': 'bestaudio', 'outtmpl': 'temp.mp3'}) as ydl:
            ydl.download([clip_url])
        audio = whisper.load_audio("temp.mp3")[:5 * 16000]  # First 5s
        result = WHISPER_MODEL.transcribe(audio)
        text = result['text']
        os.remove("temp.mp3")
        if not text.strip() or "music" in text.lower():  # Rough check
            return -0.8
    except: return 0
    return 0

def final_score(clip, weights):
    virality = calculate_virality(clip['views_last_24h'], clip['likes'], clip['comments'], clip['shares'], clip['views'])
    relevance = calculate_relevance(clip['title'] + ' ' + clip['transcript'], NICHE_KEYWORDS)
    engagement = 0.5 * (clip['likes'] + clip['comments']) + 0.3 * clip['shares'] + 0.2 * clip.get('saves', 0) / clip['views'] * 1000
    penalty = clip['age_hours'] * 0.5 if clip['age_hours'] > 12 else 0
    react_penalty = reactability_check(clip['url'])
    return (virality + relevance) * (weights['views'] * clip['views'] + weights['velocity'] * clip['views_last_24h'] + weights['engagement'] * engagement + weights['relevance'] * relevance) - penalty + react_penalty

def weekly_feedback():
    if datetime.datetime.now().weekday() != 6: return  # Sunday
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM performance ORDER BY video_id DESC LIMIT 20", conn)
    conn.close()
    if len(df) < 20: return
    # Features: source (one-hot), length, topic (one-hot)
    X = pd.get_dummies(df[['source', 'topic']])
    X['length'] = df['length']
    y = df['rpm']
    reg = LinearRegression().fit(X, y)
    # Rough re-weight: normalize coefs to sum=1
    coefs = reg.coef_
    new_weights = {k: abs(coefs[i]) for i, k in enumerate(WEIGHTS.keys())}  # Map to keys
    total = sum(new_weights.values())
    WEIGHTS.update({k: v/total for k,v in new_weights.items()})

def main():
    weekly_feedback()
    clips = fetch_trending_clips()
    filtered = []
    for clip in clips:
        if not velocity_filter(clip['growth_6h']): continue
        if deduplicate(clip['id'], clip['thumbnail_url']): continue
        score = final_score(clip, WEIGHTS)
        if score > 15:  # Threshold example
            filtered.append({**clip, 'score': score})
    df = pd.DataFrame(filtered)
    df.to_excel(EXCEL_FILE, index=False)
    return filtered[:5]  # Top 5

if __name__ == "__main__":
    main()