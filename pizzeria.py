import asyncio
from time import perf_counter
from typing import List, Dict
import json
import logging
import sys

logging.basicConfig(level=logging.INFO, format='%(message)s', stream=sys.stdout)
logger = logging.getLogger()
fileHandler = logging.FileHandler("outlog.log", mode='w')
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s')
fileHandler.setFormatter(formatter)
logger.addHandler(fileHandler)


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
        try:
            start = perf_counter()
            tasks = []
            self.dough_queue = asyncio.Queue(maxsize=50)
            self.topping_queue = asyncio.Queue(maxsize=50)
            self.oven_queue = asyncio.Queue(maxsize=50)
            self.waiter_queue = asyncio.Queue(maxsize=50)

            with open("pizza_orders.json", "r") as f:
                task_data = json.load(f)
            for count, order_data in enumerate(task_data["Pizzas"]):
                order = Order(count, order_data)
                self.orders.append(order)
                await self.dough_queue.put(order)

            [tasks.append(asyncio.create_task(self.dough_chef(i))) for i in range(self.douch_chefs)]
            # for i in range(self.douch_chefs):
            #     tasks.append(
            #         asyncio.create_task(self.dough_chef(i))
            #     )
            for i in range(self.topping_chefs):
                tasks.append(
                    asyncio.create_task(self.topping_chef(i))
                )
            for i in range(self.ovens):
                tasks.append(
                    asyncio.create_task(self.oven(i))
                )
            for i in range(self.waiters):
                tasks.append(
                    asyncio.create_task(self.waiter(i))
                )

            await self.dough_queue.join()
            await self.topping_queue.join()
            await self.oven_queue.join()
            await self.waiter_queue.join()

            for task in tasks:
                task.cancel()

            end = perf_counter()
            self.generate_report(start, end)
            self.report["TotalTime"] = end - start
            x = 1

        except Exception:
            logger.warning(f"Encountered error:", exc_info=True)

    def generate_report(self, start: float, end: float):
        total_time = 0
        logger.info(f"Total time: {int(end - start)}sec")
        logger.info("Preparation time for each order:")
        for order in self.orders:
            order_time = order.end_time - order.start_time
            total_time += order_time
            logger.info(f"Order {order.order_id + 1} took: {int(order_time)}sec")
        logger.info(f"Average order time: {int(total_time / len(self.orders))}sec")

    # async def create_tasks
    async def dough_chef(self, chef_id: int) -> None:
        while True:
            try:
                order_data = await self.dough_queue.get()
                order_id = order_data.order_id

                start = perf_counter()
                order_data.start_time = start
                logger.info(f"Dough chef #{chef_id} starting pizza #{order_id}, time = {start}")
                await asyncio.sleep(7)
                end = perf_counter()
                logger.info(f"Dough chef #{chef_id} finished pizza #{order_id}, time = {end}")

                await self.topping_queue.put(order_data)

                self.dough_queue.task_done()

            except Exception:
                logger.warning(f"Encountered error:", exc_info=True)
                self.dough_queue.task_done()

    async def topping_chef(self, chef_id: int) -> None:
        while True:
            try:
                # grab an item from the queue (if there is one)
                order_data = await self.topping_queue.get()

                # read the data we need to perform the work
                order_id: int = order_data.order_id
                topping: List[str] = order_data.topping

                # do some work that takes some time - simulated here with an async sleep
                start = perf_counter()
                print(f"Topping chef #{chef_id} starting pizza #{order_id}, time = {start}")

                while topping:
                    curr_topping = topping[:2]
                    topping = topping[2:]
                    print(
                        f"Topping chef #{chef_id} adding {curr_topping} to pizza #{order_id}, time = {perf_counter()}")
                    await asyncio.sleep(4)  # random wait time up to 2 seconds
                end = perf_counter()
                print(f"Topping chef #{chef_id} finished pizza #{order_id}, time = {perf_counter()}")

                await self.oven_queue.put(order_data)

                self.topping_queue.task_done()

            except Exception:
                logger.warning(f"Encountered error:", exc_info=True)
                self.topping_queue.task_done()

    async def oven(self, oven_id: int) -> None:
        while True:
            try:
                # grab an item from the queue (if there is one)
                order_data = await self.oven_queue.get()

                # read the data we need to perform the work
                order_id: int = order_data.order_id

                # do some work that takes some time - simulated here with an async sleep
                start = perf_counter()
                print(f"Oven #{oven_id} starting baking pizza #{order_id}, time = {start}")
                await asyncio.sleep(10)  # random wait time up to 2 seconds
                end = perf_counter()
                print(f"Oven #{oven_id} finished baking pizza #{order_id}, time = {end}")

                await self.waiter_queue.put(order_data)

                self.oven_queue.task_done()

            except Exception:
                logger.warning(f"Encountered error:", exc_info=True)
                self.oven_queue.task_done()

    async def waiter(self, waiter_id: int) -> None:
        while True:
            try:
                # grab an item from the queue (if there is one)
                order_data = await self.waiter_queue.get()

                # read the data we need to perform the work
                order_id = order_data.order_id

                # do some work that takes some time - simulated here with an async sleep
                start = perf_counter()
                print(f"Waiter #{waiter_id} starting serving pizza #{order_id}, time = {start}")
                await asyncio.sleep(5)  # random wait time up to 2 seconds
                end = perf_counter()
                print(f"Waiter #{waiter_id} finished serving pizza #{order_id}, time = {end}")
                order_data.end_time = end
                self.report[f"{order_id}"] = order_data.end_time - order_data.start_time

                self.waiter_queue.task_done()

            except Exception:
                logger.warning(f"Encountered error:", exc_info=True)
                self.waiter_queue.task_done()


def run():
    try:
        pizzeria = Pizzeria()
        asyncio.run(pizzeria.run())
    except:
        print("Problem found!!")
