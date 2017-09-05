#!/usr/bin/python

"""
Test network creating script:

Test bandwidth (using iperf) on linear networks of varying size,
 user datapaths(kernel is an option too).

Test bandwith etc with DITG too, because iperf isn't that good.

We construct a network of 5 hosts and 4 switches, connected as follows:

       h1
       |
h2 <-> s1 <-> s2 <-> h3
       |   X   |
       s3      s4
       |       |
       h4      h5

In addition to testing the bandwidth across varying numbers
of switches, this example demonstrates:

- creating a custom topology, MyMeshTopo
- using the ping() and iperf() tests from Mininet()
- testing both the kernel and user switches
- enabled Spanning Tree for the working mesh
- starting the standard minined CLI for additional testing

"""

from mininet.net import Mininet
from mininet.node import UserSwitch, OVSKernelSwitch, RemoteController
from mininet.topo import Topo
from mininet.log import lg
from mininet.util import irange, quietRun
from mininet.link import TCLink
from functools import partial
from mininet.cli import CLI

import sys
flush = sys.stdout.flush

class MyMeshTopo( Topo ):
    """Topology for a mesh of N hosts and N-1 switches."""

    def __init__( self, N, **params ):

        # Initialize topology
        Topo.__init__( self, **params )

        # Create switches and hosts
        hosts = [ self.addHost( 'h%s' % h )
                  for h in irange( 1, N ) ]
        switches = [ self.addSwitch( 's%s' % s )
                     for s in irange( 1, N - 1 ) ]

        # Wire up switches
#        last = None
#        for switch in switches:
#            if last:
#                self.addLink( last, switch )
#            last = switch

        self.addLink(switches[0], switches[1])
        self.addLink(switches[0], switches[2])
        self.addLink(switches[1], switches[3])

       #self.addController


        # Wire up hosts
        self.addLink( hosts[ 0 ], switches[ 0 ] )
        for host, switch in zip( hosts[ 1: ], switches ):
            self.addLink( host, switch )


def BandwidthTest( lengths ):

    """Check bandwidth at various lengths along a switch chain."""

    results = {}
    switchCount = max( lengths )
    hostCount = switchCount + 1

    switches = { 'reference user': UserSwitch,
                 'Open vSwitch kernel': OVSKernelSwitch }

    # UserSwitch is horribly slow with recent kernels.
    # We can reinstate it once its performance is fixed
    del switches[ 'reference user' ]

    topo = MyMeshTopo( hostCount )

    # Select TCP Reno
#    output = quietRun( 'sysctl -w net.ipv4.tcp_congestion_control=reno' )
#    assert 'reno' in output

    for datapath in switches.keys():
        print "*** testing", datapath, "datapath"
        Switch = switches[ datapath ]
        results[ datapath ] = []
        link = partial( TCLink, delay='1ms' )
        net = Mininet( topo=topo, switch=Switch,
                       controller=RemoteController, waitConnected=True,
                       link=link )

        net.addController('c1', controller=RemoteController, ip='127.0.0.1', port=6633)
        net.start()

        print "*** testing basic connectivity"
        for n in lengths:
            net.ping( [ net.hosts[ 0 ], net.hosts[ n ] ] )
        print "*** testing bandwidth"
        for n in lengths:
            src, dst = net.hosts[ 0 ], net.hosts[ n ]
            # Try to prime the pump to reduce PACKET_INs during test
            # since the reference controller is reactive
            src.cmd( 'telnet', dst.IP(), '5001' )
            print "testing", src.name, "<->", dst.name,
            bandwidth = net.iperf( [ src, dst ], seconds=10 )
            print bandwidth
            flush()
            results[ datapath ] += [ ( n, bandwidth ) ]
        #net.stop()

    for datapath in switches.keys():
        print
        print "*** Network results for", datapath, "datapath:"
        print
        result = results[ datapath ]
        print "SwitchCount\tiperf Results"
        for switchCount, bandwidth in result:
            print switchCount, '\t\t',
            print bandwidth[ 0 ], 'server, ', bandwidth[ 1 ], 'client'
        print
    print

    print '*** Running CLI\n'
    CLI( net )
    
    print 'stopping the network'
    net.stop()

if __name__ == '__main__':
    lg.setLogLevel( 'info' )
    sizes = [ 1, 4 ] #TODO make this more simple maybe
    print "*** Running BandwidthTest", sizes
    BandwidthTest( sizes  )
