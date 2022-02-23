import hashlib
import requests
import os
import json
import argparse
import tqdm

parser = argparse.ArgumentParser()
parser.add_argument("-u", "--upload", help="upload file", )
parser.add_argument("-l", "--fileList", help="file list", action="store_true")
parser.add_argument("-d", "--download", help="download file")
parser.add_argument("-s", "--save", help="save path", action="store_true")
parser.add_argument("-m", "--mail", help="send mail", action="store_true")

args = parser.parse_args()

user_agent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"
headers = {
    'User-Agent': user_agent
}


def get_file_list():
    url_get_file_list = 'http://127.0.0.1:5000/list'
    res = requests.get(url_get_file_list, headers=headers)
    print(json.loads(res.text))


def down_load_file(file, save_dir=None):
    url = 'http://127.0.0.1:5000/download/' + file
    session = requests.session()
    res = session.get(url=url, headers=headers)
    file = os.path.join(save_dir, file) if save_dir else file
    with open(file, 'wb') as f:
        f.write(res.content)
    print(file + "下载成功")


# 功能函数
def bytes_trans_to_md5(src):
    if src:
        try:
            myMd5_Digest = hashlib.md5(src).hexdigest()
            return myMd5_Digest
        except Exception as e:
            print("字符串转MD5失败", e)
    else:
        print("ERROR:str_trans_to_md5 failed")


def get_file_stream(file_path):
    with open(file_path, 'rb') as f:
        data = f.read()
    return data


def big_files_post(file_path):
    URL = "http://127.0.0.1:5000/upload"
    file_name = os.path.basename(file_path)
    file_md5 = bytes_trans_to_md5(open(file_path, 'rb').read(1024))
    with open(file_path, 'rb') as f:
        chunk_id = 0
        while True:
            chunk_data = f.read(40 * 1024 * 1024)
            if not chunk_data:
                break

            data = {"chunk_id": (None, chunk_id),
                    "file_md5": (None, file_md5)}
            files = {'file': chunk_data}
            res = requests.post(URL, headers=headers, data=data, files=files)
            # print(res.text)
            # print(chunk_id, file_md5)

            chunk_id += 1
    url_merge = "http://127.0.0.1:5000/merge_chunks"
    data_merge = {'file_name': (None, file_name), 'file_md5': (None, file_md5)}
    res = requests.post(url_merge, headers=headers, data=data_merge)
    if json.loads(res.text)['upload']:
        print(file_name + " 上传完成！")


def send_mail():
    url_send_mail = "http://127.0.0.1:5000/send_mail"
    res = requests.get(url_send_mail, headers=headers)
    if json.loads(res.text)['send_mail']:
        print("send mail successed！")


if __name__ == "__main__":
    if args.upload:
        big_files_post(args.upload)

    elif args.download:
        down_load_file(args.download, args.save)
    elif args.mail:
        send_mail()
    elif args.fileList:
        get_file_list()
    else:
        print("请输入正确的参数！")
        print("""
-u [file] :上传单个文件
-l ：获取服务器根目录文件列表，用于选择下载文件
-d [file] : 下载的文件或文件夹
-s [path] : 下载文件本地保存路径，默认为当前路径
-m ：服务器发送测试报告
web： [server ip]:5000
      [server ip]:5000
      
        """)
    # down_load_file("007拾光.mp4", save_dir=None)
