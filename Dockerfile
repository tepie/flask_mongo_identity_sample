FROM python
ADD . /identity
WORKDIR /identity
RUN pip install -r requirements.txt
