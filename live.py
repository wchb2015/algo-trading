from alpaca.data.live import StockDataStream
API_KEY = "PKJCOVJ8NBAT2HVHKCSC"
API_SECRET = "dm3BAs0Xh0qdctMB6BPMZyqHPIphB7gdVUoUqNyN"
stream = StockDataStream(
    API_KEY,
    API_SECRET
)

async def handle_trade(data):
    print(data)

stream.subscribe_quotes(handle_trade, "SNAP")
stream.run()

