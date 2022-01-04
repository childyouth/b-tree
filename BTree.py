from typing import List
import math

class Node:
    def __init__(self):
        self.keys = []
        self.subtrees:List[Node] = []

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

    def merge(self, otherNode:'Node', isMeBigger:bool, middleKey:int):
        middleKey = [middleKey]
        smaller = otherNode if isMeBigger else self
        bigger = self if isMeBigger else otherNode
        self.keys = smaller.keys + middleKey + bigger.keys
        self.subtrees = smaller.subtrees + bigger.subtrees


class BTree:
    def __init__(self, M):
        self.M = M
        self.halfM = math.ceil(M/2) -1
        self.root = Node()
        self.data = dict()
        self.leaf_cnt = dict()

    def search(self, queryKey:int)->(int, (Node, int, List[Node])):
        """
        트리에 queryKey가 있는지 확인하고 없다면 -1을, 있다면 queryKey가 존재하는 노드를 반환

        Node_info의 stack(list[Node]) 는 검색된 마지막 노드를 포함하고 있다.

        Node_info-Node ∈ Node_info-list[Node]

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


    def _inorder_traversal(self, level, target:Node):
        keys = []
        level += 1
        if len(target.subtrees) == 0:
            self.leaf_cnt[level] = self.leaf_cnt.get(level,0) + 1
            return target.keys
        for i in range(len(target.keys)):
            keys += self._inorder_traversal(level,target.subtrees[i])
            keys.append(target.keys[i])
        keys += self._inorder_traversal(level, target.subtrees[len(target.keys)])
        return keys


    def leaf_level_chk(self, target:Node):
        '''
        모든 leaf node의 level을 저장하고 해당 level에 존재하는 node의 개수를 갖는 leaf_cnt(dict) 와 노드에 저장된 모든 key(list) 반환
        :param target:
        :return:
        '''
        self.leaf_cnt = dict()
        return self.leaf_cnt, self._inorder_traversal(0,target)


    def insert(self, newkey):
        '''
        :param newkey:
        :return INTEGER: -1 = key duplicated, 0 = inserted
        '''
        newkey = int(newkey)
        code, (targetNode,idx,stack) = self.search(newkey)
        if code == 0:
            return -1
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


    def find_replacement_key(self, node:Node, idx:int)-> (int, List[Node]):
        # TODO 무조건 작은 key중 가장 큰 key로 가는게 아닌 양쪽 subtree를 모두 비교해 최적노드와 병합하도록 변경 (대체키가 소속된 노드가 가진 key값이 많은 쪽으로)
        '''
        노드의 바꿀 key 보다 작은 key 중 가장 큰 key의 index와 지나간 노드 stack을 반환하는 함수

        정렬된 key set [ k1 , ... , replacement key, target key, ... , kn ]

        Args:
            node:
            idx:

        Returns:

        '''
        stack = []
        stop = False
        targetNode = node
        while not stop:
            if len(targetNode.subtrees) == 0:
                stop = True
            stack.append(targetNode)
            if not stop:
                targetNode = targetNode.subtrees[idx]
            idx = len(targetNode.keys)
        return idx-1, stack

    def check_underflow(self, Node):
        # root 는 절반조건인 underflow의 경우를 무시한다
        if Node == self.root and len(self.root.keys) != 0:
            return False
        elif len(Node.keys) > self.halfM:
            return False
        return True
    def delete(self, delkey):
        delkey = int(delkey)
        code, (targetNode, idx, stack) = self.search(delkey)
        if code == -1:
            return -1
        targetNode = stack.pop()
        # internal node check
        if len(targetNode.subtrees) != 0:
            tmpNode = targetNode
            rplkeyidx, stack2 = self.find_replacement_key(targetNode,idx)
            targetNode = stack2.pop()
            stack += stack2
            stack2 = None
            tmpNode.keys[idx] = targetNode.keys[rplkeyidx]
            tmpNode = None
            idx = rplkeyidx
            targetNode.keys[idx] = delkey
        stop = False
        if not self.check_underflow(targetNode):
            stop = True
        targetNode.keys.pop(idx)
        siblingNode = targetNode

        # 합병/재분배
        while not stop:
            if len(stack) == 0:
                stop = True
                if self.check_underflow(targetNode):
                    self.root = siblingNode
                continue
            parentNode = stack.pop()
            targetNodeidx = parentNode.subtrees.index(targetNode)
            siblingidxs = []
            if targetNodeidx != len(parentNode.subtrees) -1:
                siblingidxs.append(targetNodeidx+1)
            if targetNodeidx != 0:
                siblingidxs.append(targetNodeidx-1)
            siblingKeysizes = list(map(lambda idx: len(parentNode.subtrees[idx].keys), siblingidxs))
            siblingidx = siblingidxs[siblingKeysizes.index(max(siblingKeysizes))]
            siblingNode = parentNode.subtrees[siblingidx]
            isSiblingBigger = bool(siblingidx - targetNodeidx +1)
            middlekeyidx = targetNodeidx if isSiblingBigger else targetNodeidx-1
            middleKey = parentNode.keys[middlekeyidx]
            if max(max(siblingKeysizes),self.halfM) == self.halfM:
                # 합병
                siblingNode.merge(targetNode,isSiblingBigger,middleKey)
                parentNode.keys.remove(middleKey)
                parentNode.subtrees.remove(targetNode)
                targetNode = parentNode
            else:
                # 재분배
                siblingKey = siblingNode.keys.pop(0 if isSiblingBigger else len(siblingNode.keys)-1)
                siblingSubtree = None
                if len(siblingNode.subtrees) != 0:
                    siblingSubtree = siblingNode.subtrees.pop(0 if isSiblingBigger else len(siblingNode.subtrees)-1)
                parentNode.keys[middlekeyidx] = siblingKey
                targetNode.addKey(middleKey,siblingSubtree)
                stop = True



