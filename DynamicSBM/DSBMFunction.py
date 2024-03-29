import pandas as pd
from gurobipy import *
from itertools import islice
import csv
import numpy as np


def csv2dict_DDEA(dea_data, in_range, out_range, link_range, Term=4, assign=False, ):
    """Read CSV file and convert it to dictionary"""
    f = open(dea_data)
    reader = csv.reader(f)
    DMU = []
    X, Y, Z = {}, {}, {}
    print("start")

    # All values in in_range should be greater than 0; otherwise, stop the function
    if all(value > 0 for value in in_range):
        in_range[:] = [x - 1 for x in in_range]
    else:
        print("Error: all values given in in_range should be greater than 0")
        # Return nothing to stop the function
        return

    # Same as the in_range (out_Range)
    if all(value > 0 for value in out_range):
        out_range[:] = [y - 1 for y in out_range]
    else:
        print("Error: all values given in out_range should be greater than 0")
        # Return nothing to stop the function
        return

    # link range
    if all(value > 0 for value in link_range):
        link_range[:] = [z - 1 for z in link_range]
    else:
        print("Error: all values given in out_range should be greater than 0")
        # Return nothing to stop the function
        return

    counter = 0
    for line in islice(reader, 1, None):

        obs = line
        key = obs[0]

        # Create dictionaries
        if (assign == False):
            if (counter % (Term)) == 0:
                DMU.append(key)  # Get DMU names
                tmp_key = key
                X[key] = []
                Y[key] = []
                Z[key] = []
                try:
                    # Give a range to get input or ouput data
                    X[key].append([float(v) for v in obs[(in_range[0]):(in_range[1] + 1)]])  # List comprehension
                    Y[key].append([float(v) for v in obs[(out_range[0]):(out_range[1] + 1)]])
                    Z[key].append([float(v) for v in obs[(link_range[0]):(link_range[1] + 1)]])

                except ValueError:
                    print("which means your data include string not number")
            else:
                try:

                    # Give a range to get input or ouput data
                    X[tmp_key].append([float(v) for v in obs[(in_range[0]):(in_range[1] + 1)]])  # List comprehension
                    Y[tmp_key].append([float(v) for v in obs[(out_range[0]):(out_range[1] + 1)]])
                    Z[tmp_key].append([float(v) for v in obs[(link_range[0]):(link_range[1] + 1)]])
                except ValueError:
                    print("which means your data include string not number")
            counter += 1

        elif (assign == True):
            if (counter % (Term)) == 0:
                DMU.append(key)  # Get DMU names
                tmp_key = key
                X[key] = []
                Y[key] = []
                Z[key] = []
                try:
                    # Give a range to get input or ouput data
                    X[key].append([float(v) for v in (list(obs[i] for i in in_range))])  # List comprehension
                    Y[key].append([float(v) for v in (list(obs[i] for i in out_range))])
                    Z[key].append([float(v) for v in (list(obs[i] for i in link_range))])

                except ValueError:
                    print("which means your data include string not number")
            else:
                try:

                    # Give a range to get input or ouput data
                    X[tmp_key].append([float(v) for v in (list(obs[i] for i in in_range))])  # List comprehension
                    Y[tmp_key].append([float(v) for v in (list(obs[i] for i in out_range))])
                    Z[tmp_key].append([float(v) for v in (list(obs[i] for i in link_range))])
                except ValueError:
                    print("which means your data include string not number")
            counter += 1

    return DMU, X, Y, Z


