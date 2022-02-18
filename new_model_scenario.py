# 郑淋文
# 时间: 2022/2/17 19:43
# 活动的开始时间依赖于情景
# 该模型求解困难
from docplex.mp.model import Model

# 项目中的活动数量
import numpy as np

import pandas as pd

from abs_objective import caculate_objective, caculate_new_objective_scenario
from backwardAll import backward, backward_update
from forwardMandatory import forwardManda
from forwardManda_update import forwardManda_update
from forwardPass import forwardPass
from initChoice import initChoice
from initData import initData
from initDuration import initDuration
from initfile import initfile
from read_gap_data import read_gap

# 项目中的活动数
from newProjectData import newProjectData, newProjectData1

actNumber = 5
# 截止日期
dtimes = [1.2]
# 情景数
# scenariosSet = [1]
# actSet = [1]
# actSet = [12,14,15,19]
scenariosSet = [100]
# scenariosSet = [5]
# 第几组数据
for group in range(1, 2):
    # 第几个实例
    # for instance in actSet:
    for instance in range(1, 2):
        # if instance in actSet:
        #     continue
        # flag = 0
        for dtime in dtimes:
            # 情景数
            for nscen in scenariosSet:
                # flag_scen  = 0
                # 写入实验结果文件
                filename = r'C:\Users\ASUS\Desktop\测试实验-srlp-ps\CPLEX\J'+ str(actNumber)+'\\'+'new_linear_test'+ '_dt_' + str(dtime) + '_'+str(nscen)+'.txt'
                # filename = r'C:\Users\ASUS\Desktop\SRLP-PS-two-linear-model-new\linear1\J' + str(actNumber)  + '_Pr_1\\' + 'new_linear_test'+ '_dt_' + str(dtime) + '_'+str(nscen)+'.txt'
                with open(filename, 'a', newline='') as f:
                    # 读取项目网络数据
                    if actNumber == 5 or actNumber == 10:
                        fileNetwork = r'D:\研究生资料\SRLP-PS-汇总-20211220\数据\SRLP_PS数据\J' + str(
                            actNumber) + '\\' + '项目网络数据' + '\\' + 'J' + str(actNumber) + '_' + str(
                            instance) + '.txt'
                    else:
                        fileNetwork = r'D:\研究生资料\RLP-PS汇总\实验数据集\PSPLIB\j' + str(actNumber) + '\\J' + str(
                            actNumber) + '_' + str(instance) + '.RCP'

                    # 初始化数据，紧前活动和紧后活动编号从1开始
                    res, duration, su, pred, req, actNo, provide_res, nrpr = initData(fileNetwork)

                    # 处理紧前活动，使活动从0开始编号
                    projPred = []
                    for i in range(1, len(pred)):
                        temp = pred[i]
                        temp = [i - 1 for i in temp]
                        projPred.append(temp)
                    # 虚开始活动
                    projPred.insert(0, [])
                    # 处理紧后活动，活动从0开始编号
                    projSu = []
                    for i in range(len(su) - 1):
                        temp = su[i]
                        temp = [i - 1 for i in temp]
                        projSu.append(temp)
                    # 虚终止活动
                    projSu.append([])

                    # 所有活动都执行，平均工期，计算截止日期
                    est_upper, lst_upper = forwardPass(duration, projSu)
                    lftn = int(est_upper[actNo - 1] *dtime)

                    # 考虑所有活动的平均工期总和作为项目完成时间的上界
                    max_lftn = sum(duration)
                    print(max_lftn)
                    print(lftn)

                    # 读取柔性项目结构
                    if actNumber == 5 or actNumber == 10:
                        datafile = r'D:\研究生资料\SRLP-PS-汇总-20211220\数据\SRLP_PS数据\J' + str(actNumber) + '\\' + str(group)
                        # print(datafile)
                    else:
                        datafile = r'D:\研究生资料\SRLP-PS汇总\数据和代码_final\SRLP-PS实验数据\J' + str(actNumber) + '\\'+ str(group)

                    # 必须执行的活动
                    fp_mandatory = datafile +  '\\mandatory\\J' + str(actNumber) + '_' + str(
                        instance) + '.txt'
                    mandatory = initfile(fp_mandatory)
                    # 可选集合
                    fp_choice = datafile + '\\choice\\J' + str(actNumber) + '_' + str(
                        instance) + '.txt'
                    choice = initChoice(fp_choice)
                    choice = np.array(choice)

                    # 所有可选活动
                    fp_choiceList = datafile + '\\choiceList\\J' + str(actNumber) + '_' + str(
                        instance) + '.txt'
                    choiceList = initfile(fp_choiceList)

                    # 依赖活动
                    fp_depend = datafile + '\\dependent\\J' + str(actNumber) + '_' + str(
                        instance) + '.txt'
                    depend = initChoice(fp_depend)
                    depend = np.array(depend)

                    # 触发选择的可选活动
                    ae = []
                    for i in range(0, choice.shape[0]):
                        ae.append(choice[i][0])

                    # we 可选活动集合
                    we = []
                    for i in range(0, choice.shape[0]):
                        temp = choice[i][1:]
                        we.append(temp)

                    # 触发依赖活动的可选活动
                    be = []
                    for i in range(0, depend.shape[0]):
                        be.append(depend[i][0])

                    # 依赖活动
                    b = []
                    for i in range(0, depend.shape[0]):
                        temp = depend[i][1:]
                        b.append(temp)
                    # print("依赖活动", b)


                    file_duration = r'D:\研究生资料\SRLP-PS-汇总-20211220\数据\SRLP-PS随机工期\J' + str(actNumber) + '\\J' + str(
                        actNumber) + '_' + str(instance) + '_duration.txt'
                    stochastic_duration = initDuration(file_duration)

                    # 每个时刻的最大资源使用量，所有资源的供应量之和
                    max_H = sum(provide_res)

                    # 创建模型
                    md1 = Model()
                    # 资源种类
                    k = [i for i in range(0, res)]
                    # 资源的单位惩罚成本
                    cost = [1]*res
                    # cost = [1/res] * res
                    # print(cost)
                    # 资源占用量
                    h = [i for i in range(1, max_H + 1)]
                    # 截止日期
                    d = [i for i in range(0, lftn + 1)]
                    # 最大的截止日期
                    max_d = [i for i in range(0, max_lftn + 1)]
                    # 活动数量列表
                    act = [i for i in range(0, actNo)]

                    # 情景
                    scenarios = nscen
                    # 情景的概率
                    num_w = [1] * scenarios
                    pro_w = [i / scenarios for i in num_w]
                    est_s = [0] * actNo
                    lst_s = [max_lftn]*actNo


                    # 置信度
                    pr_pro = 0.9
                    res_pro = 0.9

                    # 情景
                    w = [i for i in range(0, scenarios)]
                    # 活动是否执行【决策变量】
                    y_i = md1.binary_var_list(act, name='y')

                    # 活动i在情景w中的开始时间为t
                    x_itw = md1.binary_var_cube(act, max_d, w, name='x')

                    # 资源占用量
                    u_ktw = md1.integer_var_cube(k, max_d, w, name='u')

                    # 优先关系是否满足的二元变量
                    pr_w = md1.binary_var_list(w, name='pr')
                    # 资源约束是否满足的二元变量
                    res_w = md1.binary_var_list(w, name='res')

                    # 中间变量
                    z_ktw = md1.integer_var_cube(k, max_d, w, name='z')

                    p_w = md1.integer_var_list(w, name='p')
                    q_w = md1.integer_var_list(w, name='q')

                    M = 1e2
                    # theta_pr = M
                    # theta_res = M
                    # theta_d = M
                    theta_pr = max_lftn
                    # 资源
                    theta_res = max_H
                    # 截止日期
                    theta_d = max_lftn
                    # 超期成本
                    C = 3

                    md1.minimize(md1.sum(
                        pro_w[s] * (md1.sum(cost[kk] * z_ktw[kk, tt, s] for tt in range(0, lftn) for kk
                                           in k)+C*p_w[s]) for s in w))

                    # 虚开始活动的开始时间
                    for s in range(scenarios):
                        md1.add_constraint(x_itw[0, 0, s] == 1)

                    # 保证在所有情景中，执行的活动是相同的
                    for i in range(actNo):
                        for s in w:
                            md1.add_constraint(y_i[i] == md1.sum(
                                x_itw[i, tt, s] for tt in list(range(0, max_lftn+1))))

                    # 必须执行活动约束
                    for i in mandatory:
                        md1.add_constraint(y_i[i] == 1)

                    # 可选活动集合约束
                    for ii in ae:
                        md1.add_constraint(md1.sum(y_i[i] for i in we[ae.index(ii)]) == y_i[ii])

                    # 依赖活动
                    for a in be:
                        for i in b[be.index(a)]:
                            md1.add_constraint(y_i[i] == y_i[a])

                    # 优先关系约束
                    for s in range(scenarios):
                        duration = stochastic_duration[s]
                        for j in list(range(1, actNo)):
                            # 活动j的紧前活动
                            for i in projPred[j]:
                                md1.add_constraint(
                                    md1.sum((t + duration[i]) * x_itw[i, t, s] for t in
                                            list(range(0, max_lftn+1))) - theta_pr * (1 - pr_w[s]) \
                                    <= md1.sum(
                                        tt * x_itw[j, tt, s] for tt in
                                        list(range(0, max_lftn+1))) + \
                                    M * (1 - y_i[j]))

                    # 优先关系机会约束
                    md1.add_constraint(md1.sum(pro_w[i] * pr_w[i] for i in w) >= pr_pro)

                    # 资源的占用量,u_kt是从0开始的，matlab是从1开始的
                    for s in range(scenarios):
                        duration = stochastic_duration[s]
                        for kk in k:
                            for t in max_d:
                                md1.add_constraint(
                                    u_ktw[kk,t,s] == md1.sum(
                                        req[i][kk] * x_itw[i, tt, s] for i in list(range(1, actNo)) for
                                        tt in list(
                                            range(max(est_s[i], t - duration[i] + 1), min(t, lst_s[i]) + 1))
                                    ))

                    # 资源约束
                    for s in range(scenarios):
                        for t in max_d:
                            for kk in k:
                                md1.add_constraint(
                                    u_ktw[kk, t, s] - theta_res * (1 - res_w[s]) <= provide_res[kk]
                                )

                    # 资源限制机会约束
                    md1.add_constraint(md1.sum(pro_w[i] * res_w[i] for i in w) >= res_pro)


                    # 线性化目标函数
                    for s in w:
                        duration = stochastic_duration[s]
                        for kk in k:
                            for t in range(0, lftn-1):
                                # md1.add_constraint(
                                #     md1.sum(req[i][kk] * x_itw[i, tt, s] for i in list(range(1, actNo)) for
                                #             tt in list(range(max(scen_est[s][i], t - duration[i] + 1),
                                #                              min(t, scen_lst[s][i]) + 1))) - md1.sum(
                                #         req[i][kk] * x_itw[i, tt, s] for i in list(range(1, actNo)) for tt in list(
                                #             range(max(scen_est[s][i], t - duration[i]), min(t - 1, scen_lst[s][i]) + 1))
                                #     ) <= z_ktw[kk, t, s])
                                #
                                # md1.add_constraint(
                                #     md1.sum(req[i][kk] * x_itw[i, tt, s] for i in list(range(1, actNo)) for tt in list(
                                #         range(max(scen_est[s][i], t - duration[i]), min(t - 1, scen_lst[s][i]) + 1))
                                #             ) - md1.sum(req[i][kk] * x_itw[i, tt, s] for i in list(range(1, actNo)) for
                                #                         tt in list(
                                #         range(max(scen_est[s][i], t - duration[i] + 1), min(t, scen_lst[s][i]) + 1))
                                #                         ) <= z_ktw[kk, t, s])
                                md1.add_constraint(
                                    u_ktw[kk, t + 1, s] - u_ktw[kk, t, s] <= z_ktw[kk, t, s])

                                md1.add_constraint(
                                    u_ktw[kk, t, s] - u_ktw[kk, t + 1, s] <= z_ktw[kk, t, s])
                    # 线性化惩罚项
                    for s in w:
                        md1.add_constraint(md1.sum(
                            t * x_itw[actNo - 1, t,s] for t in
                            list(range(est_s[actNo - 1], lst_s[actNo - 1] + 1)
                                 )) - lftn == p_w[s] - q_w[s])



                    # 时间参数设定
                    md1.parameters.timelimit = 1800
                    # cplex在长时间得到更好的可行解时，求解可行解优先而非最优性优先
                    # md1.parameters.emphasis.mip = 2
                    # md1.parameters.mip.display = 2
                    # md1.parameters.threads = 1

                    solution = md1.solve()
                    # print(solution)
                    if solution == None:
                        print('求不出解')
                        continue
                    else:
                        # 获取目标函数值
                        d1 = md1.objective_value
                        # print(solution)
                        # 解的状态
                        status = solution.solve_status
                        # 计算时间
                        cputime = solution.solve_details.time


                        # 统计优先关系
                        temp_pr = 0
                        for i in pr_w:
                            value_temp = solution.get_var_value(i)
                            if value_temp == 1.0:
                                temp_pr += 1
                        tcpr = temp_pr/nscen
                        # 统计资源
                        temp_res = 0
                        for i in res_w:
                            value_temp = solution.get_var_value(i)
                            if value_temp == 1.0:
                                temp_res += 1
                        tcres = temp_res / nscen


                        # 重新计算及时完成率
                        # 获取每个情景的执行活动以及对应的开始时间
                        scenarios_act_time = []
                        x_it_value = solution.get_value_dict(x_itw)

                        act_time = []
                        for s in range(scenarios):
                            temp = []
                            for key, value in x_it_value.items():
                                # 情景且在该情景下执行
                                if s == key[2] and value == 1:
                                    temp.append(key)
                            scenarios_act_time.append(temp)

                        # 每个情景下的执行活动和开始时间
                        scenario_implement_act = []
                        # 包含未执行活动开始时间
                        scenario_start_time = []

                        for i in range(len(scenarios_act_time)):
                            temp = scenarios_act_time[i]
                            implement_act = []
                            act_start_time = [0] * actNo
                            for j in temp:
                                # print(j)
                                implement_act.append(j[0])
                                act_start_time[j[0]] = j[1]

                            scenario_implement_act.append(implement_act)
                            scenario_start_time.append(act_start_time)
                        # print('随机工期', stochastic_duration)
                        # # # print(lftn)
                        # print('每个情景下的开始时间', scenario_start_time)
                        # print('每个情景对应的执行活动', scenario_implement_act)
                        # 每个情景下对应的执行列表
                        vl_set = []
                        for i in range(len(scenario_implement_act)):
                            implement = [0] * actNo
                            temp_act = scenario_implement_act[i]
                            for j in temp_act:
                                implement[j] = 1
                            vl_set.append(implement)

                        tcp = 0
                        for s in range(nscen):
                            duration = stochastic_duration[s]
                            schedule = scenario_start_time[s]
                            # 执行活动
                            vl = vl_set[s]
                            # print(vl)
                            for i in range(actNo-1):
                                if vl[i] == 1:
                                    if schedule[i]+duration[i] > lftn:
                                        tcp += 1
                                        break
                        tpcp1 = (nscen-tcp)/nscen
                        # 计算目标函数值
                        # for s in w:
                        # obj = caculate_objective(nscen, scenario_implement_act, scenario_start_time,res,max_lftn,req,stochastic_duration[0:nscen],cost)
                        obj = caculate_new_objective_scenario(nscen, scenario_implement_act, scenario_start_time,res,lftn,req,stochastic_duration,cost,actNo,C,max_lftn)
                        # print(obj)


                        # 将实验结果写入文件
                        results = str(instance) + '\t' + str(status.value) + '\t' +str(tcpr)+'\t' +str(tcres)+'\t'  +str(tpcp1)+'\t'+ str(
                            format(d1, '.4f'))  + '\t'+str(obj) +'\t' + str(
                            format(cputime, '.4f')) + '\t' + str(scenarios)+'\n'
                        # print(req)
                        print(results)
                        print(instance, 'is solved')
                        # print(req,'资源')
                        # 写入文件
                        # f.write(results)



