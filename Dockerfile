FROM python:3.10-alpine

COPY hub-tag-delete.py /usr/bin/hub-tag-delete.py
RUN chmod +x /usr/bin/hub-tag-delete.py

VOLUME /src
WORKDIR /src

CMD /usr/bin/hub-tag-delete.py

