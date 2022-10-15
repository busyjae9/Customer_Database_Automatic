import connection as cn

class K_POST():
    def __init__(self, name):
        print("선택된 시트의 이름은 '{}' 입니다.".format(name))
        self.K_POST_url = 'https://docs.google.com/spreadsheets/d/1gkBEBtq9x-cplZxcgoIVkN0eRra39lnn2rQRVw7qUKk/edit#gid=239589209'
        self.sheet_name = name
        self.KP_doc = cn.gc_play.open_by_url(self.K_POST_url)
        self.sheet_KP_form = self.KP_doc.worksheet('Form')
        self.sheet_KP_code = self.KP_doc.worksheet('Country Code')
        try:
            #시트 선택
            self.sheet_KP = self.KP_doc.worksheet(self.sheet_name)
        except:
            # 이번 달 시트가 없으면 생성
            self.KP_doc.add_worksheet(title=self.sheet_name, rows="100", cols="20")
            self.sheet_KP = self.KP_doc.worksheet(self.sheet_name)
        self.KP_df = cn.pd.DataFrame(self.sheet_KP.get_all_records())
        self.KP_form_df = cn.pd.DataFrame(self.sheet_KP_form.get_all_records())
        self.KP_Code_df = cn.pd.DataFrame(self.sheet_KP_code.get_all_records())
        # self.SF_df = cn.pd.read_excel('K_POST.xlsx', sheet_name = name)
        # self.SF_form_df = cn.pd.read_excel('K_POST.xlsx', sheet_name = 'form')
        # self.SF_US_form_df = cn.pd.read_excel('K_POST.xlsx', sheet_name = 'US_STATE')
        # self.sheet = xw.Book('K_POST.xlsx').sheets(name)
        
class select_DF():
    def __init__(self):
        self.df = cn.pd.DataFrame(cn.Worksheet.select_final.get_all_records())
        self.only_df = cn.pd.DataFrame()
        self.only_df = self.only_KP()
        self.only_df = self.select_one()
        
    def only_KP(self):
        for index, row in self.df.iterrows():
            if (row['Shipping Courier'].find('KP') >= 0) & (row['Ship'][len(row['Ship']) - 1] == "O") & (row['Confirm'] != ''):
            # if (row['Shipping Courier'].find('SF Express') >= 0) & (row['Ship'][len(row['Ship']) - 1] == "O"):
                self.only_df = self.only_df.append(row)
        return self.only_df
    
    def select_one(self):
        self.only_df = self.only_df.drop_duplicates(['From Email Address'], keep = 'last')
        self.only_df = self.only_df.sort_values(by=['Date'])
        return self.only_df
    
class TO_SF_DATA(select_DF, K_POST):
    def __init__(self, name):
        self.df = cn.pd.DataFrame()
        self.select_df = select_DF()
        self.K_POST = K_POST(name)
        self.df = self.to_K_POST()
        self.df = self.arrange()
        
    def to_K_POST(self):
        for index, row in self.select_df.only_df.iterrows():
            for idx, rw in self.K_POST.KP_form_df.iterrows():
                row_address = row['Shipping Address'].split(", ")
                if str(row['Address 1']) == '':
                    recipient = str(row['Name'])
                    address = ", ".join(row_address)
                elif row['Shipping Address'].find(str(row['Address 1'])) <= 0:
                    recipient = str(row['Name'])
                    address = ", ".join(row_address)
                elif str(row['Address 1']).find(',') >= 0:
                    address1 = str(row['Address 1']).split(", ")
                    detail_idx = row_address.index(address1[0])
                    recipient = " ".join(row_address[:detail_idx]).strip().title()
                    address = ", ".join(row_address[detail_idx:]).strip().title()
                else:
                    detail_idx = row_address.index(str(row['Address 1']))
                    recipient = " ".join(row_address[:detail_idx]).strip().title()
                    address = ", ".join(row_address[detail_idx:]).strip().title()
                
                rw["수취인명"] = recipient + '(' + str(row['Name']).title() + ')'
                rw["수취인 주소"] = address
                
                row_country = row_address[-1]
                for idx, row2 in self.K_POST.KP_Code_df.iterrows():
                    if row2['국가명'].find("(") >= 0:
                        standard = row2['국가명'].split('(')[0]
                    else:
                        standard = row2['국가명']
                    
                    if row_country.find("(") >= 0:
                        row_country = row_country.split('(')[0]
                        
                    if standard.strip().lower() == row_country.strip().lower():
                        row_country = row2['국가코드']
                rw['수취인 국가코드'] = row_country
                
                if row['Item Title'].lower().find('snack') >= 0:
                    rw['내용품명'] = 'corn chip'
                    rw['HSCODE'] = '1905901090'
                elif row['Item Title'].lower().find('kpopbox') >= 0:
                    rw['내용품명'] = 'sticker'
                    rw['HSCODE'] = '4821100000'
                elif row['Item Title'].lower().find('cd') >= 0:
                    rw['내용품명'] = 'sticker'
                    rw['HSCODE'] = '8523491020'
                elif row['Item Title'].lower().find('beauty') >= 0:
                    rw['내용품명'] = 'sheet mask'
                    rw['HSCODE'] = '3307904000'
                
                rw['상품구분'] = 'Gift'
                rw['우편물구분'] = 'R'
                rw['우편물 종류 코드'] = 're'
                rw['개수'] = '1'
                rw['가격'] = 14
                rw['생산지'] = 'KR'
                self.df = self.df.append(rw)
        return self.df
        
    def print_only(self):
        print(self.df)
        
    def arrange(self):
        with open("ver.1.0.2/KP_KEY.txt", encoding='UTF-8') as sf_key:
            keys = sf_key.read().split('\t')
        self.df = self.df[keys]
        return self.df
    
    def upload(self):
        self.df = self.K_POST.KP_df.append(self.df)
        cn.pandas_to_sheets(self.df, self.K_POST.sheet_KP, True)
    
    # def upload_row(self):
    #     pandas_to_row(self.df, self.K_POST.sheet_SF, False)

if __name__ == "__main__":
    
    # sheet_name = input('어떤 시트에 SF_Express 데이터를 넣으실건가요?\n\n이름을 입력하시면 해당하는 시트에 저장됩니다.\n\nenter를 누르시면 이번 달 시트에 저장됩니다. 예를 들면 202106 시트입니다.\n\n')
    
    sheet_name= 'Main'
    
    to_sf = TO_SF_DATA(sheet_name)
    
    to_sf.print_only()
    to_sf.upload()