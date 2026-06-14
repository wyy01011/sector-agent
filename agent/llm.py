from langchain_ollama import ChatOllama


llm = ChatOllama(
    model="gemma3:1b",
    temperature=0,
    num_predict=200,
)

