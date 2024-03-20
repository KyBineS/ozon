import logging

import requests


class OnlineSim:
    def __init__(self, api_key):
        self.api_key = api_key

    def get_number(self):
        url = f'https://onlinesim.io/api/getNum.php?service=ozon&country=7&number=true&apikey={self.api_key}'
        try:
            r = requests.get(url)
            if r:
                return r.json()['number'][2:], r.json()['tzid']
        except:
            return False
        return False

    def get_code(self, tzid):
        url = f'https://onlinesim.io/api/getState.php?apikey={self.api_key}&message_to_code=1&tzid={tzid}'
        try:
            r = requests.get(url)
            if r:
                if 'msg' in r.json()[0]:
                    return r.json()[0]['msg']
        except:
            return False
        return False

o = OnlineSim('fUp35qGSN9P52X8-HSnv4E5v-7ks2R38s-B5hvxyJt-R69JjXVY7zt5DwV')
r = o.get_code(117830249)
print(r)