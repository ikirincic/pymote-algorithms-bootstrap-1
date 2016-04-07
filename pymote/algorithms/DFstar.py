from pymote.algorithm import NodeAlgorithm
from pymote.message import Message


class DFT(NodeAlgorithm):
    # algorithm input
    required_params = {'informationKey', }
    # values that are exposed to other algorithms
    default_params = {'neighborsKey': 'Neighbors'}

    def initializer(self):
        for node in self.network.nodes():
            node.memory[self.neighborsKey] = node.compositeSensor.read()['Neighbors']
            node.status = 'IDLE'
            if self.informationKey in node.memory:
                ini_node = node
        # if multiple initiators are specified only the last one is initialized
        ini_node.status = 'INITIATOR'
        self.network.outbox.insert(0, Message(header=NodeAlgorithm.INI,
destination=ini_node))

    def initiator(self, node, message):
        node.memory['unvisitedNodes'] = list(node.memory[self.neighborsKey])
        if node.memory['unvisitedNodes']:
            next_node = node.memory['unvisitedNodes'][0]
            node.send(Message(destination=next_node, header='T', data=message.data))
       ##prvome ??alji T
            node.memory['unvisitedNodes'].remove(next_node)
            for other_node in node.memory['unvisitedNodes']:                        
       ##svima drugima Visited
                 node.send(Message(destination=other_node, header='Visited',
data=message.data))
            node.status = 'VISITED'
        

    def idle(self, node, message):
        if message.header == 'T':
            node.memory['entry'] = message.source
            node.memory['unvisitedNodes'] = list(node.memory[self.neighborsKey])
            self.firstVisit(node, message)
        elif message.header == 'Visited':
            node.status = 'AVAILABLE'
        

    def visited(self, node, message):
        if message.header == 'T':
            node.memory['unvisitedNodes'].remove(message.source)
            self.visit(node, message)
        elif message.header == 'Return':
            node.memory['unvisitedNodes'].remove(message.source)
            self.visit(node, message)
        elif message.header == 'Visited':
            node.memory['unvisitedNodes'].remove(message.source)
            self.visit(node, message)

    def done(self, node, message):
        pass
    
    def available(self, node, message):
         if message.header == 'T':
            self.firstVisit(node, message) 
         elif message.header == 'Visited':
            node.memory['unvisitedNodes'].remove(message.source)
         
    
    def firstVisit(self, node, message):
        
        node.memory['entry'] = message.source
        node.memory['unvisitedNodes'] = list(node.memory[self.neighborsKey])
        node.memory['unvisitedNodes'].remove(message.source)
        if node.memory['unvisitedNodes']:
            next_node = node.memory['unvisitedNodes'][0]
            node.send(Message(destination=next_node, header='T', data=message.data))
            
            node.memory['unvisitedNodes'].remove(next_node)
            for other_node in node.memory['unvisitedNodes']:
                 node.send(Message(destination=other_node, header='Visited',
data=message.data))
            node.status = 'VISITED'
        else:
            if 'entry' in node.memory:
                node.send(Message(destination=node.memory['entry'], header='Return',
data=message.data))
            node.status = 'DONE'
        

    def visit(self, node, message):
        if node.memory['unvisitedNodes']:
            next_node = node.memory['unvisitedNodes'][0]
            node.send(Message(destination=next_node, header='T', data=message.data))
            node.status = 'VISITED'
        else:
            if 'entry' in node.memory:
                node.send(Message(destination=node.memory['entry'], header='Return',
data=message.data))
            node.status = 'DONE'

    STATUS = {
                'INITIATOR': initiator,
                'IDLE': idle,
                'AVAILABLE': available,
                'VISITED': visited,
                'DONE': done
             }
