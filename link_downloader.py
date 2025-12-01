import aiohttp
import asyncio
import os


async def download_file_with_progress(url: str, dest_path: str):
    """
    Универсальная скачка файлов.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            resp.raise_for_status()

            with open(dest_path, "wb") as f:
                async for chunk in resp.content.iter_chunked(1024 * 64):
                    f.write(chunk)

    return dest_path
