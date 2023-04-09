from __future__ import annotations

import re
from functools import lru_cache
from io import StringIO

from markdown_it import MarkdownIt
from markdown_it.renderer import RendererHTML
from rich.console import Console
from rich.markdown import Markdown


@lru_cache
def html_renderer():
    return MarkdownIt("commonmark", renderer_cls=RendererHTML)


def render_html_with_markdown_it(markdown: str) -> str:
    return html_renderer().render(markdown)


def render_html_with_rich(markdown: str) -> str:
    io_stream = StringIO()
    console = Console(
        record=True,
        file=io_stream,
        width=42,
    )
    md = Markdown(markdown, code_theme="default")
    console.print(md)
    return console.export_html()


_tag_parts = re.compile(r"^<\w[^>]+>\s+</[^>]+>$", re.M)


def avoid_start_and_stop_span(html: str):
    """
    >>> avoid_start_and_stop_span('<span class="r3">                                                   </span>')
    ''
    >>> avoid_start_and_stop_span('<span class="r1">Match newlines with </span><span class="r2">.*</span>')
    '<span class="r1">Match newlines with </span><span class="r2">.*</span>'
    >>> avoid_start_and_stop_span('</head><html>')
    '</head><html>'
    """
    return _tag_parts.sub("", html)


_consecutive_whitespace = re.compile(r"\s+<code>")


def avoid_consecutive_whitespace_before_code(html: str):
    return _consecutive_whitespace.sub(" <code>", html)

def remove_empty_lines(html: str):
    return "\n".join(line for line in html.splitlines() if line)

_style_regex = re.compile("<style>.*</style>", re.DOTALL)

def add_style_prefix(html: str, prefix: str) -> str:
    if style_section := _style_regex.search(html):
        new_style_section = []
        for line in style_section.group().splitlines():
            if line.startswith(".r"):
                new_style_section.append(f".{prefix}{line[1:]}")
            else:
                new_style_section.append(line)
        start, end = style_section.span()
        html = html[:start] + "\n".join(new_style_section) + html[end:]
    return html.replace('span class="r', f'span class="{prefix}r')


def render_html(markdown: str, style_prefix: str= ""):
    html = render_html_with_rich(markdown)

def cleanup_html(html: str):
    html = avoid_start_and_stop_span(html)
    html = avoid_consecutive_whitespace_before_code(html)
    html = remove_empty_lines(html)
    html = remove_empty_initial_spans(html)
    return html


_empty_tag_parts = re.compile(r"<span [^>]+>\s*</span>")
_non_empty_tag_parts = re.compile(r"<span [^>]+>\w+</span>")


def remove_empty_initial_spans(html: str):
    if non_empty_start := _non_empty_tag_parts.search(html):
        end = non_empty_start.start()
    else:
        end = len(html)
    def replacer(match: re.Match):
        span_end = match.end()
        if span_end < end:
            return ""
        return match.group()
    return _empty_tag_parts.sub(replacer, html)
