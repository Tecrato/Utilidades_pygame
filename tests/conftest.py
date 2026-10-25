"""Tests de `Utilidades_pygame`.

Corren sin ventana: SDL en modo `dummy`. Se ejecutan desde `site-packages` con:

    python -m pytest Utilidades_pygame/tests
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

# site-packages (este archivo vive en Utilidades_pygame/tests/)
SITE_PACKAGES = Path(__file__).resolve().parents[2]
if str(SITE_PACKAGES) not in sys.path:
    sys.path.insert(0, str(SITE_PACKAGES))

import pygame as pag
import pytest


@pytest.fixture(scope="session", autouse=True)
def pantalla():
    pag.init()
    pag.font.init()
    pag.display.set_mode((320, 240))
    yield
    pag.quit()


@pytest.fixture
def surface():
    s = pag.Surface((320, 240))
    s.fill((0, 0, 0))
    return s
