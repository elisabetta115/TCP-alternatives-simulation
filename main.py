from mininet.net import Mininet
from mininet.link import TCLink
from mininet.log import setLogLevel, info
from topologies import *
from protocols import *
from utils import *


def run_file_transfer_test(net, transport, num_hosts):
    sender = net.get('h1')  
    receivers = [net.get(f'h{i}') for i in range(2, num_hosts + 1)] 
        
    num = 2
    elapsed_time = 0
    elapsed_time_total = 0

    checksums_match = True

    info(f'Starting test on {transport}\n')
    
    if transport == 'TCP':
        initialization_results = initialize_tcp_sender(sender)
        checksum_sender = initialization_results[0]        
        for receiver in receivers:
            results = run_tcp_packet_exchange(receiver, sender.IP(), num)
        
            elapsed_time = results[0]
            checksum_receiver = results[1]

            num = num+1
            elapsed_time_total += elapsed_time 

            if checksum_sender != checksum_receiver:
                checksums_match = False
        close_tcp_sender(sender)

    elif transport == 'SCTP':
        initialization_results = initialize_sctp_sender(sender)
        checksum_sender = initialization_results[0]
        test_file = initialization_results[1]
        for receiver in receivers:
            results = run_sctp_packet_exchange(test_file, receiver, sender.IP(), num)
        
            elapsed_time = results[0]
            checksum_receiver = results[1]

            num = num+1
            elapsed_time_total += elapsed_time 

            if checksum_sender != checksum_receiver:
                checksums_match = False
        close_sctp_sender(sender)
        
    elif transport == 'DCCP':
        initialization_results = initialize_dccp_sender(sender)
        checksum_sender = initialization_results[0]
        test_file = initialization_results[1]
        for receiver in receivers:
            results = run_dccp_packet_exchange(test_file, receiver, sender.IP(), num)
        
            elapsed_time = results[0]
            checksum_receiver = results[1]

            num = num+1
            elapsed_time_total += elapsed_time 

            if checksum_sender != checksum_receiver:
                checksums_match = False
        close_dccp_sender(sender)

    elif transport == 'QUIC':
        initialization_results = initialize_quic_sender(sender)
        checksum_sender = initialization_results[0]
        test_file = initialization_results[1]
        for receiver in receivers:
            results = run_quic_packet_exchange(test_file, receiver, sender.IP(), num)
        
            elapsed_time = results[0]
            checksum_receiver = results[1]

            num = num+1
            elapsed_time_total += elapsed_time 

            if checksum_sender != checksum_receiver:
                checksums_match = False
        close_quic_sender(sender)
        
    else:
        info(f'Unsupported transport protocol: {transport}\n')
        return

    if checksums_match:
        info(f'*** Checksums over {transport} match. Data integrity verified.\n')
    else:
        info(f'*** Checksums over {transport} do not match! Data corruption detected.\n')

    info(f'*** Transfer over {transport} completed for all receivers in {elapsed_time_total:.2f} seconds\n\n')

    sender.cmd('rm -rf /tmp/www')

def main():
    setLogLevel('info')
    load_kernel_modules()
    
    topo_choice = input("Which topology would you like to use? \n(1)Star topology with switch \n(2) Large star with router \n: ")
    if topo_choice != '2' and topo_choice != '1':
        info("Invalid topology choice. Exiting.\n")
        return

    try:
        num_hosts = int(input("Enter the number of hosts (Remember: in the topolgy with the star, add +1 for the router): "))
        if num_hosts<= 1 and topo_choice == '1':
            raise ValueError("Number of hosts must be greater than 1.")
        elif num_hosts<=2 and topo_choice == '2':
            raise ValueError("Number of hosts must be greater than 2.")
    except ValueError as e:
        info(f"Invalid input for number of hosts.\n")
        return

    if topo_choice == '1':
        topo = StarTopo(num_hosts=num_hosts)
        net = Mininet(topo=topo, link=TCLink)
        net.start()
        print_topology(net)
    elif topo_choice == '2':
        topo = StarTopoWithRouter(num_hosts=num_hosts)
        net = Mininet(topo=topo, link=TCLink)
        net.start()
        configure_network(net, num_hosts)
        print_topology(net)

    protocols = ['TCP', 'SCTP', 'DCCP', 'QUIC']
    
    for proto in protocols:
        run_file_transfer_test(net, proto, num_hosts)    
    net.stop()

if __name__ == '__main__':
    main()

