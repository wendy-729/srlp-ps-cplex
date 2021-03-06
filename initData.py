import numpy as np
def not_empty(s):
    return s and s.strip()
# 读取数据
'''返回资源种类res, 每个活动的工期duration,每个活动的紧后活动 projSuccessor, 
 每个活动的紧后活动projPred, 每个活动所需资源 resource'''
'''紧前活动和紧后活动的编号都是从1开始并未处理为从0开始'''
def initData(file):
    projectData = []
    with open(file, 'r') as f:
        for line in f.readlines():
            temp = line.strip('\n')
            data = temp.split(" ")
            nums = list(filter(not_empty, data))
            nums = [int(x) for x in nums]
            projectData.append(nums)

    # 资源的数量
    res = projectData[0][1]

    # 资源供应量
    provide_res=projectData[1]

    # 每个活动所需的资源
    resource = []
    for i in range(2, len(projectData)):
        resource.append(projectData[i][1:res+1])

    # 活动的数量
    activities = len(projectData) - 2

    # 活动的工期
    duration = []
    for i in range(2, len(projectData)):
        duration.append(projectData[i][0])

    # 每个活动的紧后活动的数量
    nrsu = [0] * activities
    j = 0
    for i in range(2, len(projectData)):
        nrsu[j] = projectData[i][res+1]
        j += 1

    # 每个活动的紧后活动（活动编号从1开始）
    projSuccessor = []
    for i in range(2, activities + 2):
        # print(i)
        temp = projectData[i][res+2:]
        projSuccessor.append(temp)


    # 紧前活动的数量
    nrpr = [0] * activities
    # 紧前活动的最大数量
    max_nrpr = 0
    for i in range(activities):
        for j in range(nrsu[i]):
            temp = projSuccessor[i][j] - 1
            nrpr[temp] = nrpr[temp] + 1
            if max_nrpr < nrpr[temp]:
                max_nrpr = nrpr[temp]

    projPredecessor = np.zeros((activities, max_nrpr), dtype=np.int64)
    # 每个活动的紧前活动 多维数组
    counter = [0] * activities
    for i in range(activities):
        for j in range(nrsu[i]):
            temp = projSuccessor[i][j]-1
            projPredecessor[[temp], counter[temp]] = i+1
            counter[temp] = counter[temp] + 1

    # 将projPredecessor中的0去掉  活动编号都是从1开始的
    projPred = []
    for i in range(1, len(projPredecessor)):
        temp = []
        for j in projPredecessor[i]:
            if j != 0:
                temp.append(j)
        projPred.append(temp)
    projPred.insert(0, [])

    return res, duration, projSuccessor, projPred, resource, activities,provide_res,nrpr
