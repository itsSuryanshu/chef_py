# Chef_py
A program built to find you the most suitable recipes that can be cooked up using the ingredients you have!

### Configuration
The .env file is needed to run the program. Once made, I suggest using this template and inputting API keys for each program (exception: Langsmith is optional)
```
# --- LLM PROVIDER & CORE AGENT CONFIG ---
OPENAI_API_KEY="******"
OPENAI_MODEL_NAME="gpt-5.4"

# --- WEB SEARCH TOOLS ---
TAVILY_API_KEY="*****"

# --- OBSERVABILITY & DEBUGGING ---
LANGSMITH_TRACING="true"
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY="******"
LANGSMITH_PROJECT="chef_py"

# --- SYSTEM SETTINGS ---
PYTHONWARNINGS="ignore"
```
> Using OpenAI is not mandatory, open-weight models can also be used as long as they support multimodal (images supported soon).