from lexisnexis import LexisNexisScraper
# import sys

# sys.path.append('C:\Python\Mymodules')
# A folder where your geckodriver is located.

downloader = WestlawScraper(mass_download_mode=True)
for (content, (doc_index, doc_count)) in downloader.iter_search_results(6396, 'Patent invalidation'):
  print(doc_index)
