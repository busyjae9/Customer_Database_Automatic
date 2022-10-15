import gspread
import time
import datetime
import pandas as pd
from dateutil.relativedelta import relativedelta

from oauth2client.service_account import ServiceAccountCredentials
from pandas.core.frame import DataFrame

scope = [
'https://spreadsheets.google.com/feeds',
'https://www.googleapis.com/auth/drive',
]

json_file_name = '.Oauth client/gspreadsheet-314703-ab962f3581e6.json'

credentials = ServiceAccountCredentials.from_json_keyfile_name(json_file_name, scope)

gc = gspread.authorize(credentials)
# 주문 데이터
spreadsheet_url_1 = 'https://docs.google.com/spreadsheets/d/1StERmoqBjG1QTG4OjvDEc9dvR9DMdbJNmjf_Jm0y5Vc/edit#gid=2049974321'
# 고객 데이터
spreadsheet_url_2 = 'https://docs.google.com/spreadsheets/d/1wTiFKhl1BQ1bXFWigoR5WlVdVahR8EcZJeWFae8WTaA/edit#gid=0'
# 재고 데이터
spreadsheet_url_3 = 'https://docs.google.com/spreadsheets/d/1FUa0O_YFcq4e1KEeKfdUOvM5i_byHwtVaGLAvsaqm38/edit#gid=633669732'
# 선별 데이터
spreadsheet_url_4 = 'https://docs.google.com/spreadsheets/d/1yQvNfiPY459-uUDYLZgBCxg5bnvEnIP73veh-CpwzPQ/edit#gid=0'

# 스프레스시트 문서 가져오기 
doc_order = gc.open_by_url(spreadsheet_url_1)
doc_cus = gc.open_by_url(spreadsheet_url_2)
doc_stock = gc.open_by_url(spreadsheet_url_3)
doc_select = gc.open_by_url(spreadsheet_url_4)


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
    # 선별 데이터 시트를 가져오는 데, 해당 달에 처음 시작하면, 시트 없을 테니 해당 달에 맞는 타이틀을 가진 시트 자동 생성
    
    try:
        # 선별 데이터 시트 선택
        select = doc_select.worksheet(Time.now_str)
        select_one_month_ago = doc_select.worksheet(Time.one_month_ago_str)
        select_two_months_ago = doc_select.worksheet(Time.two_months_ago_str)
    except:
        # 이번 달 시트가 없으면 생성
        doc_select.add_worksheet(title=Time.now_str, rows="100", cols="20")
        select = doc_select.worksheet(Time.now_str)
        select_one_month_ago = doc_select.worksheet(Time.one_month_ago_str)
        select_two_months_ago = doc_select.worksheet(Time.two_months_ago_str)

# 가져온 시트로 데이터 프레임으로 변환
class Dataframes :
    order = pd.DataFrame(Worksheet.order.get_all_records())
    cus = pd.DataFrame(Worksheet.cus.get_all_records())
    select = pd.DataFrame(Worksheet.select.get_all_records())
    order_one_month = pd.DataFrame(Worksheet.order_one_month_ago.get_all_records())
    order_two_months = pd.DataFrame(Worksheet.order_two_months_ago.get_all_records())
    order_tri_months = pd.DataFrame(Worksheet.order_tri_months_ago.get_all_records())