import os
import tomllib
from pathlib import Path

import yaml


def load_config(config_path="stapler.toml"):
    path = Path(config_path)

    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")

    if path.suffix == ".toml":
        with open(path, "rb") as f:
            config = tomllib.load(f)
    elif path.suffix in [".yaml", ".yml"]:
        with open(path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}
    else:
        raise ValueError(f"Unsupported config format: {path.suffix}. Use .toml or .yaml")

    site = config.get("site", {})
    if not site.get("url"):
        raise ValueError("site.url is required in configuration")
    if not site.get("title"):
        raise ValueError("site.title is required in configuration")

    return config


def get_site_dir(config):
    return config.get("directories", {}).get("site", "site")


def get_build_dir(config):
    return config.get("directories", {}).get("build", "build")


def get_build_dev_dir(config):
    return config.get("directories", {}).get("build_dev", "build-dev")


def get_templates_dir(config):
    templates = config.get("directories", {}).get("templates", "templates")
    return os.path.join(get_site_dir(config), templates)


def get_blog_dir(config):
    if not has_blog(config):
        return None
    blog = config.get("directories", {}).get("blog", "blog")
    return os.path.join(get_site_dir(config), blog)


def has_blog(config):
    return config.get("features", {}).get("blog", {}).get("enabled", False)


def has_sitemap(config):
    return config.get("features", {}).get("sitemap", True)


def has_feeds(config):
    feeds_config = config.get("features", {}).get("feeds", True)
    if isinstance(feeds_config, bool):
        return feeds_config and has_blog(config)
    return (feeds_config.get("rss", True) or feeds_config.get("atom", True)) and has_blog(config)


def get_feed_formats(config):
    if not has_feeds(config):
        return []
    feeds_config = config.get("features", {}).get("feeds", True)
    if isinstance(feeds_config, bool):
        return ["rss", "atom"] if feeds_config else []
    formats = []
    if feeds_config.get("rss", True):
        formats.append("rss")
    if feeds_config.get("atom", True):
        formats.append("atom")
    return formats


def get_base_path(config):
    return config.get("site", {}).get("base_path", "")


def get_site_url(config):
    return config["site"]["url"]


def get_site_title(config):
    return config["site"]["title"]


def get_site_description(config):
    return config.get("site", {}).get("description", "")


def get_author_name(config):
    return config.get("site", {}).get("author", {}).get("name", "")


def get_author_email(config):
    return config.get("site", {}).get("author", {}).get("email", "")


def get_markdown_extensions(config):
    return config.get("markdown", {}).get("extensions", ["meta", "tables", "fenced_code"])


def get_blog_template(config):
    return config.get("features", {}).get("blog", {}).get("template", "blog_post.html")


def get_blog_index_template(config):
    return config.get("features", {}).get("blog", {}).get("index_template", "blog_index.html")


def get_default_template(config):
    return config.get("templates", {}).get("default", "base.html")
