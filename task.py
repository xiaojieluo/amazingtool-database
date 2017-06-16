from celery import Celery
import requests
import json

from db import db
from util import upload_qiniu, get_img

broker = 'redis://localhost:6379'
backend = 'redis://localhost:6379'

app = Celery('Collection', broker = broker, backend = backend)

@app.task(bind=True)
def ip(self, ip):
    url = 'http://ip-api.com/json/'
    try:
        r = requests.get(url+ip)
        html = r.json()

        if html.get('status', '') == 'fail':
            return '[fail]'
        else :
            update('ip', {'query':html.get('query', '')}, html)
            print(html)
            return '[ok]'

    except requests.ConnectionError as e:
        with open('log.txt', 'w') as fp:
            fp.write(ip+'...ConnectionError\n')

        raise self.retry(exc=e, countdown=5, max_retries=10)

@app.task(bind=True)
def history(self, date):
    url = 'http://www.todayonhistory.com/index.php?a=json_event&pagesize=40&month={month}&day={day}'
    try:
        r = requests.get(url.format(month=date[0], day=date[1]))
        events = list()

        if r.json():
            for tmp in r.json():
                filename = get_img(tmp.get('thumb', ''))
                info = upload_qiniu(filename)
                print(filename)
                # filename = qiniu_upload.delay(tmp)

                events.append(dict(
                    title = tmp.get('title', ''),
                    solaryear = tmp.get('solaryear', ''),
                    description = tmp.get('description', ''),
                    thumb = filename
                ))

            data = dict(
                events = events,
                month = date[0],
                day = date[1]
            )

            update('history', {'month':data['month'], 'day':data['day']}, data, force=True)
            return '[ok]'
        else:
            return '[failed]'
    except requests.ConnectionError as e:
        raise self.retry(exc=e, countdown=5, max_retries=10)

@app.task(bind=True)
def qiniu_upload(self, tmp):
    filename = get_img(tmp.get('thumb', ''))
    info = upload_qiniu(filename)
    return filename


def update(type_, query, data, force=False):
    '''
    当数据不存在时,更新 mongodb 数据库
        type_ : 类型
        data  : 要写入数据库的内容, dict 格式,
            { text:'', result:'' }
    '''
    database = db[type_]
    if isinstance(data, str):
        data = json.loads(data)

    if database.find_one(query) is None:
        print("insert database")
        database.insert_one(data)
    else:
        print("update database")
        database.find_one_and_update(query, {'$set':data})
