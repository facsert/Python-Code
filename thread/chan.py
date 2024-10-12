from time import sleep, time
from datetime import datetime
from threading import Thread

from loguru import logger

class Chan:
    """ 单个线程 """

    def __init__(self,
        func: callable,
        params: dict|None=None,
        count: int=1,
        timeout: int=0,
        interval: int=0,
    ) -> None:
        self.timeout: int|float = timeout if timeout > 0 else float('inf')
        self.count: int|float = int(count) if count > 0 else float('inf')
        self.interval: int = interval

        self.func: callable = func
        self.params: dict = params if params else {}

        self._running: bool = True

        self.output: dict[datetime, any] = {}
        self.thread: Thread = Thread(target=self.function, daemon=True)
        self.pid: int = self.thread.native_id
        self.alive: bool = self.thread.is_alive()

    def function(self) -> None:
        """ 线程执行函数 """
        if self._running is False:
            raise RuntimeError("Thread has already been started")

        index, timeout = 0, time() + self.timeout
        while True:
            if not self._running:
                break

            self.output.update({datetime.now(): self.func(**(self.params))})
            sleep(self.interval)
            index += 1

            if (index >= self.count or time() > timeout):
                self._running = False
                break

        self.alive = False

    def run(self) -> int:
        """ 执行线程 """
        self.thread.start()
        self.pid = self.thread.native_id
        self.alive = self.thread.is_alive()
        return self.pid

    def wait(self, timeout=None) -> dict[datetime, any]:
        """ 等待线程结束 """
        self.thread.join(timeout)
        self.alive = self.thread.is_alive()
        return self.output

    def stop(self) -> bool:
        """ 停止线程 """
        self._running = False
        self.alive = self.thread.is_alive()
        return self.alive is False

def chaner(chans: list[Chan], size: int=5, interval: float=0.1) -> list[Chan]:
    """ 线程池执行池
        chans list[Chan]: 线程列表
        size int: 线程池最大数量
        interval float: 轮询间隔时间
    """
    if not isinstance(size, int) or size <= 0:
        raise ValueError("size must be int and bigger than 0")

    group: list[Chan] = []
    pool: list[Chan] = []
    chans = chans[::-1]
    
    while len(pool) < size and chans:
        chan = chans.pop()
        chan.run()
        pool.append(chan)
    
    while pool:
        for index, chan in enumerate(pool):
            if chan.alive:
                continue
            
            group.append(pool.pop(index))
            if chans:
                ch = chans.pop()
                ch.run()
                pool.append(ch)
        
        sleep(interval)
    
    return group

if __name__ == '__main__':
    def wait(second: int):
        logger.info(f"wait {second} second")
        sleep(second)
        return second

    c1 = Chan(func=wait, params={'second': 3}, count=2, timeout=6, interval=1)
    c2 = Chan(func=wait, params={'second': 2}, count=2, interval=1)

    chaner([c1, c2], 2, 0.1)
    logger.info(f"{c1.output=}, {c1.alive=}, {c1.pid=}")
    logger.info(f"{c2.output=}, {c2.alive=}, {c2.pid=}")
    logger.info("finish")
