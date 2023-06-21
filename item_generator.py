
from items import Item, Recipe

def to_pos_int(value: str) -> int|None:
    try:
        casted = int(value)
        if casted <= 0:
            return None

        return casted

    except ValueError:
        return None


def parse_item(item: str) -> Item:
    values = item.split("-")
    length = len(values)

    if length == 2:

        number = to_pos_int(values[1])
        if number is None:
            raise ValueError("Item format is invalid!")

        return Item(values[0], number)
    elif length == 1:
        return Item(values[0],1)

    raise ValueError("Item format is invalid!")

def parse_items(arr: [str]) -> [Item]:
    items = []
    for i in arr:
        item:Item = parse_item(i)
        items.append(item)
    return items


def parse_recipe(name: str, arr: [str], result: str) -> Recipe:
    items = parse_items(arr)
    result = parse_item(result)
    return Recipe(name, result, items)