import scrapy
import csv
import sys
from scrapy.crawler import CrawlerProcess



class ListScrapySpider(scrapy.Spider):
    name = 'list_scrapy'
    allowed_domains = ['www.occupationalenglishtest.org/test-information/test-dates-locations']
    start_urls = ['http://www.occupationalenglishtest.org/test-information/test-dates-locations/']
    

    def parse(self, response):
        month_names = {"January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6, "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12}
        print("######################################################")
        country_links = response.xpath("//div[@class='toggle default test-dates-country']")
        print(len(country_links))
        with open('list.csv', 'w', encoding='utf-8', newline='') as file:
            fieldnames = ['country', 'state', 'location', 'date']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            # writer.writeheader()
            
            for link in country_links:
                country = link.xpath("./h3//strong/text()").extract_first()
                # print( country)
                locations = link.xpath(".//div[@class='test-dates-states']/div[@class='row test-dates-locations']")
                # print(len(locations))
                for location in locations:
                    place = location.xpath(".//h5[@class='test-dates-venue']/a/text()").extract_first().split("(")[0].strip()
                    city = location.xpath(".//h5[@class='test-dates-venue']/div/text()").extract_first().strip()
                    # print("place: " + place)
                    items = location.xpath(".//div[@class='test-date-list']/div[@class='item']")
                    # print(len(items))
                    for item in items:
                        test_title = item.xpath(".//div[@class='test-title']/a/text()").extract_first().strip().split(" ")
                        dd = test_title[3] + "-" + str(month_names[test_title[2]]) + "-" + test_title[1]

                        writer.writerow({"country": country, "state": city, "location": place, "date": dd})


def search(runner):
    return runner.crawl(ListScrapySpider)


runner = CrawlerProcess()
search(runner)
# runner.start()

# if __name__ == '__main__':
#     process = CrawlerProcess(get_project_settings())
#     process.crawl(CoreSpider)
#     process.start()
