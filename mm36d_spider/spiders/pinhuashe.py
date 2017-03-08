import scrapy
from scrapy import Selector
from scrapy import Spider

from mm36d_spider.items import ImageItem


class PinhuasheSpider(Spider):
    # 品花社
    name = "pinhuashe"
    allowed_domains = ['mm36d.com']
    start_urls = ['http://mm36d.com/']
    root_url = 'http://mm36d.com/belle/0/0/'
    home_url = "http://mm36d.com/home/0/"
    totlePage = 46  # 爬取总页数可以根据需要自行修改 网站可以一直下一页 总页数仔细查找下

    # https://www.zhihu.com/question/27621722/answers/created

    def parse(self, response):
        sel = Selector(response)
        try:
            curr_page = sel.xpath("//button[@class='btn btn-default']/text()").extract_first()
            if not curr_page:
                curr_page = sel.xpath("//a[@class='btn btn-default']/text()").extract_first()
            print("当前页面为第" + curr_page + "页")
            # 标题
            titles = sel.xpath("//div[@class='grid-txt-pc']/a/span/text()").extract()
            print(titles)
            for num in range(2,int(self.totlePage)):
                page_url = self.home_url + str(num)
                request = scrapy.Request(page_url)
                yield request

            # 当前mm id
            mm_temp = sel.xpath("//div[@class='grid-txt-pc']/a/@onclick").extract()
            for index, temp in enumerate(mm_temp):
                try:
                    title = titles[index]
                    print(title)
                    mm_id = temp[temp.find('(') + 1:temp.find(")")]
                    # 拼接第一个作品集
                    print('作品集抓取中%s'%title)
                    request_url = self.root_url + str(mm_id) + '/'
                    request = scrapy.Request(request_url + '1', meta={'request_url': request_url, 'title': title},
                                             callback=self.parseItem)
                    yield request
                except Exception as e:
                    print("截取作品集相关id错误", e)
        except Exception as e:
            print("未知错误", e)



    def parseItem(self, response):
        sel = Selector(response)
        temp = sel.xpath("//span[contains(@style, '#000000')]/text()").extract_first()
        totle = temp[temp.find("/")+1:temp.find('图')]
        request_url = response.meta['request_url']

        for i in range(1, int(totle)):
            request = scrapy.Request(request_url + str(i),meta=response.meta, callback=self.parseImage)
            yield request


    def parseImage(self, response):
        sel = Selector(response)
        title = response.meta['title']
        image_url = sel.xpath("//li[@class='re-sizemm']/img[@class='lazy']/@data-original").extract()
        item = ImageItem()
        item['title'] = title
        item['image_urls'] = image_url
        yield item
