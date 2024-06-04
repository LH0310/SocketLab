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

def start_tcp_client():
    host = config['server']['host']
    port = config['server']['port']
    
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        logger.info(f"Connected to server at {host}:{port}")

        while True:
            message = input("Enter username and password: ")
            client_socket.send(bytes(message, "utf-8"))
            logger.debug(f"Sent: {message}")

            response = client_socket.recv(1024).decode("utf-8")
            logger.info(f"Server response: {response}")

            if response == "Valid user":
                break

    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        client_socket.close()
        logger.info("Connection closed")

if __name__ == "__main__":
    start_tcp_client()
