import cv2
import threading
from http.server import BaseHTTPRequestHandler,HTTPServer
from socketserver import ThreadingMixIn
from io import StringIO,BytesIO
from PIL import Image
import time
cameras=None

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

            print(self.path[4])

            cameraIndex = int(self.path[4])
            camera = cameras[cameraIndex]
               
            while running:
                try:
                    rc, img = camera.read()
                    if not rc:
                        continue
                
                    imgRGB=cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
                    r, jpg = cv2.imencode(".jpg",imgRGB)
                    jpg_bytes = jpg.tobytes()

                    self.wfile.write("--jpgboundary\r\n".encode())
                    self.send_header('Content-type','image/jpeg')
                    self.send_header('Content-length',str(len(jpg_bytes)))
                    self.end_headers()
               
                    self.wfile.write(jpg_bytes)
                    time.sleep(0.25)

                except KeyboardInterrupt:
                    print("^C received, aborting")
                    running = False
                    break
                except ConnectionAbortedError:
                    print("Client Disconnected.")
                    running = False
                    break
                except ConnectionResetError:
                    print("Client Reset.")
                    running = False
                    break
            
        elif self.path.endswith('.html'):
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            self.wfile.write(b'<html><head></head><body>')
            self.wfile.write(b'<h1>WEBCAM OUT</h1>')
            self.wfile.write(b'<img src="/cam0.mjpg"/>')
            self.wfile.write(b'<img src="/cam1.mjpg"/>')
            self.wfile.write(b'</body></html>')
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<html><head></head><body>')
            self.wfile.write(b'<h1>PAGE NOT FOUND</h1>')
            self.wfile.write(b'</body></html>')
   
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
	"""Handle requests in a separate thread."""
def main():
    num = 0

    global cameras
    cameras = []
    while 1:
        cap = cv2.VideoCapture(num)
        if cap.isOpened():
            print(cap)
            cameras.append(cap)
            # working capture
            num += 1
        else:
            break

    try:
        PORT_NUMBER = 9000
        server = ThreadedHTTPServer(('', PORT_NUMBER), CamHandler)
        print ('Started httpserver on port ' , PORT_NUMBER)
        server.serve_forever()
    except KeyboardInterrupt:
        for cam in cameras:
            cam.release()

        print ('^C received, shutting down the web server')
        server.socket.close()

    print("All done")

if __name__ == '__main__':
	main()