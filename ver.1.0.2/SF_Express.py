import connection as cn

class SF_express():
    def __init__(self, name = cn.Time.now_str):
        print("선택된 시트의 이름은 '{}' 입니다.".format(name))
        self.SF_express_url = 'https://docs.google.com/spreadsheets/d/1AgR21QH35J0dZU8oagDom7ue6jxS60a-GeODz-luebs/edit#gid=1251707915'
        self.sheet_name = name
        self.SF_doc = cn.gc_play.open_by_url(self.SF_express_url)
        self.sheet_SF_form = self.SF_doc.worksheet('form')
        self.sheet_SF_US = self.SF_doc.worksheet('US_STATE')
        try:
            #시트 선택
            self.sheet_SF = self.SF_doc.worksheet(self.sheet_name)
        except:
            # 이번 달 시트가 없으면 생성
            self.SF_doc.add_worksheet(title=self.sheet_name, rows="100", cols="20")
            self.sheet_SF = self.SF_doc.worksheet(self.sheet_name)
        self.SF_df = cn.pd.DataFrame(self.sheet_SF.get_all_records())
        self.SF_form_df = cn.pd.DataFrame(self.sheet_SF_form.get_all_records())
        self.SF_US_form_df = cn.pd.DataFrame(self.sheet_SF_US.get_all_records())
        # self.SF_df = cn.pd.read_excel('SF_Express.xlsx', sheet_name = name)
        # self.SF_form_df = cn.pd.read_excel('SF_Express.xlsx', sheet_name = 'form')
        # self.SF_US_form_df = cn.pd.read_excel('SF_Express.xlsx', sheet_name = 'US_STATE')
        # self.sheet = xw.Book('SF_Express.xlsx').sheets(name)
        
class select_DF():
    def __init__(self):
        self.df = cn.pd.DataFrame(cn.Worksheet.select_final.get_all_records())
        self.only_df = cn.pd.DataFrame()
        self.only_df = self.only_SF()
        self.only_df = self.select_snack()
        
    def only_SF(self):
        for index, row in self.df.iterrows():
            if (row['Shipping Courier'].find('SF Express') >= 0) & (row['Ship'][len(row['Ship']) - 1] == "O") & (row['Confirm'] != ''):
            # if (row['Shipping Courier'].find('SF Express') >= 0) & (row['Ship'][len(row['Ship']) - 1] == "O"):
                self.only_df = self.only_df.append(row)
        return self.only_df

    def select_snack(self):
        for index, row in self.only_df.iterrows():
            if row['Item Title'].lower().find('ksnackregular') >= 0:
                self.only_df = self.only_df.append(row)
                self.only_df = self.only_df.sort_values(by=['Date'])
                self.only_df = self.only_df.drop_duplicates(['Reference Txn ID'], keep = 'last')
        return self.only_df
    
class TO_SF_DATA(select_DF, SF_express):
    def __init__(self, name = cn.Time.now_str):
        self.df = cn.pd.DataFrame()
        self.select_df = select_DF()
        if name == '':
            self.sf_express = SF_express(cn.Time.now_str)
        else:
            self.sf_express = SF_express(name)
        self.df = self.to_sf_express()
        self.df = self.arrange()
        
    def to_sf_express(self):
        ult_stock = cn.Dataframes.stock
        for index, row in self.select_df.only_df.iterrows():
            for idx, rw in self.sf_express.SF_form_df.iterrows():
                rw['User order number*'] = str(row['Transaction ID'])
                
                row_address = row['Shipping Address'].split(", ")
                if row['Address 1'] == '':
                    recipient = row['Name']
                    address = ''
                elif row['Shipping Address'].find(row['Address 1']) <= 0:
                    recipient = row['Name']
                    address = ''
                elif row['Address 1'].find(',') >= 0:
                    address1 = row['Address 1'].split(", ")
                    detail_idx = row_address.index(address1[0])
                    recipient = " ".join(row_address[:detail_idx]).strip().title()
                    address = ", ".join(row_address[detail_idx:-4]).strip().title()
                else:
                    detail_idx = row_address.index(row['Address 1'])
                    recipient = " ".join(row_address[:detail_idx]).strip().title()
                    address = ", ".join(row_address[detail_idx:-4]).strip().title()
                
                rw['Recipient contact*'] = recipient + '(' + str(row['Name']).title() + ')'
                rw["Recipient's detailed address*"] = address
                
                row_state = row_address[-3]
                if len(row_state) > 2:
                    for idx, row2 in self.sf_express.SF_US_form_df.iterrows():
                        if row2['US State'].strip().lower() == row_state.strip().lower():
                            row_state = row2['Postal Code']
                rw['Monthly card number'] = '0' + str(rw['Monthly card number'])
                rw['Receiving State/Province*'] = str(row_state.strip())
                rw['Receiving City*'] = str(row_address[-4].strip().title())
                # rw["Recipient's detailed address*"] = row_address[-5].strip()
                
                rw["Receiving Post Code*"] = str(row_address[-2].strip())
                if row['Contact Phone Number'] == '':
                    row['Contact Phone Number'] = '8223032142'
                rw["The recipient's phone*"] = row['Contact Phone Number']
                rw["Recipient's mobile phone*"] = row['Contact Phone Number']
                
                if row['Item Title'].lower().find('snack') >= 0:
                    for idx, i in enumerate(['chip', 'biscuit', 'cookie']):
                        rw['English declared product name {}*'.format(idx+1)] = i
                elif row['Item Title'].lower().find('beauty') >= 0:
                    for idx, i in enumerate(['cleansing foam', 'sheet mask pack', 'sunstick']):
                        rw['English declared product name {}*'.format(idx+1)] = i
                else:
                    row_items = row['Item_ex'].strip().split("\n")
                    for idx, i in enumerate(row_items):
                        isplit = i.split('-')
                        pro_ult_stock = ult_stock[ult_stock['product'].str.contains(isplit[1])].reset_index(drop=True)
                        if pro_ult_stock.empty:
                            if i.find('앨범') >= 0:
                                rw['English declared product name {}*'.format(idx+1)] = 'album'
                            else:
                                rw['English declared product name {}*'.format(idx+1)] = row_items[idx]
                        else:
                            row_items[idx] = pro_ult_stock['product_code'][0]
                            rw['English declared product name {}*'.format(idx+1)] = row_items[idx]
                        
                        if idx == 2:
                            break
                        elif len(row_items) < 3:
                            if idx == (len(row_items) - 1):
                                break
                self.df = self.df.append(rw)
        return self.df
        
    def print_only(self):
        print(self.df)
        
    def arrange(self):
        with open("ver.1.0.2/SF_KEY.txt", encoding='UTF-8') as sf_key:
            keys = sf_key.read().split('\t')
        self.df = self.df[keys]
        return self.df
    
    def upload(self):
        self.df = self.sf_express.SF_df.append(self.df)
        cn.pandas_to_sheets(self.df, self.sf_express.sheet_SF, True)
    
    # def upload_row(self):
    #     pandas_to_row(self.df, self.sf_express.sheet_SF, False)

if __name__ == "__main__":
    
    sheet_name = input('어떤 시트에 SF_Express 데이터를 넣으실건가요?\n\n이름을 입력하시면 해당하는 시트에 저장됩니다.\n\nenter를 누르시면 이번 달 시트에 저장됩니다. 예를 들면 202106 시트입니다.\n\n')
    
    to_sf = TO_SF_DATA(sheet_name)
    
    to_sf.print_only()
    to_sf.upload()