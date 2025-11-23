import os
import subprocess
from datetime import datetime, timezone

from feedgen.feed import FeedGenerator

from .. import config as cfg
from ..core.utils import parse_front_matter, warn


def process_blog(config, template_env, md_processor, data, build_dir):
    posts = []
    blog_slugs = set()

    blog_dir = cfg.get_blog_dir(config)
    if not os.path.exists(blog_dir):
        return posts

    for filename in os.listdir(blog_dir):
        if not filename.endswith(".md"):
            continue

        slug = filename.replace(".md", "")
        if slug in blog_slugs:
            warn(f"Duplicate blog slug: {slug}")
        blog_slugs.add(slug)

        filepath = os.path.join(blog_dir, filename)
        post = _process_post(config, md_processor, filepath, slug)
        if post:
            posts.append(post)

    posts.sort(
        key=lambda p: p.get("created") or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )

    blog_section = os.path.basename(blog_dir)
    blog_build_dir = os.path.join(build_dir, blog_section)
    os.makedirs(blog_build_dir, exist_ok=True)

    _generate_blog_index(config, template_env, data, blog_build_dir, blog_section, posts)
    _generate_post_pages(config, template_env, data, blog_build_dir, blog_section, posts)

    if cfg.has_feeds(config):
        _generate_feeds(config, blog_build_dir, blog_section, posts)

    return posts


def _process_post(config, md_processor, filepath, slug):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    metadata, markdown_content = parse_front_matter(content)
    html_content = md_processor.convert(markdown_content)
    md_processor.reset()

    date_str = metadata.get("date")
    if date_str:
        if isinstance(date_str, str):
            created_date = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        else:
            created_date = datetime.combine(date_str, datetime.min.time()).replace(tzinfo=timezone.utc)
    else:
        created_date = _get_git_date(filepath)
        if not created_date:
            warn(f"No date found for blog post: {os.path.basename(filepath)}")

    post = {
        "title": metadata.get("title", slug.replace("-", " ").title()),
        "slug": slug,
        "content": html_content,
        "filepath": filepath,
        "created": created_date,
    }

    if created_date:
        post["date"] = created_date.strftime("%Y-%m-%d")
        post["date_iso"] = created_date.isoformat()

    return post


def _get_git_date(filepath):
    try:
        output = subprocess.check_output(
            ["git", "log", "--follow", "--format=%H %ct", "--", filepath],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        if output:
            first_commit_ts = int(output.split("\n")[-1].split()[1])
            return datetime.fromtimestamp(first_commit_ts, tz=timezone.utc)
    except (subprocess.CalledProcessError, FileNotFoundError, ValueError):
        pass
    return None


def _generate_blog_index(config, template_env, data, blog_dir, blog_section, posts):
    base_path = cfg.get_base_path(config)
    canonical_path = f"{base_path}/{blog_section}" if base_path else f"/{blog_section}"

    with open(os.path.join(blog_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(
            template_env.get_template(cfg.get_blog_index_template(config)).render(
                posts=posts,
                active_page=blog_section,
                canonical_path=canonical_path,
                data=data,
            )
        )


def _generate_post_pages(config, template_env, data, blog_dir, blog_section, posts):
    base_path = cfg.get_base_path(config)
    for post in posts:
        canonical_path = (
            f"{base_path}/{blog_section}/{post['slug']}" if base_path else f"/{blog_section}/{post['slug']}"
        )

        post_path = os.path.join(blog_dir, f"{post['slug']}.html")
        with open(post_path, "w", encoding="utf-8") as f:
            f.write(
                template_env.get_template(cfg.get_blog_template(config)).render(
                    post=post,
                    active_page=blog_section,
                    canonical_path=canonical_path,
                    data=data,
                )
            )


def _generate_feeds(config, blog_dir, blog_section, posts):
    fg = FeedGenerator()
    fg.title(f"{cfg.get_site_title(config)} - {blog_section}")
    fg.description(cfg.get_site_description(config))
    fg.id(cfg.get_site_url(config))
    fg.link(href=f"{cfg.get_site_url(config)}/{blog_section}", rel="alternate")
    fg.language("en")

    author_name = cfg.get_author_name(config)
    if author_name:
        fg.author(
            name=author_name,
            email=cfg.get_author_email(config) or None,
            uri=cfg.get_site_url(config),
        )

    for post in posts:
        fe = fg.add_entry()
        fe.title(post["title"])
        fe.link(href=f"{cfg.get_site_url(config)}/{blog_section}/{post['slug']}")
        fe.id(f"{cfg.get_site_url(config)}/{blog_section}/{post['slug']}")
        fe.description(post["content"])
        if post.get("created"):
            fe.pubDate(post["created"])
            fe.updated(post["created"])

    formats = cfg.get_feed_formats(config)
    if "rss" in formats:
        with open(os.path.join(blog_dir, "rss.xml"), "wb") as f:
            f.write(fg.rss_str(pretty=True))
    if "atom" in formats:
        with open(os.path.join(blog_dir, "atom.xml"), "wb") as f:
            f.write(fg.atom_str(pretty=True))
