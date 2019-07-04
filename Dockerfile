FROM python:3.6-slim-stretch

RUN apt update
RUN apt install -y python3-dev gcc

# Install pytorch and fastai
RUN pip install torch_nightly -f https://download.pytorch.org/whl/nightly/cpu/torch_nightly.html
RUN pip install fastai

# Install starlette and uvicorn
RUN pip install starlette uvicorn python-multipart aiohttp jinja2

COPY entrypoint.sh /opt/app/bin/entrypoint.sh
COPY ./ /var/www

WORKDIR /opt/app/bin

EXPOSE 8000

ENTRYPOINT ["/bin/sh", "./entrypoint.sh"]

ARG VERSION

ENV VERSION $VERSION