import csv
import os
from BTree import BTree
from tqdm import tqdm

# 데이터셋이 저장된 폴더
DATASET_ROOT = "./dataset/"
# B-Tree의 way 개수
M_way = 41
# nodes = [[5,2],[2,7],[1,9],[4,8],[8,22],[11,35],[3,55]]


def file_select(fileroot):
    '''
    데이터셋 폴더에서 파일을 index로 선택하도록 하는 함수
    :param fileroot:
    :return:
    '''
    try:
        print()
        DATASET_NAMES = os.listdir(fileroot)
        print("데이터셋 목록 ", list(zip(range(len(DATASET_NAMES)), DATASET_NAMES)))
        idx = int(input("데이터셋 파일 INDEX : "))
        TARGET_PATH = os.path.join(fileroot, DATASET_NAMES[idx])
    except:
        print("파일을 읽을 수 없습니다")
        return -1,-1,-1
    return DATASET_NAMES, idx, TARGET_PATH


if __name__ == "__main__":
    btree = BTree(M_way)
    # 기능 선택 변수
    runtype = 0
    keys = []

    while runtype != 3:
        try:
            print("\n==== 실행 기능 선택")
            print("\n삽입 연속 수행 시 트리초기화")
            runtype = int(input("1. insertion\n2. deletion\n3. quit\n입력 : "))
            if runtype == 3:
                break
        except:
            continue
        print("\n==== 타겟 파일 선택")
        DATASET_NAMES, idx, TARGET_PATH = file_select(DATASET_ROOT)
        if idx == -1:
            continue
        # 삽입 기능은 비교파일이 삽입파일
        COMPARE_PATH = TARGET_PATH
        reader = csv.reader(open(TARGET_PATH, newline=''), delimiter='\t')

        # 수행 시작
        print("수행 시작")
        if runtype == 1:
            # 삽입
            # 삽입 기능 수행 시 B-Tree 초기화 ( 두 개의 파일을 연속해서 입력 불가능 )
            btree = BTree(M_way)
            for k,v in tqdm(reader):
                # 삽입된 Key를 순서대로 저장
                keys.append(k)
                if btree.insert(k) == 0:
                    # B-Tree에 삽입이 성공한 경우 ( 중복 된 Key 입력 시 -1 )
                    btree.data[int(k)] = v
        elif runtype == 2:
            # 삭제
            # 삭제기능 수행 후 비교할 파일 선택
            print("\n==== 삭제 후 비교할 파일 선택")
            _, _, COMPARE_PATH = file_select(DATASET_ROOT)
        else:
            print("실행옵션이 잘못되었습니다")
            continue

        # 삽입, 삭제 후 기능이상을 확인하기 위해 검색, 저장, 비교
        # 검색, 저장
        print("\n검색...")
        SAVE_PATH = os.path.join(DATASET_ROOT,"runtype_"+str(runtype)+".csv")
        savefile = open(SAVE_PATH,'w',encoding='utf8',newline='')
        writer = csv.writer(savefile, delimiter='\t')
        for k in tqdm(keys):
            v = btree.search(k)
            writer.writerow([k,"N/A" if v == -1 else btree.data[v[0]]])
        savefile.close()
        # B-Tree의 모든 leaf node들의 level을 확인
        # leaf_cnt(dict) 의 key가 하나 이상일 경우 잘못되었음을 확인 가능
        leaf_cnt, total_keys = btree.leaf_level_chk(btree.root)
        print("\n트리의 leaf node level ↓" )
        print(leaf_cnt)
        print()

        # 비교
        print("비교...")
        incorrect_set = []
        print("저장된 파일: "+SAVE_PATH)
        print("비교할 파일: "+COMPARE_PATH)
        savedfilereader = csv.reader(open(SAVE_PATH, newline=''),delimiter='\t')
        comparefilereader = csv.reader(open(COMPARE_PATH, newline=''),delimiter='\t')
        for (k1,v1), (k2,v2) in tqdm(zip(savedfilereader,comparefilereader)):
            incorrect = False
            if k1 != k2:
                incorrect = True
            elif v1 != v2:
                incorrect = True
            if incorrect:
                incorrect_set.append([(k1,v1),(k2,v2)])
        compareresult = open(os.path.join(DATASET_ROOT,"COMPARE_RESULT.txt"),'w',encoding='utf8')
        for l in incorrect_set:
            compareresult.write(str(l)+"\n")
        compareresult.flush()
        compareresult.close()
        print("틀린 개수 : " + str(len(incorrect_set)))