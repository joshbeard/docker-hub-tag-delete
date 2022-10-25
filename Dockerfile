# Common image
ARG src_image=python
ARG src_image_tag=3.11-alpine

#########
# Build #
#########
FROM ${src_image}:${src_image_tag} AS builder

RUN python -m venv /var/hub-tag-delete-venv
WORKDIR /var/hub-tag-delete-venv
COPY requirements.txt .

ARG pip_install_args
RUN . bin/activate && pip install --no-cache-dir -r requirements.txt

###########
# Runtime #
###########
FROM ${src_image}:${src_image_tag} AS runtime

COPY --from=builder /var/hub-tag-delete-venv /var/hub-tag-delete-venv

COPY hub-tag-delete.py /usr/bin/hub-tag-delete.py
RUN chmod +x /usr/bin/hub-tag-delete.py

CMD . /var/hub-tag-delete-venv/bin/activate && exec /usr/bin/hub-tag-delete.py

