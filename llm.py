import http.client
import json
import tool

# 也可自己替换其他模型
llm_model_name = "Qwen/Qwen2.5-72B-Instruct"


class LlmClient:
    def __init__(self):
        config = tool.load_config()
        self.config = config

    def chat_single(
        self,
        user_input,
        history=None,
        template="你是一个系统助手，请回答用户的问题",
    ):
        print("user_input:", user_input)
        conn = http.client.HTTPSConnection("api.siliconflow.cn")
        messages = [{"role": "system", "content": template}]
        if history is not None and len(history) > 0:
            history = history[-8:]
            for item in history:
                messages.append(item)
        if (
            user_input is not None
            and isinstance(user_input, dict)
            and "text" in user_input
        ):
            messages.append({"role": "user", "content": user_input["text"]})
        elif user_input is not None:
            messages.append({"role": "user", "content": user_input})
        body = {
            "model": llm_model_name,
            "messages": messages,
            "stream": False,
            "max_tokens": 4096,
        }
        payload = json.dumps(body)
        headers = {
            "Authorization": f"Bearer {self.config['silicon_sk']}",
            "Content-Type": "application/json",
        }
        conn.request("POST", "/v1/chat/completions", payload, headers)
        # 获取响应
        response = conn.getresponse()

        # 检查响应状态
        if response.status == 200:
            data = response.read()
            obj = json.loads(data.decode("utf-8"))
            print("single_output_msg:", obj["choices"][0]["message"]["content"])
            return obj["choices"][0]["message"]["content"]
        else:
            print(f"请求失败，状态码: {response.status}")
