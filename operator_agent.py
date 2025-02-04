import os
import json
import gradio as gr
from openai import OpenAI
from browser_use import Browser
from dotenv import load_dotenv

load_dotenv()

class DeepSeekOperator:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com"
        )
        self.browser = Browser()
        
    def execute_task(self, task, max_steps=5):
        system_prompt = """You are an AI operator that can complete web tasks. 
        Generate step-by-step browser actions in JSON format. 
        Respond ONLY with a JSON array of action objects. 
        Example: [{"action": "navigate", "url": "..."}, ...]
        Task: {task}"""
        
        try:
            test_messages=[
                    {"role": "system", "content": system_prompt.format(task=task)},
                    {"role": "user", "content": task}
                ],
            response = self.client.chat.completions.create(
                model="deepseek-reasoner",
                messages=[
                    {"role": "system", "content": system_prompt.format(task=task)},
                    {"role": "user", "content": task}
                ],
                stream=False
            )
            print(f"Sending message to api: {test_messages}")
            print(f"API Response Received: {response}")
            
            if not response.choices or not response.choices[0].message.content:
                raise ValueError("Empty response from API")

            # Parse JSON from API response
            try:
                steps_json = response.choices[0].message.content
                print(f"Raw JSON from API: {steps_json}")
                steps = json.loads(steps_json)
                
                # Validate parsed steps
                if not isinstance(steps, list) or not all(isinstance(item, dict) for item in steps):
                    raise ValueError("Steps must be a list of action dictionaries")
                    
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON format in steps: {str(e)}") from e
            
            print("Validated steps structure OK")
            
            result = self.browser.execute_actions(
                action_sequence=steps,
                max_iterations=max_steps
            )
            print(f"Execution Result: {result}")
            return f"Steps Generated:\n{steps}\n\nExecution Result:\n{result}"
            
        except Exception as e:
            return f"Error processing task: {str(e)}\nPlease check your API key and network connection."

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
