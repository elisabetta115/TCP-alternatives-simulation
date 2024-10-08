from mininet.topo import Topo
from mininet.link import TCLink

class StarTopo(Topo):
    def build(self, num_hosts):
        central_switch = self.addSwitch('s1')
        for i in range(1, num_hosts + 1):
            host = self.addHost(f'h{i}')
            self.addLink(host, central_switch, cls=TCLink, bw=2, loss=2, r2q=10)

class StarTopoWithRouter(Topo):
    def build(self, num_hosts=5):
        
        router = self.addHost(f'h{num_hosts}', ip=f'10.0.{num_hosts}.1/24')

        for i in range(1, num_hosts):
            host = self.addHost(f'h{i}', ip=f'10.0.{i}.1/24')
            self.addLink(host, router, cls=TCLink, bw=2, loss=2, r2q=10)

def configure_network(net, num_hosts):

    router = net.get(f'h{num_hosts}')

    router.cmd('sysctl -w net.ipv4.ip_forward=1')

    for i in range(1, num_hosts):
        host = net.get(f'h{i}')
        router_ip = f'10.0.{i}.254'

        router_interface = f'h{num_hosts}-eth{i-1}'
        router.cmd(f'ifconfig {router_interface} {router_ip} netmask 255.255.255.0')

        host.cmd(f'ip route add default via {router_ip}')

def print_topology(net):

    print("\nLinks:")
    for link in net.links:
        node1, node2 = link.intf1.node, link.intf2.node
        print(f"  {node1.name} <--> {node2.name}")


