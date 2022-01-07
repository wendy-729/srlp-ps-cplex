# 计算所有活动的最早开始时间和最晚开始时间   正向计算
def forwardPass(duration, su,mandatory):
    # 最早开始时间和最晚结束时间
    activities = len(duration)
    est = [0] * len(duration)
    eft = [0] * len(duration)
    # 第一个活动的紧后活动的est,eft
    for i in su[0]:
        eft[i] = est[i] + duration[i]
    # print(mandatory[2:])
    # 从第二个活动开始计算最早开始时间和最晚开始时间
    for i in range(1, activities):
        for j in su[i]:
            if eft[i] > est[j]:
                est[j] = eft[i]
                eft[j] = est[j] + duration[j]
    return est, eft
