def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}