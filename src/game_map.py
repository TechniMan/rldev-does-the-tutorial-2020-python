from __future__ import annotations

from typing import Iterable, Iterator, List, Optional, TYPE_CHECKING
import numpy # type: ignore
from tcod.console import Console

from entity import Actor, Item
import tile_types

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity


class GameMap:
    def __init__(self,
            engine: Engine,
            width: int,
            height: int,
            entities: Iterable[Entity] = ()
        ):
        self.engine = engine
        self.width, self.height = width, height
        self.entities = set(entities)
        self.tiles = numpy.full((width, height), fill_value=tile_types.wall, order="F")
        self.visible = numpy.full(
            (width, height), fill_value=False, order="F"
        )
        self.explored = numpy.full(
            (width, height), False, order="F"
        )

    def in_bounds(self, x: int, y: int) -> bool:
        """ Returns True if x and y are inside of the bounds of this map """
        return 0 <= x < self.width and 0 <= y < self.height

    @property
    def gamemap(self) -> GameMap:
        return self

    @property
    def actors(self) -> Iterator[Actor]:
        """ Iterate over the living actors in the map """
        yield from (
            entity
            for entity in self.entities
            if isinstance(entity, Actor) and entity.is_alive
        )

    def get_actor_at_location(self, x: int, y: int) -> Optional[Actor]:
        for actor in self.actors:
            if actor.x == x and actor.y == y:
                # we've found the actor at this space; are they alive?
                if actor.is_alive:
                    return actor
                return None
        return None

    @property
    def items(self) -> Iterator[Item]:
        """ Iterate over the items in the map """
        yield from (entity for entity in self.entities if isinstance(entity, Item))

    def get_items_at_location(self, x: int, y: int) -> List[Item]:
        """ Returns a list of all items the exist at the given location """
        results: List[Item] = []
        for item in self.items:
            if item.x == x and item.y == y:
                results.append(item)
        return results

    def get_blocking_entity_at_location(self,
            location_x: int,
            location_y: int
        ) -> Optional[Entity]:
        for entity in self.entities:
            # if this entity blocks movement and is in the given location
            if entity.blocks_movement and entity.x == location_x and entity.y == location_y:
                return entity
        # if none found, return None
        return None

    def render(self, console: Console) -> None:
        """
        Renders the map.
        Visible tiles are drawn with their "lit" colour.
        Explored tiles are drawn with their "unlit" colour.
        Other tiles are drawn as FOG.
        """
        # pass the map tile colours to the console
        console.tiles_rgb[0:self.width, 0:self.height] = numpy.select(
            [self.visible, self.explored],
            [self.tiles["lit"], self.tiles["unlit"]],
            tile_types.FOG
        )

        entities_sorted_for_rendering = sorted(self.entities, key=lambda x: x.render_order.value)

        # render entities to the console, on top of the map
        for entity in entities_sorted_for_rendering:
            # only print visible entities
            if self.visible[entity.x, entity.y]:
                console.print(entity.x, entity.y, entity.char, fg=entity.colour)
