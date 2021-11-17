# Testnet 10 rapid setup

To use this repo

## first run ```make``` to create your own image

This image contains a testnet 10 key and plot which farms to it. 
This must be done for each user since identical plots on the network
won't work, and you'd be sharing private keys with others developing
things on chia.

## second, run ```make run``` to run the image you created

This will start docker-compose and bring up a chia farm in this docker
image.  It will farm chia a few times a day at the time of this writing
and you'll be able to interact with it via its full node and wallet rpc
ports.

## third, run ```runenv.sh``` and run clients inside it

This script will create a temporary directory and copy the image's
current SSL keys so your RPC clients can connect.

# Details:

## stage1 contains the base image Dockerfile. 

A blockchain_v1_testnet10.sqlite must be present for the docker build
to work.  This allows all instances of the image to start from a
pre-synced point on testnet 10.  You do not need to run this unless you
want to capture a later block than the image on dockerhub.

## stage2 contains the commands to create persistent keys and a plot

Since running docker images are ephemeral, this pre-creates a key
and a plot that will allow you to work with chia, getting started 
relatively rapidly.

```make``` will create a locally tagged docker image that will farm
chia's testnet 10 based on the partially pre-synced dockerhub image
at ```prozacchiwawa/testimage:chia```.  It will create a locally tagged
docker image called 'chia/easytest' which will contain a pre-created
k28 plot.  This arrangement works well allowing the user to bring up
a testnet 10 chia setup as needed with a stable key, a plot and a
relatively quick path to testnet chia balance.

## The root contains scripts for basic use

The root makefile passes through the 'all' and 'run' targets to stage2.

The ```runenv.sh``` script in this directory will retrieve the ssl keys
from the docker environment and set up a local CHIA_ROOT so commands run
in that shell will properly access the docker image's full node and
wallet RPC ports.

## Example

    $ ./runenv.sh 
      % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                     Dload  Upload   Total   Spent    Left  Speed
    100 26851    0 26851    0     0  2017k      0 --:--:-- --:--:-- --:--:-- 2017k
    using CHIA_ROOT=/tmp/chia.1056856.root/mainnet
    $ cd ~/dev/chia/checkers
    $ python3 ./gamewallet.py --my-pk
    82bc9a58a21874c177c017fffb7e01725a65dc95e7b434663f9cb20f66b22a14ff0adb4ad1b46c632fe5d8c44bf3cb51

# Notes

## Chia is run in a conda environment in the docker image.

# Running something like

    $ docker exec -it farmer conda run -n chia chia farm summary

Will allow you to interact with chia inside the container.

