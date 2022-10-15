import connection as cn

def select_item(row):
    seperate = '---------'
    if str(row['Confirm']).lower() == 'a':
        item_alpha = row['Items_Alpha'].strip().split('\n')
        if seperate in item_alpha:
            idx = item_alpha.index(seperate)
            row['Item'] = '\n'.join(item_alpha[:idx])
        else:
            row['Item'] = '\n'.join(item_alpha)
    elif str(row['Confirm']).lower() == 'b':
        item_alpha = row['Items_Alpha'].strip().split('\n')
        if seperate in item_alpha:
            idx = item_alpha.index(seperate)
            row['Item'] = '\n'.join(item_alpha[idx+1:])
        else:
            row['Item'] = 'B루프가 없습니다'
    elif str(row['Confirm']) == '1':
        item_num = row['Items_Num'].strip().split('\n')
        if seperate in item_num:
            idx = item_num.index(seperate)
            row['Item'] = '\n'.join(item_num[:idx])
        # else:
        #     row['Item'] = '\n'.join(item_alpha)
    elif str(row['Confirm']) == '2':
        item_num = row['Items_Num'].strip().split('\n')
        if seperate in item_num:
            idx = item_num.index(seperate)
            row['Item'] = '\n'.join(item_num[idx+1:])
    else:
        row_date = cn.datetime.datetime.strptime(row['Date'], "%Y-%m-%d")
        row_date = row_date + cn.relativedelta(months=1)
        row_date = row_date.strftime("%m")
        row['Item'] = row_date + '월 ' + row['Item Title']
    return row

def main():
    df = cn.pd.DataFrame(cn.Worksheet.select_final.get_all_records())
    for idx, row in df.iterrows():
        if (row['Ship'][len(row['Ship'])-1] == "O") & (row['Confirm'] != ''):
            row = select_item(row)
    
    df.to_csv('log.csv')
    cn.pandas_to_sheets(df, cn.Worksheet.select_final, False)

if __name__ == "__main__":
    main()