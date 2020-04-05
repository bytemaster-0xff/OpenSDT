import cv2
import threading
from http.server import BaseHTTPRequestHandler,HTTPServer
from socketserver import ThreadingMixIn
from io import StringIO,BytesIO
from PIL import Image
import time
capture=None

num = 0

print(cv2.__version__)

class CamHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        print(self.path)

        if self.path.endswith('mjpg'):
            self.send_response(200)
            self.send_header('Content-type','multipart/x-mixed-replace; boundary=--jpgboundary')
            self.end_headers()
            running = True

            if(self.path.endswith("cam1.mjpg")):
                camera = capture[0]

            if(self.path.endswith("cam2.mjpg")):
                 camera = capture[1]
                
            if(self.path.endswith("cam3.mjpg")):
                camera = capture[2]

            while running:
                try:
                    rc, img = camera.read()
                    if not rc:
                        continue
                
                    imgRGB=cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
                    jpg = Image.fromarray(imgRGB)
                    r, buf = cv2.imencode(".jpg",imgRGB)
                    self.wfile.write(b"--jpgboundary")
                    self.send_header('Content-type','image/jpeg')
                    self.send_header('Content-length',str(len(buf)))
                    self.end_headers()
               
                    self.wfile.write(bytearray(buf))
                    self.wfile.write(b"\r\n")
                    time.sleep(0.05)

                except KeyboardInterrupt:
                    print("KEY EXCEPTION")
                    running = False
                    break
            
            print("Finished Thread")

            return

        if self.path.endswith('.html'):
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            self.wfile.write(b'<html><head></head><body>')
            self.wfile.write(b'<h1>WEBCAM OUT</h1>')
            self.wfile.write(b'<img src="/cam1.mjpg"/>')
            self.wfile.write(b'<img src="/cam2.mjpg"/>')
            self.wfile.write(b'<img src="/cam3.mjpg"/>')
            self.wfile.write(b'</body></html>')
            return

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
	"""Handle requests in a separate thread."""
def main():
    global capture
    capture = []
    capture.append(cv2.VideoCapture(0))
    capture.append(cv2.VideoCapture(1))
    capture.append(cv2.VideoCapture(2))

    try:
        PORT_NUMBER = 9000
        server = ThreadedHTTPServer(('', PORT_NUMBER), CamHandler)
        print ('Started httpserver on port ' , PORT_NUMBER)
        server.serve_forever()
    except KeyboardInterrupt:
        for cam in capture:
            cam.release()

        print ('^C received, shutting down the web server')
        server.socket.close()

    print("All done")

if __name__ == '__main__':
	main()