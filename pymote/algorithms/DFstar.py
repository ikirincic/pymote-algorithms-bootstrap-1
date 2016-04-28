from pymote.algorithm import NodeAlgorithm
from pymote.message import Message


class DFT(NodeAlgorithm):
    required_params = ()
    default_params = {'neighborsKey': 'Neighbors'}

    def initializer(self):
        for node in self.network.nodes():
            node.memory[self.neighborsKey] = node.compositeSensor.read()['Neighbors']
            node.status = 'IDLE'
            ini_node = node
        ini_node.status = 'INITIATOR'
        self.network.outbox.insert(0, Message(header=NodeAlgorithm.INI, destination=ini_node))

    def initiator(self, node, message):
        node.memory['unvisitedNodes'] = list(node.memory[self.neighborsKey])
        if node.memory['unvisitedNodes']:
            node.memory['next_node'] = node.memory['unvisitedNodes'].pop()
            node.send(Message(destination=node.memory['next_node'], header='T', data=message.data))
            next_node= node.memory['next_node']
       
            #node.memory['unvisitedNodes'].remove(next_node)
            for other_node in node.memory['unvisitedNodes']:                        
      
                 node.send(Message(destination=other_node, header='Visited', data=message.data))
            node.status = 'VISITED'
        else:
            node.status = 'DONE'
        

    def idle(self, node, message):
        if message.header == 'T':
            node.memory['unvisitedNodes'] = list(node.memory[self.neighborsKey])
            self.firstVisit(node, message)
        elif message.header == 'Visited':
            #node.memory['entry'] = message.source
            node.memory['unvisitedNodes'] = list(node.memory[self.neighborsKey])
            node.memory['unvisitedNodes'].remove(message.source)
            node.status = 'AVAILABLE'
        

    def visited(self, node, message):
        if message.header == 'T':
            #node.memory['unvisitedNodes'].remove(message.source)
            self.visit(node, message)
        elif message.header == 'Return':
            #node.memory['unvisitedNodes'].remove(message.source)
            self.visit(node, message)
        elif message.header == 'Visited':
            node.memory['unvisitedNodes'].remove(message.source)
            #self.visit(node, message)

    def done(self, node, message):
        pass
    
    def available(self, node, message):
         if message.header == 'T':
            self.firstVisit(node, message) 
         elif message.header == 'Visited':
            node.memory['unvisitedNodes'].remove(message.source)
        
    
    def firstVisit(self, node, message):
        try:                
            node.memory['unvisitedNodes'].remove(message.source)
        except ValueError:
            pass 
        node.memory['entry'] = message.source
        if node.memory['unvisitedNodes']:
            node.memory['next_node'] = node.memory['unvisitedNodes'].pop()
            node.send(Message(destination=node.memory['next_node'], header='T', data=message.data))
            node.send(Message(destination=set(node.memory[self.neighborsKey]) - set([node.memory['entry'], node.memory['next_node']]), header='Visited', data=message.data))
            node.status = 'VISITED'
        else:
            node.send(Message(destination=node.memory['entry'], header='Return', data=message.data))
            nodeNeighbors = list(node.memory[self.neighborsKey])
            nodeNeighbors.remove(node.memory['entry'])
            node.send(Message(destination=nodeNeighbors, header='Visited', data=message.data))
            node.status = 'DONE'
        

    def visit(self, node, message):
        if node.memory['unvisitedNodes']:
            node.memory['next_node'] = node.memory['unvisitedNodes'].pop()
            node.send(Message(destination=node.memory['next_node'], header='T', data=message.data))
            next_node = node.memory['next_node']
            #node.memory['unvisitedNodes'].remove(next_node)
            node.status = 'VISITED'
        else:
            if 'entry' in node.memory:
                node.send(Message(destination=node.memory['entry'], header='Return', data=message.data))
            node.status = 'DONE'
        
    STATUS = {
                'INITIATOR': initiator,
                'IDLE': idle,
                'AVAILABLE': available,
                'VISITED': visited,
                'DONE': done
             }
