import connection as cn

def warning():
    print('경고 실행 \n')
    loop_txt = cn.Dataframes.box_loop
    temp1 = loop_txt.iloc[0, 0]
    temp2 = loop_txt.iloc[1, 0]
    warning_state1 = temp1.replace(" ", "").split(",")
    warning_state2 = temp2.replace(" ", "").split(",")
    dfcheck_df1 = cn.pd.DataFrame(cn.Worksheet.select.get_all_records())
    check_df1 = dfcheck_df1
    check_df2 = dfcheck_df1

    for index1, row1 in check_df1.iterrows():
        if (row1['Shipping Courier'] == 'EMS') or (row1['Shipping Courier'] == '선박'):
            row1['Warning'] = 'Warning 2'
        elif row1['Shipping Courier'] == 'Error : shipping courier not defined':
            row1['Warning'] = 'Warning 3'
        for index2, row2 in check_df2.iterrows():
            if (row1['Name'] == row2['Name']) & (row1['Shipping Address'] != row2['Shipping Address']):
                row1['Warning'] = 'Warning 1'
                row2['Warning'] = 'Warning 1'
            elif (row1['From Email Address'] == row2['From Email Address']) & (row1['Shipping Address'] != row2['Shipping Address']):
                row1['Warning'] = 'Warning 1'
                row2['Warning'] = 'Warning 1'
            elif (row1['Shipping Courier'] == 'EMS') or (row1['Shipping Courier'] == '선박'):
                row1['Warning'] = 'Warning 2'
            elif row1['Shipping Courier'] == 'Error : shipping courier not defined':
                row1['Warning'] = 'Warning 3'
                
    df = check_df1.append(check_df2)
    df = df.drop_duplicates(['Reference Txn ID', 'From Email Address', 'Shipping Address', 'Item Title', 'Date', 'Name'], keep = 'last')

    df = df.sort_values(by=['Date'])
    cn.pandas_to_sheets(df, cn.Worksheet.select, False)

if __name__ == '__main__':
    warning()