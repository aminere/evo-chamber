class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None

    def append(self, data):
        new_node = Node(data)

        if self.head is None:
            self.head = new_node
            return

        current_node = self.head
        while current_node.next is not None:
            current_node = current_node.next

        current_node.next = new_node    

    def delete(self, data):
        if self.head is None:
            return

        if data == self.head.data:
            self.head = self.head.next            
            return

        index = 1
        current_node = self.head
        while current_node.next is not None:
            if data == current_node.next.data:
                current_node.next = current_node.next.next
                index += 1
                return
            current_node = current_node.next   

    def deleteHead(self):
        if self.head is None:
            return

        self.head = self.head.next 
