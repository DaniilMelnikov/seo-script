import csv
import requests
from bs4 import BeautifulSoup


class ParserCheckXML:
    def __init__(self, project, sitemap):
        self.project = project
        self.sitemap = sitemap

        self.soup = ''
        self.sitemap_cache = self.sitemap
        self.wrtite_name = ''
        self.list_result = []
        self.fieldnames = []


    def generator_url_from_sitemap(self):
        xml = requests.get(self.sitemap_cache).content
        soup = BeautifulSoup(xml, "xml")
        loc = soup.findAll('loc')

        for url in loc:
            url = url.string
            if('.xml' in url):
                self.sitemap_cache = url
                for url in self.generator_url_from_sitemap():
                    yield url
            yield url


    def get_soup(self, url):
        html = requests.get(url)

        if (html.status_code == 200):
            html = html.content
        else:
            return False
        
        return BeautifulSoup(html, 'html.parser')
    

    def write_file(self):
        with open(f'{self.project}/{self.wrtite_name}.csv', 'w', encoding='utf-8', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
            writer.writeheader()

            for list in self.list_result:
                writer.writerow(list)
    
    
    def constructor_noindex(self):
        self.sitemap_cache = self.sitemap
        self.wrtite_name = 'noindex'
        self.fieldnames = ['url', 'noindex', 'nofollow']
        self.list_result = []
        for url in self.generator_url_from_sitemap():
            soup = self.get_soup(url)

            if(soup):
                meta_list = soup.findAll('meta')
            else:
                self.list_result.append({'url':url, 
                                         'noindex':"Не 200", 
                                         'nofollow':"Не 200"})
                continue
        
            noindex = False
            nofollow = False
            for meta in meta_list:
                content_meta = ''
                if(meta.get('name')=='robot'):
                    content_meta = meta.get('content')

                if(content_meta == 'noindex'):
                    noindex = True
                elif(content_meta == 'nofollow'):
                    nofollow = True

            if(noindex or nofollow):
                self.list_result.append({'url':url, 
                                         'noindex':noindex, 
                                         'nofollow':nofollow})

    
    def constructor_link(self):
        self.sitemap_cache = self.sitemap
        self.wrtite_name = 'link'
        self.fieldnames = ['url', 'link', 'check']
        self.list_result = []
        for url in self.generator_url_from_sitemap():
            soup = self.get_soup(url)

            if(soup):
                link_list = soup.findAll('a')
            else:
                self.list_result.append({'url':url, 
                                         'link':"Не 200",
                                         'check': True})
            
            for link in link_list:
                check_link = True
                if(not link.get('href') or not link.string):
                    check_link = False
                    self.list_result.append({'url':url,
                                          'link':link,
                                          'check':check_link})



project = input('Название проекта(имя папки): ')
sitemap = input('Ссылка на sitemap.xml: ')
parser = ParserCheckXML(project, sitemap)


while(True):
    button = input("""
        Доступные команды:
          1 - парсит noindex
          2 - парсит link
                   
        Введи: """)
    if(button == '1'):
        parser.constructor_noindex()
        parser.write_file()
    elif(button == '2'):
        parser.constructor_link()
        parser.write_file()
    else:
        break