class Item:

    def __init__(self, name: str, quantity: int):
        self.item_name = name
        self.quantity = quantity

    def get_name(self):
        return self.item_name

    def get_quantity(self):
        return self.quantity

    def set_quantity(self, quantity: int):
        self.quantity = quantity

    def to_string(self):
        return str(self.quantity) +" "+ self.item_name



class Recipe:
    def __init__(self, name: str, result: Item, items: [Item]):
        self.name = name
        self.result = result
        self.items = items
        self.requirements_strings = []

    def get_result(self) -> Item:
        return self.result

    def get_recipe_name(self) -> str:
        return self.name

    def get_requirements(self) -> [Item]:
        return self.items

    def get_requirement_names(self) -> [str]:
        if not self.requirements_strings: # if the list is empty
            for i in self.items:
                 self.requirements_strings.append(i.get_name())

        return self.requirements_strings




    def to_string(self) -> str:
        string = ""

        length: int = len(self.items)
        counter: int = 0

        for i in self.items:

            counter = counter + 1
            if counter < length:
                string = string + i.to_string() + ", "
            else:
                string = string + i.to_string()

        return self.name +": "+ string + " -> " + self.result.to_string()




