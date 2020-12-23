# -*- coding: utf-8 -*-
# @Author:lecis
# @Time:2020/11/27 18:05
# @ Software:PyCharm
# flake8: noqa
from qiniu import Auth, put_file, etag, put_data
import qiniu.config

# 需要填写你的 Access Key 和 Secret Key
access_key = 'pPzV3IuBFze_kqQb-wEe7BRkElbNu5ivCmYzL08M'
secret_key = 'j9muVRiSR5MAg18dxY2o7WXtacglsxWuY92Sy_fe'


def image_store(image_data):
    # 构建鉴权对象
    q = Auth(access_key, secret_key)

    # 要上传的空间
    bucket_name = 'lecis'

    # 上传后保存的文件名,如果不指定，有七牛云维护
    # key = 'hehe.png'
    key = None

    # 生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, key, 3600)

    # 要上传文件的本地路径
    # localfile = './login.jpg'

    # ret, info = put_file(token, key, localfile)
    ret, info = put_data(token, key, image_data)

    # 处理上传成功返回图片名字，否则返回None
    if info.status_code == 200:
        return ret.get('key')
    else:
        return None


if __name__ == '__main__':
    # 使用with测试，可以自动关闭流
    with open('./login.jpg', 'rb') as f:
        image_store(f.read())