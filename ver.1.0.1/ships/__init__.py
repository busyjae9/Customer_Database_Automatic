import connection as cn


# 3, 4월 구매 데이터와 5월 케이팝 박스 회원 비교 후 5월에 있는 고객들이 보내야하는 지 확인하는 메소드 - 이전 2개월의 데이터와 현재 데이터 중 중복 값을 확인 후 보내야하는지 확인
# 비고가 비어있는 회원만 추출

def replaceRight(original, old, new, count_right):
    repeat = 0
    text = original
    old_len = len(old)

    count_find = original.count(old)
    if count_right > count_find:  # 바꿀 횟수가 문자열에 포함된 old보다 많다면
        repeat = count_find  # 문자열에 포함된 old의 모든 개수(count_find)만큼 교체한다
    else:
        repeat = count_right  # 아니라면 입력받은 개수(count)만큼 교체한다

    while(repeat):
      find_index = text.rfind(old)  # 오른쪽부터 index를 찾기위해 rfind 사용
      text = text[:find_index] + new + text[find_index+old_len:]

      repeat -= 1

    return text


def select_ship_one(df):
    df_not_ship = cn.pd.DataFrame()
    df_ship_id_match = cn.pd.DataFrame()
    df_ship_email_match = cn.pd.DataFrame()
    # df_ship_address_match = cn.pd.DataFrame()

    df_one_ago_blank = cn.Dataframes.order_one_month[cn.Dataframes.order_one_month['비고'] == '']
    # df_one_ago_blank = cn.Dataframes.select_one_month[cn.Dataframes.select_one_month['Ship'] == 'XXXXX']
    df['Ship'] = ''

    # 첫 달 전부 확인
    for index, row in df.iterrows():
        row['Ship'] = 'X'
        df_not_ship = df_not_ship.append(row)
        for i in list(set(df_one_ago_blank['Reference Txn ID'])):
            if row['Reference Txn ID'] == '':
                pass
            elif row['Reference Txn ID'] == i:
                row['Ship'] = 'O'
                df_ship_id_match = df_ship_id_match.append(row)
        for i in list(set(df_one_ago_blank['From Email Address'])):
            if row['From Email Address'] == i:
                row['Ship'] = 'O'
                df_ship_email_match = df_ship_email_match.append(row)
        # for i in list(set(df_one_ago_blank['Shipping Address'])):
        #     if row['Shipping Address'] == i:
        #         row['Ship'] = 'O'
        #         df_ship_address_match = df_ship_address_match.append(row)

    # 모든 데이터를 하나로 모음
    df_all_ship = df_not_ship.append(df_ship_id_match)
    df_all_ship = df_all_ship.append(df_ship_email_match)
    # df_all_ship = df_all_ship.append(df_ship_address_match)

    # 데이터 중복값을 삭제
    df_all_ship = df_all_ship.drop_duplicates(
        ['Reference Txn ID', 'From Email Address', 'Shipping Address', 'Item Title', 'Date', 'Name'], keep='last')
    df_all_ship = df_all_ship.sort_index()
    df_all_ship = df_all_ship.sort_values(by=['Ship', 'Date'], axis=0)
    df_all_ship = df_all_ship[['Date', 'Type', 'Reference Txn ID', 'Name',
                               'From Email Address', 'Shipping Address', 'Item Title', 'New', 'Ship']]
    return df_all_ship


