import os
import xml.etree.ElementTree as ET

from .. import config as cfg


def generate_sitemap(config, build_dir, posts):
    urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

    _add_url(urlset, f"{cfg.get_site_url(config)}/")

    if cfg.has_blog(config) and posts:
        blog_section = os.path.basename(cfg.get_blog_dir(config))
        _add_url(urlset, f"{cfg.get_site_url(config)}/{blog_section}/")

        for post in posts:
            lastmod = post["created"].strftime("%Y-%m-%d") if post.get("created") else None
            _add_url(
                urlset,
                f"{cfg.get_site_url(config)}/{blog_section}/{post['slug']}",
                lastmod=lastmod,
            )

    for root, _, files in os.walk(build_dir):
        for filename in files:
            if not filename.endswith(".html"):
                continue
            if filename in ["404.html", "index.html"]:
                continue

            filepath = os.path.join(root, filename)
            rel_path = os.path.relpath(filepath, build_dir)

            if cfg.has_blog(config):
                blog_section = os.path.basename(cfg.get_blog_dir(config))
                if rel_path.startswith(blog_section):
                    continue

            url_path = "/" + rel_path.replace("\\", "/").replace(".html", "")
            _add_url(urlset, f"{cfg.get_site_url(config)}{url_path}")

    tree = ET.ElementTree(urlset)
    ET.indent(tree, space="    ")
    tree.write(
        os.path.join(build_dir, "sitemap.xml"),
        encoding="utf-8",
        xml_declaration=True,
    )


def _add_url(urlset, loc, lastmod=None):
    url = ET.SubElement(urlset, "url")
    ET.SubElement(url, "loc").text = loc
    if lastmod:
        ET.SubElement(url, "lastmod").text = lastmod
