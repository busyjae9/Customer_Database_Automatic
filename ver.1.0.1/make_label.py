import connection as cn
from PIL import Image, ImageDraw, ImageFont
import textwrap

def label_select(df):
    label = cn.pd.DataFrame()
    df = df.sort_values(by=['Date'])
    df.set_index("Date")
    for index, row in df.iterrows():
        if row['Ship'][len(row['Ship']) - 1] == "O":
            # label = label.append(row)
            if row['Confirm'] != '':
                label = label.append(row)
    label = label.sort_values(by=['Date'])
    return label

def label_items(row):
    # def label_items(row, indicator):
    items = row['Item']
    items = items.strip()
    items = str(items.replace('\n', ', '))
    # if indicator == 1:
    #     items = row['Items_Num']
    #     items = str(items.split('\n---------\n')[0]).replace('\n', ', ')
    # elif indicator == 2:
    #     items = row['Items_Num']
    #     items = str(items.split('\n---------\n')[1]).replace('\n', ', ')
    # elif indicator == 'A':
    #     items = row['Items_Alpha'].replace('\n', ', ')
    # elif indicator == 'B':
    #     items = row['Items_Alpha']
    #     items = str(items.split('\n---------\n')[1]).replace('\n', ', ')
    return items

def labels(df):
    check_df1 = df
    check_df2 = df
    check_df1 = check_df1.drop_duplicates('Shipping Address', keep = 'first')
    
    label_list = []
    for index, row1 in check_df1.iterrows():
        is_address = check_df2['Shipping Address'] == row1['Shipping Address']
        same_address = check_df2[is_address]
        same_address = same_address.append(row1)
        same_address = same_address.drop_duplicates(['Date', 'Reference Txn ID'], keep = False)
        row1['Date'] = cn.datetime.datetime.strptime(row1['Date'], "%Y-%m-%d")
        row1['Date'] = row1['Date'].strftime("%m") + '월'
        if same_address.empty:
            name = row1['Shipping Courier'] + '\n' + row1['Name']
            address = row1['Shipping Address']
            if row1['Item Title'].lower().find('kpopcdbox') >= 0:
                item = row1['Date'] + ' ' + row1['Item Title'] + '\n' + row1['Album'] + ', ' + label_items(row1)
            elif row1['Item Title'].lower().find('kpopbox') >= 0:
                item = row1['Date'] + ' ' + row1['Item Title'] + '\n' + label_items(row1)
            else:
                item = row1['Date'] + ' ' + row1['Item Title']
        else:
            name = row1['Shipping Courier'] + '\n' + row1['Name']
            address = row1['Shipping Address']
            
            if row1['Item Title'].lower().find('kpopcdbox') >= 0:
                item = row1['Date'] + ' ' + row1['Item Title'] + '\n' + row1['Album'] + ', ' + label_items(row1)
            elif row1['Item Title'].lower().find('kpopbox') >= 0:
                item = row1['Date'] + ' ' + row1['Item Title'] + '\n' + label_items(row1)
            else:
                item = row1['Date'] + ' ' + row1['Item Title'] + '\n '
            
            for index, row2 in same_address.iterrows():
                row2['Date'] = cn.datetime.datetime.strptime(row2['Date'], "%Y-%m-%d")
                row2['Date'] = row2['Date'].strftime("%m") + '월'
                if name.find(row2['Name']) == -1:
                    name = name + '\n' + row2['Name']
                
                if row1['Item Title'].lower().find('kpopcdbox') >= 0:
                    item = item + '\n' + row2['Date'] + ' ' + row2['Item Title'] + '\n' + row2['Album'] + ', ' + label_items(row2)
                elif row1['Item Title'].lower().find('kpopbox') >= 0:
                    item = item + '\n' + row2['Date'] + ' ' + row2['Item Title'] + '\n' + label_items(row2)
                else:
                    item = item + '\n' + row2['Date'] + ' ' + row2['Item Title'] + '\n '
        
        if name.find("אינה מוסטובוי") >= 0:
            name = name.replace("אינה מוסטובוי", "Inna Oksenberg")
        contents = '{Name}!!!{Address}!!!{Item}'.format(Name = name, Address = address, Item = item)
        label_list.append(contents)
        
    return label_list

def make_image(message):
    
    # Image size
    W = 1980
    H = 1400
    bg_color = 'white' # 아이소프트존
    
    # font setting
    font_name = ImageFont.truetype('1_document/Roboto/Roboto-Medium.ttf', size=50)
    font_address = ImageFont.truetype('1_document/Roboto/Roboto-Medium.ttf', size=50)
    font_items = ImageFont.truetype('1_document/NanumMyeongjo.ttf', size=40)
    font_items_name = ImageFont.truetype('1_document/NanumMyeongjoBold.ttf', size=43)
    # font_name = ImageFont.truetype('/content/drive/MyDrive/customer_database/1_document/Roboto/Roboto-Medium.ttf', size=50)
    # font_address = ImageFont.truetype('/content/drive/MyDrive/customer_database/1_document/Roboto/Roboto-Medium.ttf', size=50)
    # font_items = ImageFont.truetype('/content/drive/MyDrive/customer_database/1_document/NanumMyeongjo.ttf', size=40)
    # font_items_name = ImageFont.truetype('/content/drive/MyDrive/customer_database/1_document/NanumMyeongjoBold.ttf', size=43)
    # font = ImageFont.truetype("arial.ttf", size=28)
    font_color = 'rgb(0, 0, 0)' # or just 'black'
		# 원래 윈도우에 설치된 폰트는 아래와 같이 사용 가능하나,
		# 아무리 해도 한글 폰트가 사용이 안 되어.. 같은 폴더에 다운받아 놓고 사용함.
    
    
    image =Image.new('RGB', (W, H), color = bg_color)
    draw = ImageDraw.Draw(image)
    
    # Text wraper to handle long text
	# 40자를 넘어갈 경우 여러 줄로 나눔

    message_silce = message.split('!!!')
    
    # start position for text
    xy = (150, 150)
    space = 25
    width_line = 60
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
            if len(line) > width_line:
                temp_line1 = line.split(', ')[:2]
                temp_line2 = line.split(', ')[2:]
                half_line1 = ", ".join(temp_line1) + ','
                half_line2 = ", ".join(temp_line2)
                draw.text(xy, half_line1, font=font_items, fill=font_color)
                xy = tuple(sum(elem) for elem in zip(xy, (0, height + space)))
                draw.text(xy, half_line2, font=font_items, fill=font_color)
                xy = tuple(sum(elem) for elem in zip(xy, (0, height + space*2)))
            else:
                draw.text(xy, line, font=font_items, fill=font_color)
                xy = tuple(sum(elem) for elem in zip(xy, (0, height + space*2)))
        
    
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
        if (index % 8 == 0) & (index != 0) :
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
        bg_color = 'white' # 아이소프트존
        image  = Image.new('RGB', (W, H), color = bg_color)
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
        image.save('1_label/{}.png'.format(cn.Time.now_str + '_{}'.format(label_data_pages.index(label_message) + 1)))
        # image.save('/content/drive/MyDrive/customer_database/1_label/{}.png'.format(cn.Time.now_str + '_{}'.format(label_data_pages.index(label_message) + 1)))

if __name__ == "__main__":
    save_label()
