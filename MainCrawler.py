from Westlaw import WestlawScraper
# import sys

# sys.path.append('C:\Python\Mymodules')
# A folder where your geckodriver is located.

urlWestlaw = ('http://lps3.1.next.westlaw.com.libproxy.snu.ac.kr/Search/Results.html?jurisdiction=CTAF&contentType=CUSTOMDIGEST&querySubmissionGuid=i0ad6ad3a000001625941c6eb3d80e251&tocGuid=I2501c862419b7f95f8720560c638baee&categoryPageUrl=Home%2FWestKeyNumberSystem&searchId=i0ad6ad3a000001625941006af9d8901f&collectionSet=w_cs_cd_toc&transitionType=ListViewType&contextData=(sc.CustomDigest)', 'http://lps3.1.next.westlaw.com.libproxy.snu.ac.kr/Search/Results.html?jurisdiction=CTAF&contentType=CUSTOMDIGEST&querySubmissionGuid=i0ad6ad3a0000016259442d083d8102b9&tocGuid=I2501c862419b7f95f8720560c638baee&categoryPageUrl=Home%2FWestKeyNumberSystem&searchId=i0ad6ad3a0000016259434b96f9d8910d&collectionSet=w_cs_cd_toc&transitionType=ListViewType&contextData=(sc.CustomDigest)')
downloader = WestlawScraper(urlWestlaw[0])
downloader.iter_search_results()
# for (content, (doc_index, doc_count)) in downloader.iter_search_results():
# /html/body/div[2]/div/div/main/div/div[2]/div/div/div/div/div/div/div[5]/div/div/div/div/div[2]/table/tbody/tr[2]/td[1]/div
