"""LLM 客户端封装(OpenAI 兼容协议,支持 DeepSeek/通义千问/OpenAI)"""
import json
import re
from typing import Optional
from flask import current_app


class LLMClient:
    """统一封装 LLM 调用,支持 OpenAI 兼容协议"""

    def __init__(self):
        # 延迟初始化,避免循环导入
        self._client = None

    @property
    def client(self):
        if self._client is None:
            from openai import OpenAI
            self._client = OpenAI(
                api_key=current_app.config["LLM_API_KEY"],
                base_url=current_app.config["LLM_BASE_URL"],
            )
        return self._client

    def chat(self, system_prompt: str, user_prompt: str, temperature: Optional[float] = None) -> str:
        """调用 LLM,返回文本响应"""
        resp = self.client.chat.completions.create(
            model=current_app.config["LLM_MODEL"],
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature if temperature is not None else current_app.config["LLM_TEMPERATURE"],
            max_tokens=current_app.config["LLM_MAX_TOKENS"],
            # 关键:强制 JSON 输出
            response_format={"type": "json_object"},
        )
        return resp.choices[0].message.content

    def chat_json(self, system_prompt: str, user_prompt: str, temperature: Optional[float] = None) -> dict:
        """调用 LLM 并解析为 JSON 字典

        自动兜底:
        1. 如果模型不严格遵守 response_format,从文本中提取 JSON
        2. 解析失败抛出 ValueError
        """
        text = self.chat(system_prompt, user_prompt, temperature)
        return self._extract_json(text)

    @staticmethod
    def _extract_json(text: str) -> dict:
        """从文本中提取 JSON(兼容被包裹在 ```json ... ``` 中的情况)"""
        text = text.strip()
        # 1. 直接解析
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        # 2. 提取代码块中的 JSON
        m = re.search(r"```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```", text, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(1))
            except json.JSONDecodeError:
                pass
        # 3. 贪心匹配第一个 JSON 对象/数组
        m = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(1))
            except json.JSONDecodeError:
                pass
        raise ValueError(f"LLM 响应无法解析为 JSON: {text[:200]}")


# 单例
llm_client = LLMClient()
