from numpy import append
from connection import DHL_connection as cn

class DHL():
    def __init__(self, name): # name -> list of strings
        print("선택된 시트의 이름은 '{}' 입니다.".format(name))
        self.DHL_url = 'https://docs.google.com/spreadsheets/d/1OJ2JMDM2Z9WX3enWHOmto3BMj7l_sZoWpq0uQsRlbBc/edit#gid=0'
        self.DHL_doc = cn.gc_play.open_by_url(self.DHL_url)
        self.sheet_DHL_form = self.DHL_doc.worksheet('Form')
        self.sheet_DHL_code = self.DHL_doc.worksheet('Country Code')
        self.sheet_DHL_A = self.DHL_doc.worksheet(name[0])
        self.sheet_DHL_B = self.DHL_doc.worksheet(name[1])
        self.sheet_DHL_C = self.DHL_doc.worksheet(name[2])
        self.DHL_A_df = cn.pd.DataFrame(self.sheet_DHL_A.get_all_records())
        self.DHL_B_df = cn.pd.DataFrame(self.sheet_DHL_B.get_all_records())
        self.DHL_C_df = cn.pd.DataFrame(self.sheet_DHL_C.get_all_records())
        self.DHL_form_df = cn.pd.DataFrame(self.sheet_DHL_form.get_all_records())
        self.DHL_Code_df = cn.pd.DataFrame(self.sheet_DHL_code.get_all_records())
        # self.SF_df = cn.pd.read_excel('K_POST.xlsx', sheet_name = name)
        # self.SF_form_df = cn.pd.read_excel('K_POST.xlsx', sheet_name = 'form')
        # self.SF_US_form_df = cn.pd.read_excel('K_POST.xlsx', sheet_name = 'US_STATE')
        # self.sheet = xw.Book('K_POST.xlsx').sheets(name)
        
class select_DF():
    def __init__(self):
        self.df = cn.pd.DataFrame(cn.Worksheet.select_test.get_all_records())
        self.only_df = cn.pd.DataFrame()
        self.only_DHL()
        self.select_one()
        
    def only_DHL(self):
        for index, row in self.df.iterrows():
            if (row['Shipping Courier'].find('DHL') >= 0) & (row['Ship'][len(row['Ship']) - 1] == "O") & (row['Confirm'] != ''):
            # if (row['Shipping Courier'].find('SF Express') >= 0) & (row['Ship'][len(row['Ship']) - 1] == "O"):
                self.only_df = self.only_df.append(row)
    
    def select_one(self):
        for index, row in self.only_df.iterrows():
            if self.only_df[(self.only_df['From Email Address'] == row['From Email Address']) & (self.only_df['Shipping Address'] == row['Shipping Address'])].empty == False :
                same_idx = self.only_df[(self.only_df['From Email Address'] == row['From Email Address']) & (self.only_df['Shipping Address'] == row['Shipping Address'])].index
                same_idx = list(same_idx)
                if len(same_idx) > 1:
                    for i in same_idx:
                        if same_idx.index(i) == 0 :
                            pass
                        else:
                            if self.only_df.loc[same_idx[0]]["Item_ex"].find(',') >= 0:
                                self.only_df.loc[same_idx[0], "Item_ex"] = self.only_df.loc[same_idx[0], "Item_ex"] + ',' + self.only_df.loc[i, "Item_ex"]
                                self.only_df.loc[same_idx[0], "Item Title"] = self.only_df.loc[same_idx[0], "Item Title"] + ',' + self.only_df.loc[i, "Item Title"]
                            else:
                                self.only_df.loc[same_idx[0], "Item_ex"] = self.only_df.loc[same_idx[0], "Item_ex"] + '\n' + self.only_df.loc[i, "Item_ex"]
                                self.only_df.loc[same_idx[0], "Item Title"] = self.only_df.loc[same_idx[0], "Item Title"] + ',' + self.only_df.loc[i, "Item Title"]
                self.only_df = self.only_df.drop(same_idx[1:])
        self.only_df = self.only_df.sort_values(by=['Date'])
    
