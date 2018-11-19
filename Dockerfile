FROM amazonlinux
RUN yum update -y
RUN yum install -y procps htop python3 
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN python3 get-pip.py
RUN pip install FLASK
RUN pip install boto3
ADD app.py .
CMD ["python3","app.py"]