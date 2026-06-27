from math import comb, pi
from typing import Union, Tuple

from pygame.math import Vector2

class Simple_acceleration:
    def __init__(self,vel, dir,pos) -> None:
        self.vel: float = vel
        self.dir: Vector2 = Vector2(dir)
        self.pos = Vector2(pos)
    def update(self,dt=1) -> Vector2:
        self.pos += self.dir*self.vel*dt
        return self.pos
    def follow(self,pos,dt=1):
        self.dir = (Vector2(pos)-self.pos).normalize()
        self.pos += self.dir*self.vel*dt
        return self.pos


class Curva_de_Bezier:
    def __init__(self, timer, points, extra_time: int = 1) -> None:
        self.__T = 0
        self.timer = timer
        self.extra_time = extra_time
        self.points = [Vector2(ag) for ag in points]
        if len(self.points) < 2:
            raise ValueError('Debes dar 2 puntos o mas para logar la animacion deseada (Cubic Bezier)')

    def move(self, points) -> None:
        self.points = [Vector2(ag) for ag in points]

    def set(self,progress:float) -> None:
        ' - Define en que % de la animacion estara'
        self.__T = progress

    def update(self,dt=1) -> Vector2|bool:
        self.__T += (1/self.timer) * dt
        if self.__T > self.extra_time:
            self.__T = 1
            return True
        result = Vector2(0,0)
        for i,p in enumerate(self.points):
            coeff = comb(len(self.points)-1,i) * self.__T**i * (1-self.__T)**(len(self.points)-1-i)
            result += coeff * p
        return result

class Second_Order_Dinamics:
    """
    Sistema de dinámica de segundo orden para animaciones fluidas y realistas.
    
    Parámetros:
        f: Frecuencia (Hz) - Controla la velocidad de la animación
        z: Factor de amortiguamiento - Evita oscilaciones (0 < z < 1)
        r: Respuesta inicial - 0 para empezar suave, 1 para inicio instantáneo
        coord: Posición inicial (Tuple[float, float] o Vector2)
    """
    __slots__ = ('_pi', '_k1', '_k2', '_k3', 'xp', 'y', 'yd', '_dt_crit', '_last_time')
    
    def __init__(self, f: float, z: float, r: float, coord: Union[Tuple[float, float], Vector2]):
        # Constantes del sistema
        self._pi = pi
        self._k1 = z / (self._pi * f)
        self._k2 = 1 / ((2 * self._pi * f) ** 2)
        self._k3 = r * z / (2 * self._pi * f)

        # Estado inicial
        self.xp = Vector2(coord)
        self.y = Vector2(coord)
        self.yd = Vector2(0.0, 0.0)
        
        # Ajuste para paso de tiempo variable
        self._dt_crit = 0.05  # Paso crítico para estabilidad
        self._last_time = None

    def update(self, target: Union[Tuple[float, float], Vector2], dt: float= None) -> Vector2:
        """
        Actualiza el sistema dinámico usando integración estable de Verlet.
        
        Args:
            target: Posición objetivo actual
            dt: Tiempo delta desde la última actualización (en segundos)
            
        Returns:
            Vector2: Nueva posición suavizada
        """
        if dt is None:
            dt = 1.0 / 60.0  # Asume 60 FPS como caso base
        else:
            dt = min(dt, 0.05)  # Limita a 20 FPS mínimo para estabilidad
        # Manejo automático de dt para aplicaciones en tiempo real
        if dt > self._dt_crit:
            dt = self._dt_crit
        
        
        target_vec = Vector2(target)
        
        # Cálculo de velocidad objetivo si no se proporciona
        xd = (target_vec - self.xp) / dt
        self.xp = target_vec
        
        # Integración numérica estabilizada
        self.y = self.y + self.yd * dt
        self.yd = self.yd + (target_vec + xd * self._k3 - self.y - self.yd * self._k1) * (dt / self._k2)
        
        return self.y

    @property
    def position(self) -> Tuple[float, float]:
        return (self.y.x, self.y.y)