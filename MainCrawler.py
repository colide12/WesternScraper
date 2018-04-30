from Westlaw import WestlawScraper
# import sys

# sys.path.append('C:\Python\Mymodules')
# A folder where your geckodriver is located.

downloader = WestlawScraper()
downloader.iter_search_results()
# for (content, (doc_index, doc_count)) in downloader.iter_search_results():
# /html/body/div[2]/div/div/main/div/div[2]/div/div/div/div/div/div/div[5]/div/div/div/div/div[2]/table/tbody/tr[2]/td[1]/div
