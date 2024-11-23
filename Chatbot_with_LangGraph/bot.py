from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.graph.message import add_messages
from typing import Annotated, Any, Literal, TypedDict
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_google_genai import  ChatGoogleGenerativeAI

class chatbot:
    def __init__(self):
        self.llm= ChatGoogleGenerativeAI(model= 'gemini-1.0-pro')
    
        
    def call_tool(self):
        search= TavilySearchResults(max_results=2)
        tools= [search]
        self.tool_node=ToolNode(tools=tools) 
        self.llm_with_tool= self.llm.bind_tools(tools)
        
    def call_model(self, state:MessagesState):
        messages= state['messages']
        response= self.llm_with_tool.invoke(messages)        
        return {'messages':[response]}
    
    def router_function(self,state: MessagesState) -> Literal["tools", END]:
        messages = state['messages']
        last_message = messages[-1]
        if last_message.tool_calls:
            return "tools"
        return END
        
    def __call__(self):
        self.call_tool()
        workflow = StateGraph(MessagesState)
        workflow.add_node("agent", self.call_model)
        workflow.add_node("tools", self.tool_node)
        workflow.add_edge(START, "agent")
        workflow.add_conditional_edges("agent",self.router_function,{"tools": "tools", END: END})
        workflow.add_edge("tools", 'agent')
        self.app = workflow.compile()
        return self.app
    
if __name__ == '__main__':
    mybot= chatbot()
    app= mybot()
    response= app.invoke({'messages':['who is a current prime minister of India ?']})
    print(response['messages'][-1].content)
        
        