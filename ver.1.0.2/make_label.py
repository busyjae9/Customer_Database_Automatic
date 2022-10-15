from numpy import False_, append, product, int32
import connection as cn
from PIL import Image, ImageDraw, ImageFont
import textwrap

def save_data_at_cus_2(df):
    """고객 데이터와 라벨이 뽑힌 데이터를 통합하여 저장"""
    cus_2 = cn.Dataframes.cus_2
    cus_2 = cus_2.append(df)
    # cus = cus.sort_values(by=['Date'])
    cus_2 = cus_2[['Preference','Date','Name','ID','Transaction ID','Contact Phone Number','Email','Recipient','Address','Country','List']]
    print(cus_2)
    cn.pandas_to_sheets(cus_2, cn.Worksheet.cus_2, False)
    
def save_data(row, temp_df):
    
    row_address = row['Shipping Address'].split(", ")
    if row['Address 1'] == '':
        recipient = row['Name']
    elif row['Shipping Address'].find(str(row['Address 1'])) <= 0:
        recipient = row['Name']
    elif str(row['Address 1']).find(',') >= 0:
        address1 = row['Address 1'].split(", ")
        detail_idx = row_address.index(address1[0])
        recipient = " ".join(row_address[:detail_idx]).strip().title()
    else:
        detail_idx = row_address.index(str(row['Address 1']))
        recipient = " ".join(row_address[:detail_idx]).strip().title()
    
    address = row['Shipping Address']
    df_cus = cn.Dataframes.cus
    refer_email = row['From Email Address']
    df_temp = df_cus[df_cus['Email'] == refer_email]
    
    row_Item_ex = row['Item_ex'].replace('-', '_').replace(' ', '')
    if row_Item_ex.find(',') >= 0:
        item = row_Item_ex.strip().split(',')
    else:
        item = row_Item_ex.strip().split('\n')
    item_list = ', '.join(item)
    
    if df_temp.empty == False:
        df_temp = df_temp.drop_duplicates(['Email'], keep='last')
        item_list = item_list + ', ' + df_temp.iloc[0]['List']

    if temp_df.empty == False:
        temp_df = temp_df[temp_df['Email'] == refer_email]
        if temp_df.empty == False:
            temp_df = temp_df.drop_duplicates(['Email'], keep='last')
            item_list = item_list + ', ' + temp_df.iloc[0]['List']
    
    df_dict = {
            'Preference' : [row['Preference']],
            'Date' : [row['Date']],
            'Name' : [row['Name']],
            'ID' : [row['Reference Txn ID']],
            'Transaction ID' : [row['Transaction ID']],
            'Contact Phone Number' : [str(row['Contact Phone Number'])],
            'Email' : [row['From Email Address']],
            'Recipient' : [recipient],
            'Address' : [address],
            'Country' : [row_address[-1].title()],
            'List' : [item_list]
            }
    row_df = cn.pd.DataFrame(df_dict)
    
    return row_df.iloc[0]
    
def order_check(row, df):
    if row['Reference Txn ID'] == '':
        standard1 = row['From Email Address']
        standard_txt1 = 'From Email Address'
        standard2 = row['Item Title']
        standard_txt2 = 'Item Title'
        idx = df.loc[(df[standard_txt1] == standard1) & (df[standard_txt2] == standard2)].index
        df.loc[idx[0], '비고'] = cn.Time.now_time
        # df_ex = df.loc[(df[standard_txt1] == standard1) & (df[standard_txt2] == standard2)]
    else:
        standard = row['Reference Txn ID']
        standard_txt = 'Reference Txn ID'
        idx = df.loc[(df[standard_txt] == standard)].index
        df.loc[idx[0], '비고'] = cn.Time.now_time
        # df_ex = df.loc[(df[standard_txt] == standard)]
        
    # print(df_ex)
    return df

def order_save(df):
    idx = 1
    while(True):
        try:
            cn.doc_select.add_worksheet(title='{}_배송_{}'.format(cn.Time.now_str, idx), rows="100", cols="20")
            iidx = idx
            break
        except:
            idx += 1
    
    df = df[df['Ship'] == 'labelled']
    selected_sheet = cn.doc_select.worksheet('{}_배송_{}'.format(cn.Time.now_str, iidx))
    cn.pandas_to_sheets(df, selected_sheet, False)
    
