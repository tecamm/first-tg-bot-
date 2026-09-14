"""import time
import asyncio
import requests
import aiohttp
import aiosqlite


async def task_1():
    print("Task 1 start")
    await asyncio.sleep(2)
    print("Task 1 end")

async  def task_2():
    print("Task 2 start")
    await asyncio.sleep(2)
    print("Task 2 end")

async  def main():

    start = time.time()
    t1 = asyncio.create_task(task_1())
    t2 = asyncio.create_task(task_2())
    await t1
    await t2
    end = time.time()

    print(f'Время выполнения: {end - start:.2f} сек')
asyncio.run(main())"""


"""async def tasks(task, delay):
    print(f'{task} старт')
    await asyncio.sleep(delay)
    print(f'{task} конец')

async def main():
    start = time.time()
    await asyncio.gather(
        tasks('Задача 1', 2),
        tasks('Задача 2', 4),
        tasks('Задача 3', 1),
        tasks('Задача 4', 5),
        tasks('Задача 5', 2),
        tasks('Задача 6', 3),

    )
    end = time.time()

    print(f'Время выполнения: {end - start:.2f} сек')

asyncio.run(main())

semaphore = asyncio.Semaphore(5)

async def fetch_data(url, session):
    try:
        async with semaphore:
            async with session.get(url) as result:
                if result.status != 200:
                    return None
                return await result.json()
    except Exception as e:
        print(f"Error: {e}")
        return None

async def main():
    urls = ['https://jsonplaceholder.typicode.com/posts/1'] * 100

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_data(url,session) for url in urls]
        response = await asyncio.gather(*tasks)
        print(len(response))
asyncio.run(main())"""