import typer
from typing_extensions import Annotated
from typing import Optional, List
from rich.console import Console
from rich.panel import Panel
import re
import questionary
from rich.syntax import Syntax
from rich.text import Text
import time
import httpx
import yaml
import pathlib
from litellm import completion
import litellm
import subprocess
import sys

litellm.suppress_debug_info = True

console = Console()
app = typer.Typer(
    help=Panel.fit(
        "Your AI Buddy for daily tasks",
        title="HeyCLI",
        border_style="green",
        padding=(1, 2)
    ),
    add_completion=False
)

def version_callback(value: bool) -> None:
    if value:       
        console.print("Version 1.0.1")

def get_accessible_providers():
    with console.status("Checking available AI providers...", speed=2):
        config_file_path = pathlib.Path.home() / ".heycli" / "config.yaml"
        with open(config_file_path, "r", encoding="utf-8") as file:
            config = yaml.safe_load(file)          
            providers = config["providers"]            

        valid_providers = []
        
        # Use synchronous requests instead of async
        with httpx.Client(limits=httpx.Limits(max_connections=100), timeout=10.0) as client:
            for provider in providers:
                try:
                    base_url = f'{provider["base_url"]}/models'
                    response = client.head(base_url)
                    if "application/json" in response.headers.get("content-type", "").lower():
                        valid_providers.append(provider)                        
                except Exception:                    
                    continue       
      
        return valid_providers

def get_ai_response(provider, model, messages):
    base_url = str(provider["base_url"])
    api_key = provider["api_key"]
    
    start_time = time.time()
    with console.status(f"{base_url} | {model}", speed=2):
        response = completion(
            model=f"openai/{model}",
            messages=messages,
            api_key=api_key,
            api_base=base_url,
        )        
        content = response["choices"][0]["message"]["content"]
    end_time = time.time()
    response_time = round(end_time - start_time)
    
    return content, base_url, model, response_time

def install_packages(packages):   
    for package in packages:
        package = package.strip()
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def run_script(script, base_url, model, response_time):
    console.print(
        Panel(
            Syntax(script, "python"),
            subtitle=Text(
                f"{base_url} | {model} ({response_time}s)",
                style="white on dark_green",
            ),
        )
    )
    
    if questionary.confirm("Run script?").ask():
        pip_install_pattern = r"# pip install ([\w\.,\-]+)$"
        pip_match = re.search(pip_install_pattern, script, re.MULTILINE)
        
        if pip_match:
            packages = pip_match.group(1).split(',')
            install_packages(packages)
        
        exec(script, globals())



def ask_ai(user_prompt):
    system_prompt = """
- For the given task, create a minimal, beginner-friendly Python script with clear, concise comments.
- The script should be ready to run with `exec` and be enclosed between ```python and ```.
- For all file operations use UTF-8 encoding and by default, operate in the current working directory unless specified otherwise.
- For any other requests that do not require a Python script, return only NULL without quotes or additional explanation.
- The output should be solely a single ```python``` script or NULL, with no explanation or additional text.
- Write exclusively in English.
- Do not use 'if __name__ == "...":' (e.g., if __name__ == "__main__", etc.). Instead, call functions directly at the end of the script.
This ensures the script will execute properly with the exec() function.
- If the script requires any packages to be installed, include the following line without any explanation at the end of the script:
# pip install pkg1,pkg2... (with full error message if installation fails)
- Specify package names exactly as they appear on PyPI (e.g., use `pillow` instead of `PIL`).

""".strip()

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]       

    accessible_providers = get_accessible_providers()
    
    for provider in accessible_providers:
        for model in provider["models"]:
            try:
                content, base_url, model, response_time = get_ai_response(provider, model, messages)
                
                script_pattern = r"^\s*```python\s*(.*?)\s*```\s*$"
                script_match = re.search(script_pattern, content, re.DOTALL)
                
                if script_match:
                    script = script_match.group(1).strip()
                    return {
                        "script": script,
                        "base_url": base_url,
                        "model": model,
                        "response_time": response_time
                    }
                else:
                    return {
                        "script": None,
                        "base_url": base_url,
                        "model": model,
                        "response_time": response_time
                    }
                
            except Exception:                
                continue
    
    raise Exception("ALL AI providers failed to respond. Check your network connection, API keys, and provider configurations.")

@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version",
            "-v",
            help="Display the heycli version",
            callback=version_callback,
            is_eager=True,
        ),
    ] = None,
    prompt: Annotated[Optional[List[str]], typer.Argument(help="What you want to get done")] = None,
) -> None:
    try:
        if prompt:
            full_prompt = " ".join(prompt)
            result = ask_ai(full_prompt)
            
            if result["script"]:
                run_script(result["script"], result["base_url"], result["model"], result["response_time"])
            else:
                console.print("[bold yellow]No Python script to execute.[/bold yellow]")
        else:    
            ctx.get_help()
    except Exception as e:
        console.print(f"[bold red]Error: {str(e)}[/bold red]")
        console.print_exception(theme="monokai", show_locals=True)

if __name__ == "__main__":
    app()