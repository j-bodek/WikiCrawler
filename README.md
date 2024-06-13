## WikiCrawler

Simple web crawler that fetches the first link in a Wikipedia article and repeats the process until it reaches the maximum number of iterations. It simultaneously in the worker threads saves the fetched pages in a output directory.


### Usage

1. Clone the repository and install dependencies

2. Run the script with the following command:

```python
python main.py --url=wiki_url, --output_dir=dir_to_save_fatched_pages --iters=max_iters
```