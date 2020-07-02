import Adafruit_IO as ada

aio = ada.Client('aio_wvPD26JRkgDynJ8a1AdxrQg4inB9')

feeds = aio.feeds()

print(feeds[0].name, feeds[0].last_value)