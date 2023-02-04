from random import sample, randint
import json

TOPPING = [
    "Green olives",
    "Black olives",
    "Tomato",
    "Mushroom",
    "Onion",
    "Extra cheese",
    "Green pepper",
    "Fresh garlic",
    "Fresh basil",
    "Pepperoni",
    "Anchovy"
]


def generate_order():
    res = []
    num_of_orders = randint(5, 20)

    for _ in range(num_of_orders):
        order = sample(TOPPING, randint(0, len(TOPPING)))
        res.append({"Topping": order})

    final_order = {"Pizzas": res}

    with open("pizza_orders.json", "w") as f:
        json.dump(final_order, fp=f, indent=4)
