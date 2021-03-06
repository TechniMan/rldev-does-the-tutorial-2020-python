from __future__ import annotations

import copy
import math
from typing import Optional, Tuple, Type, TypeVar, TYPE_CHECKING, Union

import colours
from render_order import RenderOrder

if TYPE_CHECKING:
    from components.ai import BaseAI
    from components.consumable import Consumable
    from components.fighter import Fighter
    from components.inventory import Inventory
    from game_map import GameMap

T = TypeVar("T", bound="Entity")


class Entity:
    """
    A generic object to represent players, enemies, items, etc.
    """

    parent: Union[GameMap, Inventory]

    def __init__(
        self,
        name: str,
        char: str,
        colour: Tuple[int, int, int],
        x: int = 0,
        y: int = 0,
        blocks_movement: bool = False,
        parent: Optional[GameMap] = None,
        render_order: RenderOrder = RenderOrder.CORPSE
    ):
        self.name = name
        self.char = char
        self.colour = colour
        self.x = x
        self.y = y
        self.blocks_movement = blocks_movement
        self.render_order = render_order
        # if gamemap isn't provided now, then it will be set later
        if parent:
            self.parent = parent
            parent.entities.add(self)

    @property
    def gamemap(self) -> GameMap:
        return self.parent.gamemap

    def spawn(self: T, gamemap: GameMap, x: int, y: int) -> T:
        """ Spawn a copy of this instance at the given location """
        clone = copy.deepcopy(self)
        clone.x = x
        clone.y = y
        clone.parent = gamemap
        gamemap.entities.add(clone)
        return clone

    def place(self, x: int, y: int, gamemap: Optional[GameMap] = None) -> None:
        """ Place this entity at a new location. Handles movement across game maps. """
        self.x = x
        self.y = y
        if gamemap:
            if hasattr(self, "parent"):
                if self.parent is self.gamemap:
                    self.gamemap.entities.remove(self)
            self.parent = gamemap
            gamemap.entities.add(self)

    def distance(self, x: int, y: int) -> float:
        """ Returns the distance between the current entity and the given point """
        # sqrt(a^2 + b^2) = c
        return math.sqrt((x - self.x)**2 + (y - self.y)**2)

    def move(self, dx: int, dy: int) -> None:
        # Move the entity by a given amount
        self.x += dx
        self.y += dy


class Actor(Entity):
    def __init__(self,
        *,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        colour: Tuple[int, int, int] = colours.DEFAULT,
        name: str = "<Unnamed>",
        ai_cls: Type[BaseAI],
        fighter: Fighter,
        inventory: Inventory
    ):
        super().__init__(
            x = x,
            y = y,
            char = char,
            colour = colour,
            name = name,
            blocks_movement = True,
            render_order = RenderOrder.ACTOR
        )
        self.ai: Optional[BaseAI] = ai_cls(self)
        self.fighter = fighter
        self.fighter.parent = self
        self.inventory = inventory
        self.inventory.parent = self

    @property
    def is_alive(self) -> bool:
        return bool(self.ai)


class Item(Entity):
    def __init__(self, *,
            x: int = 0, y: int = 0, char: str = "?", colour = colours.DEFAULT,
            name: str = "<Unnamed>", consumable: Consumable):
        super().__init__(name, char, colour, x, y, False, render_order = RenderOrder.ITEM)

        self.consumable = consumable
        self.consumable.parent = self