def DDEAfunction_input2(DMU, X, Y, Z, Term=4, W_i=1, W_t=1):
    print("Entering DDEA input-oriented CRS module..... ")
    Eff = {}  # Efficiency score
    E_adjusted = {}  # Adjusted Efficiency score
    E_term = {}  # Adjusted Term Efficiency score

    Input_Constr, Output_Constr, Link_Constr, Link_Cont_Constr = {}, {}, {}, {}

    for o in DMU:
        SO, SI, SL, L = {}, {}, {}, {}
        lamd = {}
        num_Input = len(X[DMU[0]][0])  # numbers of input
        num_Output = len(Y[DMU[0]][0])  # numbers of Output
        num_Links = len(Z[DMU[0]][0])  # numbers of Free Links

        model = Model("DySBMDEA- input oriented")
        # model.setParam('OutputFlag', 0)
        # Add decision variables
        # lamda_j_t
        for t in range(Term):
            for j in DMU:
                lamd[t, j] = model.addVar(vtype=GRB.CONTINUOUS, name="λ_%s_%s:" % (t, j))

        # input slack
        for t in range(Term):
            for m in range(num_Input):
                SI[t, m] = model.addVar(vtype=GRB.CONTINUOUS, name="SI%s_%s:" % (t, m))
        # print(SI)

        # output slack
        for t in range(Term):
            for s in range(num_Output):
                SO[t, s] = model.addVar(vtype=GRB.CONTINUOUS, name="SO%s_%s:" % (t, s))
        # print(SO)

        # free link slack  #SL[t,l]= link l Slack at term t
        for t in range(Term):
            for l in range(num_Links):
                SL[t, l] = model.addVar(vtype=GRB.CONTINUOUS, name="SL%s_%s:" % (t, l), lb=-GRB.INFINITY,
                                        ub=GRB.INFINITY)
                # Slack for Free Link is a FREE SIGN!
        # print(SL)

        model.update()

        # set objective function
        model.setObjective(
            1 / Term * (quicksum(W_t * 1 - (1 / num_Input) *
                                 (quicksum((W_i * SI[t, m]) / X[o][t][m] for m in range(num_Input)))
                                 for t in range(Term)))
            , GRB.MINIMIZE)

        # add constraints
        for t in range(Term - 1):
            for l in range(num_Links):
                model.addConstr(
                    quicksum(Z[j][t][l] * lamd[t, j] for j in DMU) == quicksum(
                        Z[j][t][l] * lamd[t + 1, j] for j in DMU))

        for t in range(Term):
            for m in range(num_Input):
                Input_Constr[o, t, m] = model.addConstr(
                    quicksum(X[j][t][m] * lamd[t, j] for j in DMU) + SI[t, m] == X[o][t][m])

        for t in range(Term):
            for s in range(num_Output):
                Output_Constr[o, t, s] = model.addConstr(
                    # quicksum(Y[j][t][s] * lamd[t, j] for j in DMU) - SO[t, s] == Y[o][t][s])
                    quicksum(Y[j][t][s] * lamd[t, j] for j in DMU) >= Y[o][t][s])  # contr for input-oriented

        for t in range(Term):
            for l in range(num_Links):
                Link_Constr[o, t, l] = model.addConstr(
                    quicksum(Z[j][t][l] * lamd[t, j] for j in DMU) + SL[t, l] == Z[o][t][l])

        # Start optimize the formulation
        model.update()
        model.optimize()

        if model.solCount > 0:
            print("objective value (Theta) = %0.3f " % model.objVal)
        else:
            print("solution status = ", model.Status)

        if model.solCount == 0:
            print("Model is infeasible")
            model.computeIIS()
            model.write("model_iis.ilp")

        Eff[o] = model.objVal  # Efficiency score
        # for i in model.getVars():
        #     #l[r][i]= "The lamda and effiency of DMU %s: %0.3f"(i.varName, i.x)
        #     print("%s %0.3f"%(i.varName, i.x))#x get the lamda values and efficeincy score

        for t in range(Term):
            for j in DMU:
                L[o] = " %s %0.3f" % (lamd[t, j].varName, lamd[t, j].x)
                # print(L[o]) #lamda

        # for t in range(Term):
        #      for m in range(num_Input):
        #          print(SI[t,m].x)

        # slack result
        SO_sol = model.getAttr('x', SO)
        print("SO_sol", SO_sol)
        SI_sol = model.getAttr('x', SI)
        print("SI_sol", SI_sol)

        SL_sol = model.getAttr('x', SL)
        print("SL_sol", SL_sol)

        # calculate adjust score
        SL_sol_I = {}  # Slack_link_free*_negative
        SL_sol_O = {}  # Slack_link_free*_positive

        for t in range(Term):
            for l in range(num_Links):
                if SL_sol[t, l] > 0:
                    SL_sol_I[t, l] = SL_sol[t, l]
                elif SL_sol[t, l] <= 0:
                    SL_sol_I[t, l] = 0
        # print("SL_sol_I",SL_sol_I)

        for t in range(Term):
            for l in range(num_Links):
                if SL_sol[t, l] >= 0:
                    SL_sol_O[t, l] = 0
                elif SL_sol[t, l] < 0:
                    SL_sol_O[t, l] = -SL_sol[t, l]
        # print("SL_sol_O",SL_sol_O)

        upper = 1 / Term * (sum(W_t * (1 - (1 / (num_Input + num_Links)) * (
                (sum((W_i * SI_sol[t, m]) / X[o][t][m] for m in range(num_Input))) +
                (sum(SL_sol_I[t, l] / Z[o][t][l] for l in range(num_Links))))
                                       ) for t in range(Term)))

        # Overall Efficiency adjust score
        E_adjusted[o] = round(upper, 4)

        print("Eff adjusted score:", E_adjusted[o])

        model.write("output.sol")

        # Term efficiency
        for t in range(Term):
            E_term[o, t] = 1 - (1 / (num_Input + num_Links)) * (
                    (sum((W_i * SI_sol[t, m]) / X[o][t][m] for m in range(num_Input))) +
                    (sum(SL_sol_I[t, l] / Z[o][t][l] for l in range(num_Links))))

    print("------------------------")

    print("================= Print RESULT SUUMMARY =====================")

    for o in DMU:
        print("Eff adjusted score of DMU %s: %4.3g" % (o, E_adjusted[o]))
        for t in range(Term):
            print("The term %s Efficiency of DMU %s:%4.3g" % (t, o, E_term[o, t]))
        print("------------------------")

