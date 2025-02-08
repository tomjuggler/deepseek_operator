# DeepSeek Operator Alternative

Open-source ChatGPT Operator alternative using DeepSeek R1 and browser automation.

## Information: 
- Created using [Aider](https://aider.chat) and [DeepSeek R1](https://deepseek.com)
- Check out the [Circus Scientist blog and tutorial site](https://circusscientist.com) for more interesting AI and IOT related projects
- DeepSeek api is pretty unreliable currently, expect this app to fail for no reason *a lot*
- MIT License have fun
- No guarantees, AI wrote the whole thing and I take no responsibility, please check the code there's not much

- DeepSeek and OpenRouter providers are functional (OpenRouter using Meta-Llama by default)
- DeepSeek API can be unreliable and slow
- Ollama remains untested due to hardware requirements

## Setup
- *tested on Python 3.12*
1. Clone repo & create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create api_secrets.py file with the following:
```bash
DEEPSEEK_API_KEY="**********"
OPENROUTER_API_KEY="****************"

```

## Usage

### Command Line Options
```bash
# Basic task execution
python operator_agent.py --task "Book flight from NYC to London on Dec 25th"

# Specify provider and model
python operator_agent.py --provider ollama --model "llama2" --task "Research AI news"
python operator_agent.py --provider openrouter --model "anthropic/claude-3-opus" --task "Analyze market trends"

# Save results to file
python operator_agent.py --task "Compare smartphone prices" --save
python operator_agent.py --task "Weather report analysis" --save --filename "weather_analysis.txt"

# Web UI with specific provider
python operator_agent.py --gradio --provider ollama
```

### Provider Options
- `--provider`: Choose AI backend (deepseek|openrouter|ollama)
  - Default: deepseek
  - Default models:
    - DeepSeek: "deepseek-reasoner"
    - OpenRouter: "meta-llama/llama-3.3-70b-instruct" (requires careful prompting but works)
    - Ollama: "deepseek-r1:1.5b" (untested)
- `--model`: Override default model for selected provider
- `--save`: Automatically save results to timestamped .txt file
- `--filename`: Specify custom filename for saved results

### Web UI
```bash
python operator_agent.py --gradio
```

### Example Tasks
- "Find cheapest iPhone 15 on Amazon and save results to file"
- "Research AI news from last week and summarize key points"
- "Book 2 tickets for Avatar 3 at nearest cinema tonight"

## Features
- 🤖 Multi-provider support (DeepSeek, OpenRouter, Ollama)
- 🌐 Browser automation integration
- 💬 Gradio web interface
- 📂 File output saving with --save/--filename
- 🔐 Local environment security
- ⚙️ Model customization per task

Note: Requires Chrome/Firefox installed. First run may download browser drivers.
