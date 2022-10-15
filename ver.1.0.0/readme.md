Ver.1.0.0 Description
===

# connection 모듈 설명

## 쓰인모듈
gspread, time, datetime, pandas, relativedelta

## 클래스 설명

### Time
- 현재 달에서 부터 3달 전까지의 기간을 %Y%m(202106)의 포맷으로 저장
- 순서대로 현재 달, 1달 전, 2달 전, 3달 전
  1. now_str
  2. one_month_ago_str
  3. two_months_ago_str
  4. tri_months_ago_str

### Worksheet
- 주문, 고객, 재고, 선별 데이터의 워크시트를 타임 클래스의 변수를 통해 연결
- select_final는 테스트용 시트
- 선별 데이터 시트는 없으면 생성될 수 있도록 try문을 통해 구분

### Dataframes
- 워크시트 클래스에서 가져온 시트들을 pandas를 통해 데이터 프레임으로 변환

# filters 모듈 설명

## 함수 설명

### select_new
- 데이터 프레임과 고객 데이터를 비교해서 새로운 회원인가, 돌아온 회원인가 확인(2달 전의 데이터만 존재하기 때문에 기존회원인지 아직 파악 안됨)
  
  #### 처리방법
  - 처리할 데이터 프레임 하나(이하 df)와 고객 데이터(이하 cus)를 인자로 받음
  - 고객 데이터 중 가져올 키
    - 'Date', 'ID', 'Name', 'Email', 'Address', 'Preference'
  - df 중 가져올 키
    - 'Date', 'Type', 'Reference Txn ID', 'Name', 'From Email Address', 'Shipping Address', 'Subject'
  - df에 새로운 키 'New'를 추가
  - df 모든 행의 'New'열에 'Yes' 추가
  - cus와 Reference Txn ID - ID, From Email Address - Email, hipping Address - Address 비교
    - 일치하면 'New'열의 'Yes'를 'Return'으로 변경
      - 미리 마련된 일치 데이터 프레임에 각각 저장
  - 비교를 완료하면 모든 데이터 프레임을 하나로 합침
    - 새로온 사람 - 주소 매치 - 이메일 매치 - 아이디 매치 순서로 합침
    - 합치는 순서에 따라 뒤에 배치
  - 중복값을 제거 후 가장 마지막 값만 keep
  - 인덱스 순으로 정렬하고 데이터 프레임 반환

### select_return
- select_new에서 받은 df_new를 한 달 전 주문 데이터와 비교해서 존재하면 기존 회원으로 변경

  #### 처리방법
  - select_new 처리방법과 동일
  - 비교 후 'New'열의 값을 'Existed'로 변경
  - 비교를 완료하면 모든 데이터 프레임을 하나로 합침
    - df_new - 이메일 매치 - 아이디 매치 순서로 합침
    - 합치는 순서에 따라 뒤에 배치
    - 주소는 주문 데이터에 존재 x -> 2021년 6월 이후 들어갈 예정
  - 중복값을 제거 후 가장 마지막 값만 keep
  - 인덱스 순으로 정렬하고 데이터 프레임 반환

### select_bi
- bi-monthly가 붙은 상품을 산 사람을 기준으로 다시 확인

  #### 처리방법
  - select_return에서 받은 df_all을 다시 확인
  - Subject 키에 bi-monthly값을 가진 행을 빈 데이터 프레임(bi_people)에 저장
  - 두 달 전 주문 데이터와 비교 : select_return와 동일
  - bi_monthly인 경우
    - 'New' 열에 있는 'Return'을 'Existed'로 변경

### filters
- 위의 모든 함수들을 엮어주어 해당 함수만 실행하면 되도록 함

# ships 모듈 설명

## 함수 설명

