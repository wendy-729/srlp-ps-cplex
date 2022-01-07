from docplex.mp.model import Model

# 项目中的活动数量
import numpy as np

import pandas as pd
from backwardAll import backward, backward_update
from forwardManda_update import forwardManda
from forwardPass import forwardPass
from initChoice import initChoice
from initData import initData
from initDuration import initDuration
from initfile import initfile
from newProjectData import newProjectData, newProjectData1


# 项目中的活动数
actNumber = 30
dtimes = [1.8]
# 置信度
db_pro = 0.9
# 组数
for group in range(1, 2):
# 第几个实例
    for instance in range(66, 67):
        for dtime in dtimes:
            # 写入实验结果文件
            filename = r'C:\Users\ASUS\Desktop\J' + str(actNumber) + '\实验结果' + '\\' + 'model_perfect_' + str(
                instance) + '_dtime_' + str(dtime) + '.txt'
            with open(filename, 'a', newline='') as f:
                # 读取项目网络数据
                if actNumber == 5 or actNumber == 10:
                    fileNetwork = r'C:\Users\ASUS\Desktop\J' + str(actNumber) + '\\' + 'J' + str(actNumber) + '_' + str(
                        instance) + '.txt'
                else:
                    fileNetwork = r'D:\研究生资料\RLP-PS汇总\实验数据集\PSPLIB\j' + str(actNumber) + '\\J' + str(
                        actNumber) + '_' + str(instance) + '.RCP'

                # 初始化数据
                res, duration, su, pred, req, actNo, provide_res,nrpr = initData(fileNetwork)

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
                lftn = int(est_upper[actNo - 1] * dtime)

                # 读取柔性项目结构
                if actNumber == 5 or actNumber == 10:
                    datafile = r'C:\Users\ASUS\Desktop\J' + str(actNumber)
                else:
                    datafile = r'D:\研究生资料\SRLP-PS汇总\数据和代码_final\SRLP-PS实验数据\J' + str(actNumber)

                # 必须执行的活动
                fp_mandatory = datafile +'\\'+str(group) + '\\mandatory\\J' + str(actNumber) + '_' + str(instance) + '.txt'
                mandatory = initfile(fp_mandatory)
                # 可选集合
                fp_choice = datafile +'\\'+str(group)+ '\\choice\\J' + str(actNumber) + '_' + str(instance) + '.txt'
                choice = initChoice(fp_choice)
                choice = np.array(choice)

                # 所有可选活动
                fp_choiceList = datafile +'\\'+str(group) + '\\choiceList\\J' + str(actNumber) + '_' + str(instance) + '.txt'
                choiceList = initfile(fp_choiceList)
                # print(choiceList)

                # 依赖活动
                fp_depend = datafile+'\\'+str(group) + '\\dependent\\J' + str(actNumber) + '_' + str(instance) + '.txt'
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

                # 更新项目结构
                # new_su, new_pred = newProjectData1(projSu, projPred, choiceList, actNo)
                # projSu = new_su
                # projPred = new_pred

                # 随机工期
                if actNumber == 5 or actNumber == 10:
                    file_duration = r'C:\Users\ASUS\Desktop\J' + str(actNumber) + '\\J' + str(actNumber) + '_' + str(
                        instance) + '_duration.txt'
                else:
                    file_duration = r'D:\研究生资料\SRLP-PS汇总\数据和代码_final\随机工期\U1' + '\\J' + str(actNumber) + '\\' + str(
                        instance) + '.txt'
                # 读取随机工期
                stochastic_duration = initDuration(file_duration)

                # 所有资源的供应量之和
                max_H = sum(provide_res)

                # 遍历几个情景，将目标函数求均值
                mean_scenarios_Set = [1]
                for mean_scenarios in mean_scenarios_Set:
                    # 所有情景获得目标函数均值
                    mean_value = 0
                    # 统计多少情景下求出最优解
                    count = 0
                    # 时间
                    all_cputime = 0
                    for scen in range(mean_scenarios):
                        # 工期
                        duration = stochastic_duration[scen]
                        # 最早开始时间和最晚开始时间
                        # 正向计算，只考虑必须执行活动
                        est, eft = forwardManda(duration, projSu, mandatory, actNo, projPred)
                        # est = [0]*actNo
                        # 逆向计算，考虑全部活动
                        lst, lft = backward_update(projSu, duration, lftn, actNo, mandatory)
                        # lst = [lftn]*actNo

                        # 创建模型
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

                        # z_kt = md1.integer_var_dict(kt, name='k')
                        z_kt = md1.continuous_var_dict(kt, name='z')


                        M = 1e3

                        # 目标函数
                        # md1.minimize(md1.sum(
                        #     cost[kk] * z_kt[kk, tt] + sum(y_kth[kk, 0, h] for h in list(range(1, max_H + 1))) for tt in
                        #     range(lftn + 1) for kk in k))
                        md1.minimize(md1.sum(cost[kk] * z_kt[kk, tt]  for tt in  range(lftn+1) for kk in k))

                        # 虚开始活动的开始时间
                        md1.add_constraint(x_it[0, 0] == 1)

                        # 必须执行活动约束
                        md1.add_constraints(
                            md1.sum(x_it[i, t] for t in list(range(est[i], lst[i] + 1))) == 1 for i in mandatory)

                        # 可选活动集合约束
                        for ii in ae:
                            md1.add_constraint(
                                md1.sum(
                                    x_it[i, t] for i in we[ae.index(ii)] for t in list(range(est[i], lst[i] + 1))) ==
                                md1.sum(x_it[ii, tt] for tt in list(range(est[ii], lst[ii] + 1))))

                        # 依赖活动
                        for a in be:
                            for i in b[be.index(a)]:
                                md1.add_constraint(
                                    md1.sum(x_it[i, t] for t in list(range(est[i], lst[i] + 1))) == \
                                    md1.sum(x_it[a, tt,] for tt in list(range(est[a], lst[a] + 1))))

                        # 截止日期约束
                        md1.add_constraint(
                            md1.sum(t * x_it[actNo - 1, t] for t in list(range(est[actNo - 1], lst[actNo - 1] + 1)
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
                                md1.add_constraint(md1.sum(y_kth[kk, t, h] for h in list(range(1, max_H + 1))) >=
                                                   md1.sum(
                                                       req[i][kk] * x_it[i, tt] for i in list(range(1, actNo)) for tt
                                                       in list(range(max(est[i], t - duration[i] + 1),
                                                                     min(t, lst[i]) + 1))
                                                   ))
                        # 资源限制
                        for t in d:
                            for kk in k:
                                md1.add_constraint(
                                    md1.sum(y_kth[kk, t, h] for h in list(range(1, max_H + 1))) <= provide_res[kk]
                                )

                        # 线性化目标函数
                        for kk in k:
                            for t in range(1, lftn + 1):
                                md1.add_constraint(md1.sum(req[i][kk] * x_it[i, tt] for i in list(range(1, actNo)) for
                                                           tt in list(
                                    range(max(est[i], t - duration[i] + 1), min(t, lst[i]) + 1))) - md1.sum(
                                    req[i][kk] * x_it[i, tt] for i in list(range(1, actNo)) for tt in list(
                                        range(max(est[i], t - duration[i]), min(t - 1, lst[i]) + 1))
                                ) <= z_kt[kk, t])

                                md1.add_constraint(
                                    md1.sum(
                                        req[i][kk] * x_it[i, tt] for i in list(range(1, actNo)) for tt in list(
                                            range(max(est[i], t - duration[i]), min(t - 1, lst[i]) + 1))
                                    ) - md1.sum(req[i][kk] * x_it[i, tt] for i in list(range(1, actNo)) for
                                                tt in list(
                                        range(max(est[i], t - duration[i] + 1), min(t, lst[i]) + 1))
                                                ) <= z_kt[kk, t])

                        for kk in k:
                            md1.add_constraint(z_kt[kk,0] == md1.sum(y_kth[kk, 0, h] for h in list(range(1, max_H + 1))))

                        md1.parameters.timelimit = 300
                        solution = md1.solve()
                        md1.parameters.mip.display = 2
                        # md1.parameters.threads = 1

                        if solution == None:
                            print('求不出解')
                            continue
                        else:
                            # print(solution)
                            count += 1
                            # 获取目标函数值
                            d1 = md1.objective_value
                            print(d1)
                            mean_value += d1
                            # 解的状态
                            status = solution.solve_status
                            cputime = solution.solve_details.time
                            # print(cputime)
                            all_cputime += cputime

                            # # 获取执行活动以及对应的开始时间
                            # x_it_value = solution.get_value_dict(x_it)
                            # act_time = []
                            # for key, value in x_it_value.items():
                            #     if value == 1:
                            #         act_time.append(key)
                            #
                            # vl = []
                            # schedule = [0 for x in range(0, actNumber + 2)]
                            # for i in range(len(act_time)):
                            #     vl.append(act_time[i][0])
                            #     schedule[act_time[i][0]] = act_time[i][1]
                            # vl = [x + 1 for x in vl]
                            # print('执行活动',vl)
                            # print('进度计划', schedule)
                            # print('随机工期', stochastic_duration[0])


                    # print(mean_value)
                    if count == mean_scenarios or count >= mean_scenarios * db_pro:
                        mean_perfect_value = mean_value/count
                        mean_cputime = all_cputime
                        results = str(instance) + '\t' + str(mean_perfect_value) + '\t' + str(mean_cputime) + '\t' + \
                                  str(status.value) +'\t'+str(mean_scenarios) + '\t'+str(count)+ '\n'
                        # print(count)
                        # print(results)

                        # f.write(results)


