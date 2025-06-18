import platformdirs
from Utilidades.maths import Vector2
from pathlib import Path

class Config:
    def __init__(
            self, window_resize: bool=None, scaled: bool=None, title: str=None, window_title: str=None, my_company: str=None, 
            author: str=None, version: str=None, description: str=None, copyright: str=None, resolution: Vector2=None, 
            min_resolution: Vector2=None, returncode: int=None, max_fps: int=None, min_fps: int=None, screenshot_dir=None, 
            save_dir: Path|None=None, icon: str=None, fonts: dict[str, str] | None = None, noframe: bool=None, **kwargs
            ):
        self.window_resize = window_resize if window_resize is not None else True
        self.scaled = scaled if scaled is not None else False
        
        self.title: str = title if title is not None else 'Programa_ejemplo'
        self.window_title: str = window_title if window_title is not None else 'Programa ejemplo'
        self.my_company: str = my_company if my_company is not None else 'Mi compañia'
        self.author: str = author if author is not None else 'Alguien nose'
        self.version: str = version if version is not None else '0.1'
        self.description: str = description if description is not None else 'Ejemplo de programa para empezar con una idea'
        self.copyright: str = copyright if copyright is not None else f'© 2025 {self.my_company} Todos los derechos reservados'
        self.resolution: Vector2 = resolution if resolution is not None else Vector2(800, 550)
        self.min_resolution: Vector2 = min_resolution if min_resolution is not None else Vector2(800//2,600//2)
        self.returncode: int = returncode if returncode is not None else 0
        self.max_fps: int = max_fps if max_fps is not None else 60
        self.min_fps: int = min_fps if min_fps is not None else 60
        self.screenshots_dir: Path = screenshot_dir if screenshot_dir is not None else platformdirs.user_pictures_path().joinpath(f'./{self.my_company}/{self.title}')
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        self.save_dir: Path = Path(save_dir) if save_dir is not None else platformdirs.user_config_path(self.title, self.my_company)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        self.fonts: dict[str, str] = fonts if fonts is not None else {}
        self.noframe: bool = noframe if noframe is not None else False
        self.icon: str|None = icon

        for x in kwargs:
            setattr(self, x, kwargs[x])