### select_ship_one
- 1달 전 주문 데이터와 df를 비교하여 배송 여부 체크
- 2021년 6월 현재는 주문 데이터의 '비고'열의 값이 비어있는 지 확인했지만, 8월 이후에는 지난 달, 지지난 달 선별 데이터의 'Ship'열의 값이 'XXXXX'인 지 확인할 예정

  #### 처리방법
  - 지난 달 주문 데이터에서 '비고'열 값이 빈칸인 것만 추출 : df_one_ago_blank
    - 2021년 8월 이후에는 선별 데이터 'Ship' 열 중 'XXXXX'인 값만 추출할 예정
  - df에 'Ship' 키 값 추가
  - 모든 'Ship' 값에 'X' 추가
  - df와 df_one_ago_blank를 Reference Txn ID, From Email Address 순으로 비교 
    - (From Email Address는 주문 데이터에 없음, 선별 데이터로 변경 시, 추가 예정)
  - 비교를 완료하면 모든 데이터 프레임을 하나로 합침
    - all_X - 이메일 매치 - 아이디 매치 순서로 합침
    - 합치는 순서에 따라 뒤에 배치
  - 중복값을 제거 후 가장 마지막 값만 keep
  - 인덱스 순으로 정렬하고 데이터 프레임 반환

### select_ship_two
- select_ship_one에서 가져온 df를 두 달 전 주문 데이터와 비교하여 배송 여부 체크
- 2021년 6월 현재는 주문 데이터의 '비고'열의 값이 비어있는 지 확인했지만, 8월 이후에는 지난 달, 지지난 달 선별 데이터의 'Ship'열의 값이 'XXXXX'인 지 확인할 예정

  #### 처리방법
  - 2달 전 주문 데이터에서 '비고'열 값이 빈칸인 것만 추출 : df_two_ago_blank
    - 2021년 8월 이후에는 선별 데이터 'Ship' 열 중 'XXXXX'인 값만 추출할 예정
  - 모든 'Ship' 값에 'X' 추가
  - df와 df_two_ago_blank를 Reference Txn ID, From Email Address 순으로 비교 
    - (From Email Address는 주문 데이터에 없음, 선별 데이터로 변경 시, 추가 예정)
  - 비교를 완료하면 모든 데이터 프레임을 하나로 합침
    - all_X - 이메일 매치 - 아이디 매치 순서로 합침
    - 합치는 순서에 따라 뒤에 배치
  - 중복값을 제거 후 가장 마지막 값만 keep
  - 인덱스 순으로 정렬하고 데이터 프레임 반환

### select_ship_2
- 이번 달에 2회 이상 구매했는 지 확인

  #### 처리방법
  - 이번 달 df 중 'From Email Address' 열의 값을 모두 저장 : email_list
  - email_list의 길이를 저장 : email_list2
  - email_list에 df 'From Email Address' 열의 값과 비교해서 email_list에 있으면 삭제
  - email_list2와 email_list의 길이를 뺐을 때, 2 이상의 값이 나오면 2회 이상 구매로 확인
    - 'Ship'열에 'O' 추가, 아니면 'X' 추가 그리고 빈 데이터 프레임(df_this_month)에 해당 행만 추가
  - df와 df_this_month 합침
  - 중복값을 제거 후 가장 마지막 값만 keep
  - 인덱스 순으로 정렬하고 데이터 프레임 반환

### select_ship_monthly
- 배송해야할 상품에 monthly로 배송비가 지급됐다면 이번 달에 바로 배송해야하는 지 확인

  #### 처리방법
  - 일단 'Ship'열에 'X' 추가
  - 모든 행의 'Subject' 값을 검사
    - monthly가 값에 있다면 추가한 'X'를 'O'로 변경
      - 만약 bi-monthly 였다면 변경한 'O'를 다시 원 상태로 변경
  - 정렬 후 변경된 df 반환

### ships
- 모든 함수를 순 차 처리 후 마지막 배송 여부 체크
  1. select_ship_one
  2. select_ship_two
  3. select_ship_2
  4. select_ship_monthly

  #### 처리방법
  - 'Ship'열에 'O'가 하나라도 존재한다면 'O' 추가, 없다면 'X' 추가
    - 'Type'열에 'Express'가 들어있다면 'Ship'열 값 앞에 'Express '추가하고 마지막에 'O'로 변경
  - 인덱스 순으로 정렬하고 데이터 프레임 반환

# box_loop 모듈 설명

## 함수 설명

### box_select
- filters와 ships로 처리된 df를 kpopbox인 고객으로 구분

  #### 처리방법
  - 'Subject'열 값 중 'kpopbox'가 포함된 값 중 'Ship'의 마지막 값이 'O'인 행만 데이터 프레임 (kpopbox_people) 추가
  - 이외의 사람들은 'etc_people' 데이터 프레임에 저장
  - 두 가지 데이터 프레임을 반환

  #### box_perfect
  - 나눈 데이터 프레임 두개를 합쳐서 반환
  
  #### box_only_kpop
  - kpopbox_people 반환

  #### box_only_etc
  - etc_people 반환

