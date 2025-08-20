# One-time helper to obtain a refresh token
import webbrowser, urllib.parse, requests, http.server, threading

AUTH="https://accounts.google.com/o/oauth2/v2/auth"
TOKEN="https://oauth2.googleapis.com/token"
SCOPE="https://www.googleapis.com/auth/youtube.upload"

def main():
    client_id=input("Client ID: ").strip(); client_secret=input("Client Secret: ").strip()
    port=8765; redirect=f"http://localhost:{port}/callback"
    params={"client_id":client_id,"redirect_uri":redirect,"response_type":"code","scope":SCOPE,"access_type":"offline","prompt":"consent"}
    url=AUTH+"?"+urllib.parse.urlencode(params)
    code_holder={"code":None}
    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            qs=urllib.parse.urlparse(self.path).query; q=urllib.parse.parse_qs(qs)
            code_holder["code"]=(q.get("code") or [None])[0]; self.send_response(200); self.end_headers(); self.wfile.write(b"You can close this window.")
        def log_message(self,*a,**k): pass
    srv = http.server.HTTPServer(("localhost",port), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    print("Opening browser..."); webbrowser.open(url)
    while not code_holder["code"]: pass
    srv.shutdown()
    data={"code":code_holder["code"],"client_id":client_id,"client_secret":client_secret,"redirect_uri":redirect,"grant_type":"authorization_code"}
    r=requests.post(TOKEN, data=data, timeout=30); r.raise_for_status(); print("REFRESH TOKEN:\\n", r.json().get("refresh_token"))

if __name__=="__main__": main()
