import pygame as pag

class mini_GUI_admin:
    def __init__(self, limit: pag.Rect) -> None:
        self.__list = []
        self.__limit = limit
    
    def add(self,mini_GUI,func=None,raw_pos=None,group:str=''):
        self.__list.append({'GUI':mini_GUI,'func':func,'raw_pos':raw_pos,'group':group})
        self.__list[-1]['GUI'].limits = self.limit
        self.__list[-1]['GUI'].direccion(self.__list[-1]['GUI'].rect)

    
    def draw(self, surface,pos, update=True):
        l = []
        for x in self.__list:
            if update and (r := x['GUI'].draw(surface,pos,update)):
                l.append(r)
        return l

    def click(self, pos):
        for i, g in sorted(enumerate(self.__list),reverse=True):
            if not (result := g['GUI'].click(pos)):
                continue
            rect1: pag.Rect = g['GUI'].rect.copy()
            if result == 'exit':
                self.__list.pop(i)
            elif result or result == 0:
                self.__list.pop(i)
                if g['func']:
                    g['func'](result)
            elif self.__list[i]['GUI'].rect.collidepoint(pos):
                self.__list.pop(i)
                self.__list.append(g)
            else:
                continue
            return True
        return False
    
    def clear(self):
        self.__list.clear()

    def clear_group(self,group:str):
        for i, g in sorted(enumerate(self.__list),reverse=True):
            if g['group'] == group:
                self.__list.pop(i)
    
    @property
    def limit(self):
        return self.__limit
    @limit.setter
    def limit(self,limit):
        self.__limit = limit
        for x in self.__list:
            x['GUI'].limits = self.__limit
            if x['raw_pos']:
                x['GUI'].pos = x['raw_pos']
            else:
                x['GUI'].pos = x['GUI'].pos


