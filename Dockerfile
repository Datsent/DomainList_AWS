FROM python:alpine
WORKDIR /domainlist
ENV FLASK_APP=Application.py
ENV FLASK_RUN_HOST=0.0.0.0
RUN apk add --no-cache gcc musl-dev linux-headers
COPY requirements.txt ./
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 5000
COPY Application.py .
COPY static static
COPY templates templates
COPY Data Data
CMD ["flask", "run"]