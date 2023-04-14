class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None
        self.queue = None

    def append(self, data):
        new_node = Node(data)

        if self.head is None:
            self.head = self.queue = new_node
            return
        
        previousQueue = self.queue
        self.queue = new_node
        previousQueue.next = self.queue

    def delete(self, data):
        if self.head is None:
            return

        if data == self.head.data:
            self.head = self.head.next            
            return

        current_node = self.head
        while current_node.next is not None:
            if data == current_node.next.data:
                current_node.next = current_node.next.next
                return
            current_node = current_node.next

    def deleteHead(self):
        if self.head is None:
            return

        self.head = self.head.next 
