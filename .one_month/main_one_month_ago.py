import connection as cn
import filter_one_month as fo
import ship_one_month as so

# 주문 데이터 중 걸러야하는 필터 설정
filter_keys = ["Subscription Payment", "Express Checkout Payment",
               "General Payment", "Mobile Payment", "Website Payment"]
df_mask = cn.Dataframes.order_one_month['Type']
is_purchase = df_mask.isin(filter_keys)

# purchase에 데이터 프레임으로 저장
purchase = cn.Dataframes.order_one_month[is_purchase]
df = cn.pd.DataFrame()

for index, row in purchase.iterrows():
    row['Date'] = cn.datetime.datetime.strptime(row['Date'], "%Y.%m.%d")
    row['Date'] = row['Date'].strftime("%Y-%m-%d")
    df = df.append(row)

df = df[['Date', 'Type', 'Reference Txn ID', 'Name',
         'From Email Address', 'Shipping Address', 'Subject']]
print(df)

# 날짜 확인
print("이번 달은 : ", cn.Time.now_str, " ", "지난 달은 : ",
      cn.Time.one_month_ago_str, " ", "지지난 달은 : ", cn.Time.two_months_ago_str,
      "지지지난달은 : ", cn.Time.tri_months_ago_str)

df_all_drop = fo.filters(df, cn.Dataframes.cus)
df_all_ship = so.ships(df_all_drop)


print(df_all_ship)
cn.pandas_to_sheets(df_all_ship, cn.Worksheet.select_one_month_ago, True)
