import asyncio
import json
from config import config, logger
from time import perf_counter
from typing import Any, Dict, List, Optional, Type
from workers import DouchChef, Oven, ToppingChef, Waiter, Worker


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
        self.douch_chefs = config["DOUCH_CHEFS"]
        self.topping_chefs = config["TOPPING_CHEFS"]
        self.ovens = config["OVENS"]
        self.waiters = config["WAITERS"]
        self.orders: List[Order] = []
        self.tasks = []

    async def run(self):
        """
        The pizzeria runner function
        
        :return:
        """
        start = perf_counter()

        self.dough_queue = asyncio.Queue()
        self.topping_queue = asyncio.Queue()
        self.oven_queue = asyncio.Queue()
        self.waiter_queue = asyncio.Queue()

        with open("pizza_orders.json", "r") as f:
            task_data = json.load(f)

        self.generate_tasks(self.douch_chefs, DouchChef, self.dough_queue, self.topping_queue)
        self.generate_tasks(self.topping_chefs, ToppingChef, self.topping_queue, self.oven_queue)
        self.generate_tasks(self.ovens, Oven, self.oven_queue, self.waiter_queue)
        self.generate_tasks(self.waiters, Waiter, self.waiter_queue)

        for count, order_data in enumerate(task_data["Pizzas"]):
            order = Order(count, order_data)
            self.orders.append(order)
            await self.dough_queue.put(order)

        await self.dough_queue.join()
        await self.topping_queue.join()
        await self.oven_queue.join()
        await self.waiter_queue.join()

        for task in self.tasks:
            task.cancel()

        end = perf_counter()
        self.generate_report(end - start)

    def generate_tasks(
        self,
        workers_count: int,
        base_worker: Type[Worker],
        in_queue: asyncio.Queue,
        out_queue: Optional[asyncio.Queue] = None
    ) -> None:
        """
        Creates the asyncio task of the workers

        :param workers_count: number of workers to be created
        :param base_worker: the worker class sent to the function
        :param in_queue: the input queue from which the worker take its tasks
        :param out_queue: the output queue to which the worker puts its finished task
        :return:
        """
        for i in range(workers_count):
            worker = base_worker(i, in_queue, out_queue)
            self.tasks.append(asyncio.create_task(worker.job()))

    def generate_report(self, total_time: float) -> None:
        """
        Generate the orders report and prints summary.

        :param total_time: the total time all orders took, from first order to last order
        :return:
        """
        report: Dict[str, Any] = dict()
        report["Orders"] = {}
        all_orders = 0

        logger.info(f"\nREPORT:")
        logger.info(f"Total time: {int(total_time)}sec")
        logger.info("Preparation time for each order:")

        for order in self.orders:
            order_time = order.end_time - order.start_time
            order_key = f"Order {order.order_id + 1}"
            report["Orders"][order_key] = {
                "Start Time": order.start_time, "End Time": order.end_time, "Total Time": order_time
            }

            all_orders += order_time
            logger.info(f"Order {order.order_id + 1}: {int(order_time)}sec")

        # calculates the average order time
        average_time = int(all_orders / len(self.orders)) if len(self.orders) else 0
        logger.info(f"Average order time: {average_time}sec")

        report["TotalTime"] = int(total_time)
        report["AverageTime"] = average_time

        with open("report.json", "w") as f:
            json.dump(report, fp=f, indent=4)


def run() -> None:
    try:
        asyncio.run(Pizzeria().run())

    except Exception:
        logger.warning(f"Encountered error:", exc_info=True)
