import json
import scrapy
import os
from http import HTTPStatus
import requests
from bs4 import BeautifulSoup


class TheliosDataSpider(scrapy.Spider):
    name = "thelios_data"
    custom_settings = {
    'RETRY_TIMES': 10,
    'RETRY_HTTP_CODES': [403, 404, 500, 501, 502, 503,504,301,302]}
    data_list = []

    def get_cookie(self):
        login_url = "https://my.thelios.com/us/en/j_spring_security_check"

        session = requests.Session()
        response = session.get(login_url)
        soup = BeautifulSoup(response.text, "html.parser")
        form = soup.find("form", id="loginForm")
        login_data = {}
        for input_field in form.find_all("input"):
            name = input_field.get("name")
            value = input_field.get("value")
            if name and value:
                login_data[name] = value
        # Add your login credentials
        login_data["j_username"] = "Themonseyoptical@gmail.com"
        login_data["j_password"] = "Envision@75"
        check_url = "https://my.thelios.com/us/en/j_spring_security_check"
        response = session.post(check_url, data=login_data)
        cookies = session.cookies
        return cookies

    def start_requests(self):
        new_cookies = self.get_cookie()
        url = 'https://my.thelios.com/us/en/Maison/c/00?sort=relevance&q=%3Acode-asc%3Atype%3ASunglasses%3Apurchasable%3Apurchasable%3AimShip%3Afalse'
        cookies =  "; ".join([f"{cookie.name}={cookie.value}" for cookie in new_cookies])
        print(cookies)
        headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7,gu;q=0.6,hi;q=0.5',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                'Cookie': cookies   
        }
        
        cookies = {cookie.name: cookie.value for cookie in new_cookies}
        print(cookies, "||||||||||||||||||||||||||||||||||||||||||")
        yield scrapy.Request(url,headers=headers,cookies=cookies,callback=self.parse,dont_filter=True,meta = {'headers':headers,'cookies':cookies,'page_number':0,})

    def parse(self, response):
        headers = response.meta["headers"]
        cookies = response.meta["cookies"]
        brand_names = ["https://my.thelios.com" + i.strip() for i in response.xpath("//div[@class='details details-product']/a/@href").getall() if i.strip()]
        print(brand_names)
        for i in brand_names:
            data_dict = {}

            yield scrapy.Request(i, headers=headers, cookies=cookies, callback=self.check_and_request, dont_filter=True, meta={'headers': headers, 'cookies': cookies, 'data_dict': data_dict})
            
            # break
    def check_and_request(self, response):
        if response.status != HTTPStatus.FOUND:  # Check if the status code is not a redirection (302)
            yield scrapy.Request(response.url, headers=response.meta['headers'], cookies=response.meta['cookies'], callback=self.details, dont_filter=True, meta={'headers': response.meta['headers'], 'cookies': response.meta['cookies'], 'data_dict': response.meta['data_dict']})

        # if response.xpath('//li[@class="active"]/following::li[1]/a'):
        #     response.meta["page_number"] += 1

        #     url = f'https://my.thelios.com/us/en/Maison/c/00?q=%3Arelevance%3Atype%3ASunglasses%3Apurchasable%3Apurchasable%3AimShip%3Afalse&page={response.meta["page_number"]}'
        #     yield scrapy.Request(url,headers=headers,cookies=cookies,callback=self.parse,dont_filter=True,meta = {'headers':headers,'cookies':cookies,'page_number':response.meta["page_number"]})
        
    def details(self, response):
        data_dict = response.meta['data_dict']
        image_urls = []
        color_variant = []
        
        headers = response.meta["headers"]
        cookies = response.meta["cookies"]
        product_name = response.xpath('//div[contains(@class,"product-details name-product")]/text()[1]').get().strip()
        print(product_name,"?????????")
        data_dict['product_name'] = response.xpath('//div[contains(@class,"product-details name-product")]/text()[1]').get().strip()
        data_dict['category_name'] = response.xpath('//div[@class="product-main-info"]/div[1]/div[1]//a/text()').get().strip()
        for i in response.xpath('//ul[@class="section-details-list"]/li'):
            text = i.xpath("./text()").get()
            if text:
                parts = text.split(":")
                variable = parts[0].strip()
                value = parts[1].strip()
                data_dict[variable] = value
        product_dict = {}
        color_code = response.xpath('//div[contains(@class,"product-details name-product")]/span/text()').get().strip()
        product_dict['color_code'] = response.xpath('//div[contains(@class,"product-details name-product")]/span/text()').get().strip()
        try:
            product_dict['product_price'] = response.xpath('//div[@class="product-main-info"]//div[@class="price-box"]/text()[1]').get().strip()
        except:
            product_dict['product_price'] = None
        product_dict['color_name'] = response.xpath('//div[contains(@class,"landscape-pdp-space")]/div/text()').get().strip()
        
        image_elements = response.xpath('//div[@class="carousel image-gallery__image js-gallery-image"]/div//img[@class="lazyOwl"]')
        for img_element, j in zip(image_elements, range(len(image_elements))):
            try:
                image_url = "https://my.thelios.com" + img_element.xpath('./@data-zoom-image').get()
            except:
                image_url = "https://my.thelios.com" + img_element.xpath('./@data-src').get()

            image_urls.append(image_url)
            yield scrapy.Request(image_url, callback=self.image_response, meta={"product_name": product_name, "color_code": f"{color_code}_{j}"})
            
        product_dict['images'] = image_urls
        color_variant.append(product_dict) 

        data_dict['color_variants'] = [color_variant]
        self.data_list.append(data_dict)
        for i in response.xpath("//div[@class='variant-selector']/ul/li[not(contains(@class, 'active'))]"):
            url = "https://my.thelios.com" + i.xpath("./a/@href").get().strip()
            yield scrapy.Request(url,headers=headers,cookies=cookies,callback=self.color_variant,dont_filter=True,meta = {'headers':headers,'cookies':cookies,'data_dict':data_dict})

    def color_variant(self,response):
        image_urls = []
        color_variant = []
        product_dict = {}
        data_dict = response.meta['data_dict']
        product_name = response.xpath('//div[contains(@class,"product-details name-product")]/text()[1]').get().strip()
        
        product_dict['color_code'] = response.xpath('//div[contains(@class,"product-details name-product")]/span/text()').get().strip()
        color_code = response.xpath('//div[contains(@class,"product-details name-product")]/span/text()').get().strip()
        try:
            product_dict['product_price'] = response.xpath('//div[@class="product-main-info"]//div[@class="price-box"]/text()[1]').get().strip()
        except:
            product_dict['product_price'] = None
        product_dict['color_name'] = response.xpath('//div[contains(@class,"landscape-pdp-space")]/div/text()').get().strip()
        
        image_elements = response.xpath('//div[@class="carousel image-gallery__image js-gallery-image"]/div//img[@class="lazyOwl"]')
        for img_element, j in zip(image_elements, range(len(image_elements))):
            try:
                image_url = "https://my.thelios.com" + img_element.xpath('./@data-zoom-image').get()
            except:
                image_url = "https://my.thelios.com" + img_element.xpath('./@data-src').get()
            image_urls.append(image_url)
            yield scrapy.Request(image_url, callback=self.image_response, meta={"product_name": product_name, "color_code": f"{color_code}_{j}"})

        product_dict['images'] = image_urls
        color_variant.append(product_dict) 
        for i in self.data_list:
            if i['product_name'] == product_name:
                if 'color_variants' in i:
                    i['color_variants'].append(color_variant)
                else:
                    i['color_variants'] = [color_variant]
    
    def image_response(self, response):
        product_name = response.meta['product_name']
        color_code = response.meta['color_code']

        image_data = response.body
        image_filename = f"image_output/{product_name}/{color_code}.jpg"
        os.makedirs(os.path.dirname(image_filename), exist_ok=True)
        with open(image_filename, 'wb') as image_file:
            image_file.write(image_data)

    def closed(self, reason):
        with open("output.json", "w") as output_file:
            json.dump(self.data_list, output_file, indent=4)