import pygame as pag
from .objs import Text_return

class GUI_admin:
    """
    # Ejemplo:

    ### Para los eventos de los inputs:
    self.GUI_manager.input_update(eventos)

    ### Para los eventos:
    (Debajo del evento de QUIT)
    elif self.GUI_manager.active >= 0:
        if evento.type == KEYDOWN and evento.key == K_ESCAPE:
            self.GUI_manager.pop()
        elif evento.type == MOUSEBUTTONDOWN and evento.button == 1:
            self.GUI_manager.click((mousex,mousey))

    ### Para dibujar:
    self.GUI_manager.draw(self.ventana,(mousex,mousey))
    """
    def __init__(self, font_simbols:str =None) -> None:
        self.__list = []
        self.active = -1
    def add(self,clase, func= None) -> None:
        self.__list.append({'GUI':clase.copy(), 'func':func})
        self.active = len(self.__list)-1
    def draw(self,surface, mouse_pos, update=True) -> pag.Rect:
        if self.active >= 0:
            return self.__list[self.active]['GUI'].draw(surface, mouse_pos)
    def click(self, pos):
        mx,my = pos
        result = self.__list[self.active]['GUI'].click((mx,my))
        if result and result['return'] in ['aceptar','cancelar']:
            if self.__list[self.active]['func']: 
                self.__list[self.active]['func'](result['result']())
            self.pop(self.active)
            self.active = -1 if not self.__list else 0
            return (self.active,result['result']())
        elif result and result['return'] in ['destroy']:
            self.pop(self.active)
            self.active = -1 if not self.__list else 0
            return False
        elif result and result['return'] == 'function':
            result['result']()
        return False
    def pop(self,index=-1) -> None:
        if len(self.__list) > 0:
            self.__list.pop(index)
            self.active = len(self.__list)-1
    def input_update(self,eventos):
        for x in self.__list:
            if isinstance(x['GUI'],Text_return):
                x['GUI'].update(eventos)

