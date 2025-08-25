from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import httpx
import json
import os
from bs4 import BeautifulSoup
from logger import logger
from config import yaml_config

load_dotenv()
logger.info("应用启动，加载环境变量")

mcp = FastMCP("docs")

USER_AGENT = "docs-app/1.0"
SERPER_URL="https://google.serper.dev/search"

docs_urls = {
    "langchain": "python.langchain.com/docs",
    "llama-index": "docs.llamaindex.ai/en/stable",
    "openai": "platform.openai.com/docs",
}

async def search_web(query: str) -> dict | None:
    payload = json.dumps({"q": query, "num": 2})
    logger.debug(f"搜索请求: {query}")

    headers = {
        "X-API-KEY": os.getenv("SERPER_API_KEY"),
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                SERPER_URL, headers=headers, data=payload, timeout=30.0
            )
            response.raise_for_status()
            logger.debug(f"搜索成功: {query}")
            return response.json()
        except httpx.TimeoutException:
            logger.warning(f"搜索超时: {query}")
            return {"organic": []}
        except Exception as e:
            logger.error(f"搜索错误: {str(e)}")
            return {"organic": []}
  
async def fetch_url(url: str):
    logger.debug(f"开始获取URL内容: {url}")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=30.0)
            soup = BeautifulSoup(response.text, "html.parser")
            text = soup.get_text()
            logger.debug(f"成功获取URL内容: {url}")
            return text
        except httpx.TimeoutException:
            logger.warning(f"获取URL内容超时: {url}")
            return "Timeout error"
        except Exception as e:
            logger.error(f"获取URL内容错误: {str(e)}")
            return f"Error: {str(e)}"

@mcp.tool()
async def get_docs(query: str, library: str):
    """
    搜索指定库的文档
    支持 langchain, openai 和 llama-index

    Args:
        query: 要搜索的查询 (如 "Chroma DB")
        library: 要搜索的库 (如 "langchain")

    Returns:
        文档内容文本
    """
    logger.info(f"开始文档搜索: 库={library}, 查询={query}")
    
    if library not in docs_urls:
        error_msg = f"不支持的库: {library}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    query = f"site:{docs_urls[library]} {query}"
    results = await search_web(query)
    
    if len(results["organic"]) == 0:
        logger.warning(f"未找到结果: 库={library}, 查询={query}")
        return "未找到结果"
    
    text = ""
    for result in results["organic"]:
        logger.debug(f"处理搜索结果: {result['link']}")
        text += await fetch_url(result["link"])
    
    logger.info(f"文档搜索完成: 库={library}, 查询={query}")
    return text


if __name__ == "__main__":
    # mcp.run(transport="stdio")
    print(yaml_config)
    mcp.settings.host = yaml_config['server']['host']
    mcp.settings.port = yaml_config['server']['port']
    # mcp.run(transport="streamable-http")
    mcp.run(transport="sse")
