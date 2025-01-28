from typing import Literal
import pygame as pag
import time
import datetime
import Utilidades as uti
from . import *
from .config_default import Config

__all__ = [
    "Base_class",
]

class Base_class:
    '''
    # Definiras las siguientes funciones:
    1) otras_variables()
    2) load_resources()
    3) generate_objs()
    4) move_objs()
    5) post_init()
    6) otro_evento(actual_screen: str, evento: pag.event.Event)
    7) update(actual_screen: str)
    8) draw_before(actual_screen: str)
    9) draw_after(actual_screen: str)
    10) on_exit()

    # Para agregar pantallas
    1) self.registrar_pantalla(alias: str)
    2) Agregar los botones y otros widgets a self.lists_screens[alias_de_pantalla]["draw"|"update"|"click"|"inputs"]
    '''
    def __init__(self,config: Config = Config(), *args, **kwargs) -> None:
        self.args = args
        self.kwargs = kwargs
        pag.init()
        pag.font.init()
        self.config = config
        self.flags = pag.DOUBLEBUF|pag.HWACCEL
        if self.config.window_resize:
            self.flags |= pag.RESIZABLE
        if self.config.scaled:
            self.flags |= pag.SCALED
        self.ventana: pag.Surface = pag.display.set_mode(self.config.resolution,  self.flags)
        self.ventana_rect: pag.Rect = self.ventana.get_rect()
        pag.display.set_caption(self.config.window_title)
        
        # Variables necesarias
        self.draw_mode: Literal["optimized","always"] = 'optimized'
        self.framerate: int = 60
        self.loading: int = 0
        self.scroll_speed: int = 15
        self.drawing: bool = True
        self.draw_background: bool = True
        self.redraw: bool = True
        self.hitboxes = False
        self.can_resize = True
        self.click = False
        self.navegate_with_keys = True
        self.running = True
        self.last_click = time.time()
        self.hwnd = pag.display.get_wm_info()['window']
        self.relog: pag.time.Clock = pag.time.Clock()
        self.updates: list[pag.Rect] = []
        self.background_color: tuple[int,int,int] = (20,20,20)

        # Otras variables
        self.delta_time: uti.Deltatime = uti.Deltatime(self.framerate)
        self.otras_variables()
        ...
        ...

        # Variables por pantalla
        self.lists_screens = {
            "main":{
                "draw": [],
                "update": [],
                "click": [],
                "inputs": []
                }
            }
        self.actual_screen = 'main'

        # Iniciar el programa
        self.GUI_manager = GUI.GUI_admin()
        self.Mini_GUI_manager = mini_GUI.mini_GUI_admin(self.ventana_rect)
        self.load_resources()
        self.generate_objs()

        # aqui puedes añadir codigo extra que se ejcutara al iniciar la aplicacion,
        self.post_init()

        self.screen_main()

        self.on_exit()
        pag.quit()
    
    def load_resources(self): ...
    def post_init(self): ...
    def otras_variables(self): ...
    def move_objs(self): ...
    def on_exit(self): ...
    def update(self, actual_screen: str): ...
    def otro_evento(self, actual_screen: str, evento: pag.event.Event): ...
    def draw_before(self, actual_screen: str): ...
    def draw_after(self, actual_screen: str): ...

    def registrar_pantalla(self, alias):
        self.lists_screens[alias] = {
            "draw": [],
            "update": [],
            "click": [],
            "inputs": []
        }
    def goto(self, alias):
        self.actual_screen = alias

    def draw_optimized(self, lista: list[Text|Button|Input|Multi_list|Select_box|Bloque]):
        if self.draw_background:
            self.ventana.fill(self.background_color)
        self.updates.clear()
            
        redraw = self.redraw
        self.redraw = False
        if redraw:
            for x in lista:
                x.redraw += 1

        self.draw_before(self.actual_screen)

        new_list = lista+[self.GUI_manager,self.Mini_GUI_manager]
        if self.loading > 0 and self.loader:
            new_list.append(self.loader)
        for i,x in enumerate(new_list):
            if not x.collide(self.ventana_rect):
                continue
            re = x.redraw
            r = x.draw(self.ventana)
            for s in r:
                self.updates.append(s)
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
        self.draw_after(self.actual_screen)
        # f
        if self.hitboxes:
            for x in self.updates:
                pag.draw.rect(self.ventana, 'green', x, 1)
        
        
        if redraw:
            pag.display.update()
        else:
            pag.display.update(self.updates)

    def draw_always(self, lista):
        if self.draw_background:
            self.ventana.fill(self.background_color)
        for x in lista:
            x.redraw += 1

        new_list = lista+[self.GUI_manager,self.Mini_GUI_manager]
        if self.loading > 0 and self.loader:
            new_list.append(self.loader)

        self.draw_before(self.actual_screen)
        for i,x in enumerate(new_list):
            x.draw(self.ventana)
        self.draw_after(self.actual_screen)

        pag.display.update()

    def exit(self):
        self.running = False
    
    def move_hover(self, direccion: str, lista):
        for i,x in sorted(enumerate(lista), reverse=True):
            if isinstance(x, Button) and x.controles_adyacentes.get('right',False) and x.hover:
                if not x.controles_adyacentes.get(direccion,False):
                    break
                x.hover = False
                x.controles_adyacentes.get(direccion,False).hover = True
                break
        else:
            for x in lista:
                if isinstance(x, Button):
                    x.hover = False
            for x in lista:
                if isinstance(x, Button):
                    x.hover = True
                    break

    def select_btns_with_arrows(self, evento: pag.event.Event, screen_alias: str):
        if evento.key == pag.K_RIGHT:
            self.move_hover('right',self.lists_screens[screen_alias]["click"])
        elif evento.key == pag.K_LEFT:
            self.move_hover('left',self.lists_screens[screen_alias]["click"])
        elif evento.key == pag.K_UP:
            self.move_hover('top',self.lists_screens[screen_alias]["click"])
        elif evento.key == pag.K_DOWN:
            self.move_hover('bottom',self.lists_screens[screen_alias]["click"])
        else: return False
        return True
    
    def select_inputs_with_TAB(self, evento: pag.event.Event, screen_alias: str):
        if len(self.lists_screens[screen_alias]["inputs"]) == 0:
            return False
        if evento.key == pag.K_TAB:
            next_typ = False
            for x in self.lists_screens[screen_alias]["inputs"]:
                if x.typing:
                    x.typing = False
                    next_typ = True
                elif next_typ:
                    x.typing = True
                    break
            else:
                return False
            return True
        else: 
            return False
    
    def eventos_en_comun(self,evento):
        mx, my = pag.mouse.get_pos()
        if evento.type == pag.MOUSEBUTTONDOWN:
            self.last_click = time.time()
            if evento.button == 1:
                self.click = True
        elif evento.type == pag.MOUSEBUTTONUP:
            self.click = False

        if evento.type == pag.QUIT:
            self.exit()
        elif evento.type == pag.KEYDOWN and evento.key == pag.K_F12 and self.config.screen_shots_dir:
            momento = datetime.datetime.today().strftime('%d-%m-%y %f')
            result = uti.win32_tools.take_window_snapshot(self.hwnd)
            surf = pag.image.frombuffer(result['buffer'],(result['bmpinfo']['bmWidth'], result['bmpinfo']['bmHeight']),'BGRA')
            pag.image.save(surf,self.config.screen_shots_dir.joinpath('Download Manager {}.png'.format(momento)))
        elif evento.type == pag.KEYDOWN and evento.key == pag.K_F11:
            self.hitboxes = not self.hitboxes
        elif evento.type == pag.WINDOWRESTORED:
            self.framerate: int = self.config.max_fps
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
            self.framerate: int = self.config.max_fps
            return True
        elif self.config.window_resize and evento.type in [pag.WINDOWRESIZED,pag.WINDOWMAXIMIZED,pag.WINDOWSIZECHANGED,pag.WINDOWMINIMIZED,pag.WINDOWSHOWN,pag.WINDOWMOVED]:
            size = pag.Vector2(pag.display.get_window_size())
            if size.x < self.config.min_resolution[0]:
                size.x = self.config.min_resolution[0]
            if size.y < self.config.min_resolution[1]:
                size.y = self.config.min_resolution[1]
            self.ventana = pag.display.set_mode(size,  self.flags)
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
    
    def update_general(self,lista,mouse_pos):
        for i,x in sorted(enumerate(lista), reverse=True):
            x.update(dt=self.delta_time.dt,mouse_pos=mouse_pos)
        self.GUI_manager.update(mouse_pos=mouse_pos)
        self.Mini_GUI_manager.update(mouse_pos=mouse_pos)
        if self.loading > 0 and self.loader:
            self.loader.update(self.delta_time.dt)

    def on_wheel_event_general(self,evento,screen_alias: str):
        for i,x in sorted(enumerate(self.lists_screens[screen_alias]["click"]), reverse=True):
            if isinstance(x, (Multi_list,List,Bloque)) and not x.scroll and x.rect.collidepoint(pag.mouse.get_pos()):
                x.rodar(evento.y*self.scroll_speed)
                return True
        return False

    def on_mouse_motion_event_general(self,evento, screen_alias: str):
        if self.click:
            for i,x in sorted(enumerate(self.lists_screens[screen_alias]["click"]), reverse=True):
                if isinstance(x, (Multi_list, List, Bloque)) and x.scroll:
                    x.rodar_mouse(evento.rel[1])
                    return True
        for i,x in sorted(enumerate(self.lists_screens[screen_alias]["click"]), reverse=True):
            x.update_hover(evento.pos)
        return False
    
    def on_mouse_click_general(self,evento,screen_alias: str):
        for i,x in sorted(enumerate(self.lists_screens[screen_alias]["click"]), reverse=True):
            if isinstance(x, (Multi_list,List)) and x.click(evento.pos,pag.key.get_pressed()[pag.K_LCTRL]):
                self.redraw = True
                return True
            elif x.click(evento.pos):
                self.redraw = True
                return True
        return False 
    
    def on_mouse_click_up_general(self,screen_alias: str):
        for i,x in sorted(enumerate(self.lists_screens[screen_alias]["click"]), reverse=True):
            if isinstance(x, (Multi_list,List, Bloque)) and x.scroll == True:
                x.scroll = False
                return True
        return False

    def on_keydown_general(self, screen_alias: str, evento):
        if evento.key == pag.K_TAB and self.navegate_with_keys:
            self.select_inputs_with_TAB(evento, self.actual_screen)
            return True
        elif self.select_btns_with_arrows(evento, self.actual_screen) and self.navegate_with_keys:
            return True
        elif evento.key == pag.K_SPACE and self.navegate_with_keys:
            for i,x in sorted(enumerate(self.lists_screens[self.actual_screen]["click"]),reverse=True):
                if x.hover:
                    x.click()
                    return True
        return False

    def screen_main(self):
        while self.running:
            self.relog.tick(self.framerate)
            self.delta_time.update()
            eventos = pag.event.get()
            for evento in eventos:
                if self.eventos_en_comun(evento):
                    self.redraw = True
                    continue
                elif evento.type == pag.KEYDOWN and self.on_keydown_general(self.actual_screen, evento):
                    ...
                elif evento.type == pag.MOUSEBUTTONDOWN and evento.button == 1 and self.on_mouse_click_general(evento, self.actual_screen):
                    ...
                elif evento.type == pag.MOUSEWHEEL and self.on_wheel_event_general(evento,self.actual_screen):
                    ...
                elif evento.type == pag.MOUSEBUTTONUP and self.on_mouse_click_up_general(self.actual_screen):
                    ...
                elif evento.type == pag.MOUSEMOTION and self.on_mouse_motion_event_general(evento,self.actual_screen):
                    ...
                else:
                    self.otro_evento(self.actual_screen, evento)
                # Ejemplo para añadir multiseleccion en las listas
                # elif evento.type == MOUSEBUTTONDOWN and evento.button == 3:
                #     if self.lista_descargas.click((mx, my),pag.key.get_pressed()[pag.K_LCTRL],button=3) and (result := self.lista_descargas.get_selects()):
                #         self.Mini_GUI_manager.add(mini_GUI.select((mx, my),
                #                                                   [self.txts['descargar'], self.txts['eliminar'],
                #                                                    self.txts['actualizar_url'], 'get url', self.txts['añadir a la cola'], self.txts['remover de la cola'], self.txts['limpiar cola'],
                #                                                    self.txts['reiniciar'], self.txts['cambiar nombre']],
                #                                                   captured=result),
                #                                   self.func_select_box)

            self.update_general(self.lists_screens[self.actual_screen]["update"], pag.mouse.get_pos())
            # Y pones el resto de logica que quieras en tu aplicacion
            self.update(self.actual_screen)

            if not self.drawing:
                continue
            if self.draw_mode == 'optimized':
                self.draw_optimized(self.lists_screens[self.actual_screen]["draw"])  # La lista a dibujar de esta pantalla
            elif self.draw_mode == 'always':
                self.draw_always(self.lists_screens[self.actual_screen]["draw"])

