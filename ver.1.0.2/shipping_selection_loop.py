import connection as cn
import filters as ft
import ships as sp
import time
from box_loop import kpopbox
from box_loop import kpopcdbox

loop_txt = cn.Dataframes.box_loop
loop_txt = loop_txt.set_index("tag")
basic_pack = loop_txt.loc['Basic Pack', 'contents']

def datetime_process_dot(x):
    x = cn.datetime.datetime.strptime(x, "%Y.%m.%d")
    x = x.strftime("%Y-%m-%d")
    # print(x)
    return x
    
def preference(df : cn.pd.DataFrame):
    if (df[df['Date'].astype(str).str.find('.') >= 0]['Date']).empty == False:
        df.loc[ : ,['Date']] = df.loc[ : ,['Date']].applymap(lambda x : datetime_process_dot(x) if x.find('.') >= 0 else x)
        df = df.applymap(lambda x : str(x).strip())
        for idx, row in df.iterrows():
            if row['Item Title'].lower().find('kpop') >= 0:
                if row['Preference'] == '':
                    refer_ID = row['Reference Txn ID']
                    is_ref = cn.Dataframes.order_one_month['Reference Txn ID'] == refer_ID
                    same_ref = cn.Dataframes.order_one_month[is_ref]
                    if same_ref.empty:
                        is_ref = cn.Dataframes.order_two_months['Reference Txn ID'] == refer_ID
                        same_ref = cn.Dataframes.order_two_months[is_ref]
                        if same_ref.empty:
                            row['Preference'] = ''
                        else:
                            row['Preference'] = same_ref.iloc[0]['Preference']
                    else:
                        row['Preference'] = same_ref.iloc[0]['Preference']
                else:
                    pass
        cn.pandas_to_sheets(df, cn.Worksheet.order, False)
        time.sleep(10)
        cn.Worksheet.order = cn.doc_order.worksheet(cn.Time.now_str)
        cn.Dataframes.order = cn.pd.DataFrame(cn.Worksheet.order.get_all_records())
    return df

def main():
    order = cn.Dataframes.order
    order = preference(order)
    filter_keys = ["Subscription Payment", "General Payment", "Mobile Payment", "Website Payment"]
    df_mask = order['Type']
    is_purchase = df_mask.isin(filter_keys)
    # purchase에 데이터 프레임으로 저장
    purchase = order[is_purchase]
    labelled = purchase[purchase['비고'] == '']
    # #주문 데이터를 필터를 걸쳐 신규, 리턴, 기존 회원 구분
    df_all_drop = ft.filters(labelled, cn.Dataframes.cus)

    # 필터를 걸친 데이터를 지난달, 지지난달 데이터와 비교, 이달 2번, monthly, express인지 확인 후 최종 배송 결정
    df_all_ship = sp.ships(df_all_drop)

    # kpop박스 루프
    box_select_loop = kpopbox.box_all(df_all_ship)
    box_select_loop = box_select_loop.assign(Warning = '')
    etc_only = kpopbox.box_only_etc(df_all_ship)

    CD_only = kpopcdbox.CD_box_all(etc_only)
    CD_only = CD_only.assign(Warning = '')
    CD_etc_only = kpopcdbox.cd_box_only_etc(etc_only)

    CD_all = CD_only.append(CD_etc_only)

    df_all = box_select_loop.append(CD_all)

    # 날짜 확인
    print("이번 달은 : ", cn.Time.now_str, " ", "지난 달은 : ", cn.Time.one_month_ago_str, " ", "지지난 달은 : ", cn.Time.two_months_ago_str)

    df_all = df_all.sort_values(by=['Date'])

    print(df_all)
    # box_select_loop.to_csv('1_document/test.csv', sep = ',', na_rep = '')
    cn.pandas_to_sheets(df_all, cn.Worksheet.select, True)
    # cn.pandas_to_sheets(df_all, cn.Worksheet.select_final, False)

    # 여기까지 해당 달에 배송이 갈 데이터를 확인해서 선별데이터에 업로드

if __name__ == "__main__":
    main()