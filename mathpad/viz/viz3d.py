"3d visualization module using k3d. Good for 3d plots and animations. Use viz2d module for 2d plotting"

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Iterable, Literal, Sequence, TypedDict, Union, Generic, TypeVar

import k3d
import k3d.objects as k3do
import numpy as np

from mathpad.core import R2, R3, t, Vector, Val, Num

K3DDrawable = TypeVar("K3DDrawable", bound=k3do.Drawable)

# define commmon hex colors for ease of use
# BLUE = 0x0000FF
# ORANGE = 0xFF9900
# BLACK = 0x000000
# RED = 
# GREEN = 0x00FF00
# CYAN = 0x00FFFF
# MAGENTA = 0xFF00FF
# WHITE = 0xFFFFFF
# YELLOW = 0xFFFF00


ColorChar = Literal['r', 'g', 'b', 'c', 'm', 'y', 'k', 'w', 'o']

class _Colors(Dict[ColorChar, int]):
    r: Literal[0x0000FF] = 0x0000FF
    g: Literal[0x00FF00] = 0x00FF00
    b: Literal[0xFF0000] = 0xFF0000
    c: Literal[0x00FFFF] = 0x00FFFF
    m: Literal[0xFF00FF] = 0xFF00FF
    y: Literal[0xFFFF00] = 0xFFFF00
    k: Literal[0x000000] = 0x000000
    w: Literal[0xFFFFFF] = 0xFFFFFF
    o: Literal[0xFF9900] = 0xFF9900

colors = _Colors()

class Viz3D(ABC, Generic[K3DDrawable]):

    State = Dict[Union[Val, Vector], np.ndarray]

    def __init__(self, vals: "set[Union[Val, Vector]]", color: "int | ColorChar", **k3d_kwargs: Any):
        self.vals = vals
        self.k3d_kwargs = k3d_kwargs
        self.drawable: "K3DDrawable | None" = None
        k3d_kwargs['color'] = colors[color] if isinstance(color, str) else color


    @abstractmethod
    def create(self, init_state: State) -> K3DDrawable:
        "Create a k3d drawable object to add to the viz3d scene"
        ...
    
    @abstractmethod
    def update(self, state: State):
        "Update the k3d drawable object to reflect new state"
        ...


# R = TypeVar("R", bound=Union[R2, R3])


class Text(Viz3D[k3do.Text]):

    def __init__(
        self,
        get_text: Callable[[Viz3D.State], str],
        position: Vector[R3],
        color: "int | ColorChar" = BLACK,
        label_box: bool = True,
        is_html: bool = False
    ):
        super().__init__(set(position), color=color, is_html=is_html, label_box=label_box)

        self.get_text = get_text
        self.position = position
    
    def create(self, init_state):
        self.drawable = k3d.text(
            text=self.get_text(init_state),
            position=init_state[self.position],
            **self.k3d_kwargs
        )
        return self.drawable
    
    def update(self, state):
        assert (d := self.drawable)
        d.text = self.get_text(state)
        d.position = state[self.position]
        

class ScreenText(Viz3D):

    def __init__(
        self,
        get_text: Callable[[Viz3D.State], str],
        position: "tuple[int, int]",
        color: "int | ColorChar" = BLACK,
        is_html: bool = False
    ):
        for p in position:
            assert 0 <= p <= 1, f"ScreenText position values must be between 0 and 1. got {p}"
        super().__init__(set(), position=position, color=color, is_html=is_html)

        self.get_text = get_text
    
    def create(self, init_state):
        self.drawable = k3d.text2d(
            self.get_text(init_state),
            **self.k3d_kwargs
        )
        return self.drawable
    
    def update(self, state):
        assert (d := self.drawable)
        d.text = self.get_text(state)

class Point(Viz3D[k3do.Points]):

    def __init__(self, position: Vector[R3], color: "int | ColorChar", point_size: float):
        assert point_size >= 0
        super().__init__({position}, color=color, point_size=point_size)
        self.position = position
    

    def create(self, init_state):
        # TODO merge multiple points into 1 call for performance?
        return k3d.points(
            [init_state[self.position]],
            **self.k3d_kwargs
        )

    def update(self, state):
        assert (d := self.drawable)
        d.positions = [state[self.position]]


class VectorViz(Viz3D[k3do.Vectors]):

    def __init__(self, origin: Vector[R3], end: Vector[R3], *, color: "int | ColorChar", head_size: float = 0.5):
        assert 0 <= head_size <= 1
        assert isinstance(origin.space, (R2, R3))
        assert isinstance(end.space, (R2, R3))

        self.origin = origin
        self.displacement = end - origin

        super().__init__(
            {origin, self.displacement},
            color=color,
            head_size=head_size
        )

    def create(self, init_state):
        
        # TODO merge multiple vectors into 1 call for performance?
        self.drawable = k3d.vectors(
            origins=[init_state[self.origin]],
            vectors=[init_state[self.displacement]],
            **self.k3d_kwargs
        )
        return self.drawable


    def update(self, state):
        assert (d := self.drawable)
        d.origins = [state[self.origin]]
        d.vectors = [state[self.displacement]]