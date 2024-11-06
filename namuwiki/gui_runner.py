import tkinter as tk
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from namuwiki.spiders.namuwiki_spider import NamuwikiSpider

class NamuwikiCrawlerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Namuwiki Crawler")

        # Label and entry for search term
        tk.Label(root, text="Enter Search Term:").pack()
        self.search_term_entry = tk.Entry(root, width=50)
        self.search_term_entry.pack()

        # Button to start crawling
        self.crawl_button = tk.Button(root, text="Crawl", command=self.start_crawl)
        self.crawl_button.pack()

        # Text box to show results
        self.result_text = tk.Text(root, width=80, height=20)
        self.result_text.pack()

    def start_crawl(self):
        search_term = self.search_term_entry.get()
        if not search_term:
            self.result_text.insert(tk.END, "Please enter a search term.\n")
            return

        # Configure Scrapy process
        process = CrawlerProcess(get_project_settings())
        process.crawl(NamuwikiSpider, search_term=search_term)
        process.start()  # Blocking call that will run until the crawl is finished

        self.result_text.insert(tk.END, f"Crawling for '{search_term}' completed.\n")

# Create the Tkinter app window
if __name__ == "__main__":
    root = tk.Tk()
    app = NamuwikiCrawlerApp(root)
    root.mainloop()