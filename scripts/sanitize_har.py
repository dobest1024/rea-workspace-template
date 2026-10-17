#!/usr/bin/env python3
"""把 HAR 转为结构分析副本；所有业务值被替换，不用于回放。"""

import argparse
import json
import os
import sys
from pathlib import Path
from urllib.parse import parse_qsl, urlsplit, urlunsplit

MASK = "[REDACTED]"


def shape(value):
    if isinstance(value, dict):
        return {key: shape(item) for key, item in value.items()}
    if isinstance(value, list):
        return [shape(item) for item in value]
    if value is None:
        return None
    if isinstance(value, bool):
        return False
    if isinstance(value, (int, float)):
        return 0
    return MASK


def names_only(items):
    return [{"name": item["name"], "value": MASK} for item in items]


def media_type(value):
    # 只保留已知媒体类型，移除 boundary 等自定义参数。
    mime = value.split(";", 1)[0].strip().lower()
    known = {"application/json", "application/x-www-form-urlencoded", "multipart/form-data",
             "text/plain", "text/html", "application/octet-stream"}
    return mime if mime in known else "application/octet-stream"


def clean_body(body):
    output = {"mimeType": media_type(body.get("mimeType", ""))}
    if "params" in body:
        output["params"] = names_only(body["params"])
    # 不解码 base64、二进制、HTML 或未知正文，也不复制扩展字段。
    if body.get("encoding") is None and output["mimeType"] == "application/json":
        try:
            output["text"] = json.dumps(shape(json.loads(body["text"])), ensure_ascii=False)
        except (KeyError, ValueError, TypeError):
            output["text"] = MASK
    elif "text" in body:
        output["text"] = MASK
    return output


def sanitize(document):
    entries = []
    for entry in document["log"]["entries"]:
        request, response = entry["request"], entry["response"]
        url = urlsplit(request["url"])
        if url.scheme not in ("http", "https") or not url.hostname:
            raise ValueError("只接受绝对 HTTP(S) URL")
        host = url.hostname
        if ":" in host:
            host = f"[{host}]"
        if url.port is not None:
            host += f":{url.port}"
        query = list(request.get("queryString", []))
        observed_names = {item["name"] for item in query}
        query += [{"name": key} for key, _ in parse_qsl(url.query, keep_blank_values=True)
                  if key not in observed_names]
        clean_request = {
            "method": request["method"],
            "url": urlunsplit((url.scheme, host, url.path, "", "")),
            "httpVersion": "HTTP/1.1",
            "cookies": [], "headers": names_only(request.get("headers", [])),
            "queryString": names_only(query), "headersSize": -1, "bodySize": -1,
        }
        if "postData" in request:
            clean_request["postData"] = clean_body(request["postData"])
        content = clean_body(response.get("content", {}))
        content["size"] = len(content.get("text", "").encode("utf-8"))
        entries.append({
            "startedDateTime": "1970-01-01T00:00:00.000Z", "time": 0,
            "request": clean_request,
            "response": {
                "status": response["status"], "statusText": "", "httpVersion": "HTTP/1.1",
                "cookies": [], "headers": names_only(response.get("headers", [])),
                "content": content, "redirectURL": "", "headersSize": -1, "bodySize": -1,
            },
            "cache": {}, "timings": {"send": 0, "wait": 0, "receive": 0},
        })
    if not entries:
        raise ValueError("HAR 没有记录")
    return {"log": {"version": "1.2", "creator": {"name": "rea-template-sanitizer", "version": "1"},
                    "comment": "Shape-only: values/timing removed. Paths and names require human review.",
                    "entries": entries}}


def write_sanitized(source, destination):
    cleaned = sanitize(json.loads(source.read_text(encoding="utf-8")))
    # O_EXCL 同时拒绝覆盖已有文件、原件和软链接。
    fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        json.dump(cleaned, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    try:
        write_sanitized(args.source, args.destination)
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
        # JSONDecodeError 中可能带原始内容，错误输出不包含输入值。
        print(f"脱敏失败（{type(error).__name__}）：检查 HAR 结构及路径，输出不能已存在。", file=sys.stderr)
        return 1
    print("结构副本已生成；导入前人工检查 URL 主机/路径、字段名中是否含身份信息。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
