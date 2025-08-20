import os, subprocess, sys

def run(cmd):
    print("[RUN]", " ".join(cmd))
    res = subprocess.run(cmd, check=True)
    return res.returncode

def main():
    os.makedirs("out", exist_ok=True)
    run([sys.executable, "scripts/generate_content.py"])
    # Upload if secrets available
    missing = [k for k in ("YT_CLIENT_ID","YT_CLIENT_SECRET","YT_REFRESH_TOKEN") if not os.environ.get(k)]
    if missing:
        print("[WARN] Missing env secrets:", missing)
        print("Assets created in ./out; set secrets to enable upload.")
        return
    run([sys.executable, "scripts/upload_to_youtube.py", "out/video.mp4", "out/thumbnail.png", "out/metadata.json"])

if __name__ == "__main__":
    main()