### preference
- df를 box_only_kpop 함수로 kpopbox 고객만 추출해서, df_cus에서 일치하는 'Preference'열의 데이터를 가져옴
- basic_pack = "shinee, monstax, bts, seventeen, redvelvet, exo, blackpink, day6, jaypark, got7, nct, vixx, straykids, twice, bigbang, ace, ateez"

  #### 처리방법
  - Reference Txn ID 값으로 비교해서 맞는 행을 임시 df에 저장
    - 임시 df가 비어있다면(고객 데이터에 없음, 신규일 확률 높음)
      - 'nothing so, '에 basic_pack을 추가
    - 임시 df에서 중복값을 제거하고 가장 최근 데이터만 남김
      - Preference 값이 비어 있다면 'nothing so, '에 basic_pack을 추가
      - Preference 값이 any라면 'nothing so, '에 basic_pack을 추가
      - Preference 값이 존재하면 해당 행에 Preference 열에 저장
  - 정렬 후 반환

### item_select1
- 오리지널 루프 셋만큼의 열 추가
- loop A, loop 1의 데이터 저장("씨리얼통", "패브릭포스터", "직자석", "저금통", "파우치", "족자", "명찰")

### box_loop1
- df를 item_select1을 돌려서 열 추가해서, 루프 A와 1을 처리

  #### 처리방법 루프 1
  - 행 별로 Preference 데이터를 쉼표를 기준으로 나누어 리스트에 저장(temp_line)
  - temp_line이 1개라면, 루프 1 Preference에 모두 저장
  - temp_line이 2개 이상이라면, 
    - 루프 1 앞에 저장할 2개짜리 그룹1과 뒤에 저장할 2개짜리 그룹2 중복을 허용하지 않고 뽑음
    - 이렇게 되면 최대 중복 선호도가 2개로 제한
    - 그룹 1은 루프 1 앞 두 개 Preference에 저장, 그룹 2는 뒤에 루프 1 뒤 두 개 Preference에 저장
  
  #### 처리방법 루프 A
  - 행 별로 Preference 데이터를 쉼표를 기준으로 나누어 리스트에 저장(temp_line)
  - temp_line이 1개라면, 아이템 별로 해당 'Preference'_'Item'의 상품이 재고 데이터에 있는 지 확인
    - 있다면 Preference에 temp_line에 있는 데이터 바로 저장
    - 없다면 'temp_line 데이터_재고 X'로 저장
  - temp_line이 2개 이상이라면, 아이템 별로 해당 'Preference'_'Item'의 상품이 재고 데이터에 있는 지 확인
    - 있다면, product_list에 해당 'Preference'열의 데이터 저장
      - product_list가 1개라면, Preference에 바로 저장
      - 0개라면, 'temp_line 중 1개_재고 X'로 저장
      - 2개 이상이라면, product_list중 1개 저장

### cell_sum
- Preference와 Item의 값을 합쳐 Preference에 저장 후, Item 열 삭제
- 재고가 없는 경우 뒤에 '_재고 X'를 합쳐 저장

### box_dup
- 랜덤으로 뽑힌 아이템이 같은 사람에게 몇 번 갔는 지 확인
- 이메일로 df와 고객 데이터를 비교한 다음 'List'에 있는 아이템과 비교해서 카운트한 값을 duplicated 열에 저장
- 중복 아이템이 들어간 경우 ', D'를 추가해서 저장


# main 설명

## part 1
- 이번 달 주문 데이터를 전 처리하는 과정
- Type 중 필요한 데이터만 필터 처리
  - filter_keys = ["Subscription Payment", "Express Checkout Payment","General Payment", "Mobile Payment", "Website Payment"]

## part 2
- 전 처리한 데이터에 필요 데이터를 추가하는 과정
- filters 함수와 ships 함수가 쓰임

## part 3
- 후 처리된 데이터를 바탕으로 kpopbox 루프를 돌리는 과정
- 최종 처리된 데이터는 선별데이터의 해당 달 시트에 저장
  
