from os import dup
import connection as cn
import random

# 케이팝 박스 구분


# def box_select(df):
#     kpopbox_people = cn.pd.DataFrame()
#     etc_people = cn.pd.DataFrame()

#     for index, row in df.iterrows():
#         if row['Item Title'].lower().find('kpopbox') >= 0:
#             if row['Ship'][len(row['Ship']) - 1] == 'O':
#                 kpopbox_people = kpopbox_people.append(row)
#             elif row['Ship'] == 'one_month':
#                 kpopbox_people = kpopbox_people.append(row)
#             elif row['Ship'] == 'two_month':
#                 kpopbox_people = kpopbox_people.append(row)


#     kpopbox_people = kpopbox_people[['Date', 'Type', 'Reference Txn ID', 'Name',
#                                      'From Email Address', 'Shipping Address', 'Item Title', 'New', 'Ship']]
#     etc_people = df.append(kpopbox_people)
#     etc_people = etc_people.drop_duplicates(
#         ['Reference Txn ID', 'From Email Address', 'Shipping Address', 'Item Title', 'Date', 'Name'], keep=False)

#     etc_people = etc_people[['Date', 'Type', 'Reference Txn ID', 'Name',
#                              'From Email Address', 'Shipping Address', 'Item Title', 'New', 'Ship']]

#     return kpopbox_people, etc_people


# def box_perfect(df):
#     kpop, etc = box_select(df)
#     result = cn.pd.concat([kpop, etc])
#     return result


# def box_only_kpop(df):
#     kpop, etc = box_select(df)
#     return kpop


# def box_only_etc(df):
#     kpop, etc = box_select(df)
#     return etc

# # 보내야하는 회원들의 선호를 조사 후 재고에서 루프에 따라 랜덤 선택(같은 그룹 제품이 2개가 초과되지 않도록 제한) - ID를 통해 선호 데이터 확인


# def preference(df):
#     df_kpop = box_only_kpop(df)
#     df_kpop['Preference'] = ''
#     df_cus = cn.Dataframes.cus
#     df_cus = df_cus.sort_values('Date', ascending=True)
#     df_pre = cn.pd.DataFrame()
#     basic_pack = "shinee, monstax, bts, seventeen, redvelvet, exo, blackpink, day6, jaypark, got7, nct, vixx, straykids, twice, bigbang, ace, ateez"

#     for index, row in df_kpop.iterrows():
#         refer_ID = row['Reference Txn ID']
#         df_temp = df_cus[df_cus['ID'] == refer_ID]
#         if df_temp.empty:
#             row['Preference'] = 'nothing so, ' + basic_pack
#             df_pre = df_pre.append(row)
#         else:
#             df_temp = df_temp.drop_duplicates(['ID'], keep='last')
#             if df_temp.iloc[0]['Preference'] == '':
#                 row['Preference'] = 'nothing so, ' + basic_pack
#             elif df_temp.iloc[0]['Preference'].lower() == 'any':
#                 row['Preference'] = 'nothing so, ' + basic_pack
#             else:
#                 row['Preference'] = df_temp.iloc[0]['Preference']
#             df_pre = df_pre.append(row)

#     df_pre = df_pre[[
#         'Date', 'Type', 'Reference Txn ID', 'Name',
#         'From Email Address', 'Shipping Address', 'Item Title', 'New', 'Ship', 'Preference']]
#     df_pre = df_pre.sort_values('Date', ascending=True)

#     return df_pre

# # Loop set 1


# def item_select1(df):
#     df = preference(df)
#     df = df.assign(
#         Preference_1='',
#         Item_1='씨리얼통',
#         Duplicated_1='',
#         Preference_2='',
#         Item_2='패브릭포스터',
#         Duplicated_2='',
#         Preference_3='',
#         Item_3='직자석',
#         Duplicated_3='',
#         Preference_4='',
#         Item_4='저금통',
#         Duplicated_4='',
#         Preference_5='',
#         Item_5='파우치',
#         Duplicated_5='',
#         Preference_6='',
#         Item_6='족자',
#         Duplicated_6='',
#         Preference_7='',
#         Item_7='명찰',
#         Duplicated_7=''
#     )

#     return df


# def box_loop1(df):
#     df_box_loop = item_select1(df)
#     pre_1_3 = ["Preference_1", "Preference_2", "Preference_3"]
#     pre_4_7 = ["Preference_4", "Preference_5",
#                "Preference_6", "Preference_7"]
#     item_1_3 = ["씨리얼통", "패브릭포스터", "직자석"]
#     ult_stock = cn.Dataframes.stock

#     #Loop2
#     for index, row in df_box_loop.iterrows():
#         temp_pre = row['Preference'].replace(" ", "")
#         temp_line = temp_pre.split(",")

