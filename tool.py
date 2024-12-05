import os
from dotenv import load_dotenv


def load_config():
    # 加载 .env 文件
    load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), ".env")))
    silicon_sk = os.getenv("SILICON_FLOW_SK")
    return {
        "silicon_sk": silicon_sk,
    }
