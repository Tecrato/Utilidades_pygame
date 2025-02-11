from typing import Literal
import platformdirs
import pygame

class Config:
    # def __init__(self, **kwargs):
    def __init__(
            self, window_resize=None, scaled=None, title=None, window_title=None, my_company=None, 
            author=None, version=None, description=None, copyright=None, resolution=None, 
            min_resolution=None, returncode=None, max_fps=None, min_fps=None, screenshot_dir=None, 
            save_dir=None, icon: pygame.Surface=None, **kwargs
            ):
        self.window_resize = window_resize if window_resize is not None else True
        self.scaled = scaled if scaled is not None else False
        
        self.title: str = title if title is not None else 'Programa_ejemplo'
        self.window_title: str = window_title if window_title is not None else 'Programa ejemplo'
        self.my_company = my_company if my_company is not None else 'Mi compañia'
        self.author: str = author if author is not None else 'Edouard Sandoval'
        self.version: str = version if version is not None else '0.0.1'
        self.description: str = description if description is not None else 'Ejemplo de programa para empezar con una idea'
        self.copyright: str = copyright if copyright is not None else '2025 Edouard Sandoval'
        self.resolution = resolution if resolution is not None else [800, 550]
        self.min_resolution = min_resolution if min_resolution is not None else [550,450]
        self.returncode = returncode if returncode is not None else 0
        self.max_fps = max_fps if max_fps is not None else 60
        self.min_fps = min_fps if min_fps is not None else 60
        self.screenshots_dir = screenshot_dir if screenshot_dir is not None else platformdirs.user_pictures_path().joinpath(f'./{self.my_company}/{self.title}')
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        self.save_dir = save_dir if save_dir is not None else platformdirs.user_config_path(self.title, self.my_company)
        self.save_dir.mkdir(parents=True, exist_ok=True)

        self.icon: pygame.Surface|None = icon

        for x in kwargs:
            setattr(self, x, kwargs[x])