def select_ship_two(df_all_ship):
    df_not_ship = cn.pd.DataFrame()
    df_ship_id_match = cn.pd.DataFrame()
    df_ship_email_match = cn.pd.DataFrame()
    # df_ship_address_match = cn.pd.DataFrame()

    df_two_ago_blank = cn.Dataframes.order_two_months[cn.Dataframes.order_two_months['비고'] == '']
    # df_two_ago_blank = cn.Dataframes.select_two_months[cn.Dataframes.select_two_months['Ship'] == 'XXXXX']

    for index, row in df_all_ship.iterrows():
        row['Ship'] = row['Ship'] + 'X'
        df_not_ship = df_not_ship.append(row)
        for i in list(set(df_two_ago_blank['Reference Txn ID'])):
            if row['Reference Txn ID'] == '':
                pass
            elif row['Reference Txn ID'] == i:
                if row['Ship'][len(row['Ship']) - 1] == 'O':
                    pass
                else:
                    row['Ship'] = replaceRight(row['Ship'], 'X', 'O', 1)
                df_ship_id_match = df_ship_id_match.append(row)
        for i in list(set(df_two_ago_blank['From Email Address'])):
            if row['From Email Address'] == i:
                if row['Ship'][len(row['Ship']) - 1] == 'O':
                    pass
                else:
                    row['Ship'] = replaceRight(row['Ship'], 'X', 'O', 1)
                df_ship_email_match = df_ship_email_match.append(row)
        # for i in list(set(df_two_ago_blank['Shipping Address'])):
        #     if row['Shipping Address'] == i:
        #         if row['Ship'].find('B') == False :
        #             row['Ship'] = row['Ship'] + 'B'
        #         df_ship_address_match = df_ship_address_match.append(row)

    # 모든 데이터를 하나로 모음
    df_all_ship = df_not_ship.append(df_ship_id_match)
    df_all_ship = df_all_ship.append(df_ship_email_match)
    # df_all_ship = df_all_ship.append(df_ship_address_match)

    df_all_ship = df_all_ship.drop_duplicates(
        ['Reference Txn ID', 'From Email Address', 'Shipping Address', 'Item Title', 'Date', 'Name'], keep='last')
    df_all_ship = df_all_ship[['Date', 'Type', 'Reference Txn ID', 'Name',
                               'From Email Address', 'Shipping Address', 'Item Title', 'New', 'Ship']]

    return df_all_ship


def select_ship_2(df_all_ship):
    # 이번 달 2회 이상 구매 확인
    df_this_month = cn.pd.DataFrame()

    for index, row in df_all_ship.iterrows():
        email_list = list(df_all_ship['From Email Address'])
        email_list2 = len(list(df_all_ship['From Email Address']))
        while row['From Email Address'] in email_list:
            email_list.remove(row['From Email Address'])
        if email_list2 - len(email_list) >= 2:
            row['Ship'] = row['Ship'] + 'O'
            df_this_month = df_this_month.append(row)
        else:
            row['Ship'] = row['Ship'] + 'X'
            df_this_month = df_this_month.append(row)

    # 데이터 중복값을 삭제하면서, 새로운 회원과 기존 회원 구분
    df_all_ship = df_all_ship.append(df_this_month)
    df_all_ship = df_all_ship.drop_duplicates(
        ['Reference Txn ID', 'From Email Address', 'Shipping Address', 'Item Title', 'Date', 'Name'], keep='last')
    df_all_ship = df_all_ship[['Date', 'Type', 'Reference Txn ID', 'Name',
                               'From Email Address', 'Shipping Address', 'Item Title', 'New', 'Ship']]
    return df_all_ship


def select_ship_monthly(df_all_ship):
    # df_not_ship = cn.pd.DataFrame()
    # df_ship_id_match = cn.pd.DataFrame()
    # df_ship_email_match = cn.pd.DataFrame()
    # # df_ship_address_match = cn.pd.DataFrame()

    # monthly 텍스트가 붙어있는 아이템은 표시
    for index, row in df_all_ship.iterrows():
        row['Ship'] = row['Ship'] + 'X'

        if row['Item Title'].lower().find('monthly') >= 0:
            row['Ship'] = replaceRight(row['Ship'], 'X', 'O', 1)
            # if row['Item Title'].lower().find('bi-monthly') >= 0:
            #     row['Ship'] = replaceRight(row['Ship'], 'O', 'X', 1)
        else:
            pass

        # df_not_ship = df_not_ship.append(row)
        # for i in list(set(df_this_month_ago_blank['Reference Txn ID'])):
        #     if row['Reference Txn ID'] == '':
        #         pass
        #     elif row['Reference Txn ID'] == i:
        #         if row['Ship'].find('V') != -1 :
        #             pass
        #         else :
        #             row['Ship'] = row['Ship'].replace('N', 'V')
        #         df_ship_id_match = df_ship_id_match.append(row)
        # for i in list(set(df_this_month_ago_blank['From Email Address'])):
        #     if row['From Email Address'] == i:
        #         if row['Ship'].find('V') != -1 :
        #             pass
        #         else :
        #             row['Ship'] = row['Ship'].replace('N', 'V')
        #         df_ship_email_match = df_ship_email_match.append(row)
        # for i in list(set(df_two_ago_blank['Shipping Address'])):
        #     if row['Shipping Address'] == i:
        #         if row['Ship'].find('B') == False :
        #             row['Ship'] = row['Ship'] + 'B'
        #         df_ship_address_match = df_ship_address_match.append(row)

    # # 모든 데이터를 하나로 모음
    # df_all_ship = df_not_ship.append(df_ship_id_match)
    # df_all_ship = df_all_ship.append(df_ship_email_match)
    # df_all_ship = df_all_ship.append(df_ship_address_match)

    # df_all_ship = df_all_ship.drop_duplicates(['Reference Txn ID', 'From Email Address', 'Shipping Address', 'Item Title', 'Date', 'Name'], keep = 'last')
    df_all_ship = df_all_ship[['Date', 'Type', 'Reference Txn ID', 'Name',
                               'From Email Address', 'Shipping Address', 'Item Title', 'New', 'Ship']]
    df_all_ship = df_all_ship.sort_index()
    return df_all_ship


