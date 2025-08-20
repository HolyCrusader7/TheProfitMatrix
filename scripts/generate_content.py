import os, json, datetime, random
from utils import ensure_dir, synth_speech_espeak, get_audio_duration, split_for_captions, make_srt, simple_vertical_bg, overlay_subtitles, build_title_desc_tags_finance, download_pexels_vertical
from sources import pick_mode, load_evergreen_csv, fetch_news_candidates, extract_query_from_title, load_stopwords

OUT="out"; DATA="data"; ensure_dir(OUT)

def build_script_evergreen(item):
    hook=item.get("hook","Money Tip"); content=item.get("content",""); breakdown=item.get("breakdown","")
    script=f"{hook}. {content} {breakdown} Follow for more finance and business insights."
    payload={"hook":hook,"content":content,"breakdown":breakdown}
    return script, payload

def build_script_news(entry):
    title=entry.get("title",""); summary=entry.get("summary",""); link=entry.get("link",""); source=entry.get("source","")
    first_sentence = summary.split(".")[0][:180] if summary else ""
    hook="Here's what's moving business today:"
    breakdown="Why it matters: developments like this can affect sentiment and strategy. Always do your own research."
    script=f"{hook} {title}. {first_sentence}. {breakdown} Follow for more finance and business insights."
    payload={"title":title,"summary":first_sentence,"link":link,"source":source}
    return script, payload

def main():
    today=datetime.date.today()
    force=os.environ.get("FORCE_MODE","").strip().lower() or None
    load_stopwords(os.path.join(DATA,"stopwords.txt"))
    mode=pick_mode(today, force)
    evergreen=load_evergreen_csv(os.path.join(DATA,"evergreen.csv"))
    if mode=="evergreen":
        item = random.choice(evergreen) if evergreen else {"hook":"Money Tip","content":"Save at least 10% of income.","breakdown":"Consistency wins."}
        script,payload = build_script_evergreen(item)
    else:
        news = fetch_news_candidates()
        if news:
            entry=news[0]; script,payload=build_script_news(entry)
        else:
            item = random.choice(evergreen) if evergreen else {"hook":"Money Tip","content":"Invest regularly.","breakdown":"DCA reduces timing risk."}
            script,payload=build_script_evergreen(item); mode="evergreen"

    wav=os.path.join(OUT,"voice.wav")
    synth_speech_espeak(script,wav)
    duration = get_audio_duration(wav)
    bg=os.path.join(OUT,"bg.mp4"); ok=False
    pexels=os.environ.get("PEXELS_API_KEY","").strip()
    query="finance office" if mode=="evergreen" else extract_query_from_title(payload.get("title","stock market"))
    if pexels:
        try: ok=download_pexels_vertical(pexels, query, duration, bg)
        except: ok=False
    if not ok: simple_vertical_bg(bg, duration)
    chunks = split_for_captions(script, max_words=9)
    srt=os.path.join(OUT,"captions.srt"); make_srt(chunks, duration, srt)
    out_video=os.path.join(OUT,"video.mp4"); overlay_subtitles(bg, srt, wav, out_video)
    # thumbnail
    make_thumbnail(mode,payload)
    # metadata
    affiliate=os.environ.get("AFFILIATE_LINK","").strip() or None
    title, desc, tags = build_title_desc_tags_finance(mode, payload, affiliate)
    meta={"title":title,"description":desc,"tags":tags}
    with open(os.path.join(OUT,"metadata.json"),"w",encoding="utf-8") as f: json.dump(meta,f,ensure_ascii=False, indent=2)

def make_thumbnail(mode,payload):
    from PIL import Image, ImageDraw, ImageFont
    w,h=1280,720; img=Image.new("RGB",(w,h),(10,14,18)); draw=ImageDraw.Draw(img)
    primary=(34,197,94); accent=(250,204,21); white=(245,245,245)
    if mode=="evergreen": title=payload.get("hook","MONEY TIP").upper(); subtitle=payload.get("content","")[:60]+"..."
    else: title="TODAY IN BUSINESS"; subtitle=payload.get("title","")[:60]+"..."
    try:
        font_big=ImageFont.truetype("DejaVuSans-Bold.ttf",88); font_small=ImageFont.truetype("DejaVuSans.ttf",46)
    except: font_big=ImageFont.load_default(); font_small=ImageFont.load_default()
    draw.rectangle([0,0,w,140], fill=(15,20,26)); draw.text((40,30), title, font=font_big, fill=primary)
    box_x,box_y,box_w,box_h=60,h-240,w-120,160; draw.rectangle([box_x,box_y,box_x+box_w,box_y+box_h], fill=(20,26,34))
    draw.text((box_x+30,box_y+45), subtitle, font=font_small, fill=white); draw.rectangle([0,h-18,w,h], fill=accent)
    img.save(os.path.join(OUT,"thumbnail.png"))

if __name__=="__main__": main()
