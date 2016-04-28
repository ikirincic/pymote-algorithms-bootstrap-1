from pymote.algorithm import NodeAlgorithm
from pymote.message import Message
from random import seed, randint

class Saturation(NodeAlgorithm):
    required_params = {}
    default_params = {'neighborsKey': 'Neighbors'}

    def initializer(self):
    	seed()
        for node in self.network.nodes():
            node.memory[self.neighborsKey] = node.compositeSensor.read()['Neighbors']
            node.status = 'AVAILABLE'
            node.memory['value'] = randint(0, 100)	    
	    
        ini_node = self.network.nodes()[0]
        self.network.outbox.insert(0, Message(header=NodeAlgorithm.INI, destination=ini_node))

    def available(self, node, message):
		nodeNeighbors = list(node.memory[self.neighborsKey])
		node.memory['neighbors'] = list(node.memory[self.neighborsKey])
		node.memory['counter'] = len(nodeNeighbors)
		node.memory['total'] = node.memory['value']
		node.memory['parent'] = 'ini'
		if message.header == NodeAlgorithm.INI:
			for i in range(len(nodeNeighbors)):
				node.send(Message(destination=nodeNeighbors[i], header='Activate', data={'v': node.memory['value']}))
			node.status = 'ACTIVE'
			
		if message.header == 'Activate':
			node.memory['parent'] = message.source
			nodeNeighbors.remove(message.source)
			for i in range(len(nodeNeighbors)):
				node.send(Message(destination=nodeNeighbors[i], header='Activate', data={'v': node.memory['value']}))
			node.memory['neighbors'] = list(node.memory[self.neighborsKey])
			if len(node.memory['neighbors']) == 1:
				node.memory['parent'] = node.memory['neighbors'].pop()
				node.send(Message(destination=node.memory['parent'], header='M', data={'v': node.memory['value']}))
				node.status = 'PROCESSING'
			else:
				node.status = 'ACTIVE'

    def active(self, node, message):
		tmp_value = message.data['v']
		if node.memory['parent'] != 'ini':
			if message.header == 'M':
				node.memory['counter'] = node.memory['counter'] - 1
				node.memory['total'] += tmp_value 
				if node.memory['counter'] == 1:
					node.memory['average'] = node.memory['total'] / ( len(node.memory['neighbors']) + 1 )
					node.send(Message(destination=node.memory['parent'], header='M', data={'v': node.memory['average']}))
					node.status = 'PROCESSING'

			
		else:
			if message.header == 'M':
				node.memory['counter'] = node.memory['counter'] - 1
				node.memory['total'] += tmp_value 
				if node.memory['counter'] == 0:
					node.memory['average'] = node.memory['total'] / ( len(node.memory['neighbors']) + 1 )
					nodeNeighbors = list(node.memory[self.neighborsKey])
					for i in range(len(nodeNeighbors)):
						node.send(Message(destination=nodeNeighbors[i], header='M', data={'v': node.memory['average']}))
					node.status = 'DONE'



    def processing(self, node, message):
		if message.header == 'M':
			nodeNeighbors = list(node.memory[self.neighborsKey])
			nodeNeighbors.remove(message.source)
			node.memory['average'] = message.data['v']
			for i in range(len(nodeNeighbors)):
				node.send(Message(destination=nodeNeighbors[i], header='M', data={'v': node.memory['average']}))
			node.status = 'DONE'
			


    STATUS = {
                'AVAILABLE': available,
                'ACTIVE': active,
                'PROCESSING': processing
             }
