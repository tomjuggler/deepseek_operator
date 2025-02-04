import os
import json
import gradio as gr
from openai import OpenAI
from browser_use import Browser
# from dotenv import load_dotenv

# load_dotenv()
from api_secrets import DEEPSEEK_API_KEY

class DeepSeekOperator:
    def __init__(self):
        self.client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com"
        )
        self.browser = Browser()
        
    def execute_task(self, task, max_steps=5):
        system_prompt = """You are an expert web automation engineer. Generate precise browser actions to complete tasks on real websites.

# Task Requirements
1. Analyze the user's goal and website structure
2. Create minimal, reliable actions using ONLY these types:
   - navigate(url): Initial page load
   - click(css_selector): Interactive elements
   - input(css_selector, text): Form fields
   - wait(seconds): Page loading time
   - scroll(pixels): Page navigation (optional)

# Website Specifics for Gumtree
- Search box: '[data-qa="search-input"]'
- Search button: '[data-qa="search-button"]'
- Sort menu: '[data-qa="sort-select"]'
- Price filter: '[data-qa="price-filter-input"]'

# Output Rules
- Return ONLY valid JSON array
- Include necessary waits after navigation (3-5s)
- Prioritize reliable CSS selectors over fragile XPaths
- Add error handling for:
  * Element not found
  * Page load timeouts
  * Unexpected popups

Example response for phone search:
[
  {{"action": "navigate", "value": "https://www.gumtree.co.za/s-cell-phone-phones/android-phones/v1c9077q0p1"}},
  {{"action": "wait", "value": 5}},
  {{"action": "click", "selector": "[data-qa='sort-select']"}},
  {{"action": "click", "selector": "[data-qa='sort-option-price-asc']"}},
  {{"action": "wait", "value": 3}},
  {{"action": "click", "selector": "[data-qa='search-result']:first-child a"}}
]"""
        
        test_messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": task}
        ]
        print(f"Sending message to api: {test_messages}")
        try:
            
            response = self.client.chat.completions.create(
                model="deepseek-reasoner",
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": task}
                ],
                stream=False
            )
            
            print(f"API Response Received: {response}")
            
            if not response.choices or not response.choices[0].message.content:
                print(f"Empty response structure: {response}")
                raise ValueError("Empty response from API")

            # Parse JSON from API response
            try:
                steps_json = response.choices[0].message.content
                print(f"Raw JSON from API: {steps_json}")
                steps = json.loads(steps_json)
                
                # Validate parsed steps
                if not isinstance(steps, list) or not all(
                    isinstance(item, dict) and 'action' in item 
                    for item in steps
                ):
                    raise ValueError("Steps must be a list of action dictionaries with 'action' keys")
                    
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
