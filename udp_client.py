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

def start_udp_client():
    host = config['server']['host']
    port = config['server']['port']
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = (host, port)
    logger.info(f"UDP Client sending to {host}:{port}")

    try:
        while True:
            message = input("Enter username and password: ")
            client_socket.sendto(message.encode("utf-8"), server_address)
            logger.debug(f"Sent: {message}")

            data, server = client_socket.recvfrom(1024)
            response = data.decode("utf-8")
            logger.info(f"Server response: {response}")

            if response == "Valid user":
                break
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        client_socket.close()
        logger.info("Connection closed")

if __name__ == "__main__":
    start_udp_client()