class TO_SF_DATA(select_DF, DHL):
    df_A = cn.pd.DataFrame()
    df_B = cn.pd.DataFrame()
    df_C = cn.pd.DataFrame()
    list_B = ['MY', 'PT', 'ZA', 'PL', 'GR', 'FI', 'HR', 'CL', 'DE', 'AT']
    list_C = ['GB', 'IE']
    list_D = ['GB']
    
    def __init__(self, name):
        self.select_df = select_DF()
        self.DHL = DHL(name)
        self.form = self.DHL.DHL_form_df.iloc[0].copy()
        self.to_DHL()
        print(self.df_A)
        # self.arrange()
        
    def to_DHL(self):
        ult_stock = cn.Dataframes.stock
        for index, row in self.select_df.only_df.iterrows():
            row_address = row['Shipping Address'].split(", ")
            row_country = row_address[-1]
            row_country = (lambda x : "U.S.A" if x.lower().replace(" ", "").find("unitedstates") >= 0 else row_country)(row_country)
            row_country = (lambda x : x.split('(')[0] if x.find("(") >= 0 else x)(row_country)
            for idx, row2 in self.DHL.DHL_Code_df.iterrows():
                standard = (lambda x : x.split('(')[0] if x.find("(") >= 0 else x)(row2['국가명'])
                row_country = (lambda x, y : row2['국가코드'] if x == y else row_country)(standard.strip().lower().replace(" ", ""), row_country.strip().lower().replace(" ", ""))
            print(row['Name'], row_country)
            if row_country in self.list_B :
                self.DHL_B(row, ult_stock, row_country)
            elif row_country in self.list_C :
                self.DHL_C(row, ult_stock, row_country)
            else:
                self.DHL_A(row, ult_stock, row_country)
        
    def address_process(self, row):
        row_address = row['Shipping Address'].split(", ")
        row_date = cn.datetime.datetime.strptime(row['Date'], "%Y-%m-%d")
        row_date = row_date.strftime("%d/%m/%Y")
        contact_number = row['Contact Phone Number']
        if contact_number == '':
            contact_number = 0
            
        if row['Address 1'] == '':
                city = row_address[-4]
                recipient = row['Name']
                address = ''
        elif row['Shipping Address'].find(row['Address 1']) <= 0:
            city = row_address[-4]
            recipient = row['Name']
            address = ''
        elif row['Address 1'].find(',') >= 0:
            address1 = row['Address 1'].split(", ")
            detail_idx = row_address.index(address1[0])
            if row_address.index(address1[1]) == row_address.index(row_address[-4]):
                city = row_address[-3]
                recipient = " ".join(row_address[:detail_idx]).strip().title()
                address = ", ".join(row_address[detail_idx:-4]).strip().title()
            else:
                city = row_address[-4]
                recipient = " ".join(row_address[:detail_idx]).strip().title()
                address = ", ".join(row_address[detail_idx:-4]).strip().title()
        else:
            detail_idx = row_address.index(row['Address 1'])
            if detail_idx == row_address.index(row_address[-4]):
                city = row_address[-3]
                recipient = " ".join(row_address[:detail_idx]).strip().title()
                address = ", ".join(row_address[detail_idx:-3]).strip().title()
            else:
                city = row_address[-4]
                recipient = " ".join(row_address[:detail_idx]).strip().title()
                address = ", ".join(row_address[detail_idx:-4]).strip().title()
        
        return row, row_address, city, recipient, address, row_date, contact_number
        
    def form_process(self, form, row_country, row, row_address, city, recipient, address, row_date, contact_number):
        form["Order Number"] = str(row['Transaction ID'])
        form["Date"] = row_date
        form["To Name"] = recipient + '(' + str(row['Name']).title() + ')'
        form["Destination Street"] = address
        form["Destination City"] = city
        form["Destination Postcode"] = row_address[-2]
        if str(form["Destination Postcode"]).find('-') >= 0:
            form["Destination Postcode"] = str(form["Destination Postcode"]).split('-')[0]
        form["Destination State"] = row_address[-3]
        form["Destination Country"] = row_address[-1]
        form["Destination Email"] = row['From Email Address']
        form["Destination Phone"] = int(contact_number)
        form['Country Code'] = row_country
        form["Weight"] = 0.5
        form["Shipping Method"] = 'DHL Express Intl'
        form["Qty"] = 1
        
        return form
    
    def item_A_process(self, row, form, ult_stock):
        form["Item Price"] = 38
        
        if row['Item_ex'].find(',') >= 0 :
            row_items = row['Item_ex'].strip().split(",")
        else:
            row_items = row['Item_ex'].strip().split("\n")
        
        row_contents = []
        for idx, i in enumerate(row_items):    
            if i.lower().find('snack') >= 0:
                temp = "snacks"
            elif i.lower().find('beauty') >= 0:
                temp = "cosmetics"

            else:
                isplit = i.strip().split('-')
                pro_ult_stock = ult_stock[ult_stock['product'].str.contains(isplit[1])].reset_index(drop=True)
                if pro_ult_stock.empty:
                    if i.find('앨범') >= 0:
                        temp = 'album'
                    else:
                        temp = i
                else:
                    i_code = pro_ult_stock['product_code'][0]
                    temp = i_code
                    
            if (temp in ["snacks", "cosmetics"]) & (temp in row_contents):
                pass
            else:
                row_contents.append(temp)
        row_content = ", ".join(row_contents)
        form["Item Name"] = row_content
        form["Contents"] = row_content
        self.df_A = self.df_A.append(form)
            
    def item_B_process(self, row, form, ult_stock, box_stock, box_price):
        if row['Item_ex'].find(',') >= 0 :
            row_items = row['Item_ex'].strip().split(",")
        else:
            row_items = row['Item_ex'].strip().split("\n")
        all_price = 0
        box_qty = 0
        print(box_price)
        box_price['box_name'].str.strip().lower().replace(' ', '')
        for i in row_items:
            pro_box_price = box_price[box_price['box_name'] == i.lower().replace(' ', '')].reset_index(drop=True)
            if all_price > 0 :
                all_price = all_price + int(pro_box_price[0]['Price'])
                box_qty += 1
            else:
                all_price = int(pro_box_price[0]['Price'])
                box_qty += 1
        
        row_contents = []
        box_stock = box_stock.astype(str).apply(lambda x : x.str.strip().lower().replace(' ', ''))
        for i in row_items:
            if (i.lower().find('snack') >= 0) or (i.lower().find('beauty') >= 0):
                pro_box_stock = box_stock[box_stock['box_name'] == i.lower().replace(' ', '')].reset_index(drop=True)
                if pro_box_stock.empty:
                    row_contents.append("경고")
                    month_idx = i.find('월')
                    bonus = i[month_idx-1:month_idx+1] + '보너스'
                    row_contents.append(bonus)
                else:
                    row_contents.extend(pro_box_stock[0]['contents'].strip().split('\n'))
                    month_idx = i.find('월')
                    bonus = i[month_idx-1:month_idx+1] + '보너스'
                    row_contents.append(bonus)
            else:
                row_contents.append(i)
                
        row_item_code = []
        row_item_price = []
        row_item_hscode = []
        for i in row_contents:
            if i.find('-') >= 0:
                isplit = i.strip().split('-')
                pro_ult_stock = ult_stock[ult_stock['product'].str.contains(isplit[1])].reset_index(drop=True)
                if pro_ult_stock.empty:
                    if i.find('앨범') >= 0:
                        i_code = 'album'
                        i_hscode = ''
                        i_price = 0
                    else:
                        i_code = i
                        i_hscode = ''
                        i_price = 0
                else:
                    i_code = pro_ult_stock[0]['product_code']
                    i_hscode = pro_ult_stock[0]['hs code']
                    i_price = int(pro_ult_stock[0]['price'])
            else:
                pro_ult_stock = ult_stock[ult_stock['product'].str.contains(i)].reset_index(drop=True)
                if pro_ult_stock.empty:
                    i_code = i
                    i_hscode = ''
                    i_price = 0
                else:
                    i_code = pro_ult_stock[0]['product_code']
                    i_hscode = pro_ult_stock[0]['hs code']
                    i_price = int(pro_ult_stock[0]['price'])
                    all_price -= i_price
            row_item_code.append(i_code)
            row_item_hscode.append(i_hscode)
            row_item_price.append(i_price)
            
        row_content = ", ".join(row_item_code)
        form["Contents"] = row_content
        
        code_df = cn.pd.DataFrame(columns=['Item', 'Code', 'Hscode', 'Price'])
        for item, code, hscode, price in row_contents, row_item_code, row_item_hscode, row_item_price:
            if item.find('보너스') >= 0:
                if box_qty == 1:
                    price = all_price
                    data = [item, code, hscode, price]
                elif box_qty > 1:
                    price = all_price/box_qty
                    data = [item, code, hscode, price]
            else:
                data = [item, code, hscode, price]
            code_df.append(cn.pd.Series(data, index=code_df.index), ignore_index=True)
        print(code_df)
        
        for idx, row in code_df.iterrows():
            form["Item Name"] = row['Code']
            form["Item Price"] = row['Price']
            form["Code"] = row['Hscode']
            self.df_B = self.df_B.append(form)

        
    def item_C_process(self, row, form, ult_stock, box_stock):
        pass
        
    def DHL_A(self, row, ult_stock, row_country):        
        form = self.form.copy()
        form = self.form_process(form, row_country, *self.address_process(row))
        form = self.item_A_process(row, form, ult_stock)
        
    def DHL_B(self, row, ult_stock, row_country):
        box_stock = cn.Dataframes.etc_box
        box_price = cn.Dataframes.box_price
        form = self.form.copy()
        form = self.form_process(form, row_country, *self.address_process(row))
        form = self.item_B_process(row, form, ult_stock, box_stock, box_price)
    
    def DHL_C(self, row, ult_stock, row_country):
        box_stock = cn.Dataframes.etc_box
        form = self.form.copy()
        form = self.form_process(form, row_country, *self.address_process(row))
    
    def print_only(self):
        print(self.df_A)
        print('-------------------------------------------------')
        print(self.df_B)
        print('-------------------------------------------------')
        print(self.df_C)
        print('-------------------------------------------------')
        
    def arrange(self):
        with open("ver.1.0.2/DHL_KEY.txt", encoding='UTF-8') as sf_key:
            keys = sf_key.read().split('\t')
        self.df_A = self.df_A[keys]
        self.df_B = self.df_B[keys]
        self.df_C = self.df_C[keys]
    
    def upload(self):
        self.df_A = self.DHL.DHL_A_df.append(self.df_A)
        cn.pandas_to_sheets(self.df, self.DHL.sheet_DHL_A, True)
        self.df_B = self.DHL.DHL_B_df.append(self.df_B)
        cn.pandas_to_sheets(self.df, self.DHL.sheet_DHL_B, True)
        self.df_C = self.DHL.DHL_C_df.append(self.df_C)
        cn.pandas_to_sheets(self.df, self.DHL.sheet_DHL_code, True)
    
    # def upload_row(self):
    #     pandas_to_row(self.df, self.K_POST.sheet_SF, False)

if __name__ == "__main__":
    
    # sheet_name = input('어떤 시트에 SF_Express 데이터를 넣으실건가요?\n\n이름을 입력하시면 해당하는 시트에 저장됩니다.\n\nenter를 누르시면 이번 달 시트에 저장됩니다. 예를 들면 202106 시트입니다.\n\n')
    
    sheet_name = ['A', 'B', 'C']
    
    to_sf = TO_SF_DATA(sheet_name)
    
    # to_sf.print_only()
    # to_sf.upload()