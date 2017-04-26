import http.server
import socketserver
import socket

PORT = 8081

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if 'lane_state' in self.path:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect(('localhost', 5050))
                sock.sendall('\n'.encode('utf-8'))
                data = sock.recv(8192)
            self.send_response(200, 'OK')
            self.wfile.write(data)
        else:
            return super(Handler, self).do_GET()

def main():
    with socketserver.TCPServer(('localhost', PORT), Handler) as httpd:
        httpd.serve_forever()

if __name__ == '__main__':
    main()
