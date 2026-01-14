import os
import json
import time
from typing import Dict, Any

import jwxtdl        
from crypto_util import encrypt_dict, decrypt_dict
from ding import send_md

# ---------- 配置 ----------
DATA_FILE = "data/encrypted.json"
STU_ID    = os.getenv("STU_ID")
STU_PWD   = os.getenv("STU_PWD")
# --------------------------
def load_last() -> Dict[str, Any]:
    """读取上一次的加密成绩；文件不存在返回空 dict"""
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, encoding="utf-8") as f:
        content = f.read().strip()
    # 如果文件是空的或格式明显不对，也返回空
    if not content or "|" not in content:
        return {}
    try:
        return decrypt_dict(content)
    except Exception:
        return {}


def save_current(data: Dict[str, Any]) -> None:
    """加密并保存本次成绩"""
    os.makedirs("data", exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        f.write(encrypt_dict(data))

def diff_and_notify(old: Dict[str, Any], new: Dict[str, Any]) -> bool:
    """对比新旧成绩，有变化则推送钉钉"""
    old_map = {c["course_name"]: c for c in old.get("courses", [])}
    new_map = {c["course_name"]: c for c in new["courses"]}

    lines = [
        "## 🎉 检测到新成绩",
        "| 课程 | 成绩 | 绩点 |",
        "| --- | --- | --- |"
    ]
    changed = False
    for name, info in new_map.items():
        if name not in old_map or old_map[name]["grade"] != info["grade"]:
            changed = True
            lines.append(f"| {name} | {info['grade']} | {info['gpa']} |")

    if changed:
        send_md("成绩更新", "\n".join(lines))
    return changed

# ---------- 业务 ----------
def suan(html: str) -> Dict[str, Any]:
    """
    解析成绩页面 → 计算平均绩点
    与你本地原逻辑完全一致，仅把文件路径改成变量
    """
    from lxml import html as lhtml

    tree = lhtml.fromstring(html)
    rows = tree.xpath("//table[@id='dataList']//tr[position()>1]")

    grade_map = {"优": 95, "良": 85, "中": 75, "及格": 65, "不及格": 0, "缺考": 0}
    courses = []

    for row in rows:
        cells = row.xpath("td")
        if len(cells) < 2:
            continue
        grade_cell = cells[5].text_content().strip()
        gpa_cell   = cells[9].text_content().strip()
        name       = cells[3].text_content().strip() if len(cells) > 3 else ""

        try:
            grade = int(grade_cell) if grade_cell.isdigit() else grade_map.get(grade_cell, 0)
            gpa   = float(gpa_cell) if gpa_cell else 0.0
        except Exception:
            grade, gpa = 0, 0.0

        courses.append({"course_name": name, "grade": grade, "gpa": gpa})

    avg_gpa = sum(c["gpa"] for c in courses) / len(courses) if courses else 0
    return {"courses": courses, "average_gpa": round(avg_gpa, 2)}

def a() -> Dict[str, Any]:
    """主抓取逻辑"""
    url = "http://zhjw.qfnu.edu.cn/jsxsd/kscj/cjcx_list"
    payload = {
        "kksj": "",  # 想抓全部可改成 ""
        "kcxz": "",
        "kcmc": "",
        "xsfs": "all"
    }
    session = jwxtdl.deng(STU_ID, STU_PWD)
    resp = session.post(url, data=payload)
    if "未查询到数据" in resp.text:
        print("❌ 未查询到成绩")
        return {}
    result = suan(resp.text)

    # 增量对比
    old = load_last()
    save_current(result)
    diff_and_notify(old, result)
    return result

# ---------- 入口 ----------
if __name__ == "__main__":
    a()