def df_to_dea(df):

    T1_X = pd.DataFrame()
    T1_X[0] = df.iloc[:, 0]
    #print(T1_X)

    T2_X = pd.DataFrame()
    T2_X[0] = df.iloc[:, 1]
    #print(T2_X)

    T3_X = pd.DataFrame()
    T3_X[0] = df.iloc[:, 2]
    #print(T3_X)

    T4_X = pd.DataFrame()
    T4_X[0] = df.iloc[:, 3]
    #print(T4_X)

    T_X = [T1_X, T2_X, T3_X, T4_X]
    #print(T_X)

    T1_Y = pd.DataFrame()
    T1_Y[0] = df.iloc[:, 4]
    #print(T1_Y)

    T2_Y = pd.DataFrame()
    T2_Y[0] = df.iloc[:, 5]
    #print(T2_Y)

    T3_Y = pd.DataFrame()
    T3_Y[0] = df.iloc[:, 6]
    #print(T3_Y)

    T4_Y = pd.DataFrame()
    T4_Y[0] = df.iloc[:, 7]
    #print(T4_Y)

    T_Y = [T1_Y, T2_Y, T3_Y, T4_Y]
    #print(T_Y)

    T1_Z = pd.DataFrame()
    T1_Z[0] = df.iloc[:, 8]
    #print(T1_Z)

    T2_Z = pd.DataFrame()
    T2_Z[0] = df.iloc[:, 9]
    #print(T2_Z)

    T3_Z = pd.DataFrame()
    T3_Z[0] = df.iloc[:, 10]
    #print(T3_Z)

    T4_Z = pd.DataFrame()
    T4_Z[0] = df.iloc[:, 11]
    #print(T4_Z)

    T_Z = [T1_Z, T2_Z, T3_Z, T4_Z]

    return T_X, T_Y, T_Z




