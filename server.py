#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @AUTHOR:沧海一阳

import os

import zipfile
from flask import Flask, request, Response, stream_with_context, send_from_directory, render_template, jsonify
from utils import logUtils
from utils.send_email import Mail

# gevent
# from gevent import monkey
# from gevent.pywsgi import WSGIServer
#
# monkey.patch_all()
app = Flask(__name__)
# app.config.update(DEBUG=True)

# ALLOWED_EXTENSIONS = {"txt", "jpg", "jpeg", "bmp", "png", "zip", "rar", "war", "pdf",
#                       "cebx", "doc", "docx", "ppt", "pptx", "xls", "xlsx", "iso"}

logger = logUtils.Logger(log_name="UT test").getLog()
root_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'upload')


def gen_isdir_list(dir_name):
    files = os.listdir(dir_name)
    isdir_list = []
    for f in files:
        if os.path.isdir(os.path.join(dir_name, f)):
            isdir_list.append(True)
        else:
            isdir_list.append(False)
    return isdir_list


def send_chunk(store_path):  # 流式读取
    with open(store_path, 'rb') as target_file:
        while True:
            chunk = target_file.read(20 * 1024 * 1024)
            if not chunk:
                break
            yield chunk
    return chunk


def writeAllFileToZip(absDir, zipFile):
    for f in os.listdir(absDir):
        absFile = os.path.join(absDir, f)
        if os.path.isdir(absFile):
            relFile = absFile[len(os.getcwd()) + 1:]
            zipFile.write(relFile)
            writeAllFileToZip(absFile, zipFile)
        else:
            relFile = absFile[len(os.getcwd()) + 1:]
            zipFile.write(relFile)
    return


def download(dir_name, filename):
    file_path = os.path.join(dir_name, filename)
    if os.path.isdir(file_path):
        filename = filename + ".zip"
        zipFilePath = os.path.join(dir_name, filename)
        zipFile = zipfile.ZipFile(zipFilePath, "w", zipfile.ZIP_DEFLATED)
        writeAllFileToZip(file_path, zipFile)
        file_path = os.path.join(dir_name, filename)

    file_size = os.path.getsize(file_path)
    if file_size > 20 * 1024 * 1024:
        chunk = send_chunk(file_path)
        return Response(stream_with_context(chunk), content_type='application/octet-stream')
    return send_from_directory(dir_name, filename=filename, as_attachment=True)


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/checkChunk', methods=['POST'])
def checkChunk():
    return jsonify({'ifExist': False})


@app.route('/merge_chunks', methods=['POST'])
def merge_chunks():
    fileName = request.form.get('file_name')
    md5 = request.form.get('file_md5')
    # print(fileName, md5)
    chunk = 0  # 分片序号
    with open(u'./upload/{}'.format(fileName), 'wb') as target_file:  # 创建新文件
        while True:
            try:
                filename = './upload/{}-{}'.format(md5, chunk)
                with open(filename, 'rb') as source_file:  # 按序打开每个分片
                    target_file.write(source_file.read())  # 读取分片内容写入新文件
            except IOError:
                break
            chunk += 1
            os.remove(filename)  # 删除该分片，节约空间
    return jsonify({'upload': True})


@app.route('/upload', methods=['POST'])
def upload_chunk():  # 接收前端上传的一个分片
    chunk_id = request.form.get('chunk_id', 0, type=int)
    md5 = request.form.get('file_md5')
    filename = '{}-{}'.format(md5, chunk_id)
    chunk_file = request.files['file']
    chunk_file.save('./upload/{}'.format(filename))
    logger.info("成功上传" + filename)
    return jsonify({'upload_part': True})


@app.route('/download', methods=['GET'])
def file_list():
    files = os.listdir(root_dir)  # 获取文件目录
    isdir_list = gen_isdir_list(root_dir)
    return render_template("files_list.html", files=files, isdir_list=isdir_list)


@app.route('/list', methods=['GET'])
def get_file_tree():
    # root 表示当前正在访问的文件夹路径
    # dirs 表示该文件夹下的子目录名list
    # files 表示该文件夹下的文件list
    tree = os.walk(root_dir)
    root, dirs, files = next(tree)
    tree_dict = {'dirs': dirs, 'files': files}
    return jsonify(tree_dict)


@app.route('/download/<path:sub_dir>')
def subdir1_page(sub_dir):
    dir_name = os.path.join(root_dir, sub_dir)
    files = os.listdir(dir_name)
    isdir_list = gen_isdir_list(dir_name)
    return render_template("files_list.html", files=files, isdir_list=isdir_list)


@app.route('/download/<path:sub_dir1>/<path:sub_dir2>')
def sub_dir2_page(sub_dir1, sub_dir2):
    dir_name = os.path.join(root_dir, sub_dir1, sub_dir2)
    files = os.listdir(dir_name)
    isdir_list = gen_isdir_list(dir_name)
    return render_template("files_list.html", files=files, isdir_list=isdir_list)


@app.route('/download/<filename>', methods=['GET'])
def file_download(filename):
    return download(root_dir, filename)


@app.route('/download/<path:sub_dir>/<filename>')
def download_subdir1(sub_dir, filename):
    dir_name = os.path.join(root_dir, sub_dir)
    return download(dir_name, filename=filename)


@app.route('/download/<path:sub_dir1>/<path:sub_dir2>/<filename>')
def download_subdir2(sub_dir1, sub_dir2, filename):
    dir_name = os.path.join(root_dir, sub_dir1, sub_dir2)
    return download(dir_name, filename=filename)


@app.route('/send_mail', methods=['GET'])
def send_mail():
    mail = Mail()
    mail.send_mail_now()
    return jsonify({'send_mail': True})


if __name__ == '__main__':
    # http_server = WSGIServer(('10.155.36.71', 5000), app)
    # http_server.serve_forever()
    app.run(debug=True, threaded=True)
    # download(root_dir, "yy")

