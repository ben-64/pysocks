#!/usr/bin/env python
import sys,socket,SocketServer,struct,select

class Socks(SocketServer.BaseRequestHandler):
    def handle(self):
        data = self.request.recv(1024)
        try:
            version,cmd,port = struct.unpack(">BBH",data[:4])
            ip = socket.inet_ntoa(data[4:8])
        except:
            return
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            sock.connect((ip,port))
        except:
            print("final server closed")
            return
        self.request.sendall("\x00\x5a\x00\x00\x00\x00\x00\x00")

        socks = {}
        socks[self.request] = sock
        socks[sock] = self.request

        while True:
            (read,write,error) = select.select([self.request,sock],[],[self.request,sock])
            if error: break
            elif read:
                for s in read:
                    data = s.recv(4096)
                    if not data: break
                    socks[s].sendall(data)
        sock.close()

class SockServer(SocketServer.ForkingMixIn, SocketServer.TCPServer):
    pass

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 1080
    SockServer.allow_reuse_address = True
    socks = SockServer(("0.0.0.0", port), Socks)
    socks.serve_forever()
