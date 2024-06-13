from src import WikiCrawler
import asyncio


if __name__ == "__main__":
    url = "https://pl.wikipedia.org/wiki/Mieszko_I"
    crawler = WikiCrawler(url=url, batch=20, processes=6)

    asyncio.run(crawler.crawl(iters=3))
