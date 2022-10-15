import gspread
import datetime
import pandas as pd
from dateutil.relativedelta import relativedelta
# from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

scope = [
'https://spreadsheets.google.com/feeds',
'https://www.googleapis.com/auth/drive'
]

# json_file_name_busy = '/content/drive/MyDrive/customer_database/1_Oauthclient/gspreadsheet-314703-ab962f3581e6.json'
# json_file_name_play = '/content/drive/MyDrive/customer_database/1_Oauthclient/elated-channel-316907-70c71ef154b4.json'
json_file_name_play = '1_Oauthclient/elated-channel-316907-70c71ef154b4.json'

# json_file_name_drive = '1_Oauthclient/client_secret_497519833740-u6f2ia3a71vp7c1d9m9u73biajcsqqd9.apps.googleusercontent.com.json'
# credentials_busy = ServiceAccountCredentials.from_json_keyfile_name(json_file_name_busy, scope)
credentials_play = ServiceAccountCredentials.from_json_keyfile_name(json_file_name_play, scope)

gc_play = gspread.authorize(credentials_play)
# 주문 데이터
spreadsheet_url_1 = '주문 데이터 스프레드 시트 URL'
# 고객 데이터
spreadsheet_url_2 = '고객 데이터 스프레드 시트 URL'
# 재고 데이터
spreadsheet_url_3 = '재고 데이터 스프레드 시트 URL'
# 선별 데이터
spreadsheet_url_4 = '선별 데이터 스프레드 시트 URL'

# 스프레스시트 문서 가져오기 
doc_order = gc_play.open_by_url(spreadsheet_url_1)
doc_cus = gc_play.open_by_url(spreadsheet_url_2)
doc_stock = gc_play.open_by_url(spreadsheet_url_3)
doc_select = gc_play.open_by_url(spreadsheet_url_4)
# doc_label = gc_play.open_by_url(spreadsheet_url_5)


# 데이터 프레임을 구글 시트에 그대로 가져다 주는 함수 정의
def iter_pd(df):
    for val in df.columns:
        yield val
    for row in df.to_numpy():
        for val in row:
            if pd.isna(val):
                yield ""
            else:
                yield val
def pandas_to_sheets(pandas_df, sheet, clear = False):
    # Updates all values in a workbook to match a pandas dataframe
    if clear:
        sheet.clear()
    (row, col) = pandas_df.shape
    cells = sheet.range("A1:{}".format(gspread.utils.rowcol_to_a1(row + 1, col)))
    for cell, val in zip(cells, iter_pd(pandas_df)):
        cell.value = val
    sheet.update_cells(cells)

# sheet title rule : 현재 시간의 YYYYMM
# example : 202105
# 그래서 datetime.date 모듈로 현재 시간을 %Y%m 서식으로 불러와서 사용
# 필요한 시간은 현재와 한 달 전, 두 달 전
class Time :
    now = datetime.date.today()
    now_str = datetime.date.strftime(now, "%Y%m")
    one_month_ago = now - relativedelta(months=1)
    one_month_ago_str = datetime.date.strftime(
        one_month_ago, "%Y%m")
    two_months_ago = now - relativedelta(months=2)
    two_months_ago_str = datetime.date.strftime(
        two_months_ago, "%Y%m")
    tri_months_ago = now - relativedelta(months=3)
    tri_months_ago_str = datetime.date.strftime(
        tri_months_ago, "%Y%m")

class Worksheet :
    # 시트 선택하기
    # 주문 데이터의 현재 달 시트
    order = doc_order.worksheet(Time.now_str)
    order_one_month_ago = doc_order.worksheet(Time.one_month_ago_str)
    order_two_months_ago = doc_order.worksheet(Time.two_months_ago_str)
    order_tri_months_ago = doc_order.worksheet(Time.tri_months_ago_str)

    # 고객 데이터의 총 누적 시트
    cus = doc_cus.worksheet('all_data')
    cd_cus = doc_cus.worksheet('kpopcd preference')

    # 재고 데이터
    stock = doc_stock.worksheet("ultimate")
    box_loop = doc_stock.worksheet("BOXLOOP")
    
    # 라벨 데이터
    # label = doc_label.worksheet(Time.now_str)

    select_one_month_ago = doc_select.worksheet(Time.one_month_ago_str)
    select_two_months_ago = doc_select.worksheet(Time.two_months_ago_str)
    select_final = doc_select.worksheet('이달 최종')

    # 선별 데이터 시트를 가져오는 데, 해당 달에 처음 시작하면, 시트 없을 테니 해당 달에 맞는 타이틀을 가진 시트 자동 생성
    try:
        # 선별 데이터 시트 선택
        select = doc_select.worksheet(Time.now_str)
    except:
        # 이번 달 시트가 없으면 생성
        doc_select.add_worksheet(title=Time.now_str, rows="100", cols="20")
        select = doc_select.worksheet(Time.now_str)
        


# 가져온 시트로 데이터 프레임으로 변환
class Dataframes :
    order = pd.DataFrame(Worksheet.order.get_all_records())
    stock = pd.DataFrame(Worksheet.stock.get_all_records())
    box_loop = pd.DataFrame(Worksheet.box_loop.get_all_records())
    cus = pd.DataFrame(Worksheet.cus.get_all_records())
    cd_cus = pd.DataFrame(Worksheet.cd_cus.get_all_records())
    select = pd.DataFrame(Worksheet.select.get_all_records())
    # label = pd.DataFrame(Worksheet.label.get_all_records())
    order_one_month = pd.DataFrame(Worksheet.order_one_month_ago.get_all_records())
    order_two_months = pd.DataFrame(Worksheet.order_two_months_ago.get_all_records())
    order_tri_months = pd.DataFrame(Worksheet.order_tri_months_ago.get_all_records())
    # select_one_month = pd.DataFrame(Worksheet.select_one_month_ago.get_all_records())
    # select_two_months = pd.DataFrame(Worksheet.select_two_months_ago.get_all_records())
    # select_tri_months = pd.DataFrame(Worksheet.order_tri_months_ago.get_all_records())
    
# class Csv :
#     file = '1_document/loop.csv'
#     f = open(file,'rt')
#     reader = csv.reader(f, index_col = 0)

#     #once contents are available, I then put them in a list
#     csv_list = []
#     for l in reader:
#         csv_list.append(l)
#     f.close()
#     #now pandas has no problem getting into a df
#     Loop_txt = pd.DataFrame(csv_list)