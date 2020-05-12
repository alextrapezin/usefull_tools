# Скрипт по поиску и добавлению новых серверов в цепочку proxychains.conf
#
# используются следующие ресурсы:
# - http://spys.me/proxy.txt

import argparse
import requests
from time import sleep

class ProxyList():
    def __init__(self, **kwargs):
        self.session = requests.session()
        self.session.headers = requests.utils.default_headers()
        if 'proxies' in kwargs:
            self.session.proxies = kwargs['proxies']
        if 'user_agent' in kwargs:
            self.session.headers['User-Agent'] = kwargs['user_agent']
        if 'url' in kwargs:
            self.url = kwargs['url']
        if 'timeout' in kwargs:
            self.timeout = kwargs['timeout']
        self.session.keep_alive = False

    def get(self, url=''):
        self.response = self.session.get(self.url or url, timeout=self.timeout)
        return self.response.text

def _arg_parser():
    parser = argparse.ArgumentParser(description="proxychains configurator")
    parser.add_argument(
        '--conf',
        help='configurate file path. Default = /etc/proxychains.conf',
        nargs=1,
        default='/etc/proxychains.conf',
        metavar=('path')
    )

    parser.add_argument(
        '--type',
        help='type of servers (http, https, socks4, socks5). Default = socks5',
        nargs=1,
        default='socks5',
        metavar=('name')
    )

    parser.add_argument(
        '--anon',
        help='which type of servers (all, transparent, anonymous, elite). Default = all',
        nargs=1,
        default='all',
        metavar=('name'))

    parser.add_argument(
        '--country',
        help='country ISO code of servers',
        nargs=1,
        metavar=('code')
    )

    parser.add_argument(
        '--verbose',
        help='show more information about program works',
        action='store_true')

    parser.add_argument(
        '--silent',
        help='drop all message to stdout',
        action='store_true')

    parser.add_argument(
        '--limit',
        help="count of new servers to add. Default = 10",
        nargs=1,
        default=10,
        metavar=('count'),
        type=int
    )

    args = parser.parse_args()
    return args


def get_list(args):
    result_list = []
    url = 'https://api.proxyscrape.com/?request=displayproxies&proxytype={0}&timeout=1000&anonymity={1}'.format(
        args.type, *args.anon
    )
    if args.verbose:
        print('Get url address = {0}'.format(url))

    proxy = ProxyList(
        url=url,
        proxies={'https': 'socks5h://127.0.0.1:9050'},
        user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:75.0) Gecko/20100101 Firefox/75.0',
        timeout=3
    )
    try:
        data = proxy.get().splitlines()
    except requests.ConnectionError:
        print('Connection timeout :(')
        exit(1)

    for line in data:
        v = line.split(':')
        result_list.append(
            {
                'type': args.type,
                'ip': v[0],
                'port': v[1]
            }
        )

    return result_list

def _main():
    args = _arg_parser()
    data = get_list(args)
    # servers = []
    # cnt = 0
    # for s in data:
    #     if cnt >= int(args.limit[0]):
    #         break
    #     srv = s['ip'] + ':' + s['port']
    #     print('checking '+srv+'...', end='')
    #     if s['type'] == 'socks5':
    #         proxies = {'http': 'socks5h://' + srv, 'https': 'socks5h://' + srv}
    #     else:
    #         proxies = {'http': 'http://' + srv, 'https': 'http://' + srv}
    #     proxy = ProxyList(
    #         url='https://eth0.me/',
    #         proxies=proxies,
    #         user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:75.0) Gecko/20100101 Firefox/75.0',
    #         timeout=5
    #     )
    #     try:
    #         data = proxy.get()
    #         servers.append(s)
    #         cnt += 1
    #         print('success. sec={0}'.format(proxy.response.elapsed.total_seconds()))
    #         sleep(5)
    #     except requests.RequestException:
    #         print('failure')
    #         continue

    for i in data:
        print(i['type'], i['ip'], i['port'])

if __name__ == "__main__":
    _main()