def take_line_two(df):
    final_df = cn.pd.DataFrame()
    is_o = df[df['Ship'].apply(lambda x: x.find('O') == 1)]
    df_two_ago_blank = cn.Dataframes.order_two_months[cn.Dataframes.order_two_months['비고'] == '']
    filter_keys = ["Subscription Payment", "Express Checkout Payment",
           "General Payment", "Mobile Payment", "Website Payment"]
    df_mask = df_two_ago_blank['Type']
    purchase = df_mask.isin(filter_keys)
    df_two_ago_blank = df_two_ago_blank[purchase]
    df_two_ago_blank = df_two_ago_blank[[
        'From Email Address', 'Date', 'Type', 'Reference Txn ID', 'Name', 'Shipping Address', 'Item Title']]
    # df_two_ago_blank = df_two_ago_blank.rename(
    #     columns={'Item Title': 'Item Title'})

    for index, row1 in df_two_ago_blank.iterrows():
        temp_df = cn.pd.DataFrame()
        for index, row2 in is_o.iterrows():
            if row1['Reference Txn ID'] == '':
                pass
            elif row1['Reference Txn ID'] == row2['Reference Txn ID']:
                temp_df = temp_df.append(row1)
            elif row1['From Email Address'] == '':
                pass
            elif row1['From Email Address'] == row2['From Email Address']:
                temp_df = temp_df.append(row1)
        if len(temp_df) >= 2:
            temp_df = temp_df.drop_duplicates(['Reference Txn ID', 'From Email Address', 'Item Title', 'Date', 'Name'], keep='last')
            # temp_df = temp_df.drop_duplicates(['Reference Txn ID', 'From Email Address', 'Shipping Address', 'Item Title', 'Date', 'Name'], keep='last')
        final_df = final_df.append(temp_df)

    final_df = final_df.assign(New = 'Existed', Ship = 'two_month_O')
    df = df.append(final_df)

    return df

def take_line_one(df):
    final_df = cn.pd.DataFrame()
    is_o = df[df['Ship'].apply(lambda x: x.find('O') == 0)]
    df_one_ago_blank = cn.Dataframes.order_one_month[cn.Dataframes.order_one_month['비고'] == '']
    filter_keys = ["Subscription Payment", "Express Checkout Payment",
           "General Payment", "Mobile Payment", "Website Payment"]
    df_mask = df_one_ago_blank['Type']
    purchase = df_mask.isin(filter_keys)
    df_one_ago_blank = df_one_ago_blank[purchase]
    df_one_ago_blank = df_one_ago_blank[
        ['From Email Address', 'Date', 'Type', 'Reference Txn ID', 'Name', 'Shipping Address', 'Item Title']]
    # df_one_ago_blank = df_one_ago_blank.rename(
    #     columns={'Item Title': 'Item Title'})

    for index, row1 in df_one_ago_blank.iterrows():
        temp_df = cn.pd.DataFrame()
        for index, row2 in is_o.iterrows():
            if row1['Reference Txn ID'] == '':
                pass
            elif row1['Reference Txn ID'] == row2['Reference Txn ID']:
                temp_df = temp_df.append(row1)
            elif row1['From Email Address'] == '':
                pass
            elif row1['From Email Address'] == row2['From Email Address']:
                temp_df = temp_df.append(row1)
        if len(temp_df) >= 2:
            temp_df = temp_df.drop_duplicates(
                ['Reference Txn ID', 'From Email Address', 'Item Title', 'Date', 'Name'], keep='last')
            # temp_df = temp_df.drop_duplicates(['Reference Txn ID', 'From Email Address', 'Shipping Address', 'Item Title', 'Date', 'Name'], keep='last')
        final_df = final_df.append(temp_df)

    final_df = final_df.assign(New = 'Existed', Ship = 'one_month_O')
    df = df.append(final_df)

    return df

