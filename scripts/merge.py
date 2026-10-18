#!/usr/bin/env python3
"""Fetch, merge and dedupe Loon-format domain rule lists.

Sources:
  - juner922/muse-loon-rules (MuseAI.list)
  - VPSDance/ai-proxy-rules (rules/loon/meta-ai.list)

Output: MuseAI-merged.list (repo root), deterministic ordering for clean diffs.
"""
import datetime
import sys
import urllib.request

SOURCES = [
    ("juner922/muse-loon-rules",
     "https://raw.githubusercontent.com/juner922/muse-loon-rules/main/MuseAI.list"),
    ("VPSDance/ai-proxy-rules",
     "https://cdn.jsdelivr.net/gh/VPSDance/ai-proxy-rules@main/rules/loon/meta-ai.list"),
]

OUTPUT = "MuseAI-merged.list"
OUTPUT_ARRS = "MuseAI.arrs"
ARRS_NAME = "MuseAI"


def fetch(name, url):
    req = urllib.request.Request(url, headers={"User-Agent": "muse-rules-merge/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        text = r.read().decode("utf-8", errors="replace")
    print(f"fetched {name}: {len(text)} chars", flush=True)
    return text


def parse(text):
    """Return (suffixes:set, domains:set). Only DOMAIN-SUFFIX / DOMAIN handled."""
    suffixes, domains = set(), set()
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 2:
            continue
        kind, value = parts[0].upper(), parts[1].lower()
        if kind == "DOMAIN-SUFFIX" and value:
            suffixes.add(value)
        elif kind == "DOMAIN" and value:
            domains.add(value)
    return suffixes, domains


def covered_by_suffix(name, suffixes):
    return any(name == s or name.endswith("." + s) for s in suffixes)


def main():
    all_suffixes, all_domains = set(), set()
    for name, url in SOURCES:
        try:
            text = fetch(name, url)
        except Exception as e:  # noqa: BLE001 - one bad source must not kill the merge
            print(f"WARN: failed to fetch {name}: {e}", file=sys.stderr, flush=True)
            continue
        s, d = parse(text)
        all_suffixes |= s
        all_domains |= d

    if not all_suffixes and not all_domains:
        print("ERROR: no rules fetched, refusing to write empty output",
              file=sys.stderr, flush=True)
        sys.exit(1)

    # Drop suffixes shadowed by a broader suffix.
    suffixes = sorted(s for s in all_suffixes if not any(
        s != o and (s == o or s.endswith("." + o)) for o in all_suffixes))
    suffix_set = set(suffixes)
    # Drop exact domains already covered by a suffix.
    domains = sorted(d for d in all_domains if not covered_by_suffix(d, suffix_set))

    today = datetime.date.today().isoformat()
    write_list(suffixes, domains, today)
    write_arrs(suffixes, domains, today)

def write_list(suffixes, domains, today):
    lines = [
        "# Muse AI (Meta) - 合并分流规则集 (自动生成, 每日更新)",
        "#",
        "# 来源:",
        "# - juner922/muse-loon-rules (MuseAI.list)",
        "# - VPSDance/ai-proxy-rules (rules/loon/meta-ai.list)",
        "#",
        "# 重要: Muse 有地区限制。域名全走代理仍可能提示\"尚未在你的国家或地区开放\",",
        "# 此时是出口 IP 问题 —— 需要美区原生/家宽 IP (机房 IP、广播 IP 会被排队)。",
        f"# 生成日期: {today}",
        "",
        "# === DOMAIN-SUFFIX ===",
        *[f"DOMAIN-SUFFIX,{s}" for s in suffixes],
        "",
        "# === DOMAIN (精确域名, 未被上方后缀覆盖) ===",
        *[f"DOMAIN,{d}" for d in domains],
        "",
    ]
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"wrote {OUTPUT}: {len(suffixes)} suffixes, {len(domains)} domains", flush=True)


def write_arrs(suffixes, domains, today):
    """Write the Anywhere (.arrs) rule set.

    Anywhere rule types: 0=IPv4 CIDR, 1=IPv6 CIDR, 2=domain suffix, 3=keyword.
    It has no exact-domain match, so DOMAIN entries are emitted as suffix
    rules too (same as the official anywhere-rules converter does).
    No `routing` header: the user picks their own proxy policy on import.
    """
    rules = [f"2, {s}" for s in suffixes] + [f"2, {d}" for d in domains]
    source_urls = [url for _, url in SOURCES]
    lines = [
        f"# NAME: {ARRS_NAME}",
        "# GENERATED-FOR: Anywhere Routing Rule Set",
        "# DESCRIPTION: Meta Muse AI 分流规则（Anywhere 专用，自动生成，每日更新）",
        f"# RULES: {len(rules)}",
        "# SKIPPED: 0",
        "# SOURCES:",
        *[f"# - {u}" for u in source_urls],
        "#",
        "# 重要: Muse 有地区限制。域名全走代理仍可能提示\"尚未在你的国家或地区开放\"，",
        "# 此时是出口 IP 问题 —— 需要美区原生/家宽 IP（机房 IP、广播 IP 会被排队）。",
        "# 导入后请手动把该规则集指向你的美国节点策略组。",
        f"# 生成日期: {today}",
        "",
        f"name = {ARRS_NAME}",
        *rules,
        "",
    ]
    with open(OUTPUT_ARRS, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"wrote {OUTPUT_ARRS}: {len(rules)} rules", flush=True)


if __name__ == "__main__":
    main()
