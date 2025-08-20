import os, sys, json, requests

TOKEN_URL = "https://oauth2.googleapis.com/token"
UPLOAD_URL = "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status"
THUMB_URL = "https://www.googleapis.com/upload/youtube/v3/thumbnails/set?videoId={video_id}"

def get_access_token(client_id, client_secret, refresh_token):
    data={"client_id":client_id,"client_secret":client_secret,"refresh_token":refresh_token,"grant_type":"refresh_token"}
    r=requests.post(TOKEN_URL, data=data, timeout=30); r.raise_for_status(); return r.json()["access_token"]

def start_resumable_upload(access_token, metadata):
    headers={"Authorization":f"Bearer {access_token}","Content-Type":"application/json; charset=UTF-8","X-Upload-Content-Type":"video/*"}
    body={"snippet":{"title":metadata["title"],"description":metadata["description"],"tags":metadata.get("tags",[]),"categoryId":"27"},"status":{"privacyStatus":"public","selfDeclaredMadeForKids":False}}
    r=requests.post(UPLOAD_URL, headers=headers, json=body, timeout=30); r.raise_for_status(); return r.headers["Location"]

def upload_video_file(upload_url, video_path):
    size=os.path.getsize(video_path); headers={"Content-Length":str(size),"Content-Type":"video/mp4"}
    with open(video_path,"rb") as f: r=requests.put(upload_url, headers=headers, data=f, timeout=600); r.raise_for_status(); return r.json()["id"]

def set_thumbnail(access_token, video_id, thumb_path):
    url=THUMB_URL.format(video_id=video_id); headers={"Authorization":f"Bearer {access_token}"}
    files={"media":("thumbnail.png", open(thumb_path,"rb"), "image/png")}
    r=requests.post(url, headers=headers, files=files, timeout=60); r.raise_for_status()

def main():
    if len(sys.argv)<4:
        print("Usage: upload_to_youtube.py <video> <thumb> <meta.json>"); sys.exit(1)
    video, thumb, meta = sys.argv[1], sys.argv[2], sys.argv[3]
    with open(meta, "r", encoding="utf-8") as f: metadata=json.load(f)
    client_id=os.environ["YT_CLIENT_ID"]; client_secret=os.environ["YT_CLIENT_SECRET"]; refresh_token=os.environ["YT_REFRESH_TOKEN"]
    token = get_access_token(client_id, client_secret, refresh_token)
    upload_url = start_resumable_upload(token, metadata)
    vid = upload_video_file(upload_url, video)
    set_thumbnail(token, vid, thumb)
    print("Uploaded video id:", vid)

if __name__=="__main__": main()
