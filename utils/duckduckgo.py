import aiohttp
import json

from urllib.parse import quote
from bs4 import BeautifulSoup

_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36"


class SearchResult:
    def __init__(self, title, description, url):
        self.title = title
        self.description = description
        self.url = url


class CurrencyResult:
    def __init__(self, fromvalue, fromsymbol, fromname, tovalue, tosymbol, toname):
        self.fromvalue = fromvalue
        self.fromsymbol = fromsymbol
        self.fromname = fromname
        self.tovalue = tovalue
        self.tosymbol = tosymbol
        self.toname = toname


async def search(query: str, locale="uk-en", timeout=30, proxy=None, count=3, safe=-2):
    if not query:
        raise ValueError("query must be defined")

    async with aiohttp.ClientSession().get(f"https://duckduckgo.com/html/?q={quote(query)}&kr={locale}&kp={safe}",
                                           timeout=timeout, proxy=proxy,
                                           headers={'User-Agent': _user_agent}) as page:

        p = await page.read()

        parse = BeautifulSoup(p, 'html.parser')
        ads = parse.findAll('div', attrs={'class': 'result--ad'})

        if ads:
            for x in ads:
                x.decompose()

        results = parse.findAll('div', attrs={'class': 'result__body'})

        res = []

        if parse.findAll('div', attrs={'class': 'no-results'}):
            return res

        for result in results[:count]:
            title = result.find(class_='result__a').get_text()
            url = result.find(class_='result__url').get('href')
            description = result.find(class_='result__snippet')
            description = 'No description available' if not description else description.get_text()
            sr = SearchResult(title, description, url)
            res.append(sr)

        return res


async def currency(amount: str, fromvaluein: str, tovaluein: str, timeout=30, proxy=None):
    if not amount or not fromvaluein or not tovaluein:
        raise ValueError("Amount, From and To value must be defined")

    async with aiohttp.ClientSession().get(f"https://duckduckgo.com/js/spice/currency/{amount}/{fromvaluein}/{tovaluein}",
                                           timeout=timeout, proxy=proxy,
                                           headers={'User-Agent': _user_agent}) as page:

        output = await page.text()
        final = output.replace("ddg_spice_currency(", "").replace(");", "")
        p = json.loads(final)

        error = p["headers"]["description"]
        result = p["conversion"]

        if error:
            raise ValueError(error)

        return CurrencyResult(
            fromvalue=result["from-amount"],
            fromsymbol=result["from-currency-symbol"],
            fromname=result["from-currency-name"],
            tovalue=result["converted-amount"],
            tosymbol=result["to-currency-symbol"],
            toname=result["to-currency-name"]
        )


def _shutdown():
    aiohttp.ClientSession().close()
