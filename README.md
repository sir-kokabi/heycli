# HeyCLI 🤖 - Your AI Buddy for Daily Tasks

![HeyCLI Preview](./heycli.jpg)

Stop wasting time on repetitive chores! `HeyCLI` is your AI-powered command-line assistant that simplifies everyday tasks. Forget writing scripts. Just run commands like `heycli remove all empty folders`. 

Zero setup, maximum efficiency!

For example, need to convert all your `.png` images to `.jpg`? Just type `heycli convert *.png to *.jpg`. Or, if you want to extract the first column of your `contacts.csv` and save it to `names.txt`, simply use `heycli extract column 1 from contacts.csv to names.txt`.

**heycli** shows the code and confirms execution before running, ensuring you're always in control.

Also, by default, it works in your current directory, so you don't have to specify the current working directory every time in your prompt.

**If you can describe it, HeyCLI can do it.**
Get your time back.

For getting free API keys, check out [Zuki Journey](https://cas.zukijourney.com/).

https://github.com/user-attachments/assets/d3e53d75-7614-45ca-a347-dca77aba51e8

## 🚀 Install
```bash
pipx install heycli (recommended)

# Set up config file at ~/.heycli/config.yaml 
# (on Windows: C:\Users\YourUsername\.heycli\config.yaml)
# Then use it!
heycli rename all files sequentially from 1
heycli sort file names by size (descending) and save in a text file
heycli change all images format to jpg
heycli find large files in my documents folder
heycli print all emails from contact-list.txt
heycli generate 10 random numbers between 100 and 1000
```

## 📝 Sample Config File

```yaml
# List faster, more reliable providers and more capable models first.
# They will be attempted in the order listed.

providers:
  - base_url: "https://api.naga.ac/v1"
    api_key: "Your API key"
    models:
      - "gpt-4o"
      - "deepseek-chat"
      - "gemini-2.0-flash"

  - base_url: "https://api.electronhub.top/v1"
    api_key: "Your API Key"
    models:
      - "claude-3-7-sonnet-20250219"
      - "gpt-4o"

  - base_url: "https://openrouter.ai/api/v1"
    api_key: "Your API key"
    models:
      - "deepseek/deepseek-chat:free"
      - "google/gemini-2.0-pro-exp-02-05:free"
```
