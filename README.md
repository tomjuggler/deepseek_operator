# DeepSeek Operator Alternative

Open-source ChatGPT Operator alternative using DeepSeek R1 and browser automation.

## Setup

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

3. Create .env file:
```bash
echo "DEEPSEEK_API_KEY=your_api_key_here" > .env
```

## Usage

### Command Line
```bash
python operator_agent.py --task "Book flight from NYC to London on Dec 25th"
```

### Web UI
```bash
python operator_agent.py --gradio
```

### Example Tasks
- "Find cheapest iPhone 15 on Amazon and save results to file"
- "Research AI news from last week and summarize key points"
- "Book 2 tickets for Avatar 3 at nearest cinema tonight"

## Features
- 🤖 DeepSeek R1 reasoning engine
- 🌐 Browser automation integration
- 💬 Gradio web interface
- 🔐 Local environment security

Note: Requires Chrome/Firefox installed. First run may download browser drivers.
