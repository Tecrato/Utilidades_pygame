import platformdirs
from Utilidades.maths import Vector2
from pathlib import Path
import os

class Config:
    def __init__(
            self, window_resize: bool=True,
            scaled: bool=False,
            title: str='Programa_ejemplo',
            window_title: str=None,
            my_company: str='Mi compañia', 
            author: str='Alguien nose',
            version: str='0.1',
            description: str='Ejemplo de programa para empezar con una idea',
            copyright: str=None,
            resolution: tuple[int,int]|list[int]|Vector2=(800, 550), 
            min_resolution: tuple[int,int]|list[int]|Vector2=(800//2,600//2),
            returncode: int=None,
            max_fps: int=60,
            min_fps: int=30,
            screenshot_dir=None, 
            save_dir: Path|None=None,
            icon: str=None,
            fonts: dict[str, str|Path|os.PathLike] | None = None,
            noframe: bool=None,
            window_transparent: bool=False,
            **kwargs
            ):
        self.window_resize = window_resize
        self.scaled = scaled
        
        self.title: str = title
        self.window_title: str = window_title if window_title is not None else self.title
        self.my_company: str = my_company
        self.author: str = author
        self.version: str = version
        self.description: str = description
        self.copyright: str = copyright if copyright is not None else f'© 2026 {self.my_company} Todos los derechos reservados'
        self.resolution: Vector2 = Vector2(resolution)
        self.min_resolution: Vector2 = Vector2(min_resolution)
        self.returncode: int = returncode if returncode is not None else 0
        self.max_fps: int = max_fps
        self.min_fps: int = min_fps
        self.screenshots_dir: Path = screenshot_dir if screenshot_dir is not None else platformdirs.user_pictures_path().joinpath(f'./{self.my_company}/{self.title}')
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        self.save_dir: Path = Path(save_dir) if save_dir is not None else platformdirs.user_config_path(self.title, self.my_company)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        self.fonts: dict[str, str] = fonts if fonts is not None else {}
        self.noframe: bool = noframe if noframe is not None else False
        self.icon: str|None = icon
        self.window_transparent: bool = window_transparent if window_transparent is not None else False

        for x in kwargs:
            setattr(self, x, kwargs[x])