#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 dist/ 里的离线包（PDF / EPUB / 单页 HTML）发布到 GitHub Release 的固定标签 `epub-latest`。

为什么用固定标签：站点和 README 里的下载链接写死成
`https://github.com/NiceCao/HowToWorkBetter/releases/download/epub-latest/HowToWorkBetter.pdf`，
以后每轮只换资源、不换链接 —— 读者收藏的链接不会失效。

用法：
    python3 tools/publish_release.py            # 上传 dist/ 下三份，并把 release 设为公开
    python3 tools/publish_release.py --dry-run  # 只检查文件与令牌，不联网上传

令牌：~/.secrets/github_token（600，不进 git、不打印）。同名资源会先删旧再传新（保证内容是最新的）。
"""
import json
import os
import pathlib
import sys
import urllib.error
import urllib.request

REPO = "NiceCao/HowToWorkBetter"
TAG = "epub-latest"
TOKEN_PATH = pathlib.Path.home() / ".secrets" / "github_token"
ASSETS = [
    ("dist/HowToWorkBetter.pdf", "application/pdf"),
    ("dist/HowToWorkBetter.epub", "application/epub+zip"),
    ("dist/HowToWorkBetter.html", "text/html; charset=utf-8"),
]


def api(url, method="GET", data=None, headers=None, raw=False):
    tok = TOKEN_PATH.read_text(encoding="utf-8").strip()
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {tok}")
    req.add_header("Accept", "application/vnd.github+json")
    if not raw:
        req.add_header("Content-Type", "application/json")
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    with urllib.request.urlopen(req, timeout=120) as r:
        body = r.read()
    if not body:
        return None  # DELETE 之类返回 204 空体，不能当作 JSON 解析
    return json.loads(body) if not raw else body


def main():
    root = pathlib.Path(__file__).resolve().parent.parent
    dry = "--dry-run" in sys.argv
    files = []
    for rel, ctype in ASSETS:
        p = root / rel
        if not p.exists():
            print(f"缺文件：{rel}（先跑 tools/build_dist.py）")
            return 1
        files.append((p, ctype))
        print(f"{rel}  {p.stat().st_size/1024:.0f} KB")
    if dry:
        print("dry-run：文件齐了，未上传")
        return 0

    # 找已有 release（草稿不会被 /tags/ 接口返回，所以用列表接口找）
    rel = next((r for r in api(f"https://api.github.com/repos/{REPO}/releases?per_page=100")
                if r["tag_name"] == TAG), None)
    if rel is None:
        rel = api(
            f"https://api.github.com/repos/{REPO}/releases",
            method="POST",
            data=json.dumps({"tag_name": TAG, "name": "离线包（PDF / EPUB / 单文件 HTML）",
                             "body": "下载：PDF、EPUB、离线单文件 HTML。内容随主线更新，链接固定。",
                             "draft": False}).encode(),
        )
    rel_id = rel["id"]

    # 同名资源先删旧（GitHub 不允许同名重复上传）
    for a in api(rel["assets_url"]):
        api(a["url"], method="DELETE")
        print(f"已删旧资源 {a['name']}")

    upload_url = rel["upload_url"].split("{")[0]
    for p, ctype in files:
        data = p.read_bytes()
        r = api(f"{upload_url}?name={p.name}", method="POST", data=data,
                headers={"Content-Type": ctype})
        print(f"已上传 {r['name']}  {r['size']/1024:.0f} KB  {r['browser_download_url']}")

    rel = api(f"https://api.github.com/repos/{REPO}/releases/{rel_id}",
              method="PATCH", data=json.dumps({"draft": False}).encode())
    print(f"release 已公开：{rel['html_url']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
