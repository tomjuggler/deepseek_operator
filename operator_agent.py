import os
import json
import gradio as gr
import httpx
import asyncio
from langchain_openai import ChatOpenAI
from browser_use import Agent
# from dotenv import load_dotenv

# load_dotenv()
from api_secrets import DEEPSEEK_API_KEY

class DeepSeekOperator:
    def __init__(self):
        self.client = ChatOpenAI(
            openai_api_key=DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com/v1",
            model="deepseek-chat",
            timeout=httpx.Timeout(60.0)
        )
        
    async def execute_task(self, task, max_steps=5):
        try:
            agent = Agent(
                task=task,
                llm=self.client
            )
            # Add explicit JSON response formatting
            result = await agent.run(max_steps=max_steps)
            return f"Execution Result:\n{result}"
            
        except json.JSONDecodeError as e:
            return f"JSON Parsing Error: {str(e)}"
        except Exception as e:
            return f"API Error: {str(e)}"

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="DeepSeek Operator")
    parser.add_argument("--task", help="Task to execute")
    parser.add_argument("--gradio", action="store_true", help="Launch Gradio UI")
    args = parser.parse_args()
    
    agent = DeepSeekOperator()
    
    if args.gradio:
        iface = gr.Interface(
            fn=agent.execute_task,
            inputs=gr.Textbox(lines=2, label="Enter Task"),
            outputs=gr.Textbox(label="Execution Results"),
            title="DeepSeek Operator"
        )
        iface.launch()
    elif args.task:
        print(asyncio.run(agent.execute_task(args.task)))
    else:
        print("Please provide either --task or --gradio argument")
