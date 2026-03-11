import os
import time
import statistics
import logging
from flask import Flask, request, render_template
import yt_dlp

# 禁用 yt-dlp 警告
logging.getLogger("yt_dlp").setLevel(logging.ERROR)

app = Flask(__name__)

# 分析函数
def analyze_channel(channel, price):
    now = time.time()
    day = 86400
    days30 = 30 * day
    days90 = 90 * day

    views30 = []
    views90 = []

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
        "playlist_items": "1-40"
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(channel + "/videos", download=False)
    except:
        return {"error": "频道读取失败"}

    videos = info.get("entries", [])
    video_ids = [v["id"] for v in videos if v]

    for vid in video_ids:
        url = "https://www.youtube.com/watch?v=" + vid

        try:
            with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True}) as ydl:
                vinfo = ydl.extract_info(url, download=False)
        except:
            continue

        view = vinfo.get("view_count")
        timestamp = vinfo.get("timestamp")
        duration = vinfo.get("duration")

        if not view or not timestamp:
            continue

        # 过滤 Shorts
        if duration and duration < 60:
            continue

        age = now - timestamp
        if age < day:
            continue

        if age <= days30:
            views30.append(view)
        if age <= days90:
            views90.append(view)

    if not views90:
        return {"error": "无法获取频道数据"}

    avg30 = sum(views30) / len(views30) if views30 else 0
    avg90 = sum(views90) / len(views90)
    median_views = statistics.median(views90)

    cpm = price / (avg90 / 1000)

    suggest_low = avg90 / 1000 * 10
    suggest_high = min(avg90 / 1000 * 30, 2000)

    result = {
        "videos30": len(views30),
        "avg30": int(avg30),
        "avg90": int(avg90),
        "median": int(median_views),
        "cpm": round(cpm, 2),
        "suggest_low": int(suggest_low),
        "suggest_high": int(suggest_high)
    }

    return result

# 首页路由
@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        channel = request.form["channel"]
        price = float(request.form["price"])
        result = analyze_channel(channel, price)
    return render_template("index.html", result=result)

# Render 支持动态端口
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
