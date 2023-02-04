import asyncio
from time import perf_counter
from typing import List, Dict
import json
from logger_config import logger
from workers import DouchChef, ToppingChef, Oven, Waiter


class Order:
    start_time: float
    end_time: float

    def __init__(self, order_id: int, order_data: Dict[str, List[str]]):
        self.order_id: int = order_id
        self.topping: List[str] = order_data["Topping"]


class Pizzeria:
    dough_queue: asyncio.Queue
    topping_queue: asyncio.Queue
    oven_queue: asyncio.Queue
    waiter_queue: asyncio.Queue

    def __init__(self):
        self.douch_chefs = 2
        self.topping_chefs = 3
        self.ovens = 1
        self.waiters = 2
        self.orders: List[Order] = []
        self.report = {}

    async def run(self):
        start = perf_counter()
        tasks = []

        self.dough_queue = asyncio.Queue(maxsize=50)
        self.topping_queue = asyncio.Queue(maxsize=50)
        self.oven_queue = asyncio.Queue(maxsize=50)
        self.waiter_queue = asyncio.Queue(maxsize=50)

        with open("pizza_orders.json", "r") as f:
            task_data = json.load(f)

        for i in range(self.douch_chefs):
            worker = DouchChef(i, self.dough_queue, self.topping_queue)
            tasks.append(asyncio.create_task(worker.job()))

        for i in range(self.topping_chefs):
            worker = ToppingChef(i, self.topping_queue, self.oven_queue)
            tasks.append(asyncio.create_task(worker.job()))

        for i in range(self.ovens):
            worker = Oven(i, self.oven_queue, self.waiter_queue)
            tasks.append(asyncio.create_task(worker.job()))

        for i in range(self.waiters):
            worker = Waiter(i, self.waiter_queue)
            tasks.append(asyncio.create_task(worker.job()))

        for count, order_data in enumerate(task_data["Pizzas"]):
            order = Order(count, order_data)
            self.orders.append(order)
            await self.dough_queue.put(order)

        await self.dough_queue.join()
        await self.topping_queue.join()
        await self.oven_queue.join()
        await self.waiter_queue.join()

        for task in tasks:
            task.cancel()

        end = perf_counter()
        self.generate_report(start, end)
        self.report["TotalTime"] = end - start

    def generate_report(self, start: float, end: float):
        total_time = 0
        logger.info(f"Total time: {int(end - start)}sec")
        logger.info("Preparation time for each order:")
        for order in self.orders:
            order_time = order.end_time - order.start_time
            total_time += order_time
            logger.info(f"Order {order.order_id + 1} took: {int(order_time)}sec")
        logger.info(f"Average order time: {int(total_time / len(self.orders))}sec")


def run():
    try:
        pizzeria = Pizzeria()
        asyncio.run(pizzeria.run())
    except Exception:
        logger.warning(f"Encountered error:", exc_info=True)
