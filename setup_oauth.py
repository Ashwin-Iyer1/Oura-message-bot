import os
import webbrowser
import json
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

CLIENT_ID = os.getenv("OURA_CLIENT_ID")
CLIENT_SECRET = os.getenv("OURA_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8000/callback"
TOKEN_FILE = "oura_tokens.json"

if not CLIENT_ID or not CLIENT_SECRET:
    print("❌ Error: OURA_CLIENT_ID or OURA_CLIENT_SECRET not found in .env file.")
    print("Please add them to your .env file and run this script again.")
    exit(1)

class OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == "/callback":
            query_params = parse_qs(parsed_path.query)
            if "code" in query_params:
                code = query_params["code"][0]
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b"<h1>Authorization Successful!</h1><p>You can close this window and check your terminal.</p>")
                
                # Exchange code for token
                exchange_code_for_token(code)
            else:
                self.send_response(400)
                self.wfile.write(b"<h1>Authorization Failed!</h1><p>No code found.</p>")
        else:
            self.send_response(404)
            self.wfile.write(b"Not Found")

def exchange_code_for_token(code):
    print("\n🔄 Exchanging authorization code for access tokens...")
    url = "https://api.ouraring.com/oauth/token"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI, 
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    
    response = requests.post(url, data=data)
    
    if response.status_code == 200:
        tokens = response.json()
        print("✅ Tokens received!")
        save_tokens(tokens)
        print(f"✅ Tokens saved to {TOKEN_FILE}")
        print("\n🎉 Setup complete! You can now run the bot.")
        # Stop the server
        os._exit(0)
    else:
        print(f"❌ Failed to exchange token: {response.text}")
        os._exit(1)

def save_tokens(tokens):
    with open(TOKEN_FILE, "w") as f:
        json.dump(tokens, f, indent=4)

def main():
    print("--- Oura OAuth2 Setup ---")
    
    # Construct Authorization URL
    # Scopes: email personal daily heartrate workout tag session spo2
    scopes = "email personal daily heartrate workout tag session spo2"
    auth_url = (
        f"https://cloud.ouraring.com/oauth/authorize?"
        f"response_type=code&client_id={CLIENT_ID}&"
        f"redirect_uri={REDIRECT_URI}&scope={scopes}&state=setup"
    )
    
    print(f"\n1. Opening browser to: {auth_url}")
    webbrowser.open(auth_url)
    
    print("\n2. Waiting for callback on http://localhost:8000/callback ...")
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, OAuthHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
