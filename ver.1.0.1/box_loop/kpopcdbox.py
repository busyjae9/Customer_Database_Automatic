import connection as cn
import random

# 케이팝 박스 구분
# 'Date', 'Type', 'Reference Txn ID', 'Name', 'From Email Address', 'Shipping Address', 'Item Title', 'New', 'Ship'

def cd_box_select(df):
    kpopcdbox_people = cn.pd.DataFrame()
    etc_people = cn.pd.DataFrame()

    for index, row in df.iterrows():
        if row['Item Title'].lower().find('kpopcdbox') >= 0:
            if row['Ship'][len(row['Ship']) - 1] == "O":
                kpopcdbox_people = kpopcdbox_people.append(row)
            else :
                etc_people = etc_people.append(row)
        else :
            etc_people = etc_people.append(row)
    
    idx = ['Date', 'Type', 'Reference Txn ID', 'Name', 'From Email Address',
        'Shipping Address', 'Item Title', 'New', 'Ship', 'Shipping Courier']
    kpopcdbox_people = kpopcdbox_people[idx]
    # etc_people = df.append(kpopcdbox_people)
    # etc_people = etc_people.drop_duplicates(
    #     ['Reference Txn ID'], keep=False)

    etc_people = etc_people[idx]

    return kpopcdbox_people, etc_people


def cd_box_perfect(df):
    kpopcd, etc = cd_box_select(df)
    result = cn.pd.concat([kpopcd, etc])
    return result


def cd_box_only_kpop(df):
    kpop, etc = cd_box_select(df)
    return kpop


def cd_box_only_etc(df):
    kpopcd, etc = cd_box_select(df)
    return etc

# 보내야하는 회원들의 선호를 조사 후 재고에서 루프에 따라 랜덤 선택(같은 그룹 제품이 2개가 초과되지 않도록 제한) - ID를 통해 선호 데이터 확인


loop_txt = cn.Dataframes.box_loop
loop_txt = loop_txt.set_index("tag")
basic_pack = loop_txt.loc['Basic Pack', 'contents']
# basic_pack = "shinee, monstax, bts, seventeen, redvelvet, exo, blackpink, day6, jaypark, got7, nct, vixx, straykids, twice, bigbang, ace, ateez"

# 고객들의 선호를 고객 데이터에서 찾아 가져온 데이터프레임에 추가는 함수

def select_pre(row):
    refer_ID = row['Reference Txn ID']
    date = cn.datetime.datetime.strptime(row['Date'], "%Y-%m-%d")
    date = date.strftime("%Y%m")
    
    is_ref = cn.Dataframes.order['Reference Txn ID'] == refer_ID
    same_ref = cn.Dataframes.order[is_ref]
    if same_ref.empty:
        if date == cn.Time.one_month_ago:
            same_ref = cn.Dataframes.order_one_month[is_ref]
            if same_ref.empty:
                row['Preference'] = ''
            row['Preference'] = same_ref.iloc[0]['Preference']
        elif date == cn.Time.two_months_ago_str:
            same_ref = cn.Dataframes.order_two_months[is_ref]
            if same_ref.empty:
                row['Preference'] = ''
            row['Preference'] = same_ref.iloc[0]['Preference']
        else:
            row['Preference'] = ''
    else:
        row['Preference'] = same_ref.iloc[0]['Preference']
    return row['Preference']

def preference(df):
    df_kpop = cd_box_only_kpop(df)
    df_kpop['Preference'] = ''
    # df_cus = cn.Dataframes.cus
    # df_cus = df_cus.sort_values('Date', ascending=True)
    df_pre = cn.pd.DataFrame()

    for index, row in df_kpop.iterrows():
        row['Preference'] = select_pre(row)
        
        if row['Preference'] == '':
            row['Preference'] = 'nothing so, ' + basic_pack
            df_pre = df_pre.append(row)
        elif row['Preference'].lower() == 'any':
            row['Preference'] = 'nothing so, ' + basic_pack
            df_pre = df_pre.append(row)
        else:
            df_pre = df_pre.append(row)

    df_pre = df_pre[[
        'Date', 'Type', 'Reference Txn ID', 'Name',
        'From Email Address', 'Shipping Address', 'Item Title', 'New', 'Ship', 'Shipping Courier', 'Preference']]
    df_pre = df_pre.sort_values('Date', ascending=True)

    return df_pre

# ver.1.0.1 ---------------------------


def box_loop_num(df):

    temp1 = loop_txt.loc['1 CD Loop', 'contents']
    item_set_loop_one = temp1.replace(" ", "").split(",")
    temp2 = loop_txt.loc['2 CD Loop', 'contents']
    item_set_loop_two = temp2.replace(" ", "").split(",")
    check_group = loop_txt.loc['추가 Group', 'contents'].replace(" ", "").split(",")

    for index, row in df.iterrows():
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
        
        one = []
        two = []

        if len(temp_line) == 1:
            choice_one = [random.choice(temp_line)
                          for i in range(len(item_set_loop_one))]
            j = 0
            for i in choice_one:
                item = i + '-' + item_set_loop_one[j]
                one.insert(len(one), item)
                j += 1

            choice_two = [random.choice(temp_line)
                          for i in range(len(item_set_loop_two))]
            j = 0
            for i in choice_two:
                item = i + '-' + item_set_loop_two[j]
                two.insert(len(two), item)
                j += 1

            str_one = "\n".join(one)
            str_two = "\n".join(two)
            str_loop_num = str_one + "\n---------\n" + str_two
            row['Loop_Num'] = 'Loop_1\n---------\nLoop_2'
            row['Items_Num'] = str_loop_num

        elif len(temp_line) >= 2:
            choicelist_1 = [random.choice(temp_line) for i in range(
                (lambda x: len(x)//2 if len(x) % 2 == 0 else len(x)//2 + 1)(item_set_loop_one))]
            choicelist_2 = [random.choice(temp_line)
                            for i in range(len(item_set_loop_one)//2)]
            choicelist_3 = choicelist_1 + choicelist_2
            j = 0
            for i in choicelist_3:
                item = i + '-' + item_set_loop_one[j]
                one.insert(len(one), item)
                j += 1

            choicelist_1 = [random.choice(temp_line) for i in range(
                (lambda x: len(x)//2 if len(x) % 2 == 0 else len(x)//2 + 1)(item_set_loop_two))]
            choicelist_2 = [random.choice(temp_line)
                            for i in range(len(item_set_loop_two)//2)]
            choicelist_3 = choicelist_1 + choicelist_2
            j = 0
            for i in choicelist_3:
                item = i + '-' + item_set_loop_two[j]
                two.insert(len(two), item)
                j += 1

            str_one = "\n".join(one)
            str_two = "\n".join(two)
            str_loop_num = str_one + "\n---------\n" + str_two
            row['Loop_Num'] = 'CD_Loop_1\n---------\nCD_Loop_2'
            row['Items_Num'] = str_loop_num

    return df


def box_loop_alpha(df, second = False):
    ult_stock = cn.Dataframes.stock

    tempA = loop_txt.loc['A CD Loop', 'contents']
    item_set_loop_A = tempA.replace(" ", "").split(",")
    tempB = loop_txt.loc['B CD Loop', 'contents']
    item_set_loop_B = tempB.replace(" ", "").split(",")
    check_group = loop_txt.loc['추가 Group', 'contents'].replace(" ", "").split(",")

    # item_set_loop_A = ["씨리얼통", "패브릭포스터", "직자석"]
    # item_set_loop_B = ["item_B_1", "item_B_2", "item_B_3"]
    if second == False :
        for index, row in df.iterrows():
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
            
            A = []
            B = []

            if len(temp_line) == 1:
                for i in item_set_loop_A:
                    product = temp_line[0] + '_' + i
                    pro_ult_stock = ult_stock[ult_stock['product'] == product]
                    product = temp_line[0] + '-' + i
                    if pro_ult_stock.empty:
                        item = product + ' 재고_X'
                        A.insert(len(A), item)
                    elif pro_ult_stock.iloc[0, 1] == 0:
                        item = product + ' 재고_X'
                        A.insert(len(A), item)
                    else:
                        A.insert(len(A), product)
                if any("재고 X" in s for s in A):
                    for i in item_set_loop_B:
                        for j in temp_line:
                            product = temp_line[0] + '_' + i
                            pro_ult_stock = ult_stock[ult_stock['product'] == product]
                            product = temp_line[0] + '-' + i
                            if pro_ult_stock.empty:
                                item = product + ' 재고_X'
                                B.insert(len(B), item)
                            elif pro_ult_stock.iloc[0, 1] == 0:
                                item = product + ' 재고_X'
                                B.insert(len(B), item)
                            else:
                                B.insert(len(B), product)
                    str_A = "\n".join(A)
                    str_B = "\n".join(B)
                    str_loop_Alpha = str_A + "\n---------\n" + str_B
                    row['Loop_Alpha'] = 'CD_Loop_A\n---------\nCD_Loop_B'
                    row['Items_Alpha'] = str_loop_Alpha
                    continue
            elif len(temp_line) >= 2:
                for i in item_set_loop_A:
                    product_list = []
                    for j in temp_line:
                        product = j + '_' + i
                        pro_ult_stock = ult_stock[ult_stock['product'] == product]
                        product = j + '-' + i
                        if pro_ult_stock.empty:
                            pass
                        elif pro_ult_stock.iloc[0, 1] == 0:
                            item = product + ' 재고_X'
                            product_list.append(item)
                        else:
                            product_list.append(product)
                    if len(product_list) >= 1:
                        choice1 = random.sample(product_list, 1)
                        A.insert(len(A), choice1[0])
                    elif len(product_list) == 0:
                        # choice_empty = random.sample(temp_line, 1)
                        item = '선호에 맞는-' + i + ' 재고_X'
                        A.insert(len(A), item)
                if any("재고_X" in s for s in A):
                    for i in item_set_loop_B:
                        product_list = []
                        for j in temp_line:
                            product = j + '_' + i
                            pro_ult_stock = ult_stock[ult_stock['product'] == product]
                            product = j + '-' + i
                            if pro_ult_stock.empty:
                                pass
                            elif pro_ult_stock.iloc[0, 1] == 0:
                                # item = product + ' 재고_X'
                                # product_list.append(item)
                                pass
                            else:
                                product_list.append(product)
                        if len(product_list) >= 1:
                            choice1 = random.sample(product_list, 1)
                            B.insert(len(B), choice1[0])
                        elif len(product_list) == 0:
                            # choice_empty = random.sample(temp_line, 1)
                            item = '선호에 맞는-' + i + ' 재고_X'
                            B.insert(len(B), item)
                    str_A = "\n".join(A)
                    str_B = "\n".join(B)
                    str_loop_Alpha = str_A + "\n---------\n" + str_B
                    row['Loop_Alpha'] = 'CD_Loop_A\n---------\nCD_Loop_B'
                    row['Items_Alpha'] = str_loop_Alpha
                    continue
            str_A = "\n".join(A)
            str_loop_Alpha = str_A
            row['Loop_Alpha'] = 'CD_Loop_A'
            row['Items_Alpha'] = str_loop_Alpha
    elif second == True :
        for index, row in df.iterrows():
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
            B = []
            
            if (row['Loop_Alpha'] == 'CD_Loop_A') & ((row['Duplicated_Alpha'].find('D') >= 0) or (row['Duplicated_Alpha'].find('1') >= 0)):
                for i in item_set_loop_B:
                    product_list = []
                    for j in temp_line:
                        product = j + '_' + i
                        pro_ult_stock = ult_stock[ult_stock['product'] == product]
                        product = j + '-' + i
                        if pro_ult_stock.empty:
                            pass
                        elif pro_ult_stock.iloc[0, 1] == 0:
                            # item = product + ' 재고_X'
                            # product_list.append(item)
                            pass
                        else:
                            product_list.append(product)
                    if len(product_list) >= 1:
                        choice1 = random.sample(product_list, 1)
                        B.insert(len(B), choice1[0])
                    elif len(product_list) == 0:
                        # choice_empty = random.sample(temp_line, 1)
                        item = '선호에 맞는-' + i + ' 재고_X'
                        B.insert(len(B), item)
                str_B = "\n".join(B)
                str_loop_Alpha = "\n---------\n" + str_B
                row['Loop_Alpha'] = 'CD_Loop_A\n---------\nCD_Loop_B'
                row['Items_Alpha'] = row['Items_Alpha'] + str_loop_Alpha
    return df

def CD_box_dup(df):
    df_cd_cus = cn.Dataframes.cus
    df_cd_cus = df_cd_cus.sort_values('Date', ascending=True)

    for index, row in df.iterrows():
        refer_email = row['From Email Address']
        df_temp = df_cd_cus[df_cd_cus['Email'] == refer_email]
        temp_alpha = row['Items_Alpha'].split('\n')
        temp_num = row['Items_Num'].split('\n')
        loop_al = []
        loop_nu = []
        if df_temp.empty:
            for i in temp_alpha:
                if i == '---------':
                    loop_al.insert(len(loop_al), '---------')
                    continue
                loop_al.insert(len(loop_al), "0")
            for i in temp_num:
                if i == '---------':
                    loop_nu.insert(len(loop_nu), '---------')
                    continue
                loop_nu.insert(len(loop_nu), "0")
        else:
            df_temp = df_temp.drop_duplicates(['Email'], keep='last')
            if df_temp.iloc[0]['List'] == '':
                for i in temp_alpha:
                    if i == '---------':
                        loop_al.insert(len(loop_al), '---------')
                        continue
                    loop_al.insert(len(loop_al), "0")
                for i in temp_num:
                    if i == '---------':
                        loop_nu.insert(len(loop_nu), '---------')
                        continue
                    loop_nu.insert(len(loop_nu), "0")
            else:
                row_list = df_temp.iloc[0]['List'].lower()
                for i in temp_alpha:
                    item_name = i.split('-')[1].split(' ')[0]
                    _name = i.replace('-', '_').replace(' 재고_X', '')
                    if i == '---------':
                        loop_al.insert(len(loop_al), '---------')
                    elif row_list.find(_name) >= 0:
                        item_count = row_list.count(item_name)
                        item_num = str(item_count) + ', ' + 'D'
                        loop_al.insert(len(loop_al), item_num)
                    else:
                        item_count = row_list.count(item_name)
                        loop_al.insert(len(loop_al), str(item_count))
                for i in temp_num:
                    item_name = i.split('-')[1].split(' ')[0]
                    _name = i.replace('-', '_').replace(' 재고_X', '')
                    if i == '---------':
                        loop_nu.insert(len(loop_nu), '---------')
                    elif row_list.find(_name) >= 0:
                        item_count = row_list.count(item_name)
                        item_num = str(item_count) + ', ' + 'D'
                        loop_nu.insert(len(loop_nu), item_num)
                    else:
                        item_count = row_list.count(item_name)
                        loop_nu.insert(len(loop_nu), str(item_count))
        str_loop_al = "\n".join(loop_al)
        str_loop_nu = "\n".join(loop_nu)
        row['Duplicated_Alpha'] = str_loop_al
        row['Duplicated_Num'] = str_loop_nu
    return df

def CD_box_all(df):
    
    df = preference(df)
    
    df = df.assign(
        Loop_Alpha='', Items_Alpha='', Duplicated_Alpha='',
        Loop_Num='', Items_Num='', Duplicated_Num='',
    )
    
    df = box_loop_alpha(df)
    df = box_loop_num(df)
    df = CD_box_dup(df)
    df = box_loop_alpha(df, second=True)
    df = CD_box_dup(df)
    return df
