from typing import Literal

#Posiciones para poner en dire
ALIGN_DIRECTION = Literal['center','left','right','top','bottom','topleft','topright','bottomleft','bottomright']
VERTICAL = Literal['vertical']
HORIZONTAL = Literal['horizontal']

TRANSPARENT_COLOR = (255, 0, 128)

DELAY_PRESSING = .3


REDRAW_CLEAN = 0    # no hay nada que dibujar
REDRAW_SELF = 1     # cambió mi apariencia: repintar mi rect
REDRAW_MOVED = 2    # cambié de sitio: mi rect + el anterior (limpiar el hueco)
REDRAW_FULL = 3     # todo (cambio de pantalla, resize)
