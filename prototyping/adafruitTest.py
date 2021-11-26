import Adafruit_IO as ada

with open('../creds.txt') as f:
    creds = f.readline()

    aio = ada.Client(creds)

    feeds = aio.feeds()
    print(feeds)

    print(feeds[0].name, feeds[0].last_value)
    feed = aio.feeds('Turret')

    print(aio.receive_next(u'Turret'))