def select_courier(df):
    df['Shipping Courier'] = ''    
    for idx, row in df.iterrows():
        is_row = df['From Email Address'] == row['From Email Address']
        df_dup = df[is_row]
        row_item = row['Item Title'].lower()
        row_address = row['Shipping Address'].replace(" ", "").split(",")
        US_filter = ['HI', 'PR', 'GU', 'AE', 'AP', 'AA']
        if df_dup.shape[0] == 1:
            row['Shipping Courier'] = 'Error : shipping courier not defined'
            if row_item.find('(dhlmonthly)') >= 0:
                row['Shipping Courier'] = 'DHL'
            elif row_item.find('(bi-monthly)') >= 0:
                row['Shipping Courier'] = 'DHL'
                if (row_address[-1] == 'UnitedStates') & (row_address[-3] in ['AE', 'AP', 'AA']):
                    row['Shipping Courier'] = 'Error : shipping courier not defined'
            elif row_item.find('(monthly)') >= 0:
                if row_address[-1] in ['Canada', 'Germany', 'UnitedKingdom', 'Italy']:
                    row['Shipping Courier'] = 'KP'
                elif row_address[-1] == 'UnitedStates':
                    row['Shipping Courier'] = 'SF Express'
                    if row_address[-3] in US_filter:
                        row['Shipping Courier'] = 'Error : shipping courier not defined'
                    elif row_address[-3] == 'AK':
                        row['Shipping Courier'] = 'KP'
        elif df_dup.shape[0] == 2:
            row['Shipping Courier'] = 'DHL'
            is_snack = False
            is_monthly = False
            for idx, row_dup in df_dup.iterrows():
                if row_dup['Item Title'].lower().find('ksnackregular') >= 0 :
                    is_snack = True
                    if row_dup['Item Title'].lower().find('(dhlmonthly)') >= 0:
                        is_monthly = False
                        is_snack = False
                else : 
                    if row_dup['Item Title'].lower().find('monthly') >= 0:
                        is_monthly = True
                        if row_dup['Item Title'].lower().find('bi-monthly') >= 0:
                            is_monthly = False
                        elif row_dup['Item Title'].lower().find('dhlmonthly') >= 0:
                            is_monthly = False
                    is_snack = False
            
            if is_snack:
                if row_address[-1] in ['Canada', 'Germany', 'UnitedKingdom']:
                    row['Shipping Courier'] = 'KP'
                elif row_address[-1] == 'UnitedStates':
                    row['Shipping Courier'] = 'SF Express'
                    if row_address[-3] in ['HI, PR']:
                        row['Shipping Courier'] = 'DHL'
                    elif row_address[-3] in ['GU', 'AE', 'AP', 'AA']:
                        row['Shipping Courier'] = 'Error : shipping courier not defined'
                    elif row_address[-3] == 'AK':
                            row['Shipping Courier'] = 'KP'
            elif is_monthly:
                if row_address[-1] in ['Canada', 'Germany', 'UnitedKingdom']:
                    row['Shipping Courier'] = 'KP'
        elif df_dup.shape[0] > 2:
            row['Shipping Courier'] = 'DHL'
        
        if row['From Email Address'] == "pomme63@outlook.com":
            row['Shipping Courier'] = 'EMS'
        elif row['From Email Address'] == "valeriamaduro@gmail.com":
            row['Shipping Courier'] = '선박'
        elif row['From Email Address'] in ["Jessica1198@gmx.de", "neijayah@gmail.com"]:
            row['Shipping Courier'] = 'KP'
    return df
        
def ships(df):
    df_one = select_ship_one(df)
    df_two = select_ship_two(df_one)
    df_2 = select_ship_2(df_two)
    df_per = select_ship_monthly(df_2)
    
    for index, row in df_per.iterrows():
        if row['Ship'].find('O') >= 0:
            row['Ship'] = row['Ship'] + 'O'
            if row['Type'].find('Express') >= 0:
                row['Ship'] = 'Express ' + row['Ship']
        elif row['Type'].find('Express') >= 0:
            row['Ship'] = row['Ship'] + 'O'
            row['Ship'] = 'Express ' + row['Ship']
        else:
            row['Ship'] = row['Ship'] + 'X'
            
    
    df_per = take_line_one(df_per)
    df_per = take_line_two(df_per)
    
    df_per = select_courier(df_per)

    df_per = df_per[['Date', 'Type', 'Reference Txn ID', 'Name', 'From Email Address', 'Shipping Address', 'Item Title', 'New', 'Ship', 'Shipping Courier']]
    
    df_per = df_per.sort_values(by=['Date'])

    return df_per
