import os
import shutil
import tempfile
import time

from colorama import Fore, Style
from jinja2 import Environment, FileSystemLoader
from markdown import Markdown

from .. import config as cfg
from ..plugins import blog, sitemap
from .utils import get_data, infer_page_metadata, parse_front_matter, warn


def build_site(config, output_dir=None, is_dev=False):
    if output_dir is None:
        output_dir = cfg.get_build_dev_dir(config) if is_dev else cfg.get_build_dir(config)

    start_time = time.time()
    print(f"{Fore.CYAN}=> Building site <={Style.RESET_ALL}")

    print("> Setting up environment... ", end="", flush=True)
    setup_start = time.time()
    temp_build_dir = tempfile.mkdtemp()

    loader_paths = [cfg.get_site_dir(config)]
    templates_dir = cfg.get_templates_dir(config)
    if os.path.exists(templates_dir):
        loader_paths.append(templates_dir)
    template_env = Environment(loader=FileSystemLoader(loader_paths))

    md_processor = Markdown(extensions=cfg.get_markdown_extensions(config))
    data = get_data()

    setup_time = time.time() - setup_start
    print(f"{Fore.GREEN}done ({setup_time * 1000:.0f}ms){Style.RESET_ALL}")

    posts = []
    if cfg.has_blog(config):
        print("> Processing blog posts... ", end="", flush=True)
        blog_start = time.time()
        posts = blog.process_blog(config, template_env, md_processor, data, temp_build_dir)
        blog_time = time.time() - blog_start
        print(f"{Fore.GREEN}{len(posts)} posts ({blog_time * 1000:.0f}ms){Style.RESET_ALL}")

    print("> Processing site files... ", end="", flush=True)
    files_start = time.time()
    _process_site_files(config, template_env, md_processor, data, temp_build_dir)
    files_time = time.time() - files_start
    print(f"{Fore.GREEN}done ({files_time * 1000:.0f}ms){Style.RESET_ALL}")

    if cfg.has_sitemap(config):
        print("> Generating sitemap... ", end="", flush=True)
        sitemap_start = time.time()
        sitemap.generate_sitemap(config, temp_build_dir, posts)
        sitemap_time = time.time() - sitemap_start
        print(f"{Fore.GREEN}done ({sitemap_time * 1000:.0f}ms){Style.RESET_ALL}")

    print("> Finalizing build... ", end="", flush=True)
    finalize_start = time.time()
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    shutil.move(temp_build_dir, output_dir)
    finalize_time = time.time() - finalize_start
    print(f"{Fore.GREEN}done ({finalize_time * 1000:.0f}ms){Style.RESET_ALL}")

    total_time = time.time() - start_time
    print(f"{Fore.GREEN}Build complete in {total_time * 1000:.0f}ms!{Style.RESET_ALL}\n")


def _process_site_files(config, template_env, md_processor, data, build_dir):
    seen_outputs = {}
    exclude_dirs = [cfg.get_templates_dir(config)]
    blog_dir = cfg.get_blog_dir(config)
    if blog_dir:
        exclude_dirs.append(blog_dir)

    site_dir = cfg.get_site_dir(config)
    for root, dirs, files in os.walk(site_dir):
        dirs[:] = [d for d in dirs if os.path.join(root, d) not in exclude_dirs]

        for filename in files:
            filepath = os.path.join(root, filename)

            if any(filepath.startswith(excluded) for excluded in exclude_dirs):
                continue
            if filename.startswith("."):
                continue

            rel_path = os.path.relpath(filepath, site_dir)

            if rel_path.endswith(".md"):
                output_path = os.path.join(build_dir, rel_path[:-3] + ".html")
            else:
                output_path = os.path.join(build_dir, rel_path)

            if output_path in seen_outputs:
                warn(f"Duplicate output: {output_path} (from {filepath} and {seen_outputs[output_path]})")
            seen_outputs[output_path] = filepath

            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            if filepath.endswith(".md"):
                _process_markdown_file(config, template_env, md_processor, data, filepath, output_path, rel_path)
            elif filepath.endswith(".html"):
                _process_html_file(config, template_env, data, filepath, output_path, rel_path)
            else:
                shutil.copy2(filepath, output_path)


def _process_markdown_file(config, template_env, md_processor, data, filepath, output_path, rel_path):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    metadata, markdown_content = parse_front_matter(content)
    html_content = md_processor.convert(markdown_content)
    md_processor.reset()

    template_name = metadata.get("template")
    if not template_name:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        return

    try:
        active_page, canonical_path = infer_page_metadata(rel_path, cfg.get_base_path(config))

        page_data = {"content": html_content}
        page_data.update(metadata)
        if "active_page" not in page_data:
            page_data["active_page"] = active_page
        if "canonical_path" not in page_data:
            page_data["canonical_path"] = canonical_path

        template = template_env.get_template(template_name)
        rendered = template.render(page=page_data, data=data)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(rendered)
    except Exception as e:
        warn(f"Failed to render {filepath}: {e}")


def _process_html_file(config, template_env, data, filepath, output_path, rel_path):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    metadata, html_content = parse_front_matter(content)

    if metadata:
        template_name = metadata.get("template", cfg.get_default_template(config))
        try:
            active_page, canonical_path = infer_page_metadata(rel_path, cfg.get_base_path(config))

            page_data = {"content": html_content}
            page_data.update(metadata)
            if "active_page" not in page_data:
                page_data["active_page"] = active_page
            if "canonical_path" not in page_data:
                page_data["canonical_path"] = canonical_path

            template = template_env.get_template(template_name)
            rendered = template.render(page=page_data, data=data)
        except Exception as e:
            warn(f"Failed to render {filepath}: {e}")
            return
    else:
        try:
            active_page, canonical_path = infer_page_metadata(rel_path, cfg.get_base_path(config))
            template = template_env.from_string(content)
            rendered = template.render(
                active_page=active_page,
                canonical_path=canonical_path,
                data=data,
            )
        except Exception as e:
            warn(f"Failed to render {filepath}: {e}")
            return

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(rendered)
