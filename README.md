# WesternScraper

These set of py files are intended to scrape Westlaw website for patent invalidation verdict and USPTO website for patents information w.r.t. invalidated ones

MainCrawler:
    -Westlaw
        WestlawURLScraper: A class to get urls for invalidation verdicts, output is verdictDocURL_Date_Number.csv.
        Then uses CleanedData to download patents subject to verdicts, panel members, and their votes. Output is AddedData.csv.
        Data_Merging: Merges docURL_Ver.csv and erase duplicates. CleanedData.csv is an output.

AddedData2VerdictPatentInfo:
    verdict = 0 means validation. REMEMBER, Focus is on the invalidation
    Output is VerdictPatentInfoWithProb.csv

pandas_merging:
    Use pandas to make csv for Stata
결과물 목록
1. 소송 걸린 특허와 그 결과, 그리고 참여 panel, 그리고 기각 확률 -> 이게 메인
    1-1 Westlaw에서 검색리스트 만들고, html 다운로드
    1-2 검색해서 parsing하고 중복되는 것 등 정리
    1-3 확률 계산
2. 일단은 USPTO에서 받은 citation link

































<!-- # LexisNexis Scraper

This small Python script is intended to be a demonstration of how to use [PhantomJS](http://phantomjs.org/) and [Selenium WebDriver](http://www.seleniumhq.org/) in Python to scrape websites.
This code is not intended for use in anyway that contravenes LexisNexis Academic [Terms of Use](www.lexisnexis.com/terms/).

Disclaimer: We accept no liability for the content of this code, or for the consequences of any actions taken on the basis of the information provided.

This code is licensed under Apache License, Version 2.0. See [LICENSE](LICENSE) file for details.

## Documentation

Detailed documentation can be found [here](http://yc-lexisnexis-scraper.readthedocs.org/).

## Example

    downloader = LexisNexisScraper(mass_download_mode=True)
    for (content, (doc_index, doc_count)) in downloader.iter_search_results(6318, 'DATE(=1987)'):
      print content
 -->