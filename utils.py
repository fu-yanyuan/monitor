import wechatpy
from wechatpy import WeChatClient, WeChatClientException
from wechatpy.client.api import WeChatMessage

import requests
from bs4 import BeautifulSoup

import json

brands = {
    '[ミズノ]' : 'mizuno',
    '[ナイキ]' : 'nike',
    '[アディダス]' : 'adidas',
    '[プーマ]' : 'puma',
    '[アシックス]' : 'acisc'
}

class Spike:
    def __init__(self, name, brand, price, code=None, link=None):
        self.name = name
        self.brand = brand
        self.price = price
        self.code = code
        self.link = link

def kamo_monitor(last_code):
    """
    kamo new arrival monitor
    """
    url = "https://www.sskamo.co.jp/s/search/cfw_stdcdsd/"
    page = requests.get(url)
    page_text = page.text
    # print(page_test)

    soup = BeautifulSoup(page_text, 'lxml')
    goods = soup.find_all('div', class_="block-goods-list-d--item-area")

    lst = []
    for g in goods:
        name = g.find('div', class_="block-goods-list-d--items-name")
        brand = g.find('div', class_="block-goods-list-d--items-brand").text
        price = g.find('div', class_="block-goods-list-d--items-price").text.replace('\t','').replace('\n', '')[1:-1]
        code = name.a['href'][6:-1]
        link = 'https://www.sskamo.co.jp' + name.a['href']
        # stop if no more new items
        if code == last_code:
            break
        # translate jp into en
        brand = brands[brand] if brand in brands else brand

        lst.append(Spike(name=name.text, 
                        brand=brand,
                        price=price,
                        code=code,
                        link=link))

    return lst

def send_template(args, templateID, data):
    """
    # appID
    # appsecret
    # templateID
      "daily check", "new arrival", "price monitor", "hi"
    # userID
    # messages
    """
    # data format
    # https://mp.weixin.qq.com/debug/cgi-bin/readtmpl?t=tmplmsg/faq_tmpl
    # data = {
    #     "items": {
    #         "value": messages,
    #         "color": "#173177"
    #     }
    # }

    try:
        client = WeChatClient(args.appID, args.appsecret)
    except WeChatClientException as e:
        # print('微信获取 token 失败，请检查 appID 和 appsecret, 或当日调用量是否已达到微信限制。')
        print('failed to get token')
        exit(502)

    wm = WeChatMessage(client)

    try:
        print('Sending...')
        res = wm.send_template(args.userID, templateID, data)
        print('Successfully Sent!')
    except WeChatClientException as e:
        print(f'Error! Error Message: {e.errmsg} Error Code: {e.errcode}')
        exit(502)

def send_text(args, text):
    client = WeChatClient(args.appID, args.appsecret)
    client.message.send_text(args.userID, text)

################### for price monitor

def kamo_get_current_price(item_code):
    """
    input: item_code
    return: (sale_flag, current_price, original_price)
    """
    url = "https://www.sskamo.co.jp/s/g/g" + item_code + "/"
    page = requests.get(url)
    page_text = page.text
    soup = BeautifulSoup(page_text, 'lxml')
    # print(soup.prettify())

    price_original = soup.find("div", class_="block-goods-price--price price js-enhanced-ecommerce-goods-price")
    if price_original: # no sale
        price = int(price_original.text[1:-2].replace(',', ''))
        return (0, price) # 0 means no sale

    sale = soup.find("div", class_="block-goods-sale--sale price js-enhanced-ecommerce-goods-price")
    if sale:
        current_sale_price = int(sale.text[2:-2].replace(',', ''))
        # original_price = int(soup.find("div", class_="block-goods-sale--price").text[2:].replace(',', ''))
        return (1, current_sale_price)

def kamo_get_original_price(item_code):
    url = "https://www.sskamo.co.jp/s/g/g" + item_code + "/"
    page = requests.get(url)
    page_text = page.text
    soup = BeautifulSoup(page_text, 'lxml')

    price_original = soup.find("div", class_="block-goods-price--price price js-enhanced-ecommerce-goods-price")
    if price_original:
        return int(price_original.text[1:-2].replace(',', ''))
    else:
        return int(soup.find("div", class_="block-goods-sale--price").text[2:].replace(',', ''))

def price_init(code_list):
    """ 
    [current, lowest, original]
    """
    data = {}
    for i in code_list:
        _, current_price = kamo_get_current_price(i)
        original_price = kamo_get_original_price(i)
        if current_price < original_price:
            data[i] = [current_price, current_price, original_price]
        else:
            data[i] = [current_price, original_price, original_price]
    # print(data)
    with open("./data/price_monitor_data.json", 'w') as f:
        json.dump(data, f, indent=4)

