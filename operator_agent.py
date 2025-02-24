import os
import json
import gradio as gr
import httpx
import asyncio
from langchain_openai import ChatOpenAI
from langchain_community.llms import Ollama
from browser_use import Agent

def format_for_file(content):
    """Convert Markdown-style output to plain text with headings"""
    formatted = []
    for line in content.split('\n'):
        if line.startswith('## '):
            # Convert markdown headers to underlined text
            heading = line[3:].strip()
            formatted.append(f"{heading.upper()}\n{'=' * len(heading)}")
        elif line.startswith('1. '):
            # Ensure list items have proper spacing
            formatted.append(f"\n{line}")
        else:
            formatted.append(line)
    # Add double newline between paragraphs
    return '\n'.join(formatted).replace('\n\n', '\n').replace('\n', '\n\n')
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

    def save_to_file(self, content, filename=None):
        """Save content to a text file"""
        try:
            if not filename:
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"summary_{timestamp}.txt"
            
            # Add formatting step before saving
            formatted_content = format_for_file(content)
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(formatted_content)
            return f"Successfully saved to {filename}"
        except Exception as e:
            return f"File save error: {str(e)}"

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

    def save_to_file(self, content, filename=None):
        """Save content to a text file"""
        try:
            if not filename:
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"summary_{timestamp}.txt"
            
            # Add formatting step before saving
            formatted_content = format_for_file(content)
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(formatted_content)
            return f"Successfully saved to {filename}"
        except Exception as e:
            return f"File save error: {str(e)}"

class OpenRouterOperator:
    def __init__(self, model="meta-llama/llama-3.3-70b-instruct"):
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
                    # "order": ["DeepInfra", "DeepSeek", "Nebius", "Novita"],
                    "allow_fallbacks": True,
                    "require_parameters": False,
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

    def save_to_file(self, content, filename=None):
        """Save content to a text file"""
        try:
            if not filename:
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"summary_{timestamp}.txt"
            
            # Add formatting step before saving
            formatted_content = format_for_file(content)
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(formatted_content)
            return f"Successfully saved to {filename}"
        except Exception as e:
            return f"File save error: {str(e)}"

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="AI Operator")
    parser.add_argument("--task", help="Task to execute")
    parser.add_argument("--gradio", action="store_true", help="Launch Gradio UI")
    parser.add_argument("--provider", choices=["deepseek", "openrouter", "ollama"], 
                      default="deepseek", help="AI provider to use")
    parser.add_argument("--model", help="Override default model for the selected provider")
    parser.add_argument("--save", action="store_true", 
                       help="Save output to file")
    parser.add_argument("--filename", 
                       help="Custom filename for saved output")
    args = parser.parse_args()
    
    agent = (
        DeepSeekOperator(model=args.model or "deepseek-reasoner") if args.provider == "deepseek" 
        else OpenRouterOperator(model=args.model or "meta-llama/llama-3.3-70b-instruct") if args.provider == "openrouter" 
        else OllamaOperator(model=args.model or "deepseek-r1:1.5b")
    )

    def format_result(raw_output):
        """Convert raw output to formatted markdown structure"""
        try:
            # Extract core content
            content = raw_output.split("Execution Result:\n", 1)[-1]
            
            # Find the final 'done' entry if present
            done_content = None
            entries = content.split('ActionResult(')
            for entry in reversed(entries):  # Search from newest to oldest
                if 'is_done=True' in entry:
                    # Extract the text content using string operations
                    text_start = entry.find("extracted_content='") + len("extracted_content='")
                    text_end = entry.find("', error=")
                    if text_start > len("extracted_content='") and text_end > text_start:
                        done_content = entry[text_start:text_end].replace('\\n', '\n')
                    break
            
            # Format based on found content
            if done_content:
                return f"## Final Result\n{done_content}"
                
            # Fallback to original formatting
            sections = [s.strip() for s in content.split('\n\n') if s.strip()]
            formatted = []
            for section in sections:
                if section.startswith("1. "):  # List items
                    formatted.append(f"## Steps Taken\n{section}")
                else:  # Main result
                    formatted.append(f"## Final Result\n{section}")
            
            return '\n\n'.join(formatted)
            
        except Exception as e:
            return f"## Processing Error\n{str(e)}\n\nRaw output:\n{raw_output}"
    
    if args.gradio:
        async def wrapper(task):
            raw_result = await agent.execute_task(task)
            return format_result(raw_result)
        
        iface = gr.Interface(
            fn=wrapper,
            inputs=gr.Textbox(lines=2, label="Enter Task"),
            outputs=gr.Markdown(label="Execution Results"),
            title=f"AI Operator ({args.provider.capitalize()})",
            examples=[
                ["Research latest AI developments and summarize key points"],
                ["Compare current LLM model capabilities"]
            ]
        )
        iface.launch()
    elif args.task:
        raw_result = asyncio.run(agent.execute_task(args.task))
        formatted_result = format_result(raw_result)
        print(formatted_result)
        
        if args.save:
            save_result = agent.save_to_file(
                formatted_result,  # Save formatted version
                args.filename
            )
            print(save_result)
    else:
        print("Please provide either --task or --gradio argument")
