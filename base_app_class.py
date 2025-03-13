from typing import Literal, Union
import pygame as pag
import time
import math
import datetime
import Utilidades as uti
import Utilidades.win32_tools as win32_tools
from . import *
from .config_default import Config

__all__ = [
    "Base_class",
]

class Base_class:
    '''
    ## Definiras las siguientes funciones:
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

    ## Para agregar pantallas
    1) self.registrar_pantalla(alias: str)
    2) Agregar los botones y otros widgets a self.lists_screens[alias_de_pantalla]["draw"|"update"|"click"|"inputs"]
    '''
    def __init__(self,config: Config = Config(), *args, **kwargs) -> None:
        self.args = args
        self.kwargs = kwargs
        pag.init()
        pag.font.init()
        self.config: Config = config
        self.flags: int = pag.DOUBLEBUF|pag.HWACCEL
        if self.config.window_resize:
            self.flags |= pag.RESIZABLE
        if self.config.scaled:
            self.flags |= pag.SCALED
        self.ventana: pag.Surface = pag.display.set_mode(self.config.resolution,  self.flags)
        self.ventana_rect: pag.Rect = self.ventana.get_rect()
        pag.display.set_caption(self.config.window_title)
        if self.config.icon:
            pag.display.set_icon(pag.image.load(self.config.icon))
        
        # Variables necesarias
        self.loader = None
        self.draw_mode: Literal["optimized","always"] = 'optimized'
        self.__framerate: int = 60
        self.__loading: int = 0
        self.scroll_speed: int = 15
        self.hwnd: int = pag.display.get_wm_info()['window']
        self.drawing: bool = True
        self.draw_background: bool = True
        self.redraw: bool = True
        self.hitboxes: bool = False
        self.can_resize: bool = True
        self.click: bool = False
        self.navegate_with_keys: bool = True
        self.running: bool = True
        self.last_click: float = time.time()
        self.relog: pag.time.Clock = pag.time.Clock()
        self.updates: list[pag.Rect] = []
        self.background_color: tuple[int,int,int] = (20,20,20)

        # Otras variables
        self.Func_pool = uti.Funcs_pool()
        self.class_intervals = uti.multithread.Interval_funcs()
        self.delta_time: uti.Deltatime = uti.Deltatime()
        self.otras_variables()
        self.accept_to_move_with_arrows = Union[Input, Button]
        
        # Variables por pantalla
        self.lists_screens: dict[str,dict[Literal['draw','update','click','inputs'],list]] = {
            "main":{
                "draw": [],
                "update": [],
                "click": [],
                "inputs": []
                }
            }
        self.actual_screen: str = 'main'
        self.overlay: list = []

        # Iniciar el programa
        # self.GUI_manager: GUI.GUI_admin = GUI.GUI_admin()
        self.Mini_GUI_manager: mini_GUI.mini_GUI_admin = mini_GUI.mini_GUI_admin(self.ventana_rect)
        self.load_resources()
        self.generate_objs()
        self.move_objs()
        self.calculate_adjacent_controls()

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
    def generate_objs(self): ...

    def registrar_pantalla(self, alias):
        self.lists_screens[alias] = {
            "draw": [],
            "update": [],
            "click": [],
            "inputs": []
        }
    def goto(self, alias):
        self.actual_screen: str = alias
        self.redraw = True
        self.click = False
        for x in self.lists_screens[alias]["click"]:
            x.hover = False
        self.Mini_GUI_manager.update_hover(pag.mouse.get_pos())
        for i,x in sorted(enumerate(self.lists_screens[self.actual_screen]["click"]), reverse=True):
            x.update_hover(pag.mouse.get_pos())
        self.calculate_adjacent_controls()

    def draw_optimized(self, lista: list[Text|Button|Input|Multi_list|Select_box|Bloque|Engranaje]):
        lista = lista.copy()
        if self.draw_background:
            self.ventana.fill(self.background_color)
        self.updates.clear()
            
        redraw = self.redraw
        self.redraw = False
        if redraw:
            for x in lista:
                x.redraw += 1

        self.draw_before(self.actual_screen)

        new_list = lista+[self.Mini_GUI_manager]
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
                        p.redraw += 1
            if re < 2:
                continue
            for y in r:
                for p in lista[:i]:
                    if p.collide(y) and p.redraw < 1:
                        p.redraw += 1
        self.draw_after(self.actual_screen)
        if self.hitboxes:
            for x in self.updates:
                pag.draw.rect(self.ventana, 'green', x, 1)
        
        
        if redraw:
            pag.display.update()
        else:
            pag.display.update(self.updates)

    def draw_always(self, lista):
        lista = lista.copy()
        if self.draw_background:
            self.ventana.fill(self.background_color)
        for x in lista:
            x.redraw += 1

        new_list = lista+[self.Mini_GUI_manager]
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
            if (isinstance(x, Button) or isinstance(x, Input)) and x.hover:
                # Si el botón o input con hover actual tiene un control adyacente en la dirección especificada
                if x.controles_adyacentes.get(direccion, None):
                    x.hover = False
                    x.controles_adyacentes[direccion].hover = True
                    
                    # Si estamos moviendo desde un Input que está siendo editado
                    if isinstance(x, Input) and x.typing:
                        x.typing = False
                    
                    return
                break
        else:
            # Si ningún botón o input tiene hover, seleccionar el primer botón o input
            for x in lista:
                if isinstance(x, Button) or isinstance(x, Input):
                    x.hover = False
            for x in lista:
                if isinstance(x, Button) or isinstance(x, Input):
                    x.hover = True
                    break

    def select_btns_with_arrows(self, evento: pag.event.Event, screen_alias: str):
        # Si el evento es TAB, salimos del Input activo y pasamos al siguiente control
        if evento.key == pag.K_TAB:
            # Buscar el control actual
            for x in self.lists_screens[self.actual_screen]["click"] + self.overlay:
                if isinstance(x, Input) and x.typing:
                    x.typing = False
                    x.typing_line = False
                    x.draw_surf()
                    return True
            return False

        direccion = {
            pag.K_RIGHT: 'right',
            pag.K_LEFT: 'left',
            pag.K_UP: 'up',
            pag.K_DOWN: 'down'
        }
        # Manejo normal de las flechas
        if evento.key in direccion:
            self.move_hover(direccion[evento.key], self.lists_screens[self.actual_screen]["click"]+self.overlay)
            return True
        return False

    def on_keydown_general(self, evento: pag.event.Event):
        # Manejar inputs
        for x in self.lists_screens[self.actual_screen]["inputs"] + [y for y in self.overlay if isinstance(y, Input)]:
            # Si el Input tiene hover y se presiona Enter o se hace clic, activar
            if isinstance(x, Input) and x.hover and x.typing and evento.key == pag.K_RETURN:
                x.typing = False
                x.typing_line = False
                x.draw_surf()
                return True
            elif isinstance(x, Input) and x.hover and x.typing and evento.key == pag.K_ESCAPE:
                x.typing = False
                x.typing_line = False
                x.draw_surf()
                return True
                
        # Si algún Input está siendo editado, darle prioridad para los eventos de flechas
        for x in self.lists_screens[self.actual_screen]["inputs"] + [y for y in self.overlay if isinstance(y, Input)]:
            if isinstance(x, Input) and x.typing and evento.key in [pag.K_LEFT, pag.K_RIGHT, pag.K_BACKSPACE, pag.K_DELETE, pag.K_RETURN]:
                # Las flechas izquierda/derecha manejan la posición de edición en el Input
                return True
        
        # Navegar con teclas de flecha si no hay inputs activos o se presionó Tab
        if self.navegate_with_keys and evento.key in [pag.K_UP, pag.K_DOWN, pag.K_LEFT, pag.K_RIGHT, pag.K_TAB]:
            return self.select_btns_with_arrows(evento, self.actual_screen)
        elif evento.key == pag.K_SPACE:
            # Activar el botón o input que tiene hover actualmente con la tecla espaciadora
            for i, x in sorted(enumerate(self.lists_screens[self.actual_screen]["click"]+self.overlay), reverse=True):
                if isinstance(x, Button) and getattr(x, 'hover', False):
                    x.click()
                    return True
                elif isinstance(x, Input) and getattr(x, 'hover', False):
                    x.typing = True
                    x.redraw += 1
                    return True
    
        return False

    def calculate_adjacent_controls(self, buttons = None):
        """
        Calcula automáticamente los controles adyacentes para cada botón basado en su posición en la pantalla.
        
        Los controles adyacentes son los botones más cercanos en cada dirección (arriba, abajo, izquierda, derecha).
        La dirección se determina por sectores angulares, dividiendo el espacio en 4 cuadrantes.
        
        Args:
            buttons (list): Lista de botones para calcular los controles adyacentes. Si es None, se usan todos los botones.
        """
        # Si no se especifican botones, usar todos los botones
        if buttons is None:
            # Obtener todos los botones e inputs de la pantalla actual
            buttons = [x for x in self.lists_screens[self.actual_screen]["click"] if isinstance(x, self.accept_to_move_with_arrows)] + [x for x in self.overlay if isinstance(x, self.accept_to_move_with_arrows)]
        
        # Asegurarse de que todos los botones tengan inicializado el diccionario controles_adyacentes
        for button in buttons:
            if not hasattr(button, 'controles_adyacentes'):
                button.controles_adyacentes = {'up': None, 'right': None, 'down': None, 'left': None}
        
        # Para cada botón, determinar sus controles adyacentes
        for i, button in enumerate(buttons):
            # Obtener todos los otros botones excepto el actual
            other_buttons = buttons[:i] + buttons[i+1:]
            
            # Para cada dirección, encontrar el botón más cercano que esté en ese sector angular
            up_buttons = []
            right_buttons = []
            down_buttons = []
            left_buttons = []
            
            # Procesar cada botón y asignarlo a la dirección correspondiente
            for other in other_buttons:
                distance = uti.Hipotenuza(button.rect.center, other.rect.center)
                angle = uti.Angulo(button.rect.center, other.rect.center)
                
                # Clasificar por sector angular (dividir en 4 cuadrantes)
                # DERECHA: -45° a 45° (o 315° a 45°)
                if (angle >= 315 or angle < 45):
                    right_buttons.append((other, distance))
                # ABAJO: 45° a 135°
                elif (45 <= angle < 135):
                    down_buttons.append((other, distance))
                # IZQUIERDA: 135° a 225°
                elif (135 <= angle < 225):
                    left_buttons.append((other, distance))
                # ARRIBA: 225° a 315°
                else:
                    up_buttons.append((other, distance))
            
            # Asignar el botón más cercano en cada dirección
            if up_buttons:
                up_buttons.sort(key=lambda x: x[1])
                button.controles_adyacentes['up'] = up_buttons[0][0]
            
            if right_buttons:
                right_buttons.sort(key=lambda x: x[1])
                button.controles_adyacentes['right'] = right_buttons[0][0]
            
            if down_buttons:
                down_buttons.sort(key=lambda x: x[1])
                button.controles_adyacentes['down'] = down_buttons[0][0]
            
            if left_buttons:
                left_buttons.sort(key=lambda x: x[1])
                button.controles_adyacentes['left'] = left_buttons[0][0]

    def eventos_en_comun(self,evento):
        if evento.type == pag.MOUSEBUTTONDOWN:
            self.last_click = time.time()
            if evento.button == 1:
                self.click = True
        elif evento.type == pag.MOUSEBUTTONUP:
            self.click = False

        if evento.type == pag.QUIT:
            self.exit()
        elif evento.type == pag.KEYDOWN and evento.key == pag.K_F12 and self.config.screenshots_dir:
            momento = datetime.datetime.today().strftime('%d-%m-%y %f')
            result = win32_tools.take_window_snapshot(self.hwnd)
            surf = pag.image.frombuffer(result['buffer'],(result['bmpinfo']['bmWidth'], result['bmpinfo']['bmHeight']),'BGRA')
            pag.image.save(surf,self.config.screenshots_dir.joinpath('{title} {momento}.png'.format(title=self.config.title,momento=momento)))
        elif evento.type == pag.KEYDOWN and evento.key == pag.K_F11:
            self.hitboxes = not self.hitboxes
        elif evento.type == pag.WINDOWRESTORED:
            self.framerate: int = self.config.max_fps
            self.redraw = True
            return True
        elif evento.type == pag.MOUSEBUTTONDOWN and evento.button in [1,3] and self.Mini_GUI_manager.click(evento.pos):
            self.redraw = True
            return True
        elif evento.type == pag.WINDOWMINIMIZED:
            self.drawing = False
            self.framerate: int = self.config.min_fps
            self.redraw = True
            return True
        elif evento.type == pag.WINDOWFOCUSLOST:
            self.framerate: int = self.config.min_fps
            self.redraw = True
            return True
        elif evento.type in [pag.WINDOWTAKEFOCUS, pag.WINDOWFOCUSGAINED,pag.WINDOWMAXIMIZED]:
            self.drawing = True
            self.framerate: int = self.config.max_fps
            self.redraw = True
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
            self.calculate_adjacent_controls()
            self.redraw = True
            return True
        elif self.loading > 0:
            return True
        return False
    
    def update_general(self):
        mouse_pos = pag.mouse.get_pos()
        for i,x in sorted(enumerate(self.lists_screens[self.actual_screen]["update"]+self.overlay), reverse=True):
            x.update(mouse_pos=mouse_pos)
        self.Mini_GUI_manager.update(mouse_pos=mouse_pos)
        if self.loading > 0 and self.loader:
            self.loader.update()
        self.update(self.actual_screen)

    def on_wheel_event_general(self,evento):
        for i,x in sorted(enumerate(self.lists_screens[self.actual_screen]["click"]+self.overlay), reverse=True):
            if x.is_hover(pag.mouse.get_pos()) and getattr(x,'use_mouse_wheel',False):
                x.on_wheel(evento.y*self.scroll_speed)
                return True
        return False

    def on_mouse_motion_event_general(self,evento):
        if self.click:
            for i,x in sorted(enumerate(self.lists_screens[self.actual_screen]["click"]+self.overlay), reverse=True):
                if getattr(x,'use_mouse_motion',False):
                    x.on_mouse_motion(evento)
                    return True
        self.Mini_GUI_manager.update_hover(evento.pos)
        for i,x in sorted(enumerate(self.lists_screens[self.actual_screen]["click"]+self.overlay), reverse=True):
            x.update_hover(evento.pos)
        return False
    
    def on_mouse_click_general(self,evento):
        for i,x in sorted(enumerate(self.lists_screens[self.actual_screen]["click"]+self.overlay), reverse=True):
            if isinstance(x, (Multi_list,List)) and x.click(evento.pos,pag.key.get_pressed()[pag.K_LCTRL]):
                return True
            elif x.click(evento.pos):
                self.redraw = True
                return True
        return False 
    
    def on_mouse_click_up_general(self):
        for i,x in sorted(enumerate(self.lists_screens[self.actual_screen]["click"]+self.overlay), reverse=True):
            x.use_mouse_motion = False
        return False

    def screen_main(self):
        while self.running:
            self.relog.tick(self.framerate)
            self.delta_time.update()
            eventos = pag.event.get()
            for x in self.lists_screens[self.actual_screen]['inputs']:
                x.eventos_teclado(eventos)
            for evento in eventos:
                if self.eventos_en_comun(evento):
                    ...
                elif evento.type == pag.KEYDOWN and self.on_keydown_general(evento):
                    ...
                elif evento.type == pag.MOUSEBUTTONDOWN and evento.button == 1 and self.on_mouse_click_general(evento):
                    ...
                elif evento.type == pag.MOUSEWHEEL and self.on_wheel_event_general(evento):
                    ...
                elif evento.type == pag.MOUSEBUTTONUP and evento.button == 1 and self.on_mouse_click_up_general():
                    ...
                elif evento.type == pag.MOUSEMOTION and self.on_mouse_motion_event_general(evento):
                    ...
                else:
                    self.otro_evento(self.actual_screen, evento)

            self.update_general()

            if not self.drawing:
                continue
            if self.draw_mode == 'optimized':
                self.draw_optimized(self.lists_screens[self.actual_screen]["draw"]+self.overlay)  # La lista a dibujar de esta pantalla
            elif self.draw_mode == 'always':
                self.draw_always(self.lists_screens[self.actual_screen]["draw"]+self.overlay)

    @property
    def framerate(self):
        return self.__framerate
    @framerate.setter
    def framerate(self, num: int):
        self.__framerate = int(num)

    @property
    def loading(self) -> int:
        return self.__loading
    @loading.setter
    def loading(self, num: int):
        self.__loading = int(num)
        self.redraw = True
        if self.__loading > 0:
            for i,x in sorted(enumerate(self.lists_screens[self.actual_screen]["click"]+self.overlay), reverse=True):
                x.update_hover((-100000,-100000))