def data_finish():
    df = cn.pd.DataFrame(cn.Worksheet.select_final.get_all_records())
    temp_df_cus = cn.pd.DataFrame()
    temp_df_order = cn.Dataframes.order_list
    df = df.sort_values(by=['Date'])
    for index, row in df.iterrows():
        if (row['Ship'][len(row['Ship'])-1] == "O") & (row['Confirm'] != ''):
            row['Ship'] = 'labelled'
            temp_df_cus = temp_df_cus.append(save_data(row, temp_df_cus))
            
            row_date = cn.datetime.datetime.strptime(row['Date'], "%Y-%m-%d")
            row_date = row_date.strftime("%Y%m")
            if row_date in cn.Time.months_list:
                idx = cn.Time.months_list.index(row_date)
                temp_df_order[idx] = order_check(row, temp_df_order[idx])
    # for index, row in df.iterrows():
    #     if (row['Ship'][len(row['Ship'])-1] == "d") & (row['Confirm'] != ''):
    #         row['Ship'] = 'labelled'
    #         temp_df = temp_df.append(save_data(row, temp_df))
    
    for idx, i in enumerate(temp_df_order):
        i = i.applymap(lambda x : str(x).strip())
        cn.pandas_to_sheets(i, cn.Worksheet.order_sheetlist[idx], False)
    order_save(df)
    save_data_at_cus_2(temp_df_cus)
    
def stock_func(i_txt, df, row):
    if i_txt.find('-') >= 0:
        item_list = i_txt.strip().split('-')
        row_ex = cn.pd.DataFrame({
            'product' : [item_list[1]],
            'preference' : [item_list[0]],
            'who' : [row['Name']],
            'stock' : [int(1)]})
        if df.loc[df['product'] == item_list[1]].empty:
            df = df.append(row_ex.iloc[0])
            df = df.reset_index(drop=True)
        elif df.loc[(df['product'] == item_list[1]) & (df['preference'] == item_list[0])].empty:
            group_idx = df.loc[df['product'] == item_list[1]].index
            idx = group_idx[-1] + 1
            temp1 = df[df.index < idx]
            temp2 = df[df.index >= idx]
            df = temp1.append(row_ex, ignore_index=True).append(temp2, ignore_index=True)
            df = df.reset_index(drop=True)
        else:
            group_idx = df.loc[(df['product'] == item_list[1]) & (df['preference'] == item_list[0])].index
            df.loc[group_idx[0], 'stock'] = df.loc[group_idx[0], 'stock'] + int(1)
            df.loc[group_idx[0], 'who'] = df.loc[group_idx[0], 'who'] + ', ' + row['Name']
    else:
        product_idx = df.loc[(df['product'] == i_txt)].index
        row_ex = cn.pd.DataFrame({
            'product' : i_txt,
            'preference' : '',
            'who' : [row['Name']],
            'stock' : [int(1)]})
        if len(product_idx) == 0:
            df = df.append(row_ex)
            df = df.reset_index(drop=True)
        elif len(product_idx) == 1:
            df.loc[product_idx[0], 'stock'] = df.loc[product_idx[0], 'stock'] + int(1)
            df.loc[product_idx[0], 'who'] = df.loc[product_idx[0], 'who'] + ', ' + row['Name']
    return df

def stock_notice(df):
    df = label_select(df)
    temp_df = cn.pd.DataFrame()
    temp_df = temp_df.assign(
        product="",
        preference="",
        who="",
        stock=""
    )
    # temp_df2 = cn.pd.DataFrame()
    # sheet_name = '1주차'
    # sheet_name2 = '2주차'
    sheet_name = input("몇 주차 배송입니까?\n(1, 2, 3, 4)\ncaution : 띄어쓰기불가\n")
    while(True):
        if not sheet_name in ['1', '2', '3', '4']:
            print("Error : there is not sheet '{}'".format(sheet_name))
            sheet_name = input('다시 입력하십시오.\n')
        else :
            print('재고 데이터가 {} 시트에 저장됩니다.\n'.format(sheet_name))
            break
    
    sheet_name = sheet_name + '주차'
    
    for index, row in df.iterrows():
        if row['Item_ex'].find(',') >= 0:
            item = row['Item_ex'].strip().split(',')
        else:
            item = row['Item_ex'].strip().split('\n')
        
        for i in item:
            print('{} of {}'.format(row['Name'], i.strip()))
            
            i_txt = i.strip()
            item_list = i_txt.strip().split('_')
            
            if len(item_list) == 3:
                temp_txt1 = "_".join(item_list[0:1])
                i_txt = temp_txt1 + "-" + item_list[2]
            elif i_txt.find('bi-monthly') >= 0:
                i_txt = i_txt.replace('-', '_')
            elif i_txt.find('-') < 0:
                i_txt = i_txt.replace('_', '-')

            temp_df = stock_func(i_txt, temp_df, row)

    # for index, row in df.iterrows():
    #     row_ex = temp_df.iloc[0].copy()
    #     for i in row['Item_ex'].strip().split('\n'):
    #         # print('{} of {}'.format(row['Name'], i))
    #         row_ex['product'] = i.strip()
    #         row_ex['preference'] = ''
    #         row_ex['stock'] = int(1)
    #         row_ex['who'] = row['Name']
    #         temp_df2 = temp_df2.append(row_ex)

    # print(temp_df)
    stock_notice_sheet = cn.doc_stock.worksheet(sheet_name)
    # stock_notice_sheet2 = cn.doc_stock.worksheet(sheet_name2)
    cn.pandas_to_sheets(temp_df, stock_notice_sheet, True)
    # cn.pandas_to_sheets(temp_df2, stock_notice_sheet2, True)

