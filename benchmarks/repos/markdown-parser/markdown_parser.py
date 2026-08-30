# markdown_parser.py - Markdown Link & Image AST Extractor
import re
from typing import List, Dict, Any


class MarkdownLinkExtractor:
    @staticmethod
    def extract_links(markdown_text: str) -> List[Dict[str, str]]:
        """
        Extract standard markdown links [text](url) and images ![alt](url):
        - Format for links: {"type": "link", "text": "...", "url": "..."}
        - Format for images: {"type": "image", "alt": "...", "url": "..."}
        - Must not match broken brackets or empty urls.
        """
        results = []
        
        # BUG: Regex incorrectly conflates links and images, and fails on exclamation mark prefix
        # BUG: Fails on parenthesis in url or anchors
        pattern = r"(\!)?\[([^\]]+)\]\(([^)]+)\)"
        
        matches = re.finditer(pattern, markdown_text)
        for m in matches:
            is_image = bool(m.group(1))
            label = m.group(2).strip()
            url = m.group(3).strip()
            
            if not url:
                continue

            if is_image:
                results.append({"type": "image", "alt": label, "url": url})
            else:
                results.append({"type": "link", "text": label, "url": url})

        return results
