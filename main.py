import csv
import os
from BTree import BTree


DATASET_ROOT = "./dataset/"
M_way = 50
# nodes = [[5,2],[2,7],[1,9],[4,8],[8,22],[11,35],[3,55]]

keys = []

if __name__ == "__main__":
    runtype = input("1. insertion\n2.deletion\n3.quit\n입력 : ")
    print("데이터셋 목록 ",os.listdir(DATASET_ROOT))
    dataset = os.path.join(DATASET_ROOT,input("데이터셋 파일 명 : "))
    reader = csv.reader(open(dataset, newline=''), delimiter='\t')
    btree = BTree(M_way)

    for k,v in reader:
        keys.append(k)
        if btree.insert(k) == 0:
            btree.data[k] = v
    # print(btree.inorder_traversal(btree.root))
    for k in keys:
        print(btree.search(k))
    print(btree.search(111))