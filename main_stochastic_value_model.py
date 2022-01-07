'''
随机规划模型的价值
'''
from docplex.mp.model import Model

# 项目中的活动数量
import numpy as np

import pandas as pd

from backwardAll import backward, backward_update
from create_model import create_stochastic_Model
from forwardMandatory import forwardManda
from forwardPass import forwardPass
from initChoice import initChoice
from initData import initData
from initDuration import initDuration
from initfile import initfile

# 项目中的活动数
from newProjectData import newProjectData1
# from stochastic_value_model import create_stochastic_Model

# 活动的规模
from read_gap_data import read_gap

actNumber = 10
dtimes = [1.5]
# 情景数
senarios_Set = [100]

# 第几组数据
for group in range(1, 2):
    # 第几个实例
    for instance in range(18, 21):
    # for instance in instance_set:
        for nscen in senarios_Set:
            for dtime in dtimes:
                # 写入实验结果文件
                filename = r'C:\Users\ASUS\Desktop\model实验结果\J' + str(actNumber) + '\\' + 'model_stochastic'  + '_dtime_' + str(dtime) + '.txt'
                with open(filename, 'a', newline='') as f:
                    # 读取项目网络数据
                    if actNumber == 5 or actNumber == 10:
                        fileNetwork = r'C:\Users\ASUS\Desktop\SRLP_PS数据\J' + str(
                            actNumber) + '\\' + '项目网络数据' + '\\' + 'J' + str(actNumber) + '_' + str(instance) + '.txt'
                    else:
                        fileNetwork = r'D:\研究生资料\RLP-PS汇总\实验数据集\PSPLIB\j' + str(actNumber) + '\\J' + str(
                            actNumber) + '_' + str(instance) + '.RCP'
                    # 初始化网络结构数据
                    res, duration, su, pred, req, actNo, provide_res,nrpr = initData(fileNetwork)
                    # 处理紧前活动，使活动从0开始编号
                    projPred = []
                    for i in range(1, len(pred)):
                        temp = pred[i]
                        temp = [i - 1 for i in temp]
                        projPred.append(temp)
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
                    lftn = int(est_upper[actNo - 1] * dtime)

                    # 扩大的截止日期，读取DE仿真的gap
                    # gap_datafile = r'C:\Users\ASUS\Desktop\测试实验\EDA\J5\4000sch_de_srlp_7_dtime_U1_2021923_de_u_kt_gap_200_1.8_200.txt'
                    # gap_d_list = read_gap(gap_datafile)
                    # gap_d = gap_d_list[instance - 1]
                    gap_d = 0
                    max_lftn = lftn + gap_d

                    # 读取柔性项目结构
                    if actNumber == 5 or actNumber == 10:
                        datafile = r'C:\Users\ASUS\Desktop\SRLP_PS数据\J' + str(actNumber)
                    else:
                        datafile = r'D:\研究生资料\SRLP-PS汇总\数据和代码_final\SRLP-PS实验数据\J' + str(actNumber) + '\\'

                    # 必须执行的活动
                    fp_mandatory = datafile + '\\' + str(group) + '\\mandatory\\J' + str(actNumber) + '_' + str(instance) + '.txt'
                    mandatory = initfile(fp_mandatory)

                    # 可选集合
                    fp_choice = datafile + '\\' + str(group) + '\\choice\\J' + str(actNumber) + '_' + str(instance) + '.txt'
                    choice = initChoice(fp_choice)
                    choice = np.array(choice)

                    # 所有可选活动
                    fp_choiceList = datafile + '\\' + str(group) + '\\choiceList\\J' + str(actNumber) + '_' + str(instance) + '.txt'
                    choiceList = initfile(fp_choiceList)

                    # 依赖活动
                    fp_depend = datafile + '\\' + str(group) + '\\dependent\\J' + str(actNumber) + '_' + str(instance) + '.txt'
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


                    # 读取随机工期
                    file_duration = r'C:\Users\ASUS\Desktop\SRLP-PS随机工期\J' + str(actNumber) + '\\J' + str(
                        actNumber) + '_' + str(instance) + '_duration.txt'
                    stochastic_duration = initDuration(file_duration)

                    # 所有资源的供应量之和
                    max_H = sum(provide_res)

                    # 计算est.lst
                    # 正向计算，只考虑必须执行活动
                    est, eft = forwardManda(duration, projSu, mandatory, actNo, projPred)
                    # 逆向计算，考虑全部活动
                    lst, lft = backward_update(projSu, duration, lftn, actNo, mandatory)

                    # 创建模型，平均工期，获得项目中执行的活动
                    md1 = Model()
                    # 资源种类
                    k = [i for i in range(0, res)]
                    # 资源的单位惩罚成本
                    cost = [1] * res
                    # 资源占用量
                    h = [i for i in range(1, max_H + 1)]
                    # 截止日期
                    d = [i for i in range(0, lftn + 1)]
                    # 活动数量列表
                    act = [i for i in range(0, actNo)]

                    it = [(i, j) for i in act for j in d]
                    kt = [(i, j) for i in k for j in d]

                    x_it = md1.binary_var_dict(it, name='x')

                    y_kth = md1.binary_var_cube(k, d, h, name='y')

                    z_kt = md1.integer_var_dict(kt, name='z')
                    u_kt = md1.integer_var_dict(kt,name='u')


                    M = 1e3

                    # 目标函数
                    md1.minimize(md1.sum(cost[kk] * z_kt[kk, tt] for tt in range(lftn + 1) for kk in k))

                    # 虚开始活动的开始时间
                    md1.add_constraint(x_it[0, 0] == 1)

                    # 必须执行活动约束
                    md1.add_constraints(
                        md1.sum(x_it[i, t] for t in list(range(est[i], lst[i] + 1))) == 1 for i in mandatory)

                    # 可选活动集合约束
                    for ii in ae:
                        md1.add_constraint(
                            md1.sum(x_it[i, t] for i in we[ae.index(ii)] for t in list(range(est[i], lst[i] + 1))) ==
                            md1.sum(x_it[ii, tt] for tt in list(range(est[ii], lst[ii] + 1))))

                    # 依赖活动
                    for a in be:
                        for i in b[be.index(a)]:
                            md1.add_constraint(
                                md1.sum(x_it[i, t] for t in list(range(est[i], lst[i] + 1))) == \
                                md1.sum(x_it[a, tt,] for tt in list(range(est[a], lst[a] + 1))))

                    # 截止日期约束
                    md1.add_constraint(md1.sum(t * x_it[actNo - 1, t] for t in list(range(est[actNo - 1], lst[actNo - 1] + 1)
                                                                                    )) <= lftn)

                    # 优先关系约束
                    for j in list(range(1, actNo)):
                        # 活动j的紧前活动
                        for i in projPred[j]:
                            md1.add_constraint(
                                md1.sum((t + duration[i]) * x_it[i, t] for t in list(range(est[i], lst[i] + 1)))
                                <= md1.sum(tt * x_it[j, tt] for tt in list(range(est[j], lst[j] + 1))) + \
                                M * (1 - md1.sum(x_it[j, tt] for tt in list(range(est[j], lst[j] + 1)))))

                    # 资源的占用量
                    for kk in k:
                        for t in d:
                            md1.add_constraint(
                                 u_kt[kk, t] == md1.sum(
                                    req[i][kk] * x_it[i, tt] for i in list(range(1, actNo)) for
                                    tt in list(
                                        range(max(est[i], t - duration[i] + 1), min(t, lst[i]) + 1)))
                                # md1.sum(y_kth[kk, t, h] for h in list(range(1, max_H + 1))) >=
                                #                md1.sum(
                                #                    req[i][kk] * x_it[i, tt] for i in list(range(1, actNo)) for tt
                                #                    in list(range(max(est[i], t - duration[i] + 1),
                                #                                  min(t, lst[i]) + 1)))
                            )
                    # 资源限制
                    for t in d:
                        for kk in k:
                            md1.add_constraint(
                                u_kt[kk, t] <= provide_res[kk]
                                # md1.sum(y_kth[kk, t, h] for h in list(range(1, max_H + 1))) <= provide_res[kk]
                            )

                    # 线性化目标函数
                    for kk in k:
                        for t in range(1, lftn+1):
                                md1.add_constraint(
                                    u_kt[kk, t] - u_kt[kk, t - 1] <= z_kt[kk, t]
                                    # md1.sum(req[i][kk] * x_it[i, tt] for i in list(range(1, actNo)) for
                                #                            tt in list(
                                #     range(max(est[i], t - duration[i] + 1), min(t, lst[i]) + 1))) - md1.sum(
                                #     req[i][kk] * x_it[i, tt] for i in list(range(1, actNo)) for tt in list(
                                #         range(max(est[i], t - duration[i]), min(t - 1, lst[i]) + 1))
                                # ) <= z_kt[kk, t]
                                                   )

                                md1.add_constraint(
                                    u_kt[kk, t - 1] - u_kt[kk, t] <= z_kt[kk, t]
                                    # md1.sum(
                                    #     req[i][kk] * x_it[i, tt] for i in list(range(1, actNo)) for tt in list(
                                    #         range(max(est[i], t - duration[i]), min(t - 1, lst[i]) + 1))
                                    # ) - md1.sum(req[i][kk] * x_it[i, tt] for i in list(range(1, actNo)) for
                                    #             tt in list(
                                    #     range(max(est[i], t - duration[i] + 1), min(t, lst[i]) + 1))
                                    #             ) <= z_kt[kk, t]
                        )

                    for kk in k:
                        md1.add_constraint(z_kt[kk, 0] == u_kt[kk, 0])
                        # md1.add_constraint(z_kt[kk, 0] == md1.sum(y_kth[kk, 0, h] for h in list(range(1, max_H + 1))))

                    md1.parameters.timelimit = 1800
                    solution = md1.solve()

                    if solution == None:
                        print('求不出解')
                        continue
                    else:
                        # 获取目标函数值
                        d1 = md1.objective_value
                        # 解的状态
                        status = solution.solve_status
                        if status.value == 1:
                            continue
                        else:
                            # 计算时间
                            cputime = solution.solve_details.time

                            # 平均工期获得的目标函数值
                            # results = str(instance) + '\t' + str(status.value) + '\t' + str(format(d1, '.4f')) + '\t' + str(
                            #     format(cputime, '.4f'))
                            # print(results)

                            # 获取执行活动和开始时间
                            x_it_value = solution.get_value_dict(x_it)
                            act_time = []
                            for key, value in x_it_value.items():
                                if value == 1:
                                    act_time.append(key)

                            # 项目中执行活动
                            vl = []
                            schedule = [0 for x in range(0, actNo)]
                            for i in range(len(act_time)):
                                vl.append(act_time[i][0])
                                schedule[act_time[i][0]] = act_time[i][1]


                            # print(vl)
                            # implement_act = ','.join(vl)
                            # for i in vl:
                            #     results = results + str(i+1) + '\t'
                            # results = results+'\n'
                            # # # 写入平均工期结果+执行活动
                            # f.write(results)
                            # print(results)



                            # 根据求出来的必须执行活动建立随机模型
                            flag, solution_stochastic, model =create_stochastic_Model(res, max_H, lftn,max_lftn, actNo, projSu, projPred,mandatory, stochastic_duration,
                                        req, provide_res, nscen,vl,ae,we,be,b)
                            if flag == 0:
                                print('求不出解')
                                continue
                            else:
                                # 获取目标函数值
                                objectValue = model.objective_value
                                # print(objectValue)
                                # 解的状态
                                status_s = solution_stochastic.solve_status
                                # 计算时间
                                cputime_s = solution_stochastic.solve_details.time
                                # 将实验结果写入文件
                                # results = str(instance) + '\t' +str(d1)+'\t'+str(cputime) +'\t'+str(status.value)+'\t'+ str(format(objectValue, '.4f')) + '\t' + str(cputime_s) + '\t' + str(status_s.value) + '\n'
                                results = str(instance) + '\t' + str(status_s.value) + '\t' + str(format(objectValue, '.4f'))  + '\t' + str(cputime_s) + '\t'+str(nscen)+'\n'
                                print(results)

                                # # 写入文件
                                f.write(results)

