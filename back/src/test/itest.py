import socket
import ssl


def check_connection(host, port=443, timeout=100 ):
    try:
        # ایجاد سوکت TCP
        sock = socket.create_connection((host, port), timeout=timeout)
        # بستن سوکت
        sock.close()
        return True, f"Connection to {host}:{port} successful."
    except socket.timeout:
        return False, f"Connection timeout to {host}:{port}."
    except socket.error as e:
        return False, f"Socket error: {e}"
    except Exception as e:
        return False, f"Unexpected error: {e}"

# تست اتصال
result, msg = check_connection("api.telegram.org", 443)
print(msg)