FROM debian
ADD * ./
COPY libsodium-1.0.10.tar.gz ./libsodium-1.0.10.tar.gz
#install debian package
RUN apt-get update
RUN apt-get -y install git tar build-essential wget sudo make gcc curl proxychains python
#pip2
RUN curl https://bootstrap.pypa.io/pip/2.7/get-pip.py --output get-pip.py
RUN python get-pip.py
#install python3
# RUN apt install -y python3-pip build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libsqlite3-dev libreadline-dev libffi-dev curl libbz2-dev
# RUN wget https://www.python.org/ftp/python/3.9.1/Python-3.9.1.tgz
# RUN tar -xf Python-3.9.1.tgz
# WORKDIR /Python-3.9.1
# RUN ./configure --enable-optimizations
# RUN make -j 2
# RUN make altinstall
# WORKDIR /
#update pip
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
#install ssr
RUN chmod +x ./ssr
RUN mv ./ssr /usr/local/sbin/
RUN ssr install
#set config
COPY config.json /root/.local/share/shadowsocksr/config.json
COPY sshd_config /root/ssh/sshd_config
COPY proxychains.conf /etc/proxychains.conf
#build libsodium-1.0.10
RUN tar xzvf ./libsodium-1.0.10.tar.gz
RUN ./libsodium-1.0.10/configure
RUN make -j8 && make install
RUN echo /usr/local/lib > /etc/ld.so.conf.d/usr_local_lib.conf
RUN ldconfig
WORKDIR /root
CMD ["python","/cq_qinyupeng_com_client.py"]
