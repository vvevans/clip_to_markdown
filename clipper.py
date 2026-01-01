#!/usr/bin/env python3

"""
Web page clipper using Tavily API to extract content into Markdown with YAML frontmatter.
"""

import os
import sys
import logging
import re
from pathlib import Path
from dotenv import load_dotenv
from tavily import TavilyClient

# Configure logging for verbose output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
LOGGER = logging.getLogger(__name__)

def setup_client():
    """Initializes the Tavily client."""
    load_dotenv()
    # Using the exact key name from original file
    api_key = os.getenv("tvly-API_KEY")
    if not api_key:
        LOGGER.error("API Key 'tvly-API_KEY' not found in environment variables.")
        sys.exit(1)
    return TavilyClient(api_key)

def sanitize_filename(filename: str) -> str:
    """Simple sanitization for filenames."""
    # Keep alphanumeric, underscores, and dots
    return "".join(c if c.isalnum() or c in (" ", ".", "_") else "_" for c in filename).replace(" ", "_")

def clean_markdown_content(content: str) -> str:
    """
    Removes comments sections and social/author follow links from markdown.
    """
    # Pattern to identify common comment section headers in markdown
    # Matches headers like "Comments", "Post a Comment", "Discussion", etc.
    comment_headers = [
        r"^#+\s+Comments?.*$",
        r"^#+\s+Discussion.*$",
        r"^#+\s+Leave a reply.*$",
        r"^#+\s+Post a Comment.*$",
        r"^---\s*$", # Horizontal rules often precede comments
    ]
    
    lines = content.splitlines()
    cleaned_lines = []
    skip_rest = False
    
    # Common keywords that indicate social/author follow sections
    follow_keywords = [
        "follow me", "follow the author", "subscribe", "twitter", 
        "linkedin", "facebook", "instagram", "newsletter", "github",
        "youtube", "mastodon"
    ]

    for line in lines:
        lower_line = line.lower()
        
        # Check for comment headers to truncate the rest of the document
        if any(re.match(pattern, line, re.IGNORECASE) for pattern in comment_headers):
            # If it's a common comment header, we likely reached the end of content
            if "comment" in lower_line or "discussion" in lower_line or line.strip() == "---":
                LOGGER.info(f"Trimming content at possible comment section: {line}")
                skip_rest = True
                break

        # Check for social follow links/lines to skip them
        if any(kw in lower_line for kw in follow_keywords):
            # If line contains follow keywords and looks like a link, CTA, or simple mention
            # We are more aggressive here to remove follow blocks
            continue

        cleaned_lines.append(line)
        
    return "\n".join(cleaned_lines).strip()

def clip_url_to_markdown(client, base_dir: Path, output_subdir: str, url: str, tags: str):
    """Clips a single URL and saves it to the specified directory with YAML frontmatter."""
    try:
        # Check for the output directory; create if it doesn't exist
        target_dir = base_dir / output_subdir
        if not target_dir.exists():
            LOGGER.info(f"Creating directory: {target_dir}")
            target_dir.mkdir(parents=True, exist_ok=True)

        LOGGER.info(f"Extracting content from: {url}...")
        output = client.extract(url, extract_depth="advanced", format="markdown")
        
        if not output.get('results'):
            LOGGER.warning(f"No results found for URL: {url}")
            return

        page_data = output['results'][0]
        title = page_data.get('title', 'web_note')
        sanitized_title = sanitize_filename(title)
        file_path = target_dir / f"{sanitized_title}.md"
        
        raw_content = page_data.get('raw_content', '')
        
        if not raw_content:
            LOGGER.warning("No content extracted from the page.")
            return

        # Clean the content
        cleaned_content = clean_markdown_content(raw_content)

        # Prepare tags for YAML (list format)
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]
        tags_yaml = ", ".join(tag_list)

        # Construct Markdown with YAML Frontmatter
        md_content = f"""---
title: "{title}"
URL: {url}
tags: [{tags_yaml}]
---

{cleaned_content}
"""

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(md_content)
        
        LOGGER.info(f"Successfully saved: {file_path}")

    except Exception as e:
        LOGGER.error(f"An error occurred while clipping {url}: {e}")

def main():
    """Main loop for the clipper program."""
    BASE_CLIP_DIR = Path("/media/vve1505/DATA/Qsync/GITNOTES/")
    tavily_client = setup_client()

    print("\n--- Web Page Clipper ---")
    
    while True:
        output_dir = input("\nEnter directory to save clips (relative to base): ").strip()
        if not output_dir:
            LOGGER.warning("Directory name cannot be empty.")
            continue

        clip_url = input("Enter URL to clip from: ").strip()
        if not clip_url.startswith(('http://', 'https://')):
            LOGGER.warning("Invalid URL format. Please include http:// or https://")
            continue

        tags = input("Enter comma-separated tags: ").strip()

        clip_url_to_markdown(tavily_client, BASE_CLIP_DIR, output_dir, clip_url, tags)
        
        choice = input("\nWould you like to clip another URL? (y/n): ").strip().lower()
        if choice != 'y':
            LOGGER.info("Exiting clipper.")
            break

if __name__ == "__main__":
    main()
