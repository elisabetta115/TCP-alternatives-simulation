import time
from mininet.log import info

def initialize_sender(sender):
    test_file = '/tmp/www/testfile'
    sender.cmd('mkdir -p /tmp/www')
    sender.cmd(f'dd if=/dev/urandom of={test_file} bs=1K count=10')
    
    checksum_sender = sender.cmd("md5sum /tmp/www/testfile | awk '{print $1}'").strip()
    return (checksum_sender, test_file)

def close_sender(sender):
    sender.cmd('rm -rf /tmp/www')    
    return

def initialize_tcp_sender(sender):
    initialization_results = initialize_sender(sender)
    server_log = f'logs/http_server.log'
    sender.cmd(f'cd /tmp/www && python3 -m http.server 8080 > {server_log} 2>&1 &')
    time.sleep(1)

    return initialization_results


def close_tcp_sender(sender):
    sender.cmd('pkill -f http.server')
    close_sender(sender)
    return

def initialize_sctp_sender(sender):
    initialization_results = initialize_sender(sender)
    server_log = f'logs/socat_server_DCCP.log'
    sender.cmd(f'socat -d -d -x -v -u SCTP-LISTEN:8080,fork,reuseaddr - > {server_log} 2>&1 &')
    time.sleep(1)

    return initialization_results

def close_sctp_sender(sender):
    close_sender(sender)    
    return

def initialize_dccp_sender(sender):
    initialization_results = initialize_sender(sender)
    server_log = f'logs/socat_server_DCCP.log'
    sender.cmd(f'socat -d -d -x -v -u DCCP-LISTEN:8081,fork,reuseaddr - > {server_log} 2>&1 &')

    return initialization_results

def close_dccp_sender(sender):
    sender.cmd('pkill socat >/dev/null 2>&1')
    close_sender(sender)
    return

def initialize_quic_sender(sender):
    initialization_results = initialize_sender(sender)
    caddyfile_content = f"""     
        https://{sender.IP()}:443 {{
            root * /tmp/www
            file_server
            tls internal
            bind {sender.IP()}
        }}
        """

    caddyfile_path = "/tmp/Caddyfile"
    with open(caddyfile_path, "w") as f:
        f.write(caddyfile_content)
        
    sender.cmd(f'cp {caddyfile_path} /tmp/Caddyfile')

    sender.cmd('caddy run --config /tmp/Caddyfile > logs/caddy.log 2>&1 &')

    time.sleep(1)

    return initialization_results

def close_quic_sender(sender):
    sender.cmd('pkill caddy')
    sender.cmd('rm -rf /tmp/Caddyfile')
    close_sender(sender)
    return


def run_tcp_packet_exchange(receiver, senderIP, num):

    downloaded_file = f'/tmp/downloaded_testfile_{num}'
    
    start_time = time.time()
    receiver.cmd(f'curl http://{senderIP}:8080/testfile -o {downloaded_file}')
    end_time = time.time()
    
    checksum_receiver = receiver.cmd(f"md5sum {downloaded_file} | awk '{{print $1}}'").strip()

    receiver.cmd(f'rm -f {downloaded_file}')
    
    return (end_time - start_time, checksum_receiver, checksum_receiver)

def run_sctp_packet_exchange(test_file, receiver, senderIP, num):

    client_log = f'logs/socat_client_DCCP_{num}.log'

    start_time = time.time()
    receiver.cmd(f'socat -d -d -x -v -u FILE:{test_file} SCTP:{senderIP}:8080 > {client_log} 2>&1')
    end_time = time.time()
    

    checksum_receiver = receiver.cmd(f"md5sum {test_file} | awk '{{print $1}}'").strip()

    receiver.cmd('pkill socat')

    return (end_time - start_time, checksum_receiver, checksum_receiver)

def run_dccp_packet_exchange(test_file, receiver, senderIP, num):
    
    client_log = f'logs/socat_client_DCCP_{num}.log'
    
    time.sleep(1)
    start_time = time.time()
    
    receiver.cmd(f'socat -d -d -x -v -u FILE:{test_file} DCCP:{senderIP}:8081 > {client_log} 2>&1')
    end_time = time.time()

    checksum_receiver = receiver.cmd(f'md5sum {test_file}').split()[0]
    receiver.cmd('pkill socat')
    
    return (end_time - start_time, checksum_receiver, checksum_receiver)


def run_quic_packet_exchange(test_file, receiver, senderIP, checksum_sender):

    download_path = "/tmp/downloaded_testfile"
    
    start_time = time.time()
    receiver.cmd(f'curl -k -v -4 --http3 https://{senderIP}:443/testfile -o {download_path} > logs/curl.log 2>&1')
    end_time = time.time()

    checksum_receiver = receiver.cmd(f'md5sum {download_path}').split()[0]

    return (end_time - start_time, checksum_receiver, checksum_receiver)
