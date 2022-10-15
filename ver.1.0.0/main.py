import connection as cn
import filters as ft
import ships as sp
import box_loop as bl

# part 1
# 주문 데이터 중 걸러야하는 필터 설정
filter_keys = ["Subscription Payment", "Express Checkout Payment",
           "General Payment", "Mobile Payment", "Website Payment"]
df_mask = cn.Dataframes.order['Type']
is_purchase = df_mask.isin(filter_keys)

# purchase에 데이터 프레임으로 저장
purchase = cn.Dataframes.order[is_purchase]

# 날짜 문자열을 형식에 맞춰 변경

def datetime_process_dot(df):
    df_pro = cn.pd.DataFrame()
    for index, row in df.iterrows():
        row['Date'] = cn.datetime.datetime.strptime(row['Date'], "%Y. %m. %d")
        row['Date'] = row['Date'].strftime("%Y-%m-%d")
        df_pro = df_pro.append(row)

    df_pro = df_pro[['Date', 'Type', 'Reference Txn ID', 'Name',
         'From Email Address', 'Shipping Address', 'Subject']]

    return df_pro

df = datetime_process_dot(purchase)

# 날짜 확인
print("이번 달은 : ", cn.Time.now_str, " ", "지난 달은 : ",
      cn.Time.one_month_ago_str, " ", "지지난 달은 : ", cn.Time.two_months_ago_str)

# part 2
# 주문 데이터를 필터를 걸쳐 신규, 리턴, 기존 회원 구분
df_all_drop = ft.filters(df, cn.Dataframes.cus)

# 필터를 걸친 데이터를 지난달, 지지난달 데이터와 비교, 이달 2번, monthly, express인지 확인 후 최종 배송 결정
df_all_ship = sp.ships(df_all_drop)

# part 3
# kpop박스 루프 A, 1
box_select_loop = bl.box_loop1(df_all_ship)
box_select_loop = bl.box_dup(box_select_loop)
etc_only = bl.box_only_etc(df_all_ship)
df_all = box_select_loop.append(etc_only)
df_all = df_all.sort_values(by='Date')

# print(df_all)

cn.pandas_to_sheets(df_all, cn.Worksheet.select, True)
# 여기까지 해당 달에 배송이 갈 데이터를 확인해서 선별데이터에 업로드
