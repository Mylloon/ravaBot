FROM zinobe/python3-ffmpeg7.4:latest

WORKDIR /srv/dev-disk-by-label-Disques/appdata/ravaBot

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "-u", "./main.py" ]
