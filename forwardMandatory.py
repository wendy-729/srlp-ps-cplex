# 只考虑必须执行活动的正向计算
def forwardManda(duration, su, mandatory, actNo, pred):
    est = [0] * len(duration)
    eft = [0] * len(duration)
    # 第一个活动的紧后活动的est.eft
    for i in su[0]:
        if i in mandatory:
            eft[i] = est[i] + duration[i]
            break
    # 从第二个活动开始计算最早开始时间和最晚开始时间
    for i in range(1, actNo):
        # 计算最早开始时间和最晚开始时间
        for j in pred[i]:  # 活动i的紧前活动
            if j in mandatory:
                if est[j] + duration[j] > est[i]:
                    est[i] = est[j] + duration[j]
        eft[i] = est[i] + duration[i]
    # 虚终止活动的最早开始时间
    for i in mandatory:
        if est[i]+duration[i] > est[actNo-1]:
            est[actNo-1] = est[i]+duration[i]
    return est, eft
