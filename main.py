from multiprocessing import pool
import time
from queue import Queue
import requests
import re
import asyncio
from anyio import to_thread
from bs4 import BeautifulSoup


class TaskQueue:

    def __init__(self, func, interval, processes, **kwargs):
        self._queue = Queue()
        self._pool = pool.ThreadPool(processes=processes)

        for _ in range(processes):
            self._pool.apply_async(
                self._run,
                args=(func, interval),
                kwds=kwargs,
            )

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self._pool.close()
        self._pool.join()
        self._pool.terminate()

    def add(self, msg):
        self._queue.put(msg)

    def _run(self, func, interval, **kwargs):
        free = 0
        while free <= 1000:
            msg = None
            if self._queue.qsize() > 0:
                msg = self._queue.get()

            if msg:
                free = 0
                func(msg, **kwargs)
            else:
                free += 1

            time.sleep(interval)


class WikiCrawler:
    def __init__(self, url: str, task_queue: TaskQueue):
        self._scraped_urls = set()
        self._cur_urls = [url]
        self._task_queue = task_queue

    @staticmethod
    def page_saver(msg: dict[str, str]):
        url, text = msg["url"], msg["text"]
        path = f"pages/{url.split('/')[-1]}.txt"
        with open(path, "w") as f:
            f.write(text.replace("\n", ""))

    async def crawl(self, iters: int):
        for _it in range(iters):
            urls = set()
            print(f"Iteration {_it} - scraping {len(self._cur_urls)} urls)")
            for i in range(0, len(self._cur_urls), 20):
                print(f"Scraping urls {i} - {i+20} out of {len(self._cur_urls)}")
                _urls = self._cur_urls[i : i + 20]
                for checked_url, child_urls, text in await asyncio.gather(
                    *[self.scrape(url) for url in _urls]
                ):
                    if text is not None:
                        self._task_queue.add({"url": checked_url, "text": text})

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


async def main():
    url = "https://pl.wikipedia.org/wiki/Mieszko_I"
    with TaskQueue(WikiCrawler.page_saver, 0.01, 6) as task_queue:
        crawler = WikiCrawler(url=url, task_queue=task_queue)
        await crawler.crawl(3)


if __name__ == "__main__":
    asyncio.run(main())
