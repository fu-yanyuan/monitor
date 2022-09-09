import json
import argparse
import schedule
import datetime
import time

from utils import send_message, kamo_monitor

def daily_test():
    # load configure files
    parser = argparse.ArgumentParser()
    args2 = parser.parse_args()
    with open('./configs/dailytest.json', "r") as config_file:
        configs = json.load(config_file)
    args2.__dict__.update(configs)    

    daily_data = {
        "datetime": {
            "value": str(datetime.datetime.now()),
            "color": "#173177"
        }
    }

    send_message(args2, daily_data)
    print('daily test done')

def kamo_test(args):
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

        send_message(args, data)

        # save new last code
        last_code['kamo_lastcode'] = lst[0].code
        with open("./data/data.json", 'w') as f:
            json.dump(last_code, f, indent=4)

def schedule_plan(time_list):
    schedule.clear()
    
    for t in time_list:
        schedule.every().day.at(t).do(kamo_test, args).tag('kamo')

    # print(schedule.get_jobs())

    schedule.every().day.at('07:59').do(daily_test).tag('daily_test')
    schedule.every().day.at('23:00').do(daily_test).tag('daily_test')

if __name__ == '__main__':
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