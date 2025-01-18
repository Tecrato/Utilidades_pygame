import pygame as pag
import sys
import os
import datetime
import pyperclip
from pathlib import Path
import Utilidades as uti
import Utilidades_pygame as uti_pag

os.chdir(Path(__file__).parent)
TITLE: str = 'Program'
RESOLUCION = [800, 550]
MIN_RESOLUTION = [550,450]
RETURNCODE = 0
MAX_FPS = 60

class Program:
    def __init__(self) -> None:
        pag.init()
        pag.font.init()
        self.ventana: pag.Surface = pag.display.set_mode(RESOLUCION, pag.RESIZABLE|pag.DOUBLEBUF)
        self.ventana_rect: pag.Rect = self.ventana.get_rect()
        pag.display.set_caption(TITLE)
        
        # Variables necesarias
        self.drawing: bool = True
        self.draw_background: bool = True
        self.framerate: int = 60
        self.loading: int = 0
        self.redraw: bool = True
        self.hitboxes = False
        self.relog: pag.time.Clock = pag.time.Clock()
        self.updates: list[pag.Rect] = []
        self.background_color: tuple[int,int,int] = (20,20,20)

        # Otras variables
        self.delta_time: uti.Deltatime = uti.Deltatime(self.framerate)
        ...
        ...

        # Variables por pantalla
        # Principal:
        # self.list_to_draw_main: list[uti_pag.Text|uti_pag.Button|uti_pag.Input|uti_pag.Multi_list|uti_pag.List|uti_pag.Bloque] = []
        # self.list_to_update_main: list[uti_pag.Text|uti_pag.Button|uti_pag.Input|uti_pag.Multi_list|uti_pag.List|uti_pag.Bloque] = []
        # self.list_to_click_main: list[uti_pag.Button|uti_pag.Bloque] = []
        # self.list_inputs: list[uti_pag.Input] = []
        self.lists_screens = {
            "main":{
                "draw": [],
                "update": [],
                "click": [],
                "inputs": []
                }
            }
        ...

        # Pantalla de configuracion
        # self.list_to_draw_config: list[uti_pag.Text|uti_pag.Button|uti_pag.Input|uti_pag.Multi_list|uti_pag.List|uti_pag.Bloque] = []
        # self.list_to_click_config: list[uti_pag.Button|uti_pag.Bloque] = []
        # self.list_inputs_config: list[uti_pag.Input] = []
        # ... --------------------> Es un ejemplo de como se puede hacer una pantalla de configuracion

        # Iniciar el programa
        self.load_resources()
        self.generate_objs()

        # aqui puedes añadir codigo extra que se ejcutara al iniciar la aplicacion,
        # self.func_ejemplo1()
        # self.empezar_tarea_en_segundo_plano()


        # Algoritmo para pasar de pantalla sin que esten unas dentro de otras
        self.screens_bools: dict[str, bool] = {'main': True}

        self.ciclo_general = [self.screen_main]
        self.cicle_try = 0

        while self.cicle_try < 5:
            self.cicle_try += 1
            for x in self.ciclo_general:
                x()
        pag.quit()

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
        self.texto1 = uti_pag.Text('Texto de ejemplo', 20, None, (RESOLUCION[0]/2,50), dire='top')
        self.boton1 = uti_pag.Button('Boton de ejemplo', 20, None, (100,100), dire='center')
        ...

        # Tambien se debe agregar a las respiectivas listas
        self.lists_screens["main"]["draw"].extend([self.texto1,self.boton1])
        self.lists_screens["main"]["update"].extend([self.texto1,self.boton1])
        self.lists_screens["main"]["click"].extend([self.boton1])

        # Y se mueven los objetos a su posicion en pantalla
        self.move_objs()

    # Para mover los objetos denuevo, cuando la ventana cambie de tamaño
    def move_objs(self):
        ...

    # Para dibujar los objetos de las utilidades
    def draw_objs(self, lista: list[uti_pag.Text|uti_pag.Button|uti_pag.Input|uti_pag.Multi_list|uti_pag.Select_box|uti_pag.Bloque]):
        if self.draw_background:
            self.ventana.fill(self.background_color)
            
        redraw = self.redraw
        self.redraw = False
        if redraw:
            for x in lista:
                x.redraw += 1

        new_list = lista+[self.GUI_manager,self.Mini_GUI_manager]
        if self.loading > 0 and self.loader:
            new_list.append(self.loader)
        self.updates.clear()
        for i,x in sorted(enumerate(lista+[self.GUI_manager,self.Mini_GUI_manager]),reverse=False): #,self.loader
            re = x.redraw
            r = x.draw(self.ventana)
            for s in r:
                self.updates.append(s)
            if self.hitboxes:
                for x in r:
                    pag.draw.rect(self.ventana, 'green', x, 1)
            for y in r:
                for p in lista[i+1:]:
                    if p.collide(y) and p.redraw < 1:
                        p.redraw = 1
            if re < 2:
                continue
            for y in r:
                for p in lista[:i]:
                    if p.collide(y) and p.redraw < 1:
                        p.redraw = 1
        
        
        if redraw:
            pag.display.update()
        else:
            pag.display.update(self.updates)

    def exit(self):
        for x in self.screens_bools.keys():
            self.screens_bools[x] = False

    def eventos_en_comun(self,evento):
        mx, my = pag.mouse.get_pos()
        if evento.type == pag.QUIT:
            self.exit()
        elif evento.type == pag.KEYDOWN and evento.key == pag.K_F12:
            momento = datetime.datetime.today().strftime('%y%m%d_%f')
            pag.image.save(self.ventana,'screenshot_{}_{}.png'.format(TITLE,momento))
        elif evento.type == pag.KEYDOWN and evento.key == pag.K_F11:
            self.hitboxes = not self.hitboxes
        elif evento.type == pag.WINDOWRESTORED:
            self.framerate: int = MAX_FPS
            return True
        elif evento.type == pag.MOUSEBUTTONDOWN and evento.button in [1,3] and self.Mini_GUI_manager.click(evento.pos):
            return True
        elif evento.type == pag.WINDOWMINIMIZED:
            self.drawing = False
            self.framerate: int = 30
            return True
        elif evento.type == pag.WINDOWFOCUSLOST:
            self.framerate: int = 30
            return True
        elif evento.type in [pag.WINDOWTAKEFOCUS, pag.WINDOWFOCUSGAINED,pag.WINDOWMAXIMIZED]:
            self.drawing = True
            self.framerate: int = MAX_FPS
            return True
        elif evento.type in [pag.WINDOWRESIZED,pag.WINDOWMAXIMIZED,pag.WINDOWSIZECHANGED,pag.WINDOWMINIMIZED,pag.WINDOWSHOWN,pag.WINDOWMOVED]:
            size = pag.Vector2(pag.display.get_window_size())
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
    
    def screen_main(self):
        if self.screens_bools['main']:
            self.cicle_try = 0
            self.redraw = True
        
        while self.screens_bools['main']:
            self.relog.tick(self.framerate)
            self.delta_time.update()

            mx, my = pag.mouse.get_pos()
            eventos = pag.event.get()
            for evento in eventos:
                if self.eventos_en_comun(evento):
                    self.redraw = True
                    continue
                elif evento.type == pag.KEYDOWN:
                    if evento.key == pag.K_ESCAPE:
                        self.exit()
                    elif evento.key == pag.K_v and pag.key.get_pressed()[pag.K_LCTRL]:
                        for x in self.lists_screens["main"]["inputs"]:
                            if x.typing:
                                x.set(pyperclip.paste())
                elif evento.type == pag.MOUSEBUTTONDOWN and evento.button == 1 and not self.on_mouse_click_general(evento, self.lists_screens["main"]["click"]):
                    ...
                elif evento.type == pag.MOUSEWHEEL and not self.wheel_event_general(evento,self.lists_screens["main"]["click"]):
                    ...
                elif evento.type == pag.MOUSEBUTTONUP:
                    for i,x in sorted(enumerate(self.lists_screens["main"]["click"]), reverse=True):
                        if isinstance(x, (uti_pag.Multi_list,uti_pag.List, uti_pag.Bloque)):
                            x.scroll = False
                elif evento.type == pag.MOUSEMOTION and not self.mouse_motion_event_general(evento,self.lists_screens["main"]["click"]):
                    ...
                # Ejemplo para añadir multiseleccion en las listas
                # elif evento.type == MOUSEBUTTONDOWN and evento.button == 3:
                #     if self.lista_descargas.click((mx, my),pag.key.get_pressed()[pag.K_LCTRL],button=3) and (result := self.lista_descargas.get_selects()):
                #         self.Mini_GUI_manager.add(mini_GUI.select((mx, my),
                #                                                   [self.txts['descargar'], self.txts['eliminar'],
                #                                                    self.txts['actualizar_url'], 'get url', self.txts['añadir a la cola'], self.txts['remover de la cola'], self.txts['limpiar cola'],
                #                                                    self.txts['reiniciar'], self.txts['cambiar nombre']],
                #                                                   captured=result),
                #                                   self.func_select_box)

            self.update_general(self.lists_screens["main"]["update"], (mx,my))
            # Y pones el resto de cosas que quieres que se actualizen
            ...

            if self.drawing:
                self.draw_objs(self.lists_screens["main"]["draw"])  # La lista a dibujar de esta pantalla

    def update_general(self,lista,mouse_pos):
        for i,x in sorted(enumerate(lista), reverse=True):
            x.update(dt=self.delta_time.dt,mouse_pos=mouse_pos)
        self.GUI_manager.update(mouse_pos=mouse_pos)
        self.Mini_GUI_manager.update(mouse_pos=mouse_pos)
        if self.loading > 0 and self.loader:
            self.loader.update(self.delta_time.dt)

    def wheel_event_general(self,evento,lista):
        for i,x in sorted(enumerate(lista), reverse=True):
            if isinstance(x, (uti_pag.Multi_list,uti_pag.List,uti_pag.Bloque)) and not x.scroll:
                x.rodar(evento.y*15)
                return True
        # aqui va el codigo que el programador desee (recordar acabar con return True para que no ejecute el resto de eventos)
        return False

    def mouse_motion_event_general(self,evento, lista):
        for i,x in sorted(enumerate(lista), reverse=True):
            if isinstance(x, (uti_pag.Multi_list, uti_pag.List, uti_pag.Bloque)) and x.scroll:
                x.rodar_mouse(evento.rel[1])
                return True
            
        # aqui va el codigo que el programador desee (recordar acabar con return True para que no ejecute el resto de eventos)
        return False
    
    def on_mouse_click_general(self,evento,lista):
        for i,x in sorted(enumerate(lista), reverse=True):
            if isinstance(x, (uti_pag.Multi_list,uti_pag.List)) and x.click(evento.pos,pag.key.get_pressed()[pag.K_LCTRL]):
                self.redraw = True
                return True
            elif x.click(evento.pos):
                self.redraw = True
                return True
        # aqui va el codigo que el programador desee (recordar acabar con return True para que no ejecute el resto de eventos)
        ...
        ...
        ...
        return False

if __name__ == '__main__':
    Program()
    sys.exit(RETURNCODE)
