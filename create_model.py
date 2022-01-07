from docplex.mp.model import Model

from backwardAll import backward, backward_update
from forwardMandatory import forwardManda
from newProjectData import upateRelation


def create_stochastic_Model(res, max_H, lftn, max_lftn, actNo, projSu, projPred,mandatory, stochastic_duration,
                            req, provide_res, nscen, newMandatory, ae, we, be, b):
    # 标记求出最优解
    flag = 0
    # 创建模型
    md = Model()
    # 资源种类
    k = [i for i in range(0, res)]
    # 资源的单位惩罚成本
    cost = [1] * res
    # 资源占用量
    h = [i for i in range(1, max_H + 1)]
    # 截止日期
    d = [i for i in range(0, lftn + 1)]
    # 扩大的截止日期
    max_d = [i for i in range(0, max_lftn + 1)]
    # 活动数量列表
    act = [i for i in range(0, actNo)]

    # 情景
    scenarios = nscen
    # 情景的概率
    num_w = [1] * scenarios
    pro_w = [i / scenarios for i in num_w]
    # 计算每个情景下，每个活动的可能的最早开始时间和最晚开始时间
    scen_est = []
    scen_lst = []

    # print(newMandatory)
    # 项目结构已经确定，则可以正常计算最早开始和最晚开始时间
    # 更新项目结构
    projSu, projPred = upateRelation(projSu, projPred, actNo, mandatory)
    for s in range(scenarios):
        duration = stochastic_duration[s]
        # 正向计算，只考虑必须执行活动
        est_s, eft_s = forwardManda(duration, projSu, newMandatory, actNo, projPred)
        # 逆向计算，考虑全部活动
        lst_s, lft_s = backward_update(projSu, duration, max_lftn, actNo, newMandatory)
        scen_est.append(est_s)
        scen_lst.append(lst_s)


    # 置信度
    db_pro = 1
    pr_pro = 1
    res_pro = 1
    # 情景
    w = [i for i in range(0, scenarios)]
    # 活动是否执行【决策变量】
    y_i = md.binary_var_list(act, name='y', lb = 0)

    # 活动i在情景w中的开始时间为t
    x_itw = md.binary_var_cube(act, max_d, w, name= 'x')


    # 在情景w，截止日期是否满足的二元变量
    db_w = md.binary_var_list(w, name='db')

    # 优先关系是否满足的二元变量
    pr_w = md.binary_var_list(w, name='pr')
    # 资源约束是否满足的二元变量
    res_w = md.binary_var_list(w, name='res')


    var_list_y = [(a, b, c, e) for a in k for b in max_d for c in h for e in w]
    p_kthw = md.binary_var_dict(var_list_y, name='p')
    # 中间变量
    z_ktw = md.integer_var_cube(k, max_d, w, name='z')
    u_ktw = md.integer_var_cube(k, max_d, w, name='u')
    

    M = 1e2
    theta_pr = M
    theta_res = M
    theta_d = M
    # theta_pr = lftn
    # # 资源
    # theta_res = max_H
    # # 截止日期
    # theta_d = lftn + 1


    # 绝对值目标函数
    md.minimize(md.sum(pro_w[s] * md.sum(cost[kk] * z_ktw[kk, tt, s] for tt in range(max_lftn + 1) for kk in k) for s in w))

    # 虚开始活动的开始时间
    for s in range(scenarios):
        md.add_constraint(x_itw[0, 0, s] == 1)

    # 必须执行活动约束，newMandatory是已经确定的执行活动
    for i in newMandatory:
        md.add_constraint(y_i[i] == 1)

    # 可选活动集合约束
    for ii in ae:
        md.add_constraint(md.sum(y_i[i] for i in we[ae.index(ii)]) == y_i[ii])

    # 依赖活动
    for a in be:
        for i in b[be.index(a)]:
            md.add_constraint(y_i[i] == y_i[a])
    

    # 保证在所有情景中，执行的活动是相同的
    # for i in newMandatory:
    for i in range(actNo):
        for s in w:
            md.add_constraint(y_i[i] == md.sum(x_itw[i, tt, s] for tt in list(range(scen_est[s][i], scen_lst[s][i] + 1))))

    # for i in range(actNo):
    #     for s in w:
    #         if i in newMandatory:
    #             md.add_constraint(1 == md.sum(
    #                      x_itw[i, tt, s] for tt in list(range(scen_est[s][i], scen_lst[s][i] + 1))))
    #         else:
    #             md.add_constraint(0 == md.sum(
    #                 x_itw[i, tt, s] for tt in list(range(scen_est[s][i], scen_lst[s][i] + 1))))

    # 截止日期约束
    for s in range(scenarios):
        md.add_constraint(md.sum(
            t * x_itw[actNo - 1, t, s] for t in list(range(scen_est[s][actNo - 1], scen_lst[s][actNo - 1] + 1)
                 )) - theta_d * (1 - db_w[s]) <= lftn)

    # 截止日期机会约束
    md.add_constraint(md.sum(pro_w[i] * db_w[i] for i in w) >= db_pro)

    # 优先关系约束
    for s in range(scenarios):
        duration = stochastic_duration[s]
        for j in list(range(1, actNo)):
            # 活动j的紧前活动
            for i in projPred[j]:
                md.add_constraint(md.sum((t + duration[i]) * x_itw[i, t, s] for t in
                            list(range(scen_est[s][i], scen_lst[s][i] + 1))) - theta_pr * (1 - pr_w[s]) \
                    <= md.sum(
                        tt * x_itw[j, tt, s] for tt in list(range(scen_est[s][j], scen_lst[s][j] + 1))) + \
                    M * (1 - md.sum(x_itw[j, tt, s] for tt in list(range(scen_est[s][j], scen_lst[s][j] + 1)))))

    # 优先关系机会约束
    md.add_constraint(md.sum(pro_w[i] * pr_w[i] for i in w) >= pr_pro)

    # 资源的占用量
    for s in range(scenarios):
        duration = stochastic_duration[s]
        for kk in k:
            for t in max_d:
                md.add_constraint(
                        md.sum(u_ktw[kk, t, s]) == md.sum(
                            req[i][kk] * x_itw[i, tt, s] for i in list(range(1, actNo)) for
                            tt in list(range(max(scen_est[s][i], t - duration[i] + 1), min(t, scen_lst[s][i]) + 1))
                            )


                    # md.sum(p_kthw[kk, t, h, s] for h in list(range(1, max_H + 1))) >= md.sum(
                    #     req[i][kk] * x_itw[i, tt, s] for i in list(range(1, actNo)) for
                    #     tt in list(
                    #         range(max(scen_est[s][i], t - duration[i] + 1), min(t, scen_lst[s][i]) + 1))
                    # )
                )

    # 资源约束
    for s in range(scenarios):
        for t in max_d:
            for kk in k:
                md.add_constraint(
                    u_ktw[kk, t, s] - theta_res * (1 - res_w[s]) <= provide_res[kk]
                    # md.sum(p_kthw[kk, t, h, s] for h in list(range(1, max_H + 1)))
                    # - theta_res * (1 - res_w[s]) <= provide_res[kk]
                )

    # 资源限制机会约束
    md.add_constraint(md.sum(pro_w[i] * res_w[i] for i in w) >= res_pro)
    # 线性化
    for s in w:
        duration = stochastic_duration[s]
        for kk in k:
            for t in range(1, max_lftn+1):
                md.add_constraint(
                #     md.sum(req[i][kk] * x_itw[i, tt, s] for i in list(range(1, actNo)) for
                #                            tt in list(
                #     range(max(scen_est[s][i], t - duration[i] + 1), min(t, scen_lst[s][i]) + 1))) - md.sum(
                #     req[i][kk] * x_itw[i, tt, s] for i in list(range(1, actNo)) for tt in list(
                #         range(max(scen_est[s][i], t - duration[i]), min(t - 1, scen_lst[s][i]) + 1))
                # ) <= z_ktw[kk, t, s]
                    u_ktw[kk, t, s] - u_ktw[kk, t - 1, s] <= z_ktw[kk, t, s]
                  )

                md.add_constraint(
                    # md.sum(req[i][kk] * x_itw[i, tt, s] for i in list(range(1, actNo)) for tt in list(
                        # range(max(scen_est[s][i], t - duration[i]), min(t - 1, scen_lst[s][i]) + 1))
                        #     ) - md.sum(req[i][kk] * x_itw[i, tt, s] for i in list(range(1, actNo)) for
                        #                 tt in list(
                        # range(max(scen_est[s][i], t - duration[i] + 1), min(t, scen_lst[s][i]) + 1))
                        #                 ) <= z_ktw[kk, t, s]
                    u_ktw[kk, t - 1, s] - u_ktw[kk, t, s] <= z_ktw[kk, t, s]
                )
    for s in w:
        for kk in k:
            md.add_constraint(z_ktw[kk, 0, s] == u_ktw[kk, 0, s])
            # md.add_constraint(z_ktw[kk, 0, s] == md.sum(p_kthw[kk, 0, h, s] for h in list(range(1, max_H + 1))))

    # 时间参数设定
    md.parameters.timelimit = 1800
    solution = md.solve()
    # print(solution)

    if solution:
        # # 获取目标函数值
        # d1 = md.objective_value
        # # 解的状态
        # status = solution.solve_status
        # # 计算时间
        # cputime = solution.solve_details.time
        # # 将实验结果写入文件
        # results = str(d1) + '\t' + str(cputime) + '\t' + str(status.value) + '\n'
        # print(results)
        flag = 1


    return flag, solution, md
