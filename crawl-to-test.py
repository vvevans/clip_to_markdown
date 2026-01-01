import marimo

__generated_with = "0.18.4"
app = marimo.App(width="medium")


@app.cell
def _():
    from dotenv import load_dotenv
    from tavily import TavilyClient
    import os
    from pathlib import Path
    from pprint import pprint
    return Path, TavilyClient, load_dotenv, os, pprint


@app.cell
def _(load_dotenv):
    load_dotenv()
    return


@app.cell
def _():
    base_clip_dir = "/media/vve1505/DATA/Qsync/GITNOTES/"
    return


@app.cell
def _(TavilyClient, os):
    api_key = os.getenv("tvly-API_KEY")
    tavily_client = TavilyClient(api_key)
    response = tavily_client.crawl("https://docs.tavily.com", max_depth=3, instructions="Find all pages on the Python SDK")

    print(response)
    return (tavily_client,)


@app.cell
def _(pprint, tavily_client):
    output = tavily_client.extract("https://www.marktechpost.com/2025/08/23/json-prompting-for-llms-a-practical-guide-with-python-coding-examples/", extract_depth="advanced", format="markdown")

    pprint(output)
    return (output,)


@app.cell
def _(Path, output):
    output_dir = Path("/media/vve1505/DATA/Qsync/GITNOTES/Clipped/")
    page_data = output['results'][0]
    md_content = page_data['raw_content']
    page_title = page_data.get('title', 'web_note')


    file_path = output_dir/f"{page_title}.md".replace(" ", "_") # Simple sanitization

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"Saved: {file_path}")
    return


if __name__ == "__main__":
    app.run()
