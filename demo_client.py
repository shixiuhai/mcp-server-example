from fastmcp import Client
import asyncio

async def test_demo():
    async with Client("http://127.0.0.1:8009/sse") as client:
        # 列出工具
        tools = await client.list_tools()
        print("工具列表:", tools)
        
        # 调用示例工具
        if "hello_world" in tools:
            result = await client.call("hello_world")
            print("调用结果:", result)

asyncio.run(test_demo())

