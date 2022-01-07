# 活动从0开始编号
def initDuration(file):
    data=[]
    with open(file, 'r') as f:
        for line in f.readlines():
            # temp=line.split()
            temp = line.strip('\n').split("\t")
            temp = [int(x) for x in temp]
            data.append(temp)
    # print('原始数据', data)
    return data