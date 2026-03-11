import yt_dlp
import time
import statistics
import logging

logging.getLogger("yt_dlp").setLevel(logging.ERROR)

print("YouTube KOL分析工具")

channel = input("请输入YouTube频道链接: ")
price = float(input("请输入合作费用(USD): "))

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
except Exception as e:
    print("频道读取失败:", e)
    input()
    exit()

videos = info.get("entries", [])

if not videos:
    print("未找到频道视频")
    input()
    exit()

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

    # 过滤Shorts
    if duration and duration < 60:
        continue

    age = now - timestamp

    # 忽略1天内视频
    if age < day:
        continue

    if age <= days30:
        views30.append(view)

    if age <= days90:
        views90.append(view)

    time.sleep(0.5)

if not views90:
    print("无法获取频道数据")
    input()
    exit()

avg30 = sum(views30) / len(views30) if views30 else 0
avg90 = sum(views90) / len(views90)

median_views = statistics.median(views90)

cpm = price / (avg90 / 1000)

suggest_low = avg90 / 1000 * 10
suggest_high = min(avg90 / 1000 * 30, 2000)

print("\n====== KOL数据分析 ======")

print("最近30天视频数:", len(views30))
print("最近30天平均播放:", int(avg30))

print("90天平均播放:", int(avg90))
print("中位播放:", int(median_views))

print("\nCPM:", round(cpm, 2))

print("\n建议报价区间:")
print(int(suggest_low), "~", int(suggest_high), "USD")

print("\n======合作判断======")

if avg90 < 5000:
    print("❌ 播放量低于5000")

elif price > 2000:
    print("❌ 报价超过2000")

elif cpm > 30:
    print("❌ CPM过高")

else:
    print("✅ 可以合作")

input("\n按回车退出")