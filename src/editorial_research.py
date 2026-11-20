"""Fetch RSS headlines into timestamped idea briefs. No LLM or invented facts."""
import argparse
import datetime as dt
import json
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--limit",type=int,default=8)
    a=p.parse_args()
    feeds=json.loads((ROOT/"editorial/feeds.json").read_text(encoding="utf-8"))["feeds"]
    items=[]; errors=[]
    for feed in feeds:
        try:
            req=urllib.request.Request(feed["url"],headers={"User-Agent":"PSYOPSNEWS-Research/0.3"})
            with urllib.request.urlopen(req,timeout=12) as response:
                data=response.read(2_000_000)
            root=ET.fromstring(data)
            for item in root.findall(".//item")[:a.limit]:
                title=item.findtext("title","").strip()
                link=item.findtext("link","").strip()
                published=item.findtext("pubDate","").strip()
                if title and link:
                    items.append({"feed":feed["name"],"title":title,"url":link,"published":published})
        except Exception as exc:
            errors.append({"feed":feed["name"],"error":str(exc)})
    today=dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out=ROOT/"output";out.mkdir(exist_ok=True)
    payload={"generated_utc":today,"stories":items,"feed_errors":errors,"note":"Headlines only; verify article content before factual scripts."}
    (out/"research.json").write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
    lines=["# PSYOPSNEWS – Nyhetsunderlag",f"Skapat UTC: {today}","","Rubriker är idéunderlag, inte verifierade fullständiga artiklar.",""]
    for item in items:
        lines.extend([f"## {item['title']}",f"Källa: {item['feed']} | {item['published']}",item["url"],""])
    for err in errors:
        lines.append(f"Flödesfel: {err['feed']}: {err['error']}")
    (out/"research.md").write_text("\n".join(lines),encoding="utf-8")
    print(f"Saved {len(items)} headlines, {len(errors)} feed errors")
if __name__=="__main__": main()
