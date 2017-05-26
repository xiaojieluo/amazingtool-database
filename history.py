import task
import sys
import os

last_day = [1,1]
history_file = 'history_day.txt'

if os.path.isfile(history_file):

    with open(history_file, 'r') as fp:
        tmp_c = fp.read()

    day_c = list(map(int, tmp_c.split('.')))

    if len(day_c) == 2:
        last_day = day_c
        print("\nStart crawling from "+ str(last_day[0]) + '/'+ str(last_day[1]))
    else:
        print("\nread "+ history_file + ' failed...')
        print('Start crawling from 01/01\n')

for month in range(1, 13):
    if month < int(last_day[0]): continue

    if month in (1, 3, 5, 7, 8, 10, 12):
        all_day = 31
    elif month in (4, 6, 9, 11):
        all_day = 30
    elif month == 2:
        # TODO: 这里应该判断下是不是闰年,不过 todayonhistory.com 不支持 2 月29 号的查询,暂时先这样
        all_day = 28

    for day in range(1, all_day+1):
        if day < int(last_day[1]):continue
        last_day[1] = 1

        date = [str(month), str(day)]
        print(date)
        try:
            if os.path.isfile(history_file):
                os.remove(history_file)
            result = task.history.delay(date)
            print('{date}....{result}'.format(date=('/'.join(date)), result=result.get()))

        except KeyboardInterrupt as e:
            with open(history_file, 'wt') as fp:
                fp.write('.'.join(date))
                print("\n\nsystem exit...")
                print('last day {date} write in {file}\n'.format(date='.'.join(date),file=history_file))
                sys.exit()
