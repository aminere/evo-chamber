class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None
        self.queue = None
        self.size = 0

    def append(self, data):
        new_node = Node(data)
        self.size += 1

        if self.head == None:
            self.head = self.queue = new_node
            return
        
        previousQueue = self.queue
        self.queue = new_node
        previousQueue.next = self.queue

    def delete(self, data):
        if self.head == None:
            return

        if data == self.head.data:
            self.head = self.head.next            
            self.size -= 1
            return

        current_node = self.head
        while current_node.next != None:
            if data == current_node.next.data:
                current_node.next = current_node.next.next
                self.size -= 1
                return
            current_node = current_node.next
        print(f"Data not found in list: {data}")

    def deleteHead(self):
        if self.head == None:
            return

        self.head = self.head.next
        self.size -= 1
