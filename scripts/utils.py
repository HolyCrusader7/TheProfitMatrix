import os, re, json, math, random, subprocess
from typing import List

def ensure_dir(p): os.makedirs(p, exist_ok=True)

def synth_speech_espeak(text: str, wav_out: str, voice: str="en+f3", speed_wpm: int=170, pitch: int=35):
    cmd = ["espeak-ng","-v",voice,"-s",str(speed_wpm),"-p",str(pitch),"-g","5","-w",wav_out,text]
    subprocess.run(cmd, check=True)

def get_audio_duration(path: str) -> float:
    import json, subprocess
    result = subprocess.run(["ffprobe","-v","error","-select_streams","a:0","-show_entries","stream=duration","-of","json",path], capture_output=True, text=True, check=True)
    data = json.loads(result.stdout)
    return float(data["streams"][0]["duration"])

def split_for_captions(text: str, max_words: int=9):
    words = text.strip().split()
    return [" ".join(words[i:i+max_words]) for i in range(0,len(words),max_words)]

def make_srt(chunks, total_duration, path):
    def fmt(t): h=int(t//3600); m=int((t%3600)//60); s=int(t%60); ms=int((t-int(t))*1000); return f"{h:02}:{m:02}:{s:02},{ms:03}"
    n=len(chunks) or 1; start=0.25; per=max(0.9,(total_duration-0.5)/n)
    t=start; lines=[]
    for i,ch in enumerate(chunks,1):
        s=t; e=min(total_duration, s+per)
        lines.append(f"{i}\n{fmt(s)} --> {fmt(e)}\n{ch}\n")
        t=e
    with open(path,"w",encoding="utf-8") as f: f.write("\\n".join(lines))

def simple_vertical_bg(output, duration, width=1080, height=1920, fps=30):
    cmd = ["ffmpeg","-y","-f","lavfi","-i",f"color=c=black:s={width}x{height}:d={duration}","-f","lavfi","-i",f"noise=alls=20:allf=t+u:all_seed=42:s={width}x{height}:d={duration}","-filter_complex","[1]format=gray,eq=contrast=1.2[noise];[0][noise]blend=all_mode=overlay:all_opacity=0.08,format=yuv420p[v]","-map","[v]","-r",str(fps),"-t",str(duration),output]
    subprocess.run(cmd, check=True)

def overlay_subtitles(video_in, srt_path, audio_wav, video_out):
    vf = f"subtitles='{srt_path}':force_style='Fontsize=42,OutlineColour=&H000000&,BorderStyle=3,Outline=2'"
    cmd = ["ffmpeg","-y","-i",video_in,"-i",audio_wav,"-vf",vf,"-c:a","aac","-b:a","192k","-shortest",video_out]
    subprocess.run(cmd, check=True)

def download_pexels_vertical(api_key, query, min_duration, out_path):
    import requests, math, os, json, subprocess
    headers={"Authorization":api_key}; params={"query":query,"per_page":10,"orientation":"portrait","size":"large"}
    r=requests.get("https://api.pexels.com/videos/search", headers=headers, params=params, timeout=30)
    if r.status_code!=200: return False
    data=r.json(); vids=data.get("videos",[])
    if not vids: return False
    files=vids[0].get("video_files",[])
    if not files: return False
    url=sorted(files, key=lambda f: abs((f.get("width",0)/max(f.get("height",1),1)) - (1080/1920)))[0]["link"]
    tmp=out_path+".tmp.mp4"
    vr=requests.get(url, timeout=60)
    if vr.status_code!=200: return False
    with open(tmp,"wb") as f: f.write(vr.content)
    dur = get_audio_duration(tmp) if os.path.exists(tmp) else 4.0
    loops = max(1, math.ceil(min_duration/max(dur,0.1)))
    filter_chain = "scale=1080:-2,boxblur=luma_radius=min(h\\,w)/40,scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(1080-iw)/2:(1920-ih)/2"
    cmd = ["ffmpeg","-y","-stream_loop",str(loops-1),"-i",tmp,"-filter:v",filter_chain,"-t",str(min_duration),"-an",out_path]
    subprocess.run(cmd, check=True)
    os.remove(tmp)
    return True

def build_title_desc_tags_finance(mode, payload, affiliate_link=None):
    if mode=="evergreen":
        hook=payload.get("hook","Money Tip"); content=payload.get("content","")
        title=f"{hook}: {content[:60]}"
        desc=f"{hook}\\n\\n{content}\\n\\nTakeaway: {payload.get('breakdown','')}\\n"
    else:
        title_raw=payload.get("title","Today in Business"); title=f"Today in Business: {title_raw[:80]}"
        summary=payload.get("summary",""); src=payload.get("source",""); link=payload.get("link","")
        desc=f"{title_raw}\\n\\nSummary: {summary}\\nSource: {src}\\nLink: {link}\\n"
    if affiliate_link:
        desc += f"\\n—\\nSupport the channel: {affiliate_link}\\n"
    tags=["finance","business","investing","money","shorts","economy","markets"]
    return title, desc, tags
