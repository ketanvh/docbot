import requests
from bs4 import BeautifulSoup
import re
import os
from dotenv import load_dotenv

# Load environment variables and set up debug functionality
load_dotenv()
DEBUG = os.getenv("DEBUG", "False").lower() in ["true", "1", "t", "yes", "y"]

def debug_log(message):
    if DEBUG:
        print(f"DEBUG [Website Processor]: {message}")

def process_website(url):
    """
    Process a website URL and extract content in markdown format.
    
    Args:
        url (str): URL of the website to process
        
    Returns:
        str: Extracted content in markdown format
    """
    debug_log(f"Processing website URL: {url}")
    
    try:
        # Validate URL
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        debug_log(f"Validated URL: {url}")
        
        # Make request to the website
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        debug_log(f"Website request successful: Status code {response.status_code}")
        
        # Parse HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        debug_log("HTML content parsed successfully")
        
        # Extract title
        title = soup.title.string if soup.title else "Untitled Page"
        debug_log(f"Page title: {title}")
        
        # Remove script and style elements
        for script_or_style in soup(['script', 'style', 'header', 'footer', 'nav']):
            script_or_style.decompose()
        debug_log("Removed script, style, header, footer, and nav elements")
        
        # Initialize content with title
        content = f"# Website: {title}\n\nURL: {url}\n\n"
        
        # Extract headings and their content
        for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            heading_level = int(heading.name[1])
            heading_text = heading.get_text().strip()
            
            if heading_text:
                content += f"{'#' * heading_level} {heading_text}\n\n"
                debug_log(f"Extracted heading: {heading_text}")
                
                # Get all paragraph siblings until next heading
                sibling = heading.next_sibling
                paragraph_content = ""
                
                while sibling and not sibling.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    if sibling.name == 'p':
                        paragraph_text = sibling.get_text().strip()
                        if paragraph_text:
                            paragraph_content += paragraph_text + "\n\n"
                    sibling = sibling.next_sibling
                
                content += paragraph_content
        
        # Extract any remaining paragraphs that aren't under headings
        additional_content = ""
        for paragraph in soup.find_all('p'):
            if not any(parent.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'] for parent in paragraph.parents):
                paragraph_text = paragraph.get_text().strip()
                if paragraph_text and len(paragraph_text) > 20:  # Skip very short paragraphs
                    additional_content += paragraph_text + "\n\n"
        
        # Add additional content if there is any
        if additional_content:
            content += "## Additional Content\n\n" + additional_content
            debug_log("Added additional content")
        
        # Clean up content
        content = re.sub(r'\n{3,}', '\n\n', content)  # Replace multiple newlines
        
        debug_log(f"Website processing complete: {len(content)} characters extracted")
        return content.strip()
    except Exception as e:
        debug_log(f"ERROR processing website: {str(e)}")
        return f"Error processing website {url}: {str(e)}"
