import connection as cn

SET_KEY = ['Date', 'Type', 'Transaction ID', 'Contact Phone Number', 'Reference Txn ID', 'Name', 'From Email Address', 'Address 1', 'Shipping Address', 'Item Title']
set_new = ['Date', 'Type', 'Transaction ID', 'Contact Phone Number', 'Reference Txn ID', 'Name', 'From Email Address', 'Address 1', 'Shipping Address', 'Item Title', 'New']

# 주문 데이터 중 ID, email, address를 고객 데이터와 비교하는 함수
def select_new(df, df_cus): 
    df_new_new = cn.pd.DataFrame()
    df_id_match = cn.pd.DataFrame()
    df_email_match = cn.pd.DataFrame()
    df_address_match = cn.pd.DataFrame()
    
    # 고객 데이터와 구매 데이터 필요 키만 추출
    df_cus_processed = df_cus[['Date', 'ID', 'Name', 'Email', 'Address', 'Preference']]
    df_processed = df[SET_KEY]
    df_processed.assign(New = 'Error')
    for index, row in df_processed.iterrows():
        row['New'] = 'Yes'
        df_new_new = df_new_new.append(row)
        for i in list(set(df_cus_processed['ID'])):
            if row['Reference Txn ID'] == i:
                row['New'] = 'Return'
                df_id_match = df_id_match.append(row)
        for i in list(set(df_cus_processed['Email'])):
            if row['From Email Address'] == i:
                row['New'] = 'Return'
                df_email_match = df_email_match.append(row)
        for i in list(set(df_cus_processed['Address'])):
            if row['Shipping Address'] == i:
                row['New'] = 'Return'
                df_address_match = df_address_match.append(row)
    
    # 기존 고객 대상으로 돌아온 사람인지 확인
    df_all = df_new_new.append(df_address_match)
    df_all = df_all.append(df_email_match)
    df_all = df_all.append(df_id_match)
    # 데이터 중복값을 삭제하면서, 새로운 회원과 기존 회원 구분
    df_all = df_all.drop_duplicates(['Reference Txn ID', 'From Email Address', 'Shipping Address', 'Item Title', 'Date', 'Name'], keep = 'last')
    df_all = df_all.sort_values(by='Date')
    df_all = df_all.sort_index()
    df_all = df_all[set_new]
    return df_all

# 지난 달의 주문 데이터 중 ID, email, address를 이번 달 주문 데이터와 비교하는 함수
def select_return(df_new):
    df_one = cn.pd.DataFrame(cn.Worksheet.order_one_month_ago.get_all_records())
    df_return_id_match = cn.pd.DataFrame()
    df_return_email_match = cn.pd.DataFrame()
    df_return_address_match = cn.pd.DataFrame()

    for index, row in df_new.iterrows():
        for i in list(set(df_one['Reference Txn ID'])):
            if row['Reference Txn ID'] == i:
                row['New'] = 'Existed'
                df_return_id_match = df_return_id_match.append(row)
        for i in list(set(df_one['From Email Address'])):
            if row['From Email Address'] == i:
                row['New'] = 'Existed'
                df_return_email_match = df_return_email_match.append(row)
        for i in list(set(df_one['Shipping Address'])):
            if row['Shipping Address'] == i:
                row['New'] = 'Existed'
                df_return_address_match = df_return_address_match.append(row)

    # 기존 고객 대상으로 돌아온 사람인지 확인
    df_all = df_new.append(df_return_email_match)
    df_all = df_all.append(df_return_id_match)
    df_all = df_all.append(df_return_address_match)
    df_all = df_all.drop_duplicates(['Reference Txn ID', 'From Email Address', 'Shipping Address', 'Item Title', 'Date', 'Name'], keep = 'last')
    df_all = df_all.sort_index()
    df_all = df_all[set_new]
    return df_all

# bi-monthly가 붙은 상품을 산 사람을 기준으로 다시 확인하는 함수
def select_bi(df_all):
    bi_people = cn.pd.DataFrame()
    
    for index, row in df_all.iterrows():
        if row['Item Title'].find('bi-monthly'):
            bi_people = bi_people.append(row)

    bi_people = bi_people[set_new]
    
    # bi-monthly 회원을 2달 전 데이터로 확인해서 존재할 경우 New 속성이 Return인 경우 Existed로 변경
    df_two = cn.pd.DataFrame(cn.Worksheet.order_two_months_ago.get_all_records())
    for index, row in bi_people.iterrows():
        for i in list(set(df_two['Reference Txn ID'])):
            if row['Reference Txn ID'] == i:
                if row['New'] == 'Return' : 
                    row['New'] = row['New'].replace('Return',"Existed")
        for i in list(set(df_two['From Email Address'])):
            if row['From Email Address'] == i:
                if row['New'] == 'Return' : 
                    row['New'] = row['New'].replace('Return',"Existed")
        for i in list(set(df_two['Shipping Address'])):
            if row['Shipping Address'] == i:
                if row['New'].find('Return') == False : 
                    row['New'] = row['New'].replace('Return',"Existed")

    df_all = df_all.append(bi_people)

    # 데이터 중복값을 삭제하면서, 새로운 회원과 기존 회원 구분
    df_all = df_all.drop_duplicates(['Reference Txn ID', 'From Email Address', 'Shipping Address', 'Item Title', 'Date', 'Name'], keep = 'last')
    df_all = df_all.sort_values(by='Date')
    df_all = df_all.sort_index()
    df_all_drop = df_all[set_new]
    return df_all_drop

def filters(df, df_cus):
    df_new = select_new(df, df_cus)
    df_return = select_return(df_new)
    return select_bi(df_return)