def Dynamic_SBM(X, Y, Term, orientation, VRS, W_i, W_t, Z_Good=None, Z_Bad=None, Z_Free=None, Z_Fix=None):
    "this model is from Tone, Tsutsui (2010) Dynamic DEA paper"
    Result = pd.DataFrame()
    Eff = {}  # Efficiency score
    E_adjusted = {}  # Adjusted Efficiency score
    E_term = {}  # Adjusted Term Efficiency score
    E_adjusted_term = {}

    Input_Constr, Output_Constr = {}, {}
    Link_Free_Constr, Link_Good_Constr, Link_Bad_Constr, Link_Fix_Constr = {}, {}, {}, {}
    Lamda_Constr = {}

    num_Input = X[0].shape[1]  # numbers of input
    num_Output = Y[0].shape[1]  # numbers of Output



    if Z_Good is not None:
        num_Good_Links = Z_Good[0].shape[1]  # numbers of Good Links
    else:
        num_Good_Links = 0

    if Z_Free is not None:
        num_Free_Links = Z_Free[0].shape[1]  # numbers of Free Links
    else:
        num_Free_Links = 0

    if Z_Bad is not None:
        num_Bad_Links = Z_Bad[0].shape[1]  # numbers of Bad Links
    else:
        num_Bad_Links = 0

    if Z_Fix is not None:
        num_Fix_Links = Z_Fix[0].shape[1]  # numbers of Fix Links
    else:
        num_Fix_Links = 0


    print("\n ============== Model Specificaiton " + orientation + " oriented ..." + VRS + " VRS =====================")

    for o in range(X[0].shape[0]):
        DMU = X[0].shape[0]

        # print("Printing DMU...", DMU)
        SO, SI, L = {}, {}, {}
        SL_Good, SL_Free, SL_Bad, SL_Fix = {}, {}, {}, {}
        lamd = {}

        model = Model("DSBMDEA")
        model.setParam('OutputFlag', 0)  # Muting the optimize function

        # Add decision variables
        # lamda_j_t
        for t in range(Term):
            for j in range(DMU):
                lamd[t, j] = model.addVar(vtype=GRB.CONTINUOUS, name="λ_%s_%s:" % (t, j))

        # input slack
        for t in range(Term):
            if type(X[t]) == pd.DataFrame:
                for m in range(num_Input):
                    SI[t, m] = model.addVar(vtype=GRB.CONTINUOUS, name="SI%s_%s:" % (t, m))
        # print(SI)

        # output slack
        for t in range(Term):
            if type(Y[t]) == pd.DataFrame:
                for s in range(num_Output):
                    SO[t, s] = model.addVar(vtype=GRB.CONTINUOUS, name="SO%s_%s:" % (t, s))
        # print(SO)

        # free link slack  #SL_Free[t,l]= link l Slack at term t
        for t in range(Term):
            if Z_Free is not None:
                for l in range(num_Free_Links):
                    SL_Free[t, l] = model.addVar(vtype=GRB.CONTINUOUS, name="SL_Free%s_%s:" % (t, l), lb=-GRB.INFINITY,
                                                 ub=GRB.INFINITY)
                    # Slack for Free Link is a FREE SIGN!

        # Good Link Slack  #SL_Good[t, l]
        for t in range(Term):
            if Z_Good is not None:
                for l in range(num_Good_Links):
                    SL_Good[t, l] = model.addVar(vtype=GRB.CONTINUOUS, name="SL_Good%s_%s:" % (t, l))

        # Bad Link Slack  #SL_Bad[t, l]
        for t in range(Term):
            if Z_Bad is not None:
                for l in range(num_Bad_Links):
                    SL_Bad[t, l] = model.addVar(vtype=GRB.CONTINUOUS, name="SL_Bad%s_%s:" % (t, l))

        # Fix Link do not have slacks!
        #
        # if (orientation == 'non'):
        #     e = model.addVar(vtype=GRB.CONTINUOUS, name = "e")

        model.update()

        objective_XX = 0
        objective_YY = 0


        # set Objective
        if (orientation == 'input'):
            # if type(X) == pd.DataFrame:
            objective_XX = (1 / Term * (quicksum(W_t[t] * (1 - (1 / (num_Input + num_Bad_Links)) *
                                                           ((quicksum(W_i[m] * SI[t, m] / X[t][m][o] for m in
                                                                      range(num_Input))) +
                                                            (quicksum(SL_Bad[t, l] / Z_Bad[t][l][o] for l in
                                                                      range(num_Bad_Links)))))
                                                 for t in range(Term))))

            model.setObjective(objective_XX, GRB.MINIMIZE)


        elif (orientation == 'output'):

            objective_YY = (1 / Term * (quicksum(W_t[t] * (1 + (1 / (num_Output + num_Good_Links)) *
                                                           ((quicksum(W_i[m] * SO[t, m] / Y[t][m][o] for m in
                                                                      range(num_Output))) +
                                                            (quicksum(SL_Good[t, l] / Z_Good[t][l][o] for l in
                                                                      range(num_Good_Links)))))
                                                 for t in range(Term))))
            model.setObjective(objective_YY, GRB.MAXIMIZE)


        elif (orientation == 'non'):

            objective_XX = (1 / Term * (quicksum(W_t[t] * (1 - (1 / (num_Input + num_Bad_Links)) *
                                                           ((quicksum(W_i[m] * SI[t, m] / X[t][m][o] for m in
                                                                      range(num_Input))) +
                                                            (quicksum(SL_Bad[t, l] / Z_Bad[t][l][o] for l in
                                                                      range(num_Bad_Links)))))
                                                 for t in range(Term))))

            # objective_XX = (1 / Term * (quicksum(W_t[t] * (1 - (1 / num_Input + num_Bad_Links) *
            #                                                ((quicksum(W_i[m] * SI[t, m] / X[t][m][o] for m in
            #                                                           range(num_Input))) +
            #                                                 (quicksum(SL_Bad[t, l] / Z_Bad[t][l][o] for l in
            #                                                           range(num_Bad_Links)))))
            #                                      for t in range(Term))))

            # objective_YY = 1/(1 / Term * (quicksum(W_t[t] * (1 + (1 / num_Output + num_Good_Links) *
            #                                                ((quicksum(W_i[m] * SO[t, m] / Y[t][m][o] for m in
            #                                                           range(num_Output))) +
            #                                                 (quicksum(SL_Good[t, l] / Z_Good[t][l][o] for l in
            #                                                           range(num_Good_Links)))))
            #                                      for t in range(Term))))

            # final_obj = objective_XX * objective_YY

            model.setObjective(objective_XX, GRB.MINIMIZE)


        # add constraints (2)
        for t in range(Term - 1):
            # Free Link
            if Z_Free is not None:
                for l in range(num_Free_Links):
                    model.addConstr(quicksum(Z_Free[t][l][j] * lamd[t, j] for j in range(X[0].shape[0])) ==
                                    quicksum(Z_Free[t][l][j] * lamd[t + 1, j] for j in range(X[0].shape[0])))

            # Good Link
            if Z_Good is not None:
                for l in range(num_Good_Links):
                    model.addConstr(quicksum(Z_Good[t][l][j] * lamd[t, j] for j in range(X[0].shape[0])) ==
                                    quicksum(Z_Good[t][l][j] * lamd[t + 1, j] for j in range(X[0].shape[0])))

            # Bad Link
            if Z_Bad is not None:
                for l in range(num_Bad_Links):
                    model.addConstr(quicksum(Z_Bad[t][l][j] * lamd[t, j] for j in range(X[0].shape[0])) ==
                                    quicksum(Z_Bad[t][l][j] * lamd[t + 1, j] for j in range(X[0].shape[0])))

            # Fix Link
            if Z_Fix is not None:
                for l in range(num_Fix_Links):
                    model.addConstr(quicksum(Z_Fix[t][l][j] * lamd[t, j] for j in range(X[0].shape[0])) ==
                                    quicksum(Z_Fix[t][l][j] * lamd[t + 1, j] for j in range(X[0].shape[0])))

        # add constraints (3)
        for t in range(Term):

            # Input
            if type(X[t]) == pd.DataFrame:
                for m in range(num_Input):
                    Input_Constr[t, m, o] = model.addConstr(
                        quicksum(X[t][m][j] * lamd[t, j] for j in range(X[0].shape[0])) + SI[t, m] == X[t][m][o])
            # Output
            if type(Y[t]) == pd.DataFrame:
                for s in range(num_Output):
                    Output_Constr[t, s, o] = model.addConstr(
                        quicksum(Y[t][s][j] * lamd[t, j] for j in range(X[0].shape[0])) - SO[t, s] == Y[t][s][o])

            # Free Link
            if Z_Free != 0:
                for l in range(num_Free_Links):
                    Link_Free_Constr[t, l, o] = model.addConstr(
                        quicksum(Z_Free[t][l][j] * lamd[t, j] for j in range(X[0].shape[0])) + SL_Free[t, l] ==
                        Z_Free[t][l][o])
            else:
                Z_Free = 0

            # Good Link
            if Z_Good != 0:
                for l in range(num_Good_Links):
                    Link_Good_Constr[t, l, o] = model.addConstr(
                        quicksum(Z_Good[t][l][j] * lamd[t, j] for j in range(X[0].shape[0])) - SL_Good[t, l] ==
                        Z_Good[t][l][o])
            else:
                Z_Good = 0

            # Bad Link
            if Z_Bad != 0:
                for l in range(num_Bad_Links):
                    Link_Bad_Constr[t, l, o] = model.addConstr(
                        quicksum(Z_Bad[t][l][j] * lamd[t, j] for j in range(X[0].shape[0])) + SL_Bad[t, l] ==
                        Z_Bad[t][l][o])
            else:
                Z_Bad = 0

            # Fix Link
            if Z_Fix != 0:
                for l in range(num_Fix_Links):
                    Link_Fix_Constr[t, l, o] = model.addConstr(
                        quicksum(Z_Fix[t][l][j] * lamd[t, j] for j in range(X[0].shape[0])) == Z_Fix[t][l][o])
            else:
                Z_Fix = 0

            if VRS == 'yes':
                Lamda_Constr[o, t] = model.addConstr(quicksum(lamd[t, j] for j in range(X[0].shape[0])) == 1)

        if (orientation == "non"):
        #transform non-linear case to linear
            model.addConstr(1 == (1 / Term * (quicksum(W_t[t] * (1 + (1 / num_Output + num_Good_Links) *
                                                           ((quicksum(W_i[m] * SO[t, m]  / Y[t][m][o] for m in
                                                                      range(num_Output))) +
                                                            (quicksum(SL_Good[t, l] / Z_Good[t][l][o] for l in
                                                                      range(num_Good_Links)))))
                                                 for t in range(Term)))))


        # Start optimize the formulation
        model.update()
        model.optimize()

        # if model.solCount > 0:
        #     print("objective value (Theta) = %0.3f " % model.objVal)
        # else:
        #     print("solution status = ", model.Status)
        #
        # if model.solCount == 0:
        #     print("Model is infeasible")
        #     model.computeIIS()
        #     model.write("model_iis.ilp")

        # Slack_df = pd.DataFrame()
        # slack result
        SO_sol = model.getAttr('x', SO)
        df_SO_sol = pd.DataFrame.from_dict(SO_sol, orient='index',
                                           columns=["Output slack " + str(i + 1) for i in range(num_Output)])
        df_SO_sol.reset_index(inplace = True, drop = True)
        # Result.at[o, 'Output slack'] = SO_sol

        SI_sol = model.getAttr('x', SI)
        # Result.at[o, 'Input slack'] = SI_sol
        df_SI_sol = pd.DataFrame.from_dict(SI_sol, orient='index',
                                           columns=["Input slack " + str(i + 1) for i in range(num_Input)])
        # df_SO_sol["SI_sol"]  = df_SO_sol
        # df_SO_sol = pd.DataFrame.from_dict(SO_sol, orient= 'index', columns= [ "Output slack " + str(i + 1) for i in range (num_Output)])
        df_SI_sol.reset_index(inplace = True, drop = True)
        # df_SO_sol.assign()from_dict(SI_sol, orient= 'index', columns= [ "Input slack " + str(i + 1) for i in range (num_Input)] )

        if len(SL_Good) != 0:
            SL_Good_sol = model.getAttr('x', SL_Good)
            df_SL_Good_sol = pd.DataFrame.from_dict(SL_Good_sol, orient='index',
                                                    columns=["Good Link slack " + str(i + 1) for i in
                                                             range(num_Good_Links)])
            df_SL_Good_sol.reset_index(inplace = True, drop = True)
        else:
            df_SL_Good_sol = pd.DataFrame()

        if len(SL_Free) != 0:
            SL_Free_sol = model.getAttr('x', SL_Free)
            df_SL_Free_sol = pd.DataFrame.from_dict(SL_Free_sol, orient='index',
                                                    columns=["Free Link slack " + str(i + 1) for i in
                                                             range(num_Free_Links)])
            df_SL_Free_sol.reset_index(inplace = True, drop = True)

        else:
            df_SL_Free_sol = pd.DataFrame()

        if len(SL_Bad) != 0:
            SL_Bad_sol = model.getAttr('x', SL_Bad)
            df_SL_Bad_sol = pd.DataFrame.from_dict(SL_Bad_sol, orient='index',
                                                   columns=["Bad Link slack " + str(i + 1) for i in
                                                            range(num_Bad_Links)])
            df_SL_Bad_sol.reset_index(inplace = True, drop = True)
        else:
            df_SL_Bad_sol = pd.DataFrame()

        if len(SL_Fix) != 0:
            SL_Fix_sol = model.getAttr('x', SL_Fix)
            df_SL_fix_sol = pd.DataFrame.from_dict(SL_Fix_sol, orient='index',
                                                   columns=["Fix Link slack " + str(i + 1) for i in
                                                            range(num_Fix_Links)])
            df_SL_fix_sol.reset_index(inplace = True, drop = True)
        else:
            df_SL_fix_sol = pd.DataFrame()

        df_SL_All = pd.concat([df_SL_Good_sol, df_SL_Free_sol, df_SL_Bad_sol, df_SL_fix_sol], axis=1)
        #todo check what to do with this df[slacks, term, DMUo]
        if (orientation == 'input'):

            Result.at[o, 'Overall Efficiency Score'] = model.objVal
            # print("Overall Eff score", Result.at[o, 'Overall Efficiency Score'])

            # Term efficiency
            for t in range(Term):
                E_term[o, t] = 1 - (1 / (num_Input + num_Bad_Links)) * (
                        (sum(W_i[m] * SI_sol[t, m] / X[t][m][o] for m in range(num_Input))) +
                        (sum(SL_Bad_sol[t, l] / Z_Bad[t][l][o] for l in range(num_Bad_Links))))
                Result.at[o, 'Term Efficiency' + str(t + 1)] = E_term[o, t]


        elif (orientation == 'output'):
            Result.at[o, 'Overall  Efficiency Score'] = 1 / model.objVal

            # Term efficiency
            for t in range(Term):
                E_term[o, t] = 1/(1 + (1 / (num_Output + num_Good_Links)) * (
                        (sum((W_i[s] * SO_sol[t, s]) / Y[t][s][o] for s in range(num_Output))) +
                        (sum(SL_Good_sol[t, l] / Z_Good[t][l][o] for l in range(num_Good_Links)))))
                Result.at[o, 'Term Efficiency' + str(t + 1)] = E_term[o, t]


        elif (orientation == 'non'):
            Result.at[o, 'Overall  Efficiency Score'] = model.objVal

            # Term efficiency
            for t in range(Term):
                XX = 1 - (1 / (num_Input + num_Bad_Links)) * (
                        (sum((W_i[m] * SI_sol[t, m]) / X[t][m][o] for m in range(num_Input))) +
                        (sum(SL_Bad_sol[t, l] / Z_Bad[t][l][o] for l in range(num_Bad_Links))))
                YY = 1 + (1 / (num_Output + num_Good_Links)) * (
                        (sum((W_i[s] * SO_sol[t, s]) / Y[t][s][o] for s in range(num_Output))) +
                        (sum(SL_Good_sol[t, l] / Z_Good[t][l][o] for l in range(num_Good_Links))))

                E_term[o, t] = XX / YY
                Result.at[o, 'Term Efficiency' + str(t + 1)] = E_term[o, t]

        # Eff[o] = model.objVal  #Efficiency score
        # for i in model.getVars():
        #     #l[r][i]= "The lamda and effiency of DMU %s: %0.3f"(i.varName, i.x)
        #     print("%s %0.3f"%(i.varName, i.x))#x get the lamda values and efficeincy score

        for t in range(Term):
            for j in range(DMU):
                L[o, t] = (lamd[t, j].x)
                Result.at[o, 'Lamda' + str(t + 1)] = L[o, t]

        # calculate adjust score
        SL_Free_sol_I = {}  # Slack_link_free*_negative
        SL_Free_sol_O = {}  # Slack_link_free*_positive

        if len(SL_Free) != 0:
            for t in range(Term):
                for l in range(num_Free_Links):
                    if SL_Free_sol[t, l] > 0:
                        SL_Free_sol_I[t, l] = SL_Free_sol[t, l]
                    elif SL_Free_sol[t, l] <= 0:
                        SL_Free_sol_I[t, l] = 0
            df_SL_Free_sol_I = pd.DataFrame.from_dict(SL_Free_sol_I, orient='index',
                                                      columns=["Free Link slack Input (Adjusted) " + str(i + 1) for i in
                                                               range(num_Free_Links)])
            df_SL_Free_sol_I.reset_index(inplace = True, drop = True)

            for t in range(Term):
                for l in range(num_Free_Links):
                    if SL_Free_sol[t, l] >= 0:
                        SL_Free_sol_O[t, l] = 0
                    elif SL_Free_sol[t, l] < 0:
                        SL_Free_sol_O[t, l] = -SL_Free_sol[t, l]
            df_SL_Free_sol_O = pd.DataFrame.from_dict(SL_Free_sol_O, orient='index',
                                                      columns=["Free Link slack Output (Adjusted) " + str(i + 1) for i
                                                               in range(num_Free_Links)])
            df_SL_Free_sol_O.reset_index(inplace = True, drop = True)
            df_SL_All = pd.concat([df_SL_All, df_SL_Free_sol_I, df_SL_Free_sol_O], axis=1)
        else:
            df_SL_All = pd.concat([df_SL_All], axis=1)

        # print(df_SL_All)

        if (orientation == 'input'):

            adjust_Eff_Score = (1 / Term * (sum(W_t[t] * (1 - (1 / (num_Input + num_Bad_Links + num_Free_Links)) * (
                    (sum(W_i[m] * SI_sol[t, m] / X[t][m][o] for m in range(num_Input))) +
                    (sum(SL_Bad_sol[t, l] / Z_Bad[t][l][o] for l in range(num_Bad_Links))) + (
                        sum(SL_Free_sol_I[t, l] / Z_Free[t][l][o] for l in range(num_Free_Links))))) for t in
                                                range(Term))))
            Result.at[o, 'Adjusted Overall Efficiency Score'] = adjust_Eff_Score

            # Term efficiency
            for t in range(Term):
                E_adjusted_term[o, t] = 1 - (1 / (num_Input + num_Bad_Links + num_Free_Links)) * (
                        (sum((W_i[m] * SI_sol[t, m]) / X[t][m][o] for m in range(num_Input))) +
                        (sum(SL_Bad_sol[t, l] / Z_Bad[t][l][o] for l in range(num_Bad_Links))) +
                        (sum(SL_Free_sol_I[t, l] / Z_Free[t][l][o] for l in
                             range(num_Free_Links))))
                Result.at[o, 'Adjusted Term Efficiency' + str(t + 1)] = E_adjusted_term[o, t]



        elif (orientation == 'output'):

            adjust_Eff_Score = (1 / Term * (sum(W_t[t] * (1 + (1 / (num_Output + num_Good_Links + num_Free_Links)) *
                                                          ((sum(W_i[m] * SO_sol[t, m] / Y[t][m][o] for m in
                                                                range(num_Output))) +
                                                           (sum(SL_Good_sol[t, l] / Z_Good[t][l][o] for l in
                                                                range(num_Good_Links))) + (
                                                               sum(SL_Free_sol_O[t, l] / Z_Free[t][l][o] for l in
                                                                   range(num_Free_Links)))))
                                                for t in range(Term))))
            Result.at[o, 'Adjusted Overall Efficiency Score'] = 1 / adjust_Eff_Score

            # Term efficiency
            for t in range(Term):
                E_adjusted_term[o, t] = 1/(1 + (1 / (num_Output + num_Good_Links + num_Free_Links)) * (
                        (sum((W_i[s] * SO_sol[t, s]) / Y[t][s][o] for s in range(num_Output))) +
                        (sum(SL_Good_sol[t, l] / Z_Good[t][l][o] for l in range(num_Good_Links))) +
                        (sum(SL_Free_sol_O[t, l] / Z_Free[t][l][o] for l in
                             range(num_Free_Links)))))
                Result.at[o, 'Adjusted Term Efficiency' + str(t + 1)] = E_adjusted_term[o, t]

        elif (orientation == 'non'):

            adj_XX = (1 / Term * (sum(W_t[t] * (1 - (1 / (num_Input + num_Bad_Links + num_Free_Links)) *
                                                     ((sum(W_i[m] * SI_sol[t, m] / X[t][m][o] for m in
                                                                range(num_Input))) +
                                                      (sum(SL_Bad_sol[t, l] / Z_Bad[t][l][o] for l in
                                                                range(num_Bad_Links))) + (
                                                          sum(SL_Free_sol_I[t, l] / Z_Free[t][l][o] for l in
                                                                   range(num_Free_Links)))))
                                                     for t in range(Term))))
            adj_YY = (1 / Term * (sum(W_t[t] * (1 + (1 / (num_Output + num_Good_Links + num_Free_Links)) *
                                                     ((sum(W_i[m] * SO_sol[t, m] / Y[t][m][o] for m in
                                                                range(num_Output))) +
                                                      (sum(SL_Good_sol[t, l] / Z_Good[t][l][o] for l in
                                                                range(num_Good_Links))) + (
                                                          sum(SL_Free_sol_O[t, l] / Z_Free[t][l][o] for l in
                                                                   range(num_Free_Links)))))
                                                     for t in range(Term))))
            adjust_Eff_Score = adj_XX / adj_YY

            Result.at[o, 'Adjusted Overall Efficiency Score'] = adjust_Eff_Score

            # Term efficiency
            for t in range(Term):
                XX = 1 - (1 / (num_Input + num_Bad_Links + num_Free_Links)) * (
                        (sum((W_i[m] * SI_sol[t, m]) / X[t][m][o] for m in range(num_Input))) +
                        (sum(SL_Bad_sol[t, l] / Z_Bad[t][l][o] for l in range(num_Bad_Links))) +
                        sum(SL_Free_sol_I[t, l] / Z_Free[t][l][o] for l in
                            range(num_Free_Links)))
                YY = 1 + (1 / (num_Output + num_Good_Links + num_Free_Links)) * (
                        (sum((W_i[s] * SO_sol[t, s]) / Y[t][s][o] for s in range(num_Output))) +
                        (sum(SL_Good_sol[t, l] / Z_Good[t][l][o] for l in range(num_Good_Links))) +
                        sum(SL_Free_sol_O[t, l] / Z_Free[t][l][o] for l in
                            range(num_Free_Links)))

                E_adjusted_term[o, t] = XX / YY
                Result.at[o, 'Adjusted Term Efficiency' + str(t + 1)] = E_adjusted_term[o, t]
                # print("Eff adjusted term score", round(E_adjusted_term[o, t]))

        model.write("output.sol")

    print("===================  RUN RESULT SUUMMARY ========================")


    for o in range(DMU):
        print("Eff adjusted score of DMU %s: %4.3g" % (o, Result.at[o, 'Adjusted Overall Efficiency Score']))
        for t in range(Term):
            print("The term %s Efficiency of DMU %s:%4.3g" % (t, o, E_adjusted_term[o, t]))
        print("------------------------")

    return Result
