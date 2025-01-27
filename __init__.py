from .Animaciones import Curva_de_Bezier, Second_Order_Dinamics, Simple_acceleration
from .Barras_progreso import Barra_de_progreso
from .particles import Particles
from .sparks import Spark
from .bloque import Bloque

from . import GUI
from . import mini_GUI

from .texts import Text
from .texts import Button
from .texts import Input
from .texts import List
from .texts import Multi_list
from .texts import Select_box
from .texts import App_menu

from .figuras.poligono_regular import Poligono_regular
from .figuras.poligono_irregular import Poligono_irregular
from .figuras.engranajes import Engranaje

from Utilidades import memosize

from .graficas import *

__all__ = [
    # Optimizacion
    "memosize",
    
    # Texts
    "App_menu",
    "Text",
    "Button",
    "Input",
    "List",
    "Multi_list",
    "Select_box",

    # Figures
    "Poligono_regular",
    "Poligono_irregular",
    "Engranaje",
    "Barra_de_progreso",

    # GUI
    "GUI",
    "mini_GUI",

    # other classes
    "Curva_de_Bezier",
    "Second_Order_Dinamics",
    "Simple_acceleration",
    "Particles",
    "Spark",
    "Bloque",
]

print(
    "Bienvenido a las utilidades para pygame, Hecho por Edouard Sandoval\n"
    "Para empezar leer la guia y crear una clase que herede de 'Utilidades_pygame.base_app_class.Base_class'"
)
