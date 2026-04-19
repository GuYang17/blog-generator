#!/usr/bin/env python3

from dataclasses import dataclass
from datetime import datetime
import os
from pathlib import Path
import rich
import markdown
import sys
from jinja2 import Template


NAME = 'GuYang17'


# TODO: 添加INFO, WARNING等日志级别
def show_error(message: str):
    rich.print(f'[red bold][Error][/red bold]: {message}')


@dataclass
class Article:
    title: str
    date: datetime
    content_markdown: str
    result_html: str
    final_html: str
    link: str


def load_articles() -> list[Article]:
    '''
    Load articles from the source directory. Each article is expected to be a markdown file with the format:
    YYYY-MM-DD | Title.md
    '''
    articles: list[Article] = []
    source_dir = Path('./source/articles')

    # TODO: 加强错误处理
    try:
        for filename in os.listdir(source_dir):
            file = source_dir / filename
            if file.is_file() and file.suffix == '.md':
                date, title = file.stem.split(' | ')
                with open(file, 'r', encoding='utf-8') as f:
                    content_markdown = f.read()
                article = Article(
                    title=title,
                    date=datetime.strptime(date, '%Y-%m-%d'),
                    content_markdown=content_markdown,
                    result_html='',
                    final_html='',
                    link=f'{date} | {title}.html'
                )
                articles.append(article)
    except Exception as e:
        show_error(f'Failed to load articles: {e}')
        sys.exit(1)

    return articles


def convert_articles(articles: list[Article]) -> list[Article]:
    '''
    Convert markdown content of each article to HTML.
    '''
    for article in articles:
        try:
            article.result_html = markdown.markdown(article.content_markdown)
        except Exception as e:
            show_error(f'Failed to convert article "{article.title}": {e}')
            sys.exit(1)
    return articles


def load_article_template() -> Template:
    '''
    Load article template.
    '''
    template_path = Path('./source/templates/article.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    return Template(template_content)


def load_index_template() -> Template:
    '''
    Load index template.
    '''
    template_path = Path('./source/templates/index.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    return Template(template_content)


def render_article(article: Article, template: Template) -> str:
    '''
    Render an article using the provided template.
    '''
    try:
        final_html = template.render(article=article)
        return final_html
    except Exception as e:
        show_error(f'Failed to render article "{article.title}": {e}')
        sys.exit(1)


def render_index(articles: list[Article], template: Template) -> str:
    '''
    Render the index page using the provided template and list of articles.
    '''
    try:
        return template.render(articles=articles, name=NAME)
    except Exception as e:
        show_error(f'Failed to render index page: {e}')
        sys.exit(1)


def generate_output(articles: list[Article], index_html: str):
    '''
    Generate output files for articles and index page.
    '''
    output_dir = Path('./output')
    output_dir.mkdir(exist_ok=True)

    # Generate article HTML files
    for article in articles:
        article_filename = f'{article.date.strftime("%Y-%m-%d")} | {article.title}.html'
        article_path = output_dir / article_filename
        try:
            with open(article_path, 'w', encoding='utf-8') as f:
                f.write(article.final_html)
        except Exception as e:
            show_error(f'Failed to write article "{article.title}" to file: {e}')
            sys.exit(1)

    # Generate index HTML file
    index_path = output_dir / 'index.html'
    try:
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(index_html)
    except Exception as e:
        show_error(f'Failed to write index page to file: {e}')
        sys.exit(1)

    # Copy static files
    static_dir = Path('./source/static')
    for item in static_dir.iterdir():
        if item.is_file():
            try:
                target_path = output_dir / item.name
                with open(item, 'rb') as src, open(target_path, 'wb') as dst:
                    dst.write(src.read())
            except Exception as e:
                show_error(f'Failed to copy static file "{item.name}": {e}')
                sys.exit(1)


def main():
    articles = load_articles()
    articles = convert_articles(articles)
    article_template = load_article_template()
    index_template = load_index_template()
    for article in articles:
        article.final_html = render_article(article, article_template)
    index_html = render_index(articles, index_template)
    generate_output(articles, index_html)


if __name__ == '__main__':
    main()