#         if len(temp_line) == 1:
#             row[pre_4_7] = [random.choice(temp_line) for i in range(4)]
#         elif len(temp_line) >= 2:
#             choicelist_1 = random.sample(temp_line, 2)
#             choicelist_2 = random.sample(temp_line, 2)
#             choicelist_3 = choicelist_1 + choicelist_2
#             row[pre_4_7] = choicelist_3

#     #Loop1
#     for index, row in df_box_loop.iterrows():
#         temp_pre = row['Preference'].replace(" ", "")
#         temp_line = temp_pre.split(",")

#         if len(temp_line) == 1:
#             for i in item_1_3:
#                 idx = item_1_3.index(i)
#                 for j in temp_line:
#                     product = j + '_' + i
#                     pro_ult_stock = ult_stock[ult_stock['product'] == product]
#                     if pro_ult_stock.empty:
#                         row[pre_1_3[idx]] = j + '_재고 X'
#                     else:
#                         row[pre_1_3[idx]] = j
#         if len(temp_line) >= 2:
#             for i in item_1_3:
#                 idx = item_1_3.index(i)
#                 product_list = []
#                 for j in temp_line:
#                     product = j + '_' + i
#                     pro_ult_stock = ult_stock[ult_stock['product'] == product]
#                     if pro_ult_stock.empty:
#                         pass
#                     else:
#                         product_list.append(j)

#                 if len(product_list) == 1:
#                     choice1 = random.sample(product_list, 1)
#                     row[pre_1_3[idx]] = choice1[0]
#                 elif len(product_list) == 0:
#                     choice3 = random.sample(temp_line, 1)
#                     row[pre_1_3[idx]] = choice3[0] + '_재고 X'
#                 else:
#                     choice2 = random.sample(product_list, 1)
#                     row[pre_1_3[idx]] = choice2[0]

#     return df_box_loop


# def cell_sum(df):
#     preference_list = ['Preference_1', 'Preference_2', 'Preference_3',
#                        'Preference_4', 'Preference_5', 'Preference_6', 'Preference_7']
#     item_list = ['Item_1', 'Item_2', 'Item_3',
#                  'Item_4', 'Item_5', 'Item_6', 'Item_7']

#     for index, row in df.iterrows():
#         for i in preference_list:
#             idx = preference_list.index(i)
#             if row[preference_list[idx]].find('_재고 X') >= 0:
#                 row[preference_list[idx]] = row[preference_list[idx]].replace('_재고 X', '')
#                 pre_item_name = row[preference_list[idx]] + '_' + row[item_list[idx]] + '_재고 X'
#             else:
#                 pre_item_name = row[preference_list[idx]] + '_' + row[item_list[idx]]

#             row[preference_list[idx]] = pre_item_name

#     df = df.drop(item_list, axis=1)
#     return df


# # 중복 검사하는 함수
# def box_dup(df):
#     df_cus = cn.Dataframes.cus
#     df_cus = df_cus.sort_values('Date', ascending=True)
#     df_pre = cn.pd.DataFrame()
#     preference_list = ['Preference_1', 'Preference_2', 'Preference_3',
#                        'Preference_4', 'Preference_5', 'Preference_6', 'Preference_7']
#     item_list = ['Item_1', 'Item_2', 'Item_3',
#                  'Item_4', 'Item_5', 'Item_6', 'Item_7']
#     duplicated_list = ['Duplicated_1', 'Duplicated_2', 'Duplicated_3',
#                        'Duplicated_4', 'Duplicated_5', 'Duplicated_6', 'Duplicated_7']

#     for index, row in df.iterrows():
#         refer_email = row['From Email Address']
#         df_temp = df_cus[df_cus['Email'] == refer_email]
#         if df_temp.empty:
#             row[duplicated_list] = '0'
#         else:
#             df_temp = df_temp.drop_duplicates(['Email'], keep='last')
#             if df_temp.iloc[0]['List'] == '':
#                 row[duplicated_list] = '0'
#             else:
#                 row_list = df_temp.iloc[0]['List'].lower()
#                 for i in preference_list:
#                     idx = preference_list.index(i)
#                     pre_item_name = row[preference_list[idx]
#                                         ] + '_' + row[item_list[idx]]
#                     item_name = row[item_list[idx]]
#                     if row_list.find(pre_item_name) >= 0:
#                         item_count = row_list.count(item_name)
#                         row[duplicated_list[idx]] = str(
#                             item_count) + ', ' + 'D'
#                     else:
#                         item_count = row_list.count(item_name)
#                         row[duplicated_list[idx]] = str(item_count)

#     df = cell_sum(df)

#     return df


# # 랜덤 선택된 상품을 기존에 보낸 데이터와 확인 후 해당 품목이 몇 번 보내졌는 지 확인 - email을 통해 기존 배송 물품 데이터 확인


# # pandas_to_sheets(df_all_box, worksheet_select, True)
