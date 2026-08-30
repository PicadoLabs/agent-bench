import pytest
from markdown_parser import MarkdownLinkExtractor


def test_standard_hyperlinks():
    md = "Visit [Google](https://google.com) or read the [Docs](https://docs.agentbench.dev)."
    links = MarkdownLinkExtractor.extract_links(md)
    assert len(links) == 2
    assert links[0] == {"type": "link", "text": "Google", "url": "https://google.com"}
    assert links[1] == {"type": "link", "text": "Docs", "url": "https://docs.agentbench.dev"}


def test_image_tags_distinct_from_links():
    md = "Here is a logo: ![AgentBench Logo](https://img.example.com/logo.png) and a link [Home](https://example.com)."
    links = MarkdownLinkExtractor.extract_links(md)
    assert len(links) == 2
    assert links[0] == {"type": "image", "alt": "AgentBench Logo", "url": "https://img.example.com/logo.png"}
    assert links[1] == {"type": "link", "text": "Home", "url": "https://example.com"}


def test_ignore_empty_or_malformed_links():
    md = "Broken [no url]() and unclosed [bracket (http://bad.com)"
    links = MarkdownLinkExtractor.extract_links(md)
    assert len(links) == 0
