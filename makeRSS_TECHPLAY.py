import requests
import re
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os

def main():
    output_file = "makeRSS_TECHPLAY.xml"
    feed_url = "https://rss.techplay.jp/event/w3c-rss-format/rss.xml"
    include_words = ["生成AI", "ChatGPT", "DX", "自動化", "RPA", "ノーコード", "ローコード", "人工知能"]

    # 既存のRSSフィードを読み込む
    existing_links = set()
    if os.path.exists(output_file):
        tree = ET.parse(output_file)
        root = tree.getroot()
        for item in root.findall(".//item/link"):
            existing_links.add(item.text)
    else:
        root = ET.Element("rss", version="2.0")
        channel = ET.SubElement(root, "channel")
        title = "TECH PLAYの特定のキーワードを含むRSS"
        description = "TECH PLAYから特定のキーワードを含む記事を提供します。"
        ET.SubElement(channel, "title").text = title
        ET.SubElement(channel, "description").text = description
        ET.SubElement(channel, "link").text = "https://example.com"

    response = requests.get(feed_url)
    rss_content = response.text
    channel = root.find("channel")

    items = re.findall(r'<item[^>]*>([\s\S]*?)<\/item>', rss_content)
    for item in items:
        title = re.search(r'<title>(.*?)<\/title>', item).group(1)
        link = re.search(r'<link>(.*?)<\/link>', item).group(1)
        description = re.search(r'<description>([\s\S]*?)<\/description>', item).group(1)
        date = re.search(r'<pubDate>(.*?)<\/pubDate>', item).group(1)

        # 既存のリンクならスキップ
        if link in existing_links:
            continue

        # 含めたいワードが含まれているかチェック
        if any(word in title or word in description for word in include_words):
            new_item = ET.SubElement(channel, "item")
            ET.SubElement(new_item, "title").text = title
            ET.SubElement(new_item, "link").text = link
            ET.SubElement(new_item, "description").text = description
            ET.SubElement(new_item, "pubDate").text = date

    xml_str = ET.tostring(root)
    # 不正なXML文字を取り除く
    xml_str = re.sub(u'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', xml_str.decode()).encode()

    xml_pretty_str = minidom.parseString(xml_str).toprettyxml(indent="  ")

    with open(output_file, "w") as f:
        f.write(xml_pretty_str)

if __name__ == "__main__":
    main()
