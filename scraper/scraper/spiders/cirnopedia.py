import scrapy

import datetime as dt

RARITY_NAMES = [
    '1★ (C)',
    '2★ (U)',
    '3★ (R)',
    '4★ (SR)',
    '5★ (SSR)'
]

class CirnoSpider(scrapy.Spider):
    name = "cirnopedia"
    allowed_domains = ['fate-go.cirnopedia.org']

    def __init__(self, *args, **kwargs):
        self.url = kwargs.pop('url', None)
        super().__init__(*args, **kwargs)

    def start_requests(self):
        yield scrapy.Request(self.url, self.parse)

    def parse_list_td(self, td):
        for item in td.css('.tooltip > .item'):
            rarity, s_class = [x.strip() for x in item.css('ch3::text').get().split('★ ', 1)]
            if not rarity: continue 
            rarity = int(rarity)
            yield {
                'name': item.css('ch1::text').get().strip(),
                'class': s_class,
                'rarity_num': rarity,
                'rarity': RARITY_NAMES[rarity-1],
            }

    def parse_date_text(self, text, year):
        dates = [str(year)+'-'+d.split('(', 1)[0].strip() 
            for d in text.split(' to ', 1)]
        if text.count('/') < 2:
            dates = [dates[0]]*2
        fmt = r'%Y-%m/%d'
        return [dt.datetime.strptime(d, fmt).date() for d in dates]


    def parse(self, response):
        columns = None
        start_year = 2015
        for i, table in enumerate(response.css('table')):
            year = start_year+i
            if not columns:
                columns = (th.css('::text').get().strip() for th in table.css('th'))
                columns = [c.lower().replace(' ', '-') for c in columns]
                columns[0] = 'name'
            for tr in table.css('tbody > tr'):
                img = tr.css('.banner::attr(src)').get()
                img = response.urljoin(img)

                tds = tr.css('td')
                texts = [t.get().strip() for t in tds[0].css(':not(font)::text')]
                texts = [t for t in texts if t]
                event = ' '.join(texts[:-1])
                start, end = self.parse_date_text(texts[-1], year)

                right_columns = [list(self.parse_list_td(tds[k])) 
                    for k in range(1, 3)]
                out = dict(zip(columns, [event] + right_columns))
                out['start'] = start 
                out['end'] = end
                yield out