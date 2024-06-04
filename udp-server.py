from concurrent.futures import ThreadPoolExecutor
import socket
import logging
import logging.config
import yaml

# 加载配置文件
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# 设置日志
logging.config.dictConfig(config['logging'])
logger = logging.getLogger(__name__)

def handle_request(data, addr, server_socket):
    try:
        message = data.decode("utf-8")
        logger.info(f"Received from {addr}: {message}")
        
        response = "Valid user" if message == "username password" else "Invalid user"
        server_socket.sendto(response.encode("utf-8"), addr)
        logger.debug(f"Sent to {addr}: {response}")
    except Exception as e:
        logger.error(f"Error handling request from {addr}: {e}")

def start_udp_server():
    host = config['server']['host']
    port = config['server']['port']
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((host, port))
    logger.info(f"UDP Server listening on {host}:{port}")

    with ThreadPoolExecutor(max_workers=10) as executor:
        while True:
            try:
                data, addr = server_socket.recvfrom(1024)
                # 将请求提交给线程池处理
                executor.submit(handle_request, data, addr, server_socket)
            except Exception as e:
                logger.error(f"Error receiving data: {e}")

if __name__ == "__main__":
    start_udp_server()
