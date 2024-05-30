from collections import OrderedDict
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException, Response, status
from fastapi.responses import StreamingResponse
from llama_index.llms.openai_like import OpenAILike
from pydantic import BaseModel

from server.config import AgentConfig
from src.simple_agent import Agent

# 初始化 FastAPI 应用
app = FastAPI()

# 保存活跃的用户会话，使用 OrderedDict 以保持插入顺序
agent_pool: OrderedDict[UUID, Agent] = OrderedDict()
MAX_AGENTS = 100  # 设置最大容量

# 请求体的数据模型
class ChatRequest(BaseModel):
    query: str

# FastAPI路由处理函数
@app.post("/chat/{agent_id}")
async def chat(agent_id: UUID, request: ChatRequest):
    agent = agent_pool.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"response": agent.chat(request.query)}

@app.get("/stream-chat/{agent_id}")
async def stream_chat(agent_id: UUID, request: ChatRequest):
    agent = agent_pool.get(agent_id)
    if not agent:
        return Response(status_code=status.HTTP_404_NOT_FOUND, content="Agent not found")
    def generate_messages():
        for message_chunk in agent.stream_chat(request.query):
            yield message_chunk
    return StreamingResponse(generate_messages(), media_type="text/plain")

@app.post("/start-session")
async def start_session(config: AgentConfig):
    if len(agent_pool) >= MAX_AGENTS:
        # 移除最旧的 Agent
        agent_pool.popitem(last=False)

    # 创建一个新的AI模型实例
    llm = OpenAILike(
        model=config.model_name,
        api_base=config.api_base,
        api_key=config.api_key,
        # 目前 config 里面均为 chat_model
        is_chat_model=True,
        **config.generate_args
    )
    # 创建一个新的会话ID和Agent
    new_agent_id = uuid4()
    agent_pool[new_agent_id] = Agent(llm=llm, system_prompt=config.system_prompt)
    return {"session_id": new_agent_id}

@app.post("/end-session/{agent_id}")
async def end_session(agent_id: UUID):
    if agent_id in agent_pool:
        del agent_pool[agent_id]
        return {"status": "session ended"}
    else:
        raise HTTPException(status_code=404, detail="Agent not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)  # noqa: S104