def label_select(df):
    label = cn.pd.DataFrame()
    df = df.sort_values(by=['Date'])
    df.set_index("Date")
    for index, row in df.iterrows():
        if row['Ship'][len(row['Ship'])-1] == "O":
            # label = label.append(row)
            if row['Confirm'] != '':
                label = label.append(row)
    label = label.sort_values(by=['Date'])
    return label

def label_items(row):
    items = row['Item_ex']
    items = items.strip()
    items = str(items.replace('\n', ', '))
    return items

def labels(df):
    check_df1 = df
    check_df2 = df
    check_df1 = check_df1.drop_duplicates('Shipping Address', keep='first')

    label_list = []
    for index, row1 in check_df1.iterrows():
        is_address = check_df2['Shipping Address'] == row1['Shipping Address']
        same_address = check_df2[is_address]
        same_address = same_address.append(row1)
        same_address = same_address.drop_duplicates(
            ['Date', 'Reference Txn ID'], keep=False)
        row1['Date'] = cn.datetime.datetime.strptime(row1['Date'], "%Y-%m-%d")
        row1['Date'] = row1['Date'].strftime("%m") + '월'
        
        row_address = row1['Shipping Address'].split(", ")
        if row1['Address 1'] == '':
            recipient = row1['Name']
        elif row1['Shipping Address'].find(row1['Address 1']) <= 0:
            recipient = row1['Name']
        elif row1['Address 1'].find(',') >= 0:
            address1 = row1['Address 1'].split(", ")
            detail_idx = row_address.index(address1[0])
            recipient = " ".join(row_address[:detail_idx]).strip().title()
        else:
            detail_idx = row_address.index(row1['Address 1'])
            recipient = " ".join(row_address[:detail_idx]).strip().title()
        
        if same_address.empty:
            name = row1['Shipping Courier'] + '\n' + \
                recipient + '(' + row1['New'] + ')'
            address = row1['Shipping Address']
            if row1['Item Title'].lower().find('kpopcdbox') >= 0:
                # item = row1['Date'] + ' ' + row1['Item Title'] + '\n' + row1['Album'] + ', ' + label_items(row1)
                item = row1['Date'] + ' ' + \
                    row1['Item Title'] + '\n' + label_items(row1)
            elif row1['Item Title'].lower().find('kpopbox') >= 0:
                item = row1['Date'] + ' ' + \
                    row1['Item Title'] + '\n' + label_items(row1)
            else:
                item = row1['Date'] + ' ' + \
                    row1['Item Title'] + '\n' + label_items(row1)
        else:
            name = row1['Shipping Courier'] + '\n' + \
                recipient + '(' + row1['New'] + ')'
            address = row1['Shipping Address']

            if row1['Item Title'].lower().find('kpopcdbox') >= 0:
                # item = row1['Date'] + ' ' + row1['Item Title'] + '\n' + row1['Album'] + ', ' + label_items(row1)
                item = row1['Date'] + ' ' + \
                    row1['Item Title'] + '\n' + label_items(row1)
            elif row1['Item Title'].lower().find('kpopbox') >= 0:
                item = row1['Date'] + ' ' + \
                    row1['Item Title'] + '\n' + label_items(row1)
            else:
                item = row1['Date'] + ' ' + \
                    row1['Item Title'] + '\n' + label_items(row1)

            for index, row2 in same_address.iterrows():
                row2['Date'] = cn.datetime.datetime.strptime(
                    row2['Date'], "%Y-%m-%d")
                row2['Date'] = row2['Date'].strftime("%m") + '월'
                row_address = row2['Shipping Address'].split(", ")
                if row2['Address 1'] == '':
                    recipient = row2['Name']
                elif row2['Shipping Address'].find(row2['Address 1']) <= 0:
                    recipient = row2['Name']
                elif row2['Address 1'].find(',') >= 0:
                    address1 = row2['Address 1'].split(", ")
                    detail_idx = row_address.index(address1[0])
                    recipient = " ".join(row_address[:detail_idx]).strip().title()
                else:
                    detail_idx = row_address.index(row2['Address 1'])
                    recipient = " ".join(row_address[:detail_idx]).strip().title()

                if name.lower().find(row2['Name'].lower()) == -1:
                    name = name + ' & ' + recipient + '(' + row2['New'] + ')'

                if row2['Item Title'].lower().find('kpopcdbox') >= 0:
                    # item = item + '\n' + row2['Date'] + ' ' + row2['Item Title'] + '\n' + row2['Album'] + ', ' + label_items(row2)
                    item = item + '\n' + \
                        row2['Date'] + ' ' + row2['Item Title'] + \
                        '\n' + label_items(row2)
                elif row2['Item Title'].lower().find('kpopbox') >= 0:
                    item = item + '\n' + \
                        row2['Date'] + ' ' + row2['Item Title'] + \
                        '\n' + label_items(row2)
                else:
                    item = item + '\n' + \
                        row2['Date'] + ' ' + row2['Item Title'] + \
                        '\n' + label_items(row2)

        if name.find("אינה מוסטובוי") >= 0:
            name = name.replace("אינה מוסטובוי", "Inna Oksenberg")
        contents = '{Name}!!!{Address}!!!{Item}'.format(
            Name=name, Address=address, Item=item)
        label_list.append(contents)

    return label_list

