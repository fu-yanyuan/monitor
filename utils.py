import wechatpy
from wechatpy import WeChatClient, WeChatClientException
from wechatpy.client.api import WeChatMessage

import requests
from bs4 import BeautifulSoup

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

def send_message(args, data):
    """
    # appID
    # appsecret
    # templateID
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
        res = wm.send_template(args.userID, args.templateID, data)
        print('Successfully Sent!')
    except WeChatClientException as e:
        print(f'Error! Error Message: {e.errmsg} Error Code: {e.errcode}')
        exit(502)