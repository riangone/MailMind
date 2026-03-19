"""
MCP Weather Tool — 天气查询工具

配置（.env）：
  MCP_SERVERS=weather
  MCP_SERVER_WEATHER=python -m ai.mcp_weather_server
  WEATHER_API_KEY=xxx

使用方式：
  邮件中调用：{"task_type": "mcp_call", "task_payload": {"server": "weather", "tool": "get_weather", "args": {"location": "Tokyo"}}}
"""

import json
import sys
import requests
import os
from typing import Optional

WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY", "")
WEATHER_DEFAULT_LOCATION = os.environ.get("WEATHER_DEFAULT_LOCATION", "Beijing")


def get_weather(location: str = None) -> dict:
    """获取指定地区的天气信息"""
    location = location or WEATHER_DEFAULT_LOCATION
    if not WEATHER_API_KEY:
        return {"error": "WEATHER_API_KEY 未配置"}

    try:
        resp = requests.get(
            "https://api.weatherapi.com/v1/current.json",
            params={"key": WEATHER_API_KEY, "q": location, "lang": "zh"},
            timeout=10,
        )
        resp.raise_for_status()
        d = resp.json()
        loc = d["location"]
        cur = d["current"]
        return {
            "location": loc["name"],
            "country": loc["country"],
            "localtime": loc["localtime"],
            "condition": cur["condition"]["text"],
            "temp_c": cur["temp_c"],
            "feelslike_c": cur["feelslike_c"],
            "humidity": cur["humidity"],
            "wind_kph": cur["wind_kph"],
            "wind_dir": cur["wind_dir"],
            "vis_km": cur["vis_km"],
        }
    except Exception as e:
        return {"error": str(e)}


# MCP 工具定义
TOOLS = [
    {
        "name": "get_weather",
        "description": "获取指定地区的实时天气信息",
        "inputSchema": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "城市名称或地区，例如 'Tokyo', 'Beijing', 'New York'",
                }
            },
            "required": [],
        },
    }
]


def handle_tool_call(tool_name: str, args: dict) -> str:
    """处理 MCP 工具调用"""
    if tool_name == "get_weather":
        result = get_weather(args.get("location"))
        return json.dumps(result, ensure_ascii=False)
    else:
        return json.dumps({"error": f"未知工具：{tool_name}"}, ensure_ascii=False)


# MCP 服务器主循环（stdio 传输）
def main():
    """MCP 服务器入口"""
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            msg = json.loads(line.strip())
            method = msg.get("method")
            msg_id = msg.get("id")

            if method == "initialize":
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "weather", "version": "1.0"},
                    },
                }
            elif method == "tools/list":
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {"tools": TOOLS},
                }
            elif method == "tools/call":
                tool_name = msg.get("params", {}).get("name")
                args = msg.get("params", {}).get("arguments", {})
                result = handle_tool_call(tool_name, args)
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [{"type": "text", "text": result}]
                    },
                }
            elif method == "notifications/initialized":
                continue  # 无需响应
            else:
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {"code": -32601, "message": f"未知方法：{method}"},
                }

            sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
            sys.stdout.flush()

        except json.JSONDecodeError:
            continue
        except Exception as e:
            resp = {
                "jsonrpc": "2.0",
                "id": msg_id if "msg_id" in dir() else None,
                "error": {"code": -32603, "message": str(e)},
            }
            sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
