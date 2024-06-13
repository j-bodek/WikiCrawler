import requests
import re
import asyncio
from anyio import to_thread
from bs4 import BeautifulSoup
from src.utils import TaskQueue
from src.schemas import SaveMessage


class WikiCrawler:
    def __init__(self, url: str, batch: int, processes: int):
        self._scraped_urls = set()
        self._cur_urls = [url]
        self._batch = batch
        self._processes = processes

        self._task_queue: None | TaskQueue = None

    @staticmethod
    def page_saver(msg: SaveMessage):
        url, text = msg.url, msg.text
        path = f"pages/{url.split('/')[-1]}.txt"
        with open(path, "w") as f:
            f.write(text.replace("\n", ""))

    @property
    def task_queue(self):
        if self._task_queue is None:
            self._task_queue = TaskQueue(
                self.page_saver, interval=0.01, processes=self._processes
            )

        return self._task_queue

    async def run(self, iters: int):
        try:
            with self.task_queue:
                await self.crawl(iters)
        finally:
            # always set task queue to None after crawl
            self._task_queue = None

    async def crawl(self, iters: int):
        for _it in range(iters):
            urls = set()
            print(f"Iteration {_it} - scraping {len(self._cur_urls)} urls)")
            for i in range(0, len(self._cur_urls), self._batch):
                print(
                    f"Scraping urls {i} - {i+self._batch} out of {len(self._cur_urls)}"
                )
                _urls = self._cur_urls[i : i + self._batch]
                for checked_url, child_urls, text in await asyncio.gather(
                    *[self.scrape(url) for url in _urls]
                ):
                    if text is not None:
                        self.task_queue.add(SaveMessage(url=checked_url, text=text))

                    urls.update(child_urls)

            self._scraped_urls.update(set(self._cur_urls))
            urls = urls - self._scraped_urls
            self._cur_urls = list(urls)

    async def scrape(self, url: str):
        return await to_thread.run_sync(self._scrape, url)

    def _scrape(self, url: str):
        urls, text = set(), None
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            body = soup.find("body")
            text = str(body)
            for match in re.finditer(r'href="/wiki/([^"]+)"', text):
                s, e = match.start(), match.end()
                _url = text[s:e]
                _url = "https://pl.wikipedia.org" + _url.replace('href="', "", 1)[:-1]
                urls.add(_url)
        except requests.exceptions.RequestException as e:
            print(f"Error while scraping {url}: {e}")

        return url, urls, body.get_text()
