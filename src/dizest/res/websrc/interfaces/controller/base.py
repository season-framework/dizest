import season
import datetime
import json
import os

class Controller:
    def __startup__(self, wiz):
        self.__wiz__ = wiz
        wiz.session = wiz.model("session").use()
        sessiondata = wiz.session.get()
        wiz.response.data.set(session=sessiondata)

        config = wiz.model("dizest/config").load()
        if config is None: config = dict()
        wiz.response.data.set(hubconfig=config)

    def parse_json(self, jsonstr, default=None):
        try:
            return json.loads(jsonstr)
        except:
            pass
        return default

    def json_default(self, value):
        if isinstance(value, datetime.date):
            return value.strftime('%Y-%m-%d %H:%M:%S')
        return str(value).replace('<', '&lt;').replace('>', '&gt;')

    def set_menu(self, **kwargs):
        data = wiz.response.data.get("menu")
        if data is None:
            data = dict()

        for key in kwargs:
            data[key] = self.__menu__(kwargs[key])
        
        wiz.response.data.set(menu=data)

    def __menu__(self, menus):
        wiz = self.__wiz__
        request = wiz.request
        for menu in menus:
            pt = None
            if 'pattern' in menu: pt = menu['pattern']
            elif 'url' in menu: pt = menu['url']

            if pt is not None:
                if request.match(pt): menu['class'] = 'active'
                else: menu['class'] = ''

            if 'child' in menu:
                menu['show'] = ''
                for i in range(len(menu['child'])):
                    child = menu['child'][i]
                    cpt = None
                
                    if 'pattern' in child: cpt = child['pattern']
                    elif 'url' in child: cpt = child['url']

                    if menu['class'] == 'active':
                        menu['show'] = 'show'

                    if cpt is not None:
                        if request.match(cpt): 
                            menu['child'][i]['class'] = 'active'
                        else: 
                            menu['child'][i]['class'] = ''
        return menus
