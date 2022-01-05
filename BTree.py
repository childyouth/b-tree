from typing import List
import math

class Node:
    def __init__(self):
        self.keys = []
        self.subtrees:List[Node] = []

    def addKey(self, key, newsubtree:'Node'=None, isMeBigger:bool=False):
        '''
        해당 노드의 알맞은 key 순서에 삽입. subtree가 갱신될 필요가 있을때는 subtree또한 알맞은 순서에 삽입

        * 삽입 과정에서는 항상 self보다 큰 값을 넣은 새 노드가 삽입된다
        * 삭제 과정에서는 인접한 두 형제노드 중 최적의 값을 삽입하게 되므로 newsubtree의 위치를 정해줘야 한다
        * newsubtree의 위치를 정해주는 것이 isMeBigger flag이다

        :param key:
        :param newsubtree:
        :param isMeBigger:
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
        # key가 들어갈 위치를 알아도 subtree가 존재하던곳이 왼쪽(작은)인지 오른쪽(큰)인지에 따라 key의 앞에 설지 뒤에 설지 갈림
        if newsubtree is not None:
            if isMeBigger:
                self.subtrees.insert(idx, newsubtree)
            else:
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
        '''
        삭제과정에서 병합되는 노드

        병합되는 형제노드가 큰지 작은지에 따라 더해지는 위치가 달라진다

        Args:
            otherNode:
            isMeBigger:
            middleKey:

        Returns:

        '''
        middleKey = [middleKey]
        smaller = otherNode if isMeBigger else self
        bigger = self if isMeBigger else otherNode
        self.keys = smaller.keys + middleKey + bigger.keys
        self.subtrees = smaller.subtrees + bigger.subtrees


class BTree:
    def __init__(self, M):
        self.M = M
        self.HALF_M = math.ceil(M / 2) - 1
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
        # 추가할 key가 이미 존재하는 경우
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
                # root에서 분기 시 트리 높이 증가
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
                # 인자로 들어오는 idx로 좌측 subtree로 향해야 하기 때문에 먼저 targetNode를 변경
                targetNode = targetNode.subtrees[idx]
            # 선행키를 찾기 위해 가장 큰 subtree로 향한다
            idx = len(targetNode.keys)
        return idx-1, stack

    def check_underflow(self, Node):
        # root 는 절반조건인 underflow의 경우를 무시한다
        if Node == self.root and len(self.root.keys) != 0:
            return False
        elif len(Node.keys) > self.HALF_M:
            return False
        return True

    def delete(self, delkey):
        '''
        삭제대상이 없는경우 -1, 있는경우 해당되는 key를 삭제하고 0을 반환하는 b tree 삭제 연산
        Args:
            delkey:

        Returns:

        '''
        delkey = int(delkey)
        code, (targetNode, idx, stack) = self.search(delkey)
        if code == -1:
            return -1
        targetNode = stack.pop()
        # internal node check
        if len(targetNode.subtrees) != 0:
            tmpNode = targetNode
            # 선행키를 찾는다.
            # key가 존재하는 index는 subtree에서 해당 key보다 작은 subtree의 index와 같기 때문에 key의 index를 넣는다
            rplkeyidx, stack2 = self.find_replacement_key(targetNode,idx)
            targetNode = stack2.pop()
            stack += stack2
            stack2 = None
            # internal node에 존재하던 삭제대상 key를 선행키 값으로 변경한다
            tmpNode.keys[idx] = targetNode.keys[rplkeyidx]
            tmpNode = None
            # leaf node에 위치하게된 삭제대상 key의 index
            idx = rplkeyidx
            targetNode.keys[idx] = delkey
        stop = False
        # 합병/재분배 과정이 필요없이 삭제가 가능한 경우 바로 종료할 수 있도록 한다
        if not self.check_underflow(targetNode):
            stop = True
        targetNode.keys.pop(idx)
        # targetNode가 루트 노드이고 underflow가 발생하게 된다면 트리의 레벨을 줄이면서 root가 sibling을 가르키게 된다.
        # sibling을 None으로 초기화 하는 경우 트리의 시작점을 잃게 되는경우가 존재할 수 있어 targetNode로 초기화한다.
        siblingNode = targetNode

        # 합병/재분배
        while not stop:
            if len(stack) == 0:
                stop = True
                if self.check_underflow(targetNode):
                    self.root = siblingNode
                continue
            parentNode = stack.pop()
            # 부모노드의 subtrees에서 targetNode의 index
            targetNodeidx = parentNode.subtrees.index(targetNode)
            # 부모노드의 subtrees에서 targetNode와 이웃한 형제노드(들)의 index
            siblingidxs = []
            # targetNode가 양끝에 위치하는 경우 형제노드 후보는 한개뿐이다.
            if targetNodeidx != len(parentNode.subtrees) -1:
                siblingidxs.append(targetNodeidx+1)
            if targetNodeidx != 0:
                siblingidxs.append(targetNodeidx-1)
            # 합병/재분배 과정을 선택하기 위해 형제노드들의 key 개수를 구한다
            siblingKeysizes = list(map(lambda idx: len(parentNode.subtrees[idx].keys), siblingidxs))
            # 가장 많은 key를 가진 형제노드의 부모노드->subtrees 에서의 index
            siblingidx = siblingidxs[siblingKeysizes.index(max(siblingKeysizes))]
            siblingNode = parentNode.subtrees[siblingidx]
            # 형제노드가 targetNode보다 큰지 판단하는 boolean. -1 or 1이 나오므로 boolean형 처리를 위해 +1
            isSiblingBigger = bool(siblingidx - targetNodeidx +1)
            # 형제노드와 targetNode를 구분하는 중간키
            middlekeyidx = targetNodeidx if isSiblingBigger else targetNodeidx-1
            middleKey = parentNode.keys[middlekeyidx]
            if max(max(siblingKeysizes), self.HALF_M) == self.HALF_M:
                # 합병
                # 모든 형제노드가 underflow 위험이 있는 경우 '합병'
                siblingNode.merge(targetNode,isSiblingBigger,middleKey)
                parentNode.keys.remove(middleKey)
                parentNode.subtrees.remove(targetNode)
                # 합병은 상위노드로 삭제전파된다
                targetNode = parentNode
            else:
                # 재분배
                # 키를 더 많이 보유한 형제노드에게서 key를 끌어오는 '재분배'
                siblingKey = siblingNode.keys.pop(0 if isSiblingBigger else len(siblingNode.keys)-1)
                siblingSubtree = None
                if len(siblingNode.subtrees) != 0:
                    siblingSubtree = siblingNode.subtrees.pop(0 if isSiblingBigger else len(siblingNode.subtrees)-1)
                parentNode.keys[middlekeyidx] = siblingKey
                # addKey에서 인자로 받는 boolean은 addKey 대상 노드가 더 큰가 이므로 not을 붙인다
                targetNode.addKey(middleKey,siblingSubtree,not isSiblingBigger)
                stop = True
        return 0


