import os
from pathlib import Path
import requests
import time
import argparse
import threading
from multiprocessing import Process
import asyncio
import aiohttp

PATH = Path('images')


def download_img(url, dir_path=PATH):
    start_time = time.time()
    response = requests.get(url)
    filename = url.split('/')[-1]
    with open(os.path.join(dir_path, filename), 'wb') as f:
        for data in response.iter_content(1024):
            f.write(data)
    end_time = time.time() - start_time
    print(f'Загрузка {filename} заняла {end_time:.2f} сек')


def parse():
    parser = argparse.ArgumentParser(description='Парсер изображений по URL-адресам')
    parser.add_argument('-u', '--urls', nargs='+', type=str, help='Список URL-адресов')
    parser.add_argument('-f', '--file', type=str, default='images.txt',
                        help='Путь к файлу со списком URL-адресов (по умолчанию images.txt)')
    return parser.parse_args()


async def download_img_as(url, dir_path=PATH):
    start_time = time.time()
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            item = await response.read()
            filename = url.split('/')[-1]
            with open(os.path.join(dir_path, filename), 'wb') as f:
                f.write(item)
    end_time = time.time() - start_time
    print(f'Загрузка {filename} заняла {end_time:.2f} сек')


def download_img_thread(urls):
    threads = []
    start_time = time.time()

    for url in urls:
        thread = threading.Thread(target=download_img, args=(url,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    end_time = time.time() - start_time
    print(f'Многопоточная загрузка заняла {end_time:.2f} сек')


def download_img_process(urls):
    processes = []
    start_time = time.time()

    for url in urls:
        process = Process(target=download_img, args=(url,))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    end_time = time.time() - start_time
    print(f'Многопроцессорная загрузка заняла {end_time:.2f} сек')


async def download_img_async(urls):
    tasks = []
    start_time = time.time()

    for url in urls:
        task = asyncio.create_task(download_img_as(url))
        tasks.append(task)

    await asyncio.gather(*tasks)

    end_time = time.time() - start_time
    print(f'Асинхронная загрузка заняла {end_time:.2f} сек')


if __name__ == '__main__':
    args = parse()
    urls = args.urls

    if not urls:  # Если URL не переданы, читаем из файла
        with open(args.file, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]

    if not os.path.exists(PATH):
        os.mkdir(PATH)

    print(f'Загрузка {len(urls)} изображений через многопоточный подход')
    download_img_thread(urls)

    print(f'Загрузка {len(urls)} изображений через многопроцессорный подход')
    download_img_process(urls)

    print(f'Загрузка {len(urls)} изображений асинхронным подходом')
    asyncio.run(download_img_async(urls))
