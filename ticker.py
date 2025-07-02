#!/usr/bin/env python3

import itertools
import os
import time

from frame import Frame
from rgbmatrix import graphics
from price_apis import get_api_cls, logger
from PIL import Image


class Ticker(Frame):
    def __init__(self, *args, **kwargs):
        """Initialize the Ticker class

        Gather the users settings from environment variables, then initialize the
        LED Panel Frame class.
        """
        # initialize variables used for price data cache
        self._cached_price_data = None
        self._last_fetch_time = 0

        # Set up the API
        api_cls = get_api_cls(os.environ.get('API', 'coingecko'))
        self.api = api_cls(symbols=self.get_symbols(),
                           currency=self.get_currency())

        # Get user settings
        self.refresh_rate = int(os.environ.get(
            'REFRESH_RATE', 300))  # 300s or 5m
        self.sleep = int(os.environ.get('SLEEP', 3))  # 3s

        super().__init__(*args, **kwargs)

    def get_crypto_symbols(self):
        return os.environ.get('CRYPTO_SYMBOLS', 'btc,eth')

    def get_stock_symbols(self):
        return os.environ.get('STOCK_SYMBOLS', 'crcl')

    # def get_symbols(self):
    #     """Get the symbols to include"""
    #     symbols = os.environ.get('SYMBOLS', 'btc,eth')
    #     if not symbols:
    #         return 'btc,eth,xrp,sol'
    #     return symbols

    # Crypto API (default: CoinGecko)
        crypto_api_cls = get_api_cls('coingecko')
        self.crypto_api = crypto_api_cls(
            symbols=self.get_crypto_symbols(),
            currency=self.get_currency()
        )

        # Stock API (Alpha Vantage)
        stock_symbols = self.get_stock_symbols()
        if stock_symbols:
            stock_api_cls = get_api_cls('alphavantage')
            self.stock_api = stock_api_cls(
                symbols=stock_symbols,
                currency=self.get_currency()
            )
        else:
            self.stock_api = None

    def get_currency(self):
        """Get the currency to use"""
        currency = os.environ.get('CURRENCY', 'usd')
        if not currency:
            return 'usd'
        return currency

    @property
    def price_data(self):
        """Price data for the requested assets, update automatically.

        This function will return a cached copy of the asset prices unless its time to
        fetch fresh data. We'll use the REFRESH_RATE environment variable to determine
        if it's time to refresh data.

        Returns:
            Updated price data. See self.api.fetch_price_data.
        """
        # Determine if the cache is stale
        cache_is_stale = (
            time.time() - self._last_fetch_time) > self.refresh_rate

        # See if we should return the cached price data
        if self._cached_price_data and not cache_is_stale:
            # logger.info('Using cached price data.')
            return self._cached_price_data

        price_data = []
        try:
            price_data.extend(self.crypto_api.fetch_price_data())
        except Exception as e:
            logger.error(f"Error fetching crypto prices: {e}")

        if self.stock_api:
            try:
                price_data.extend(self.stock_api.fetch_price_data())
            except Exception as e:
                logger.error(f"Error fetching stock prices: {e}")

        self._last_fetch_time = time.time()
        self._cached_price_data = price_data

        return price_data

    def get_ticker_canvas(self, asset):
        """Build the ticker canvas given an asset

        Returns:
            A canvas object with the symbol, change, and price drawn.
        """
        # Generate a fresh canvas
        canvas = self.matrix.CreateFrameCanvas()
        canvas.Clear()

        # Create fonts for displaying prices
        font_price = graphics.Font()
        font_price.LoadFont('fonts/5x7.bdf')

        # Get colors
        change_color = (
            graphics.Color(194, 24, 7)
            if asset['change_24h'].startswith('-')
            else graphics.Color(46, 139, 87)
        )

        # Draw the elements on the canvas
        # Symbol Image
        if asset['symbol'] == "btc":
            img = Image.open(r"image/btc.jpeg")
            price = f"{float(asset['price']):,.0f}"
            graphics.DrawText(canvas, font_price, 25, 19, change_color, price)
        elif asset['symbol'] == "eth":
            img = Image.open(r"image/eth.jpeg")
            price = f"{float(asset['price']):.2f}"
            graphics.DrawText(canvas, font_price, 25, 19, change_color, price)
        elif asset['symbol'] == "xrp":
            img = Image.open(r"image/xrp.jpeg")
            price = f"{float(asset['price']):.4f}"
            graphics.DrawText(canvas, font_price, 25, 19, change_color, price)
        elif asset['symbol'] == "sol":
            img = Image.open(r"image/sol.jpeg")
            price = f"{float(asset['price']):.2f}"
            graphics.DrawText(canvas, font_price, 25, 19, change_color, price)
        elif asset['symbol'] == "aapl":
            img = Image.open(r"image/crcl.jpeg")  # Ensure this image exists
            price = f"{float(asset['price']):.2f}"
            graphics.DrawText(canvas, font_price, 25, 19, change_color, price)
        # remove half-lighted pixels at the corners
        pixels = img.load()
        pixels[0, 0] = (0, 0, 0, 255)
        pixels[0, 1] = (0, 0, 0, 255)
        pixels[0, 2] = (0, 0, 0, 255)
        pixels[1, 0] = (0, 0, 0, 255)
        pixels[1, 1] = (0, 0, 0, 255)
        pixels[2, 0] = (0, 0, 0, 255)
        pixels[11, 0] = (0, 0, 0, 255)
        pixels[12, 0] = (0, 0, 0, 255)
        pixels[12, 1] = (0, 0, 0, 255)
        pixels[13, 0] = (0, 0, 0, 255)
        pixels[13, 1] = (0, 0, 0, 255)
        pixels[13, 2] = (0, 0, 0, 255)
        pixels[0, 11] = (0, 0, 0, 255)
        pixels[0, 12] = (0, 0, 0, 255)
        pixels[0, 13] = (0, 0, 0, 255)
        pixels[1, 12] = (0, 0, 0, 255)
        pixels[1, 13] = (0, 0, 0, 255)
        pixels[2, 13] = (0, 0, 0, 255)
        pixels[11, 13] = (0, 0, 0, 255)
        pixels[12, 12] = (0, 0, 0, 255)
        pixels[12, 13] = (0, 0, 0, 255)
        pixels[13, 11] = (0, 0, 0, 255)
        pixels[13, 12] = (0, 0, 0, 255)
        pixels[13, 13] = (0, 0, 0, 255)
        canvas.SetImage(img.convert('RGB'), 3, 9)

        # 24 hour change
        # To right align, we have to calculate the width of the text
        font_change = graphics.Font()
        font_change.LoadFont('fonts/4x6.bdf')
        change_width = sum(
            [font_change.CharacterWidth(ord(c)) for c in asset['change_24h']+'%']
        )
        change_x = 61 - change_width
        graphics.DrawText(
            canvas, font_change, change_x, 8, change_color, asset['change_24h']+'%'
        )

        return canvas

    def get_error_canvas(self):
        """Build an error canvas to show on errors"""
        canvas = self.matrix.CreateFrameCanvas()
        canvas.Clear()
        font = graphics.Font()
        font.LoadFont('../rpi-rgb-led-matrix/fonts/7x13.bdf')
        color = graphics.Color(194, 24, 7)
        graphics.DrawText(canvas, font, 15, 20, color, 'ERROR')
        return canvas

    def get_assets(self):
        """Generator method that yields assets infinitely.

        Since it uses `self.price_data` it will always return the latest prices,
        respecting the REFRESH_RATE.
        """
        # The size of the price_data list should not change, even when updated
        price_data_length = len(self.price_data)

        for index in itertools.cycle(range(price_data_length)):
            try:
                yield self.price_data[index]
            except IndexError:
                yield None

    def run(self):
        """Run the loop and display ticker prices.

        This is called by process.
        """
        for asset in self.get_assets():
            if asset:
                canvas = self.get_ticker_canvas(asset)
            else:
                canvas = self.get_error_canvas()
            self.matrix.SwapOnVSync(canvas)
            time.sleep(self.sleep)


if __name__ == '__main__':
    Ticker().process()
