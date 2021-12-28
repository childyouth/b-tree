

class Node:
    def __init__(self):
        self.keys = []
        self.subtrees = []

    def addKey(self, key, newsubtree=None):
        '''
        :param key:
        :param newsubtree:
        :return:
        '''
        idx = 0
        rightmost = True
        for i in range(len(self.keys)):
            idx = i
            if self.keys[i] > key:
                rightmost = False
                break
        if rightmost:
            idx = len(self.keys)
        self.keys.insert(idx,key)
        if newsubtree is not None:
            self.subtrees.insert(idx+1, newsubtree)

    def split(self, M):
        '''
        현재 노드를 반으로 나누어 키값이 작은쪽을 취하고 오른쪽을 가지는 새로운 노드와 두 노드의 부모키를 반환
        현재 노드는 항상 새로운노드보다 같거나 많은(+1) 키 개수를 갖는다
        :param M:
        :return newkey, newSubTree:

        '''
        newNode = Node()
        half = int(len(self.keys)/2)
        _key = self.keys[half]
        newNode.keys = self.keys[half+1:len(self.keys)]
        newNode.subtrees = self.subtrees[half+1:len(self.subtrees)]
        self.keys = self.keys[0:half]
        self.subtrees = self.subtrees[0:half+1]

        return _key,newNode


class BTree:
    def __init__(self, M):
        self.M = M
        self.root = Node()
        self.data = dict()

    def search(self, queryKey):
        queryKey = int(queryKey)
        targetNode = self.root
        depth = 0
        while targetNode is not None:
            depth += 1
            rightmost = True
            for i in range(len(targetNode.keys)):
                if targetNode.keys[i] == queryKey:
                    return queryKey, depth
                if targetNode.keys[i] > queryKey:
                    if len(targetNode.subtrees) != 0:
                        targetNode = targetNode.subtrees[i]
                        rightmost = False
                        break
                    return -1
            if rightmost:
                if len(targetNode.subtrees) != 0:
                    targetNode = targetNode.subtrees[len(targetNode.keys)]
                    continue
                else:
                    break
        return -1

    def inorder_traversal(self, target:Node):
        keys = []
        if len(target.subtrees) == 0:
            return target.keys
        for i in range(len(target.keys)):
            keys += self.inorder_traversal(target.subtrees[i])
            keys.append(target.keys[i])
        keys += self.inorder_traversal(target.subtrees[len(target.keys)])
        return keys

    def insert(self, newkey):
        '''
        :param newkey:
        :return INTEGER: -1 = key duplicated, 0 = inserted
        '''
        newkey = int(newkey)
        stack = []
        targetNode = self.root
        while len(targetNode.subtrees) != 0:
            stack.append(targetNode)
            rightmost = True
            for i in range(len(targetNode.keys)):
                if targetNode.keys[i] == newkey:
                    return -1
                if targetNode.keys[i] > newkey:
                    targetNode = targetNode.subtrees[i]
                    rightmost = False
                    break
            if rightmost:
                targetNode = targetNode.subtrees[len(targetNode.keys)]

        finish = False
        newSubTree = None
        while not finish:
            targetNode.addKey(newkey, newSubTree)
            if len(targetNode.keys) <= self.M-1:
                finish = True
                continue

            newkey, newSubTree = targetNode.split(self.M)

            if len(stack) > 0:
                targetNode = stack.pop()
            else:
                self.root = Node()
                self.root.keys.append(newkey)
                self.root.subtrees += [targetNode, newSubTree]
                finish = True
        return 0