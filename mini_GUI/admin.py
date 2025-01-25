import pygame as pag
from .objs import desicion_popup, simple_popup, select

class mini_GUI_admin:
    def __init__(self, limit: pag.Rect) -> None:
        self.__list: list[desicion_popup|select|simple_popup] = []
        self.__limit = limit
        self.gui_count = 0
        self.redraw = 1
    
    def add(self,mini_GUI,func=None,raw_pos=None,group:str=''):
        self.__list.append({'GUI':mini_GUI,'func':func,'raw_pos':raw_pos,'group':group, 'id':self.gui_count})
        self.__list[-1]['GUI'].limits = self.limit
        self.__list[-1]['GUI'].direccion(self.__list[-1]['GUI'].rect)
        self.gui_count += 1
        return self.gui_count-1

    
    def draw(self, surface):
        l = []
        for x in self.__list:
            if (r := x['GUI'].draw(surface)):
                l.append(r)
        return l
    
    def update(self, pos=None, **kwargs):
        for x in self.__list:
            x['GUI'].update(pos=pos, **kwargs)
    def update_hover(self, mouse_pos=(-100000,-100000)):
        for x in self.__list:
            x['GUI'].update_hover(mouse_pos=mouse_pos)

    def click(self, pos):
        for i, g in sorted(enumerate(self.__list),reverse=True):
            if not (result := g['GUI'].click(pos)) and not g['GUI'].rect.collidepoint(pos):
                continue
            if result == 'exit':
                self.__list.pop(i)
            elif result or result == 0:
                self.__list.pop(i)
                if g['func']:
                    g['func'](result)
            elif self.__list[i]['GUI'].rect.collidepoint(pos):
                self.__list.pop(i)
                self.__list.append(g)
                return True
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
    
    def pop(self,identifier: int):
        for i, g in sorted(enumerate(self.__list),reverse=True):
            if g['id'] == identifier:
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

    def get_update_rects(self):
        lista = []
        for x in self.__list:
            if isinstance(x['GUI'],select):
                lista.append(x['GUI'].rect)
        return lista