from urlparse import urlparse
import re
import BaseHTTPServer
import urllib
import webbrowser

def prompt(scope, client_id, redirect_uri):
    ''' prompts the user to login returns the user token
	suitable for use with the spotipy.Spotify constructor

        Parameters:

         - scope - the desired scope of the request
         - client_id - the client id of your app
         - redirect_uri - the redirect URI of your app
    '''

    # Request for auto opening the browser and copying the access token
    #print "Opening your spotify . . ."
    webbrowser.open('https://accounts.spotify.com/authorize?' + urllib.urlencode({
			'response_type': 'token',
			'client_id': client_id,
			'scope': scope,
			'redirect_uri': redirect_uri
		}))
    parse = urlparse(redirect_uri)
    server = AuthorizationServer(parse.hostname, parse.port)
    try:
        while True:
            server.handle_request()
    except Authorization as auth:
        return auth.access_token

class AuthorizationServer(BaseHTTPServer.HTTPServer):
	def __init__(self, host, port):
		BaseHTTPServer.HTTPServer.__init__(self, (host, port), AuthorizationHandler)

	# Disable the default error handling.
	def handle_error(self, request, client_address):
		raise

class AuthorizationHandler(BaseHTTPServer.BaseHTTPRequestHandler):
	def do_GET(self):
		# The Spotify API has redirected here, but access_token is hidden in the URL fragment.
		# Read it using JavaScript and send it to /token as an actual query string...
		if self.path.startswith('/redirect'):
			self.send_response(200)
			self.send_header('Content-Type', 'text/html')
			self.end_headers()
			self.wfile.write('<script>location.replace("token?" + location.hash.slice(1));</script>')
		# Read access_token and use an exception to kill the server listening...
		elif self.path.startswith('/token?'):
			self.send_response(200)
			self.send_header('Content-Type', 'text/html')
			self.end_headers()
			self.wfile.write('<script>close()</script>Thanks! You may now close this window.')
			raise Authorization(re.search('access_token=([^&]*)', self.path).group(1))
		else:
			self.send_error(404)

	# Disable the default logging.
	def log_message(self, format, *args):
		pass
	
class Authorization(Exception):
	def __init__(self, access_token):
		self.access_token = access_token
