import requests
from prompt_toolkit import prompt

from client.utils import load_config

# 设置后端服务器的URL
API_URL = "http://127.0.0.1:8000"

def start_session(model_config):
    """开始一个新的聊天会话并返回会话ID"""
    response = requests.post(f"{API_URL}/start-session", json=model_config, timeout=10)
    if response.status_code == 200:
        session_id = response.json()["session_id"]
        print(f"New session started with session ID: {session_id}")
        return session_id
    else:
        print("Failed to start a new session with the server.")
        print("Response:", response.text)  # 打印详细的错误响应
        return None

def end_session(session_id):
    """结束一个聊天会话并清除会话"""
    response = requests.post(f"{API_URL}/end-session/{session_id}", timeout=10)
    if response.status_code == 200:
        print("Session ended successfully.")
    else:
        print("Failed to end the session.")
        print(response.text)

def stream_message(session_id, message):
    """以流式方式发送消息并打印响应"""
    response = requests.get(f"{API_URL}/stream-chat/{session_id}", json={"query": message}, timeout=10, stream=True)
    if response.status_code == 200:
        print("AI: ", end="")
        for chunk in response.iter_content(chunk_size=None):
            if chunk:
                print(chunk.decode(), end="", flush=True)
        print()
    else:
        print("Failed to send message to the server.")

def main():
    configs = load_config(config_path="config/model_config.json")
    print("Available AI Models:")
    for idx, config in enumerate(configs):
        print(f"{idx + 1}: {config['config_name']}")

    choice = int(prompt("Choose an AI model to use, only inupt the number: ")) - 1
    model_config = configs[choice]

    session_id = start_session(model_config)
    if session_id:
        while True:
            user_input = prompt("You: ")
            if user_input.lower() == "quit":
                print("Exiting the chat.")
                end_session(session_id)
                break
            stream_message(session_id, user_input)

if __name__ == "__main__":
    main()
