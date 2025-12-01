import http.server
import socketserver
import json
import csv
import os
from datetime import datetime

PORT = 8000
CSV_FILE = 'emails.csv'

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/submit-email':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                email = data.get('email')
                
                if email:
                    self.save_email(email)
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'status': 'success'}).encode('utf-8'))
                else:
                    self.send_error(400, "Email not provided")
            except Exception as e:
                print(f"Error processing request: {e}")
                self.send_error(500, "Internal Server Error")
        else:
            self.send_error(404, "Not Found")

    def save_email(self, email):
        file_exists = os.path.isfile(CSV_FILE)
        
        with open(CSV_FILE, 'a', newline='') as csvfile:
            fieldnames = ['timestamp', 'email']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow({
                'timestamp': datetime.now().isoformat(),
                'email': email
            })
        print(f"Saved email: {email}")

print(f"Serving at http://localhost:{PORT}")
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    httpd.serve_forever()
