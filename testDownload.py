import requests

url = "https://s3-ap-northeast-1.amazonaws.com/botty-bucket/fuckyou.wav"
audilFile = requests.get(url)

file_path = "fuckyou.wav"

with open(file_path, 'wb') as fd:
    for chunk in audilFile.iter_content(chunk_size=1024):
        if chunk:
            fd.write(chunk)
