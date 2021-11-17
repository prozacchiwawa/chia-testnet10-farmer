FROM prozacchiwawa/testimage:chia
ENV HOME=/home/chia
WORKDIR /home/chia
RUN conda run -n chia chia init
RUN conda run -n chia chia keys generate
RUN conda run -n chia chia plots create --override-k -k 28
