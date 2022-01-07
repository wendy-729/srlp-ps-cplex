def read_gap(file):
    data=[]
    with open(file, 'r') as f:
        for line in f.readlines():
            # temp = line.split()
            temp = line.strip('\n').split("\t")
            # print(temp)
            data.append(int(temp[1]))
            # print(data)
            # nums = list(filter(not_empty, data))
            # nums = [int(x) for x in nums]
            # data.append(nums)
    # print('原始数据', data)
    return data