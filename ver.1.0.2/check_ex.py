import connection as cn

df = cn.pd.DataFrame(cn.Worksheet.select_final.get_all_records())
df_cus = cn.Dataframes.cus
df_cus = df_cus.sort_values('Date', ascending=True)
loop_txt = cn.Dataframes.box_loop
loop_txt = loop_txt.set_index("tag")
check_group = loop_txt.loc['추가 Group', 'contents'].replace(" ", "").split(",")

for idx, row in df.iterrows():
    refer_email = row['From Email Address']
    df_temp = df_cus[df_cus['Email'] == refer_email]
    if row['Item_ex'] == '':
        pass
    else:
        temp_item = row['Item_ex'].split('\n')
        temp_pre = row['Preference'].replace(" ", "")
        if temp_pre.find('nothingso,') >= 0:
            temp_pre = temp_pre.replace('nothingso,', '')
        temp_line = temp_pre.split(",")
        for i in check_group:
            if i in temp_line:
                name = loop_txt.loc[i, 'contents'].replace(" ", "").split(",")
                members = []
                for j in name:
                    members.insert(len(members), i + '_' + j)
                temp_line.extend(members)
        
        
        check_pre = []
        check_dup = []
        if df_temp.empty:
            for i in temp_item:
                check_dup.insert(len(check_dup), "0")
        else:
            df_temp = df_temp.drop_duplicates(['Email'], keep='last')
            if df_temp.iloc[0]['List'] == '':
                for i in temp_item:
                    check_dup.insert(len(check_dup), "0")
            else:
                row_list = df_temp.iloc[0]['List'].lower()
                for i in temp_item:
                    if '-' in i:
                        item_name = i.split('-')[1]
                    else:
                        item_name = i
                    _name = i.replace('-', '_')
                    
                    if row_list.find(_name) >= 0:
                        item_count = row_list.count(item_name)
                        item_num = str(item_count) + ', ' + 'D'
                        check_dup.insert(len(check_dup), item_num)
                    else:
                        item_count = row_list.count(item_name)
                        check_dup.insert(len(check_dup), str(item_count))
        str_check_dup = "\n".join(check_dup)
        row['dup_check'] = str_check_dup
        
        for i in temp_item:
            if '-' in i:
                pre_name = i.split('-')[0]
            else:
                pre_name = i

            if pre_name in temp_line:
                pre_check = '존재'
                check_pre.insert(len(check_pre), pre_check)
            else:
                pre_check = 'X'
                check_pre.insert(len(check_pre), pre_check)
        str_check_pre = "\n".join(check_pre)
        row['pre_check'] = str_check_pre
    
cn.pandas_to_sheets(df, cn.Worksheet.select_final, True)