import pygame as pag
import sys
import datetime
import pyperclip
import Utilidades as uti
import Utilidades_pygame as uti_pag

from pygame import Vector2

TITLE: str = 'Program'
RESOLUCION = [800, 550]
MIN_RESOLUTION = [550,450]

class Program:
    def __init__(self) -> None:
        self.ventana: pag.Surface = pag.display.set_mode(RESOLUCION, pag.RESIZABLE|pag.DOUBLEBUF)
        self.ventana_rect: pag.Rect = self.ventana.get_rect()
        pag.display.set_caption(TITLE)
        
        # Variables necesarias
        self.drawing: bool = True
        self.draw_background: bool = True
        self.framerate: int = 60
        self.loading: int = 0
        self.redraw: bool = True
        self.relog: pag.time.Clock = pag.time.Clock()
        self.updates: list[pag.Rect] = []
        self.background_color: tuple[int,int,int] = (20,20,20)

        # Otras variables
        self.delta_time: uti.Deltatime = uti.Deltatime(self.framerate)
        ...
        ...

        # Variables por pantalla
        # Principal:
        self.list_to_draw_main: list[uti_pag.Text|uti_pag.Button|uti_pag.Input|uti_pag.Multi_list|uti_pag.List|uti_pag.Bloque] = []
        self.list_to_click_main: list[uti_pag.Button|uti_pag.Bloque] = []
        self.list_inputs: list[uti_pag.Input] = []
        ...

        # Pantalla de configuracion
        # self.list_to_draw_config: list[uti_pag.Text|uti_pag.Button|uti_pag.Input|uti_pag.Multi_list|uti_pag.List|uti_pag.Bloque] = []
        # self.list_to_click_config: list[uti_pag.Button|uti_pag.Bloque] = []
        # self.list_inputs_config: list[uti_pag.Input] = []
        # ... --------------------> Es un ejemplo de como se puede hacer una pantalla de configuracion

        # Iniciar el programa
        self.load_resources()
        self.generate_objs()


        # Algoritmo para pasar de pantalla sin que esten unas dentro de otras
        self.screen_main_bool: bool = True
        ...                                         # Agregar variables booleanas para cada pantalla

        self.ciclo_general = [self.main_cycle]
        self.cicle_try = 0

        while self.cicle_try < 5:
            self.cicle_try += 1
            for x in self.ciclo_general:
                x()

    def load_resources(self):
        # Para cargar tu archivo json de configuraciones
        # Y alguna Base de datos si es necesario
        ... 

    def save_json(self):
        # Para guardar tu archivo json de configuraciones
        ... 

    # Donde se va a generar el texto, inputs, y demas cosas
    def generate_objs(self) -> None:
        # Cosas varias
        # uti.GUI.configs['fuente_simbolos'] = self.font_simbolos      ----   # Esto es para la GUI que retorna texto, mientras lo la uses no es obligatorio
        self.GUI_manager = uti_pag.GUI.GUI_admin()
        self.Mini_GUI_manager = uti_pag.mini_GUI.mini_GUI_admin(self.ventana_rect)

        # El resto de textos y demas cosas
        ...

        # Y se mueven los objetos a su posicion en pantalla
        self.move_objs()

    # Para mover los objetos denuevo, por ejemplo cuando la ventana cambie de tamaño
    def move_objs(self):
        ...

    # Para dibujar los objetos de las utilidades
    def draw_objs(self, lista: list[uti.Text|uti.Button|uti.Input|uti.Multi_list|uti.Select_box]):
        if self.draw_background:
            self.ventana.fill((20, 20, 20))
            
        redraw = self.redraw
        self.redraw = False
        if redraw:
            for x in lista:
                x.redraw = 2

        # if self.loading > 0:
        #     self.loader.update(self.delta_time.dt)
        #     self.loader.redraw = 1
        self.updates.clear()
        for i,x in sorted(enumerate(lista+[self.GUI_manager,self.Mini_GUI_manager]),reverse=False): #,self.loader
            if isinstance(x, (uti.Button,uti.Select_box,uti.mini_GUI.mini_GUI_admin,uti.GUI.GUI_admin)):
                r = x.draw(self.ventana, pag.mouse.get_pos())
            else:
                r = x.draw(self.ventana)
            [self.updates.append(s) for s in r]
            for y in r:
                for p in lista[i+1:]:
                    if p.collide(y):
                        p.redraw += 1
        
        if redraw:
            pag.display.update()
        else:
            pag.display.update(self.updates)

    def eventos_en_comun(self,evento):
        mx, my = pag.mouse.get_pos()
        if evento.type == pag.QUIT:
            pag.quit()
            sys.exit()
        elif evento.type == pag.KEYDOWN and evento.key == pag.K_F12:
            momento = datetime.datetime.today().strftime('%y%m%d_%f')
            pag.image.save(self.ventana,'screenshot_{}_{}.png'.format(TITLE,momento))
        elif evento.type == pag.WINDOWRESTORED:
            return True
        elif evento.type == pag.MOUSEBUTTONDOWN and evento.button in [1,3]:
            if self.Mini_GUI_manager.click(evento.pos):
                return True
        elif evento.type == pag.WINDOWMINIMIZED:
            self.drawing = False
            return True
        elif evento.type == pag.WINDOWFOCUSLOST:
            self.framerate = 30
            return True
        elif evento.type in [pag.WINDOWTAKEFOCUS, pag.WINDOWFOCUSGAINED,pag.WINDOWMAXIMIZED]:
            self.framerate = 60
            self.drawing = True
            return True
        elif evento.type in [pag.WINDOWRESIZED,pag.WINDOWMAXIMIZED,pag.WINDOWSIZECHANGED,pag.WINDOWMINIMIZED,pag.WINDOWSHOWN,pag.WINDOWMOVED]:
            size = Vector2(pag.display.get_window_size())
            if size.x < MIN_RESOLUTION[0]:
                size.x = MIN_RESOLUTION[0]
            if size.y < MIN_RESOLUTION[1]:
                size.y = MIN_RESOLUTION[1]
            self.ventana = pag.display.set_mode(size, pag.RESIZABLE|pag.DOUBLEBUF)
            self.ventana_rect = self.ventana.get_rect()

            self.move_objs()
            return True
        elif self.loading > 0:
            return True
        elif self.GUI_manager.active >= 0:
            if evento.type == pag.KEYDOWN and evento.key == pag.K_ESCAPE:
                self.GUI_manager.pop()
            elif evento.type == pag.MOUSEBUTTONDOWN and evento.button == 1:
                self.GUI_manager.click((mx, my))
            return True
        return False
    
    def main_cycle(self):
        if self.screen_main_bool:
            self.cicle_try = 0
            self.redraw = True
        
        while self.screen_main_bool:
            self.relog.tick(self.framerate)
            self.delta_time.update()

            mx, my = pag.mouse.get_pos()
            eventos = pag.event.get()
            self.GUI_manager.input_update(eventos)
            for evento in eventos:
                if self.eventos_en_comun(evento):
                    self.redraw = True
                    continue
                elif evento.type == pag.KEYDOWN:
                    if evento.key == pag.K_ESCAPE:
                        pag.quit()
                        sys.exit()
                    elif evento.key == pag.K_v and pag.key.get_pressed()[pag.K_LCTRL]:
                        for x in self.list_inputs:
                            if x.typing:
                                x.set(pyperclip.paste())
                elif evento.type == pag.MOUSEBUTTONDOWN and evento.button == 1:
                    for i,x in sorted(enumerate(self.list_to_click_main), reverse=True):
                        if isinstance(x, (uti_pag.Multi_list,uti_pag.List)) and x.click((mx,my),pag.key.get_pressed()[pag.K_LCTRL]):
                            self.redraw = True
                            break
                        elif x.click((mx, my)):
                            self.redraw = True
                            break
                elif evento.type == pag.MOUSEWHEEL and not self.wheel_event_main(evento,self.list_to_click_main):
                    ...
                elif evento.type == pag.MOUSEMOTION and not self.mouse_motion_event_main(evento,self.list_to_click_main):
                    ...
                # elif evento.type == MOUSEBUTTONDOWN and evento.button == 3:
                #     if self.lista_descargas.click((mx, my),pag.key.get_pressed()[pag.K_LCTRL],button=3) and (result := self.lista_descargas.get_selects()):
                #         self.Mini_GUI_manager.add(mini_GUI.select((mx, my),
                #                                                   [self.txts['descargar'], self.txts['eliminar'],
                #                                                    self.txts['actualizar_url'], 'get url', self.txts['añadir a la cola'], self.txts['remover de la cola'], self.txts['limpiar cola'],
                #                                                    self.txts['reiniciar'], self.txts['cambiar nombre']],
                #                                                   captured=result),
                #                                   self.func_select_box)
                
            for x in self.list_to_draw_main:
                x.update(dt=self.delta_time.dt)
            if self.drawing:
                self.draw_objs(self.list_to_draw_main)  # La lista a dibujar de esta pantalla

    def wheel_event_main(self,evento,lista):
        for i,x in sorted(enumerate(lista), reverse=True):
            if isinstance(x, (uti_pag.Multi_list,uti_pag.List)) and x.scroll:
                x.rodar(evento.y*15)
                return True
        return False

    def mouse_motion_event_main(self,evento, lista):
        for i,x in sorted(enumerate(lista), reverse=True):
            if isinstance(x, (uti_pag.Multi_list,uti_pag.List)) and x.scroll:
                x.rodar_mouse(evento.rel[1])
                return True
        return False

if __name__ == '__main__':
    pag.init()
    Program()
