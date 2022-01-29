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
            for t in range(1, deadline+1):
                temp = c[k] * abs(u[k][t] - u[k][t-1])
                obj += temp
            obj += u[k][0]
        # all_obj+=obj
        all_obj += obj*(1/nscen)
    return all_obj

