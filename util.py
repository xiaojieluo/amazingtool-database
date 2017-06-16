import requests
from PIL import Image
from io import BytesIO
from qiniu import Auth,put_file, etag
import qiniu.config
import asyncio
import os

def get_img(url='http://www.todayonhistory.com/uploadfile/2015/1130/20151130092633424.jpg'):
    '''
    从 url 中下载图片，并上传到七牛云存储
    返回值为 七牛云存储外链
    '''

    path = './image/'
    filename = url.split('/')[-1]
    fullname = path+filename

    if os.path.isdir(path):
        pass
    else:
        os.mkdir(path)


    if url == '':
        return ''
    if url[0:4] != 'http' and url[-3:] == ('jpg' or 'png' or 'JPG'):
        url = 'http://www.todayonhistory.com' + url

    try:
        r = requests.get(url)
        if r.status_code != 200:
            print('requests error')
            return ''

        with open(path+filename, 'wb') as fp:
            fp.write(r.content)
        return filename
    except:
        return ''


    # await upload_qiniu(fullname, filename)


def upload_qiniu(filename):
    access_key = 'q4-ZjBAaOWt5pDR2OHTiGkpDenf1m5y3D1zC5p7-'
    secret_key = 'KLPTXKmhcwHyOXbGzoQJJgZixcM0iHZDDjHN100i'
    bucket_name = 'history'

    if filename == '':
        return

    localfile = './image/'+filename
    q = Auth(access_key, secret_key)

    token = q.upload_token(bucket_name, filename, 3600)


    ret, info = put_file(token, filename, localfile)

    return info

if __name__ == '__main__':
    get_img()
