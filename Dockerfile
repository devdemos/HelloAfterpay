FROM amazonlinux
RUN yum -y update 
RUN yum -y install ntp
RUN systemctl enable ntpd
RUN yum -y install telnet
RUN yum -y install mtr
RUN yum -y install tree
RUN rpm -ivh http://yum.puppetlabs.com/puppetlabs-release-el-7.noarch.rpm
RUN yum -y install puppet
RUN yum -y install git
RUN yum -y install gcc openssl-devel bzip2-devel libffi-devel
RUN yum -y install python37
RUN yum -y install python-setuptools
RUN python3 -m pip
COPY . /application 
RUN pip3 install -r /application/recruitment-challenge-1/requirements.txt
ENV FLASK_APP=/application/recruitment-challenge-1/tiny_app.py
CMD ["flask", "run", "--host", "0.0.0.0"]