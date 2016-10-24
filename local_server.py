from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.request
import urllib.parse
import time
import json
import ssl

host_name = "localhost"
host_port = 3000

"""
This server will help in getting access and refresh tokens from Login with 
Amazon. Be sure to add https://host_name:host_port to your allowed javascript 
origins for the applications associated with the client Id used.
"""

client_id = 'Your Login with Amazon Client Id'
client_secret = 'Your Login with Amazon Client Secret'
redirect_uri = 'https://{}:{}'.format(host_name, host_port)
scope = "profile"


class MyServer(BaseHTTPRequestHandler):

    def do_GET(self):

        if 'Referer' in self.headers:
            params = urllib.parse.urlparse(self.path)
            query = urllib.parse.parse_qs(params.query)
            if 'code' not in query:
                self.wfile.write(b'Code not found.')
            else:
                auth_code = query['code'][0]

                params = {
                    'grant_type': 'authorization_code',
                    'code': auth_code,
                    'redirect_uri': redirect_uri,
                    'client_id': client_id,
                    'client_secret': client_secret}

                data = urllib.parse.urlencode(params)

                req = urllib.request.Request(
                    url='https://api.amazon.com/auth/o2/token',
                    data=data.encode('utf-8'))

                with urllib.request.urlopen(req) as f:
                    response = f.read().decode('utf-8')

                if 'access_token' not in response:
                    self.wfile.write(b'access_token not found.')
                else:
                    json_data = json.loads(response)
                    access_token = json_data['access_token']
                    refresh_token = json_data['refresh_token']
                    self.access_token = access_token
                    self.refresh_token = refresh_token
                    self.display_tokens()

        else:
            params = {
                'client_id': client_id,
                'scope': scope,
                'response_type': 'code',
                'redirect_uri': redirect_uri,
                'state': 'thisisatest'}

            login_uri = 'https://www.amazon.com/ap/oa?{}'.format(
                urllib.parse.urlencode(params))
            print(login_uri)
            self.send_response(302)
            self.send_header('Location', login_uri)
            self.end_headers()

    def display_tokens(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(
            'access_token: <input style="width:90%;" type="text" value="{}" /><br/><br/>refresh_token: <input style="width:90%;" type="text" value="{}" /><br/><br/>'.format(
                urllib.parse.quote_plus(self.access_token),
                urllib.parse.quote_plus(self.refresh_token)).encode('utf-8'))

my_server = HTTPServer((host_name, host_port), MyServer)
my_server.socket = ssl.wrap_socket(
    my_server.socket,
    certfile='./server.crt',
    server_side=True,
    keyfile="./server.key")


try:
    print(
        time.asctime(), "Server Started - https://{}:{}".format(host_name, host_port))
    print(
        "Browse to https://{}:{} and confirm the security exception.".format(host_name, host_port))
    my_server.serve_forever()
except KeyboardInterrupt:
    pass

my_server.server_close()
print(
    time.asctime(), "Server Stopped - https://{}:{}".format(host_name, host_port))
