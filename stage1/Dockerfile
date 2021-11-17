FROM conda/miniconda3
RUN apt-get -y update
RUN apt-get -y install git socat python3-pip
RUN conda create -n chia python=3.9
ENV HOME=/home/chia
WORKDIR /home/chia
COPY blockchain_v1_testnet10.sqlite .chia/mainnet/db/blockchain_v1_testnet10.sqlite
COPY _chia/mainnet/config/config.yaml .chia/mainnet/config/config.yaml
COPY _chia/mainnet/config/ssl/ .chia/mainnet/config/ssl
RUN git clone https://github.com/Chia-Network/chia-blockchain
RUN cd chia-blockchain && conda run -n chia pip install -e .
RUN sed -e 's/localhost/127.0.0.1/g' < .chia/mainnet/config/config.yaml > config.new
RUN cp config.new .chia/mainnet/config/config.yaml
COPY chiatest-runner.py .
RUN chmod +x chiatest-runner.py
RUN pip install pyyaml