def make_image(message):

    # Image size
    W = 1980
    H = 1400
    bg_color = 'white'  # 아이소프트존

    # font setting
    font_name = ImageFont.truetype(
        '1_document/Roboto/Roboto-Medium.ttf', size=50)
    font_address = ImageFont.truetype(
        '1_document/Roboto/Roboto-Medium.ttf', size=50)
    font_items = ImageFont.truetype(
        '1_document/NanumBarunGothicLight.ttf', size=55)
    font_items_name = ImageFont.truetype(
        '1_document/NanumBarunGothic.ttf', size=50)
    # font_name = ImageFont.truetype('/content/drive/MyDrive/customer_database/1_document/Roboto/Roboto-Medium.ttf', size=50)
    # font_address = ImageFont.truetype('/content/drive/MyDrive/customer_database/1_document/Roboto/Roboto-Medium.ttf', size=50)
    # font_items = ImageFont.truetype('/content/drive/MyDrive/customer_database/1_document/NanumMyeongjo.ttf', size=40)
    # font_items_name = ImageFont.truetype('/content/drive/MyDrive/customer_database/1_document/NanumMyeongjoBold.ttf', size=43)
    # font = ImageFont.truetype("arial.ttf", size=28)
    font_color = 'rgb(0, 0, 0)'  # or just 'black'
    # 원래 윈도우에 설치된 폰트는 아래와 같이 사용 가능하나,
    # 아무리 해도 한글 폰트가 사용이 안 되어.. 같은 폴더에 다운받아 놓고 사용함.

    image = Image.new('RGB', (W, H), color=bg_color)
    draw = ImageDraw.Draw(image)

    # Text wraper to handle long text
    # 40자를 넘어갈 경우 여러 줄로 나눔

    message_silce = message.split('!!!')

    # start position for text
    xy = (100, 100)
    space = 25
    width_line = 4
    width_address = 40

    lines = message_silce[0].split('\n')
    for line in lines:
        width, height = font_name.getsize(line)
        draw.text(xy, line, font=font_name, fill=font_color)
        xy = tuple(sum(elem) for elem in zip(xy, (0, height + space)))
    xy = tuple(sum(elem) for elem in zip(xy, (0, space * 2)))

    lines = textwrap.wrap(message_silce[1], width_address)
    for line in lines:
        width, height = font_address.getsize(line)
        draw.text(xy, line, font=font_address, fill=font_color)
        xy = tuple(sum(elem) for elem in zip(xy, (0, height + space)))
    xy = tuple(sum(elem) for elem in zip(xy, (0, space * 2)))

    lines = message_silce[2].split('\n')
    for idx, line in enumerate(lines):
        if idx % 2 == 0:
            width, height = font_items_name.getsize(line)
            draw.text(xy, line, font=font_items_name, fill=font_color)
            xy = tuple(sum(elem) for elem in zip(xy, (0, height + space)))
        else:
            width, height = font_items.getsize(line)
            if (len(line.split(',')) >= 3) and (len(line.split(',')) <= 4):
                line = line.replace(" ", "")
                temp_line1 = line.split(',')[:2]
                temp_line2 = line.split(',')[2:]
                half_line1 = ", ".join(temp_line1) + ','
                half_line2 = ", ".join(temp_line2)
                draw.text(xy, half_line1, font=font_items, fill=font_color)
                xy = tuple(sum(elem) for elem in zip(xy, (0, height + space)))
                draw.text(xy, half_line2, font=font_items, fill=font_color)
                xy = tuple(sum(elem)
                           for elem in zip(xy, (0, height + space*2)))
            elif len(line.split(',')) > width_line:
                line = line.replace(" ", "")
                temp_line1 = line.split(',')[:2]
                temp_line2 = line.split(',')[2:4]
                temp_line3 = line.split(',')[4:]
                half_line1 = ", ".join(temp_line1) + ','
                half_line2 = ", ".join(temp_line2) + ','
                half_line3 = ", ".join(temp_line3)
                draw.text(xy, half_line1, font=font_items, fill=font_color)
                xy = tuple(sum(elem) for elem in zip(xy, (0, height + space)))
                draw.text(xy, half_line2, font=font_items, fill=font_color)
                xy = tuple(sum(elem) for elem in zip(xy, (0, height + space)))
                draw.text(xy, half_line3, font=font_items, fill=font_color)
                xy = tuple(sum(elem)
                           for elem in zip(xy, (0, height + space*2)))
            else:
                draw.text(xy, line, font=font_items, fill=font_color)
                xy = tuple(sum(elem)
                           for elem in zip(xy, (0, height + space*2)))

    # 인덱스를 파일 이름으로 저장
    # image.save('1_label/{}.png'.format(idx))
    return image

def make_page(df):

    label = label_select(df)
    messages = []
    messages.extend(labels(label))
    label_data = []
    print('{}개의 메시지가 들어있습니다.'.format(len(messages)))
    for i in messages:
        label_data.append(make_image(i))
    print('{}개의 사진이 들어있습니다.'.format(len(label_data)))

    label_data_pages = []
    temp = []
    for index, content in enumerate(label_data):
        if (index % 8 == 0) & (index != 0):
            label_data_pages.append(temp)
            temp = []
            temp.append(content)
            if content == label_data[-1]:
                label_data_pages.append(temp)
        else:
            temp.append(content)
            if content == label_data[-1]:
                label_data_pages.append(temp)
    print('최종 {}장의 페이지가 들어있습니다.'.format(len(label_data_pages)))
    return label_data_pages

def save_label():
    df = cn.pd.DataFrame(cn.Worksheet.select_final.get_all_records())
    label_data_pages = make_page(df)
    for label_message in label_data_pages:
        W = (1980*2)+30
        H = (1400*4)+50
        bg_color = 'white'  # 아이소프트존
        image = Image.new('RGB', (W, H), color=bg_color)
        # width_bar = Image.new('RGB', (W, 10), color = 'black')
        # height_bar = Image.new('RGB', (10, H), color = 'black')
        # H2 = 1410
        # W2 = 1990
        # image.paste(width_bar, (0, 0))
        # image.paste(width_bar, (0, H2))
        # image.paste(width_bar, (0, H2*2))
        # image.paste(width_bar, (0, H2*3))
        # image.paste(width_bar, (0, H2*4))
        # image.paste(height_bar, (0, 0))
        # image.paste(height_bar, (W2, 0))
        # image.paste(height_bar, (W2*2, 0))

        x = 10
        y = 10
        for index, message in enumerate(label_message):
            if index == 0:
                image.paste(message, (x, y))
            elif index % 2 == 0:
                y = y + message.height + 10
                image.paste(message, (x, y))
            else:
                image.paste(message, ((message.width + (x * 2)), y))

        # image.show()
        image.save('1_label/{}.png'.format(cn.Time.now_str +
                                           '_{}'.format(label_data_pages.index(label_message) + 1)))
        # image.save('/content/drive/MyDrive/customer_database/1_label/{}.png'.format(cn.Time.now_str + '_{}'.format(label_data_pages.index(label_message) + 1)))

if __name__ == "__main__":
    save_label()
    df = cn.pd.DataFrame(cn.Worksheet.select_final.get_all_records())
    stock_notice(df)
    data_finish()