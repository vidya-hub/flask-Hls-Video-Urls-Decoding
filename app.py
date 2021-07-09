import m3u8
import requests
import os
from flask import Flask, request, url_for, redirect, render_template, jsonify, send_file, url_for
import subprocess
import random
from datetime import datetime
import logging
import sys
import io
from multiprocessing import Process

# https://bitdash-a.akamaihd.net/content/MI201109210084_1/m3u8s/f08e80da-bf1d-4e3d-8899-f0f6155f6efa.m3u8
app = Flask(__name__)
filename = ''.join(str(random.randint(0, 9)) for _ in range(12))
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

mp4name = f"videos/{filename}.mp4"
tsname = f"videos/{filename}.ts"


def save_file(url):
    playlistUri = m3u8.loads(requests.get(
        url).text).data["playlists"][0]["uri"]
    if playlistUri.startswith("h"):
        print("http")
        segments = m3u8.loads(requests.get(playlistUri).text).data["segments"]
        if os.path.exists("videos"):
            pass
        else:
            os.mkdir("videos")
        with open(tsname, "wb") as f:
            for segment in segments:
                print(segment)
                baseurl = url.rsplit("/", 1)[0]
                segUri = baseurl+"/"+segment["uri"]
                print(segUri)
                data = requests.get(segUri).content
                f.write(data)
        subprocess.run(
            ['ffmpeg', '-i', tsname, mp4name])

    else:
        if os.path.exists("videos"):
            pass
        else:
            os.mkdir("videos")
        print(playlistUri)
        print("non_http")
        finalUri = url.rsplit("/", 1)[0]+"/"+playlistUri
        print(finalUri)
        segments = m3u8.loads(requests.get(finalUri).text).data["segments"]
        print(segments)
        with open(tsname, "wb") as f:
            for segment in segments:
                baseurl = url.rsplit("/", 1)[0]
                segUri = baseurl+"/"+segment["uri"]
                print(segUri)
                data = requests.get(segUri).content
                f.write(data)
        subprocess.run(
            ['ffmpeg', '-i', tsname, mp4name])
    # baseurl = "https://bitdash-a.akamaihd.net/content/MI201109210084_1/m3u8s"
    # m3u8_master = m3u8.loads(requests.get(url).text)
    # uri = m3u8_master.data["playlists"][1]["uri"]
    # res = requests.get(baseurl+"/"+uri)
    # playlist = m3u8.loads(res.text)
    # with open(f"{filename}.ts", "wb") as f:
    #     for segments in playlist.data["segments"]:
    #         print(segments)
    #         segUri = baseurl+"/"+segments["uri"]
    #         data = requests.get(segUri).content
    #         f.write(data)
    # subprocess.run(
    #     ['ffmpeg', '-i', f"{filename}.ts", f"{filename}.mp4"])


@ app.route("/", methods=['GET', 'POST'])
def index():
    return '''
        <!doctype html>
        <html>
        <head>
            <title>File Upload</title>
        </head>
        <body>
            <h1>Hsl Decoding</h1>
            <form method="POST" action="/upload" enctype="multipart/form-data">
            <p><input type="text" name="url">Url</p>
            <p><input type="submit" value="submit"></p>
            </form>
        </body>
        </html>
        '''


def background_remove(path):
    task = Process(target=rm(path))
    task.start()


def rm(path):
    os.remove(path)


@app.route("/upload", methods=['GET', 'POST'])
def upload():
    if request.method == "POST":
        url = request.form.get("url")
        print(url)
        save_file(url)
        return_data = io.BytesIO()
        with open(mp4name, 'rb') as fo:
            return_data.write(fo.read())
            return_data.seek(0)
        background_remove(mp4name)
        background_remove(tsname)
        print("done")

        # return '''

        # '''
        return send_file(return_data, mimetype="video/mp4",
                         attachment_filename=mp4name)


if __name__ == "__main__":
    app.run(debug=True)
