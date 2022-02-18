# 郑淋文
# 时间: 2022/1/8 10:21
import numpy as np
def caculate_objective(nscen, scenario_vl, scenario_schedule,resNo,deadline,req,scenario_duration,c):
    all_obj = 0
    for i in range(nscen):
        obj = 0
        vl = scenario_vl[i]
        # print(vl)
        schedule = scenario_schedule[i]
        duration = scenario_duration[i]
        # print(schedule)
        u = np.zeros((resNo, deadline+1))

        for act in vl:
            for k in range(resNo):
                # print(schedule[act])
                # print(schedule[act] + duration[act])
                # print('-------------------')
                for t in range(schedule[act], schedule[act] + duration[act]):
                    u[k][t] += req[act][k]

        # 计算目标函数值
        for k in range(resNo):
            all_temp = 0
            for t in range(1, deadline):
                temp = c[k] * abs(u[k][t] - u[k][t-1])
                # 修改目标函数
                # temp = c[k]*abs(u[k][t+1]-u[k][t])
                obj += temp
            obj += u[k][0]
        # all_obj+=obj
        all_obj += obj*(1/nscen)
        # 超出i
    return all_obj

def caculate_new_objective(nscen, implement_act, schedule,resNo,deadline,req,scenario_duration,c,C,actNo,max_lftn):
    all_obj = 0
    for i in range(nscen):
        obj = 0
        duration = scenario_duration[i]
        # print(schedule)
        u = np.zeros((resNo, max_lftn))

        for act in implement_act:
            for k in range(resNo):
                # print(schedule[act] + duration[act])
                for t in range(schedule[act], schedule[act] + duration[act]):
                    u[k][t] += req[act][k]

        # 计算目标函数值
        for k in range(resNo):
            for t in range(0, deadline-1):
                temp = c[k] * abs(u[k][t+1] - u[k][t])
                obj += temp

        all_obj += obj
        # print(obj)
    all_obj *=(1/nscen)
    # 超出截止日期
    if schedule[actNo-1]>deadline:
        all_obj+=(schedule[actNo-1]-deadline)*C
    return all_obj

def caculate_new_objective_scenario(nscen, scenario_vl, scenario_schedule,resNo,deadline,req,scenario_duration,c,actNo,C,max_lftn):
    all_obj = 0
    for i in range(nscen):
        obj = 0
        vl = scenario_vl[i]
        # print(vl)
        schedule = scenario_schedule[i]
        duration = scenario_duration[i]
        # # print(schedule)
        # u = np.zeros((resNo, deadline+1))

        u = np.zeros((resNo, max_lftn+1))

        for act in vl:
            for k in range(resNo):
                # print(schedule[act] + duration[act])
                # print(max_lftn
                if schedule[act] + duration[act]>max_lftn:
                    temp = deadline
                else:
                    temp = schedule[act] + duration[act]
                for t in range(schedule[act], temp):
                    u[k][t] += req[act][k]

        # 计算目标函数值
        for k in range(resNo):
            for t in range(0, deadline - 1):
                temp = c[k] * abs(u[k][t + 1] - u[k][t])
                obj += temp

        all_obj += obj
        if schedule[actNo - 1] > deadline:
            all_obj += (schedule[actNo - 1] - deadline) * C
    all_obj *= (1 / nscen)
    return all_obj