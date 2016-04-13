from pymote.networkgenerator import NetworkGenerator
from pymote.simulation import Simulation
from pymote.algorithms import DFstar
from pymote.npickle import write_pickle
from pymote.network import Network

def node_network():
	net = Network()
	net.add_node(pos=(300, 300), commRange=80)
	return net

def random_network():
	net_gen = NetworkGenerator(10, commRange=400)
	net = net_gen.generate_random_network()
	return net

def line_network():
	net = Network()
	net.add_node(pos=(100, 100), commRange=150)
	net.add_node(pos=(200, 200), commRange=150)	
	net.add_node(pos=(300, 300), commRange=150)	
	net.add_node(pos=(400, 400), commRange=150)	
	net.add_node(pos=(500, 500), commRange=150)
	return net

def triangle_network():
	net = Network()
	net.add_node(pos=(200, 200), commRange=120)
	net.add_node(pos=(200, 300), commRange=120)
	net.add_node(pos=(250, 250), commRange=120)
	return net


d

def test_network():
	net = node_network()
	net.algorithms = (DFstar, )
        net.nodes()[0].memory['I']= 'information'
	sim = Simulation(net)

	try:
		sim.run()
	except Exception, e:
		write_pickle(net, 'net_exception.npc.gz')
		raise e
	for node in net.nodes():
		
		assert node.status == 'DONE'
		assert len(node.memory['unvisitedNodes']) == 0

if __name__=='__main__':
	test_network()
