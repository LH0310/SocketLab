import logging.config
import selectors
import socket
import threading
import logging
import yaml

# 读取配置
with open('config.yaml') as f:
    config = yaml.safe_load(f)

logging.config.dictConfig(config['logging'])
logger = logging.getLogger(__name__)

# MainReactor 类，用于主线程监听连接请求
class MainReactor:
    def __init__(self, host, port, sub_reactors):
        self.sel = selectors.DefaultSelector()
        self.sub_reactors = sub_reactors
        self.next_reactor = 0

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((host, port))
        self.sock.listen(100)
        self.sock.setblocking(False)
        self.sel.register(self.sock, selectors.EVENT_READ, self.accept)

    def accept(self, sock, mask):
        conn, addr = sock.accept()
        logger.info(f'Accepted connection from {addr}')
        conn.setblocking(False)
        self.assign_to_sub_reactor(conn)

    def assign_to_sub_reactor(self, conn):
        sub_reactor = self.sub_reactors[self.next_reactor]
        self.next_reactor = (self.next_reactor + 1) % len(self.sub_reactors)
        sub_reactor.register(conn)

    def run(self):
        logger.info(f'MainReactor running on {config["server"]["host"]}:{config["server"]["port"]}')
        while True:
            events = self.sel.select()
            for key, mask in events:
                callback = key.data
                callback(key.fileobj, mask)

# SubReactor 类，用于子线程处理连接
class SubReactor(threading.Thread):
    def __init__(self):
        super().__init__()
        self.sel = selectors.DefaultSelector()

    def register(self, conn):
        self.sel.register(conn, selectors.EVENT_READ, self.read)

    def run(self):
        while True:
            events = self.sel.select()
            for key, mask in events:
                callback = key.data
                callback(key.fileobj, mask)

    def read(self, conn, mask):
        try:
            data = conn.recv(1024)
            if data:
                message = data.decode("utf-8")
                logger.info(f'Received message: {message}')
                response = "Valid user" if message == "username password" else "Invalid user"
                conn.send(response.encode("utf-8"))
            else:
                logger.info(f'Closing connection {conn}')
                self.sel.unregister(conn)
                conn.close()
        except Exception as e:
            logger.error(f'Error reading connection: {e}')
            self.sel.unregister(conn)
            conn.close()

def main():
    sub_reactors = [SubReactor() for _ in range(4)]
    for reactor in sub_reactors:
        reactor.start()

    main_reactor = MainReactor(config['server']['host'], config['server']['port'], sub_reactors)
    main_reactor.run()

if __name__ == '__main__':
    main()
