import os
import json
import gradio as gr
import httpx
import asyncio
from langchain_openai import ChatOpenAI
from langchain_community.llms import Ollama
from browser_use import Agent
# from dotenv import load_dotenv

# load_dotenv()
from api_secrets import DEEPSEEK_API_KEY, OPENROUTER_API_KEY

class OllamaOperator:
    def __init__(self, model="deepseek-r1:1.5b"):
        self.client = Ollama(
            base_url="http://localhost:11434",
            model=model,
            temperature=0.3,
            timeout=120
        )
        
    async def execute_task(self, task, max_steps=20):
        try:
            agent = Agent(task=task, llm=self.client)
            result = await agent.run(max_steps=max_steps)
            return f"Execution Result:\n{result}"
        except Exception as e:
            return f"Ollama Error: {str(e)}"

class DeepSeekOperator:
    def __init__(self, model="deepseek-reasoner"):
        self.client = ChatOpenAI(
            openai_api_key=DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com/v1",
            model=model,
            timeout=httpx.Timeout(120.0)
        )
        
    async def execute_task(self, task, max_steps=20):
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

class OpenRouterOperator:
    def __init__(self, model="deepseek/deepseek-r1"):
        self.client = ChatOpenAI(
            openai_api_key=OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
            model=model,
            timeout=httpx.Timeout(120.0),
            default_headers={
                "HTTP-Referer": "https://circusscientist.com",
                "X-Title": "DeepSeek Operator",
                # Add provider preferences as JSON string in headers
                "HTTP-Provider": json.dumps({
                    "order": ["DeepInfra", "DeepSeek", "Nebius", "Novita"],
                    "allow_fallbacks": True,  # Changed to True to allow finding tool-supporting providers
                    "require_parameters": True,  # Added to ensure providers support all parameters
                    "sort": "price"
                })
            }
        )
        
    async def execute_task(self, task, max_steps=20):
        try:
            agent = Agent(
                task=task,
                llm=self.client
            )
            result = await agent.run(max_steps=max_steps)
            return f"Execution Result:\n{result}"
            
        except json.JSONDecodeError as e:
            return f"JSON Parsing Error: {str(e)}"
        except Exception as e:
            return f"API Error: {str(e)}"

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="AI Operator")
    parser.add_argument("--task", help="Task to execute")
    parser.add_argument("--gradio", action="store_true", help="Launch Gradio UI")
    parser.add_argument("--provider", choices=["deepseek", "openrouter", "ollama"], 
                      default="deepseek", help="AI provider to use")
    parser.add_argument("--model", help="Override default model for the selected provider")
    args = parser.parse_args()
    
    agent = (
        DeepSeekOperator(model=args.model or "deepseek-reasoner") if args.provider == "deepseek" 
        else OpenRouterOperator(model=args.model or "deepseek/deepseek-r1") if args.provider == "openrouter" 
        else OllamaOperator(model=args.model or "deepseek-r1:1.5b")
    )
    
    if args.gradio:
        iface = gr.Interface(
            fn=agent.execute_task,
            inputs=gr.Textbox(lines=2, label="Enter Task"),
            outputs=gr.Textbox(label="Execution Results"),
            title=f"AI Operator ({args.provider.capitalize()})"
        )
        iface.launch()
    elif args.task:
        print(asyncio.run(agent.execute_task(args.task)))
    else:
        print("Please provide either --task or --gradio argument")
