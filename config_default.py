import platformdirs

class Config:
    def __init__(self):
        self.window_resize = True
        self.scaled = False

        self.title: str = 'Programa_ejemplo'
        self.my_company = 'Mi compañia'
        self.author: str = 'Edouard Sandoval'
        self.version: str = '0.0.1'
        self.description: str = 'Ejemplo de programa para empezar con una idea'
        self.copyright: str = '2025 Edouard Sandoval'
        self.resolution = [800, 550]
        self.min_resolution = [550,450]
        self.returncode = 0
        self.max_fps = 60
        self.screenshots_dir = platformdirs.user_pictures_path().joinpath(f'./{self.my_company}/{self.title}')
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)

        # self.font_mononoki: str = 'C:/Users/Edouard/Documents/fuentes/mononoki Bold Nerd Font Complete Mono.ttf'
        # self.font_simbolos: str = 'C:/Users/Edouard/Documents/fuentes/Symbols.ttf'

        self.save_dir = platformdirs.user_config_path(self.title, self.my_company)
        self.save_dir.mkdir(parents=True, exist_ok=True)