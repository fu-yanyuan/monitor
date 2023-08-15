import json
import argparse
import schedule
import datetime
import time

from utils import send_template, kamo_monitor, send_text
from utils import price_init, kamo_get_current_price

def daily_test(args):
    # load configure files
    # parser = argparse.ArgumentParser()
    # args2 = parser.parse_args()
    # with open('./configs/dailytest.json', "r") as config_file:
    #     configs = json.load(config_file)
    # args2.__dict__.update(configs)    

    daily_data = {
        "datetime": {
            "value": str(datetime.datetime.now()),
            "color": "#173177"
        }
    }

    send_template(args, args.templateID['daily check'], daily_data)
    print('daily test done')
    with open(log_file, 'a') as f:
        f.write('\n')
        f.write(f'daily test done at {str(datetime.datetime.now())}')

def kamo_new_arrival(args):
    # get last code 
    with open("./data/data.json", "r") as f:
        last_code = json.load(f)

    lst = kamo_monitor(last_code['kamo_lastcode'])

    if lst != []:
        new_msgs = []
        for item in lst:
            msg = '\n'.join([item.brand, item.name, item.price])
            new_msgs.append(msg)
        total_msg = '\n\n'.join(new_msgs)

        data = {
            "items": {
                "value": total_msg,
                "color": "#173177"
            }
        }

        send_template(args, args.templateID["new arrival"], data)

        # save new last code
        last_code['kamo_lastcode'] = lst[0].code
        with open("./data/data.json", 'w') as f:
            json.dump(last_code, f, indent=4)

def kamo_price_monitor(args):
    """
    item: [current_price, lowest_price, original_price]
    """

    with open("./data/price_monitor_data.json", "r") as f:
        items = json.load(f)

    messages = []
    for i in items:
        last_price, lowest_price = items[i][0], items[i][1]
        
        sale_flag, current_price = kamo_get_current_price(i)
        items[i][0] = current_price
        if sale_flag:
            if current_price < lowest_price:
                items[i][1] = current_price
                messages.append(f'{i}  org:{items[i][2]}, cur is lowest:{current_price}')
    
    if messages != []:

        total_msg = "\n".join(messages)
        data = {
        "items": {
            "value": total_msg,
            "color": "#FF0000"
            }
        }
        
        send_template(args, args.templateID["price monitor"], data)

    with open("./data/price_monitor_data.json", 'w') as f:
        json.dump(items, f, indent=4)

def kamo_test(args):
    kamo_new_arrival(args)
    # kamo_price_monitor(args)
    print('kamo_test done')

    with open(log_file, 'a') as f:
        f.write('\n')
        f.write(f'kamo_test done at {str(datetime.datetime.now())}')

def schedule_plan(time_list):
    schedule.clear()
    
    for t in time_list:
        schedule.every().day.at(t).do(kamo_test, args).tag('kamo')

    # print(schedule.get_jobs())

    schedule.every().day.at('07:59').do(daily_test, args).tag('daily_test')
    schedule.every().day.at('23:00').do(daily_test, args).tag('daily_test')

if __name__ == '__main__':
    # create log file 
    log_file  = str(datetime.datetime.now())[:16] + '.txt'
    with open(log_file, 'a') as log:
        log.write(str(datetime.datetime.now()))

    # load configure files
    print('running...')
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', '-c',
                            type=str,
                            default='./configs/config.json',
                            help='config files')
    args = parser.parse_args()

    if args.config:
        with open(args.config, "r") as config_file:
            configs = json.load(config_file)
    args.__dict__.update(configs)
    print('config file loaded')

    # send_text(args, 'start!')
    print('initial message send')

    # intialization for price monitor
    code_list = ['DJ4977-001',
                'DJ4977-343',
                'DC0748-407',
                'DJ4978-001',
                '106751-01'] # wirte the item codes here
    price_init(code_list)
    print('price monitor initiated')

    time_list = ['08:00:10', '08:01:10', '08:30:10', '08:31:10', 
                 '09:00:10', '09:01:10', '09:30:10', '09:31:10', 
                 '10:00:10', '10:01:10', '10:30:10', '10:31:10', 
                 '11:00:10', '11:01:10', '11:30:10', '11:31:10', 
                 '12:00:10', '12:01:10', '12:30:10', '12:31:10', 
                 '13:00:10', '13:01:10', '13:30:10', '13:31:10', 
                 '14:00:10', '14:01:10', '14:30:10', '14:31:10', 
                 '15:00:10', '15:01:10', '15:30:10', '15:31:10', 
                 '16:00:10', '16:01:10', '16:30:10', '16:31:10', 
                 '17:00:10', '17:01:10', '17:30:10', '17:31:10', 
                 '18:00:10', '18:01:10', '18:30:10', '18:31:10']
    schedule_plan(time_list)
    print('schedule planned')

    while True:
        schedule.run_pending()
        time.sleep(1)