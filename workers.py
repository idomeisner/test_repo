import asyncio
from abc import ABC, abstractmethod
from time import perf_counter
from logger_config import logger
from typing import List, Optional


class Worker(ABC):
    def __init__(self, idx: int, in_queue: asyncio.Queue, out_queue: Optional[asyncio.Queue] = None):
        self.idx = idx
        self.in_queue = in_queue
        self.out_queue = out_queue

    @abstractmethod
    async def job(self):
        pass


class DouchChef(Worker):
    def __init__(self, *args):
        super().__init__(*args)

    async def job(self):
        while True:
            try:
                order_data = await self.in_queue.get()
                order_id = order_data.order_id

                start = perf_counter()
                order_data.start_time = start
                logger.info(f"Dough chef #{self.idx} starting pizza #{order_id}, time = {start}")
                await asyncio.sleep(7)
                logger.info(f"Dough chef #{self.idx} finished pizza #{order_id}, time = {perf_counter()}")

                await self.out_queue.put(order_data)
                self.in_queue.task_done()

            except Exception:
                logger.warning(f"Encountered error:", exc_info=True)
                self.in_queue.task_done()


class ToppingChef(Worker):
    def __init__(self, *args):
        super().__init__(*args)

    async def job(self):
        while True:
            try:
                # grab an item from the queue (if there is one)
                order_data = await self.in_queue.get()

                # read the data we need to perform the work
                order_id: int = order_data.order_id
                topping: List[str] = order_data.topping

                # do some work that takes some time - simulated here with an async sleep
                logger.info(f"Topping chef #{self.idx} starting pizza #{order_id}, time = {perf_counter()}")

                while topping:
                    curr_topping = topping[:2]
                    topping = topping[2:]
                    logger.info(
                        f"Topping chef #{self.idx} adding {curr_topping} to pizza #{order_id}, time = {perf_counter()}")
                    await asyncio.sleep(4)  # random wait time up to 2 seconds

                logger.info(f"Topping chef #{self.idx} finished pizza #{order_id}, time = {perf_counter()}")

                await self.out_queue.put(order_data)

                self.in_queue.task_done()

            except Exception:
                logger.warning(f"Encountered error:", exc_info=True)
                self.in_queue.task_done()


class Oven(Worker):
    def __init__(self, *args):
        super().__init__(*args)

    async def job(self):
        while True:
            try:
                # grab an item from the queue (if there is one)
                order_data = await self.in_queue.get()

                # read the data we need to perform the work
                order_id: int = order_data.order_id

                # do some work that takes some time - simulated here with an async sleep
                logger.info(f"Oven #{self.idx} start baking pizza #{order_id}, time = {perf_counter()}")
                await asyncio.sleep(10)  # random wait time up to 2 seconds
                logger.info(f"Oven #{self.idx} finished baking pizza #{order_id}, time = {perf_counter()}")

                await self.out_queue.put(order_data)
                self.in_queue.task_done()

            except Exception:
                logger.warning(f"Encountered error:", exc_info=True)
                self.in_queue.task_done()


class Waiter(Worker):
    def __init__(self, *args):
        super().__init__(*args)

    async def job(self):
        while True:
            try:
                # grab an item from the queue (if there is one)
                order_data = await self.in_queue.get()

                # read the data we need to perform the work
                order_id = order_data.order_id

                # do some work that takes some time - simulated here with an async sleep
                logger.info(f"Waiter #{self.idx} start serving pizza #{order_id}, time = {perf_counter()}")
                await asyncio.sleep(5)  # random wait time up to 2 seconds
                end = perf_counter()
                logger.info(f"Waiter #{self.idx} finished serving pizza #{order_id}, time = {end}")
                order_data.end_time = end
                # self.report[f"{order_id}"] = order_data.end_time - order_data.start_time

                # await self.out_queue.put(order_data)
                self.in_queue.task_done()

            except Exception:
                logger.warning(f"Encountered error:", exc_info=True)
                self.in_queue.task_done()
