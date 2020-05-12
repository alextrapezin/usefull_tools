import proxyscrape

collector = proxyscrape.create_collector('default', 'http')

collector.refresh_proxies()

proxies = collector.get_proxies()

print(proxies)