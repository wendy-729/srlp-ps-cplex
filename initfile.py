# 活动从0开始编号
def initfile(file):
    data=[]
    with open(file, 'r') as f:
        for line in f.readlines():
            # temp = line.split()
            temp=line.strip('\n').split(",")
            # 活动编号从0开始
            data = [int(x)-1 for x in temp]
            # print(data)
            # nums = list(filter(not_empty, data))
            # nums = [int(x) for x in nums]
            # data.append(nums)
    # print('原始数据', data)
    return data

def initfile1(file):
    data=[]
    with open(file, 'r') as f:
        for line in f.readlines():
            # temp = line.split()
            temp=line.strip('\n').split(",")
            # 活动编号从0开始
            data = [int(x) for x in temp]
            # print(data)
            # nums = list(filter(not_empty, data))
            # nums = [int(x) for x in nums]
            # data.append(nums)
    # print('原始数据', data)
    return data