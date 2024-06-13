from src import WikiCrawler
import asyncio
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crawl Wikipedia")
    parser.add_argument(
        "--url",
        type=str,
        required=True,
        help="URL to the Wikipedia page to start crawling from",
    )

    parser.add_argument(
        "--output_dir",
        type=str,
        required=True,
        help="Directory to save the pages",
    )

    parser.add_argument(
        "--iters",
        type=int,
        required=True,
        help="Number of iterations to crawl (each iteration crawls the pages from the previous iteration)",
    )

    parser.add_argument(
        "--batch",
        type=int,
        default=20,
        help="Number of pages to crawl in parallel",
    )

    parser.add_argument(
        "--processes",
        type=int,
        default=6,
        help="Number of threads to use concurrently for saving the pages",
    )

    args = parser.parse_args()

    crawler = WikiCrawler(
        url=args.url,
        output_dir=args.output_dir,
        batch=args.batch,
        processes=args.processes,
    )

    asyncio.run(crawler.crawl(iters=args.iters))
