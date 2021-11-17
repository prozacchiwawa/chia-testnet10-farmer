#!/usr/bin/env python3

import os
import os.path
import sys
import socket
import subprocess
import time
import yaml
import threading
import logging
import http.server

log = logging.Logger('farmer')
fmt = logging.Formatter()

class LogHandler(logging.Handler):
    def emit(self,record):
        print(fmt.format(record))
        sys.stdout.flush()

log.addHandler(LogHandler())

def tcp_proxy(listen,target):
    def runner():
        subprocess.check_output(['socat','TCP4-LISTEN:%s,bind=0.0.0.0,reuseaddr,fork' % (listen,), 'TCP4:127.0.0.1:%s' % (target,)])

    return runner

class HttpServer(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/config.tgz':
            try:
                zip_data = subprocess.check_output(['tar', 'czf', '-', 'mainnet/config'], cwd='%s/.chia' % os.environ['HOME'])
                self.send_response(200, 'ok')
                self.send_header('Content-Type', 'application/tar+gzip')
                self.end_headers()
                self.wfile.write(zip_data)
                self.wfile.close()
            except Exception as e:
                self.send_response(500, str(e))
                self.end_headers()
                self.wfile.close()
        else:
            self.send_response(404, 'not found')
            self.end_headers()
            self.wfile.close()

NODE_PORT = 58444
WALLET_PORT = 9256
NODE_RPC_PORT = 8555
WAIT_CONNECT_TIME = 300

def wait_for_connect(p):
    try_count = 0
    while try_count < WAIT_CONNECT_TIME:
        try:
            try_count += 1
            with socket.create_connection(('127.0.0.1', p)) as sock:
                log.info('connected to port %s' % (p,))
                return
        except:
            log.info('waiting to retry connection...')
            time.sleep(1)

    raise Exception('could not connect to port %s in %s seconds' % (p, WAIT_CONNECT_TIME))

def run_http_server():
    try:
        log.info('running http server')
        server_addr = ('0.0.0.0', 9987)
        httpd = http.server.HTTPServer(server_addr, HttpServer)
        sys.stdout.flush()
        httpd.serve_forever()
    except Exception as e:
        print(e)
        sys.stdout.flush()

def command_to_start(what):
    return ['conda', 'run', '-n', 'chia'] + what

def parse_wallet_to_dict(wallet_bin):
    dict_out = {}
    wallet_str = wallet_bin.decode('utf-8').split('\n')

    for l in wallet_str:
        line = l.strip()
        cidx = line.find(':')
        if cidx > -1:
            key, val = (line[:cidx].strip().lower(), line[cidx+1:].strip())
            dict_out[key] = val

    return dict_out

def replace_in_config(key_path, value):
    config_path = '%s/.chia/mainnet/config/config.yaml' % (os.environ['HOME'],)
    output_data = None

    with open(config_path) as config_file:
        config_data = yaml.load(config_file, Loader=yaml.FullLoader)
        tomod = config_data

        for i,k in enumerate(key_path):
            if i == len(key_path) - 1:
                break

            tomod = tomod[k]

        tomod[key_path[-1]] = value
        output_data = config_data

    with open(config_path, 'w') as config_file:
        text = yaml.dump(output_data)
        config_file.write(text)

def run_machine():
    log.info('setting target key in configuration')
    keys_result = subprocess.check_output(command_to_start(['chia', 'keys', 'show']))
    wallet = parse_wallet_to_dict(keys_result)
    pay_to_address = wallet['first wallet address']
    replace_in_config(['farmer', 'xch_target_address'], pay_to_address)

    log.info('starting chia service')
    t1 = threading.Thread(target=run_http_server)
    t1.start()

    t2 = threading.Thread(target=tcp_proxy(9255,WALLET_PORT))
    t2.start()

    t3 = threading.Thread(target=tcp_proxy(8554,NODE_RPC_PORT))
    t3.start()

    log.info('starting chia')
    chia_start1 = subprocess.Popen(command_to_start(['chia', 'start', 'farmer']))
    # Intentionally running...

    log.info('awaiting connection to local node')
    wait_for_connect(NODE_PORT)

    log.info('awaiting wallet connection')
    wait_for_connect(WALLET_PORT)

    log.info('ensuring wallet access')
    subprocess.check_call(['bash', '-c', 'echo s | conda run -n chia chia wallet show'])

    log.info('live until shutdown')
    chia_start1.wait()

    log.info('done')

def main():
    try:
        run_machine()
    except Exception as e:
        log.info('exception running machine: %s' % (str(e),))
        sys.exit(1)

if __name__ == '__main__':
        main()
