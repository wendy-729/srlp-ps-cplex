def newProjectData(su, pred, choiceList, actNo, mandatory):
    # print(choiceList)
    new_pred = pred
    new_su = su
    for i in range(1, actNo - 1):
        if i in mandatory:
            flag1 = 0
            # 紧前活动
            jinqian = pred[i]
            for j in jinqian:
                # 如果紧前活动不是必须执行活动
                if j in choiceList:
                    flag1 = 1
                if flag1 == 1:
                    if i not in su[0]:
                        new_su[0].append(i)
                        new_pred[i].append(0)
                        break
                else:
                    continue
            # 紧后活动
            flag2 = 0
            jinhou = su[i]
            for j in jinhou:
                # 紧后活动不是必须执行活动
                if j in choiceList:
                    flag2 = 1
                if flag2 == 1:
                    if actNo - 1 not in jinhou:
                        # new_projRelation[i,new_nrsu[i]+2]=actNo
                        # new_projRelation[i,1]+=1
                        # new_nrsu[i]+=1
                        new_su[i].append(actNo - 1)
                        # new_nrpr[actNo-1]+=1
                        new_pred[actNo - 1].append(i)
                        break
                else:
                    continue
    # print(new_su)
    return new_su, new_pred
'''
如果一个活动的所有紧前活动都是可选活动，则其紧前活动集合添加虚开始活动0；
如果一个活动的所有紧后活动都是可选活动，则其紧前活动集合添加虚终止活动actNo-1
'''
def newProjectData1(su, pred, choiceList, actNo):
    new_pred = pred
    new_su = su
    for i in range(1, actNo):
        # 紧前活动
        jinqian = pred[i]
        count = 0
        for j in jinqian:
            # 如果紧前活动不是必须执行活动
            if j in choiceList:
                count += 1
        # 活动i的所有紧前活动都是不必须执行活动
        if count == len(jinqian):
            if i not in su[0]:
                new_su[0].append(i)
                new_pred[i].append(0)

        # 紧后活动
        flag2 = 0
        jinhou = su[i]
        for j in jinhou:
            # 紧后活动不是必须执行活动
            if j in choiceList:
                flag2 += 1

        if flag2 == len(jinhou):
            if actNo - 1 not in jinhou:
                new_su[i].append(actNo - 1)
                new_pred[actNo - 1].append(i)


    return new_su, new_pred
'''
如果一个活动的所有紧前活动都是可选活动，则其紧前活动集合添加虚开始活动0；
如果一个活动的所有紧后活动都是可选活动，则其紧前活动集合添加虚终止活动actNo-1
'''
def upateRelation(su, pred, actNo, mandatory):
    new_pred = pred
    new_su = su
    for i in range(1, actNo):
        # 紧前活动
        jinqian = pred[i]
        count = 0
        for j in jinqian:
            # 如果紧前活动不是必须执行活动
            if j not in mandatory:
            # if j in choiceList:
                count += 1
        # 活动i的所有紧前活动都是不必须执行活动
        if count == len(jinqian):
            if i not in su[0]:
                new_su[0].append(i)
                new_pred[i].append(0)

        # 紧后活动
        flag2 = 0
        jinhou = su[i]
        for j in jinhou:
            # 紧后活动不是必须执行活动
            if j not in mandatory:
            # if j in choiceList:
                flag2 += 1

        # 所有紧后活动都不是必须执行活动
        if flag2 == len(jinhou):
            if actNo - 1 not in jinhou:
                new_su[i].append(actNo - 1)
                new_pred[actNo - 1].append(i)

    return new_su, new_pred

