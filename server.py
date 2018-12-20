#!/usr/bin/python
from http.server import BaseHTTPRequestHandler,HTTPServer
from os import curdir, sep
import io, os
import cgi
from zipfile import ZipFile

PORT_NUMBER = 8080

#This class will handles any incoming request from
#the browser 
class myHandler(BaseHTTPRequestHandler):
	
	def folderListing(self, folder):
		if not os.path.exists(folder):
			os.mkdir(folder)

		htmlf = open('template.html', 'r')
		html = htmlf.read()
		htmlf.close()
		table = '<table class="table table-hover table-striped">'
		table += '<thead class="thead-dark"> <tr> <th scope="col"> Filename </th> <th> </th> </tr> </thead>'
		table += '<tbody>'

		ext = ['.dbf', '.prj', '.shx', '.shp']

		
		for file in os.listdir(folder):
			tr = '<tr>'
			if '.shp' in file:
				td = '<td>'
				base = os.path.splitext(file)[0]
				valid = True
				for e in ext:
					if not os.path.exists(os.path.join(folder, base + e)):
						valid = False
						break

				if not valid:
					continue

				# If don't exist zip file create a new one to contain all files 
				# needed for a useful shapefile
				if not os.path.exists(os.path.join(folder, base + '.zip')):
					with ZipFile(os.path.join(folder, base + '.zip'), 'w') as zipf:
						for e in ext:
							zipf.write(os.path.join(folder, base + e))

						zipf.close()

				td += base
				td += '</td>'

				td += '<td> <a href="' + os.path.join(folder, base + '.zip') + '" download>'
				td += 'Download file </a></td>'

				tr += td
				tr += '</tr>'

				table += tr

		table += '</tbody>'
		table += '</table>'

		htmls = html.split('<div class="col-md-8">')
		response = htmls[0] + '<div class="col-md-8">' + table + htmls[1]

		return response


	#Handler for the GET requests
	def do_GET(self):
		if self.path=="/":
			self.path="/index.html"

		if self.path=='/shplist':
			self.send_response(200)
			self.send_header('Content-type','text/html')
			self.end_headers()
			r = self.folderListing('genshps')
			self.wfile.write(bytes(r, 'utf-8'))

			return

		try:
			#Check the file extension required and
			#set the right mime type

			sendReply = False
			if self.path.endswith(".html"):
				mimetype='text/html'
				sendReply = True
			if self.path.endswith(".jpg"):
				mimetype='image/jpg'
				sendReply = True
			if self.path.endswith(".gif"):
				mimetype='image/gif'
				sendReply = True
			if self.path.endswith(".js"):
				mimetype='application/javascript'
				sendReply = True
			if self.path.endswith(".css"):
				mimetype='text/css'
				sendReply = True

			if sendReply == True:
				#Open the static file requested and send it
				f = io.FileIO(curdir + sep + self.path) 
				self.send_response(200)
				self.send_header('Content-type',mimetype)
				self.end_headers()
				self.wfile.write(f.readall())
				f.close()
			return


		except IOError:
			self.send_error(404,'File Not Found: %s' % self.path)

	#Handler for the POST requests
	def do_POST(self):
		if self.path=="/execute":
			form = cgi.FieldStorage(
				fp=self.rfile, 
				headers=self.headers,
				environ={'REQUEST_METHOD':'POST',
		                 'CONTENT_TYPE':self.headers['Content-Type'],
			})

			print("Your name is: %s" % form["imglist"].value)
			self.send_response(200)
			self.end_headers()
			self.wfile.write(bytes("Thanks %s !" % form["imglist"].value, 'utf-8'))
			return			


try:
	#Create a web server and define the handler to manage the
	#incoming request
	server = HTTPServer(('', PORT_NUMBER), myHandler)
	print('Started httpserver on port ' , PORT_NUMBER)
	
	#Wait forever for incoming htto requests
	server.serve_forever()

except KeyboardInterrupt:
	print('^C received, shutting down the web server')
	server.socket.close()
