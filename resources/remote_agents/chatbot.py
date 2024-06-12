from langchain_openai import ChatOpenAI

def chatbot(state: State):
    llm = ChatOpenAI(model="gpt-4")
    return {"messages": [llm.invoke(state["messages"])]}