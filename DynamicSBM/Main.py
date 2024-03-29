from gurobipy import *
import pandas as pd
import DSBMFunction

# def df_to_dea(df):
#
#     T1_X = pd.DataFrame()
#     T1_X[0] = df.iloc[:, 0]
#     #print(T1_X)
#
#     T2_X = pd.DataFrame()
#     T2_X[0] = df.iloc[:, 1]
#     #print(T2_X)
#
#     T3_X = pd.DataFrame()
#     T3_X[0] = df.iloc[:, 2]
#     #print(T3_X)
#
#     T4_X = pd.DataFrame()
#     T4_X[0] = df.iloc[:, 3]
#     #print(T4_X)
#
#     T_X = [T1_X, T2_X, T3_X, T4_X]
#     #print(T_X)
#
#     T1_Y = pd.DataFrame()
#     T1_Y[0] = df.iloc[:, 4]
#     #print(T1_Y)
#
#     T2_Y = pd.DataFrame()
#     T2_Y[0] = df.iloc[:, 5]
#     #print(T2_Y)
#
#     T3_Y = pd.DataFrame()
#     T3_Y[0] = df.iloc[:, 6]
#     #print(T3_Y)
#
#     T4_Y = pd.DataFrame()
#     T4_Y[0] = df.iloc[:, 7]
#     #print(T4_Y)
#
#     T_Y = [T1_Y, T2_Y, T3_Y, T4_Y]
#     #print(T_Y)
#
#     T1_Z = pd.DataFrame()
#     T1_Z[0] = df.iloc[:, 8]
#     #print(T1_Z)
#
#     T2_Z = pd.DataFrame()
#     T2_Z[0] = df.iloc[:, 9]
#     #print(T2_Z)
#
#     T3_Z = pd.DataFrame()
#     T3_Z[0] = df.iloc[:, 10]
#     #print(T3_Z)
#
#     T4_Z = pd.DataFrame()
#     T4_Z[0] = df.iloc[:, 11]
#     #print(T4_Z)
#
#     T_Z = [T1_Z, T2_Z, T3_Z, T4_Z]
#
#
#
#     #print("####### Z #######")
#     #print(T_Z)
#
#     # print("Check Z shape...")
#     # print(T_Z[0].shape[1])
#     # print(T_Z[0].shape[0])
#     # print(T_Z[1].shape[0])
#     # #print(T_Z[1][1][1])
#     # print(T_Z[1][0][0])
#     # print(T_Z[1][0][1])
#     # print(T_Z[1][0][2])
#     # print(T_Z[3][0][1])
#     # print(T_Z)
#     return T_X, T_Y, T_Z

def main():
    df = pd.read_csv("Sample_Dataset/DDEA_example_data.csv", index_col=0)
    # print(df)
    W_i = [1] #Weights for inputs
    W_t = [1,1,1,1] #Weights for outputs
    # W_t = pd.DataFrame(wt)
    T_X, T_Y, T_Z = DSBMFunction.df_to_dea(df)
    Test_Result = DSBMFunction.Dynamic_SBM(T_X, T_Y, Term=4, orientation="input", VRS='no', Z_Free=T_Z, W_t= W_t, W_i = W_i)
    # Test_Result.to_excel("Test_Result.xlsx")

    # Test_Result_output = DSBMFunction.Dynamic_SBM(T_X, T_Y, Term=4, orientation="output", VRS='no', Z_Free=T_Z, W_t= W_t, W_i = W_i)
    #Test_Result_output.to_excel("Test_Result_output.xlsx")
    #print(Test_Result_output)




if __name__ =="__main__":
    main()




