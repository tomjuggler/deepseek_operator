import os
import gradio as gr
from openai import OpenAI
from browser_use import BrowserClient
from dotenv import load_dotenv

load_dotenv()

class DeepSeekOperator:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com/v1"
        )
        self.browser = BrowserClient()
        
    def execute_task(self, task, max_steps=5):
        system_prompt = """You are an AI operator that can complete web tasks. 
        Generate step-by-step browser actions to achieve: {task}"""
        
        response = self.client.chat.completions.create(
            model="deepseek-reasoner",
            messages=[
                {"role": "system", "content": system_prompt.format(task=task)},
                {"role": "user", "content": task}
            ]
        )
        
        steps = response.choices[0].message.content
        result = self.browser.execute(steps, max_steps=max_steps)
        return f"Steps Generated:\n{steps}\n\nExecution Result:\n{result}"

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
        print(agent.execute_task(args.task))
    else:
        print("Please provide either --task or --gradio argument")
