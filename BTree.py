from typing import List

class Node:
    def __init__(self):
        self.keys = []
        self.subtrees = []

    def addKey(self, key, newsubtree=None):
        '''
        해당 노드의 알맞은 key 순서에 삽입. subtree가 갱신될 필요가 있을때는 subtree또한 알맞은 순서에 삽입
        :param key:
        :param newsubtree:
        :return:
        '''
        idx = 0
        # 가장 큰 값으로 들어간다면 idx를 반복문 밖에서 변경해야한다
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
        self.leaf_cnt = dict()
    def search(self, queryKey:int)->(int, (Node, int, List[Node])):
        """
        트리에 queryKey가 있는지 확인하고 없다면 -1을, 있다면 queryKey가 존재하는 노드를 반환

        :param queryKey: 검색대상 key
        :return :
            return_code(int): 트리에서 queryKey가 검색이 안되는 경우 -1, 검색 된 경우 0
            Node_info(Node,int,list[Node]): return_code가 -1인 경우 (queryKey가 들어갈 후보 노드, 노드에 key를 삽입할 index, 노드 검색 stack),
            트리에 queryKey가 존재한다면 (존재하는 노드, 노드에서 key의 index, 노드 검색 stack)
        """
        queryKey = int(queryKey)
        targetNode = self.root
        stack = []
        stop = False
        while not stop:
            if len(targetNode.subtrees) == 0:
                stop = True
            stack.append(targetNode)
            rightmost = True
            for i in range(len(targetNode.keys)):
                if targetNode.keys[i] == queryKey:
                    return 0,(targetNode, i, stack)
                if targetNode.keys[i] > queryKey:
                    if not stop:
                        targetNode = targetNode.subtrees[i]
                        rightmost = False
                        break
                    return -1,(targetNode, i, stack)
            if rightmost:
                if not stop:
                    targetNode = targetNode.subtrees[len(targetNode.keys)]
                continue
        return -1, (targetNode, len(targetNode.keys), stack)


    def inorder_traversal(self, level, target:Node):
        keys = []
        level += 1
        if len(target.subtrees) == 0:
            self.leaf_cnt[level] = self.leaf_cnt.get(level,0) + 1
            return target.keys
        for i in range(len(target.keys)):
            keys += self.inorder_traversal(level,target.subtrees[i])
            keys.append(target.keys[i])
        keys += self.inorder_traversal(level, target.subtrees[len(target.keys)])
        return keys


    def leaf_level_chk(self, target:Node):
        '''
        모든 leaf node의 level을 저장하고 해당 level에 존재하는 node의 개수를 갖는 leaf_cnt(dict) 와 노드에 저장된 모든 key(list) 반환
        :param target:
        :return:
        '''
        self.leaf_cnt = dict()
        return self.leaf_cnt, self.inorder_traversal(0,target)


    def insert(self, newkey):
        '''
        :param newkey:
        :return INTEGER: -1 = key duplicated, 0 = inserted
        '''
        newkey = int(newkey)
        code, (targetNode,idx,stack) = self.search(newkey)
        targetNode = stack.pop()
        finish = False
        newSubTree = None
        while not finish:
            targetNode.addKey(newkey, newSubTree)
            # overflow check
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


    def delete(self, delkey):
        delkey = int(delkey)