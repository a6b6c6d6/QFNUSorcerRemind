import os 
from datetime import datetime, timezone, timedelta
from typing import Dict, Any 
import jwxtdl 
from crypto_util import encrypt_dict, decrypt_dict 
from ding import send_md 

# ---------- 配置 ---------- 
DATA_FILE = "data/encrypted.json" 
STU_ID = os.getenv("STU_ID") 
STU_PWD = os.getenv("STU_PWD") 
# -------------------------- 

# ---------- 工具 ---------- 
def load_last() -> Dict[str, Any]:
    """读取上一次的加密成绩；文件不存在或解密失败返回空 dict"""
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, encoding="utf-8") as f:
        content = f.read().strip()
        if not content:
            return {}
        try:
            return decrypt_dict(content)
        except Exception:
            print("⚠️ 历史成绩解密失败，视为首次运行")
            return {}

def save_current(data: Dict[str, Any]) -> None:
    """加密并保存本次成绩"""
    os.makedirs("data", exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        f.write(encrypt_dict(data))

def get_beijing_time():
    """获取北京时间"""
   
    beijing_tz = timezone(timedelta(hours=8))
    return datetime.now(beijing_tz)
    

def diff_and_notify(old: Dict[str, Any], new: Dict[str, Any]) -> bool:
    old_map = {c["course_name"]: c for c in old.get("courses", [])}
    changed_blocks = []
    
    for c in new["courses"]:
        old_c = old_map.get(c["course_name"])
        if not old_c or old_c["grade"] != c["grade"]:
            block = "\n".join([
                f"📘 **{c['course_name']}**",
                f"🎯 成绩：**{c['grade']}**", 
                f"⭐ 绩点：**{c['gpa']}**",
            ])
            changed_blocks.append(block)
    
    if not changed_blocks:
        print("ℹ️ 暂无新成绩，不推送通知")
        return False
    
    # 使用双换行符分隔不同的成绩条目
    grade_content = "\n\n".join(changed_blocks)
    
    now_time = get_beijing_time().strftime("%Y-%m-%d %H:%M")
    
    # 重新组织消息结构
    lines = [
        "## 🚀 成绩更新提醒",
        "",
        "✨ **检测到新的成绩发布：**", 
        "",
        grade_content,  # 这里会包含成绩条目，条目之间用双换行分隔
        "",
        "──────────────",
        f"📊 **当前平均绩点：{new.get('average_gpa', 0)}**",
        f"🕒 检测时间：{now_time}（北京时间）",
    ]
    
    send_md("成绩更新", "\n".join(lines))
    print("✅ 已推送钉钉通知")
    return True


# ---------- 业务 ---------- 
def suan(html: str) -> Dict[str, Any]:
    """解析成绩页面 → 计算平均绩点"""
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
        gpa_cell = cells[9].text_content().strip()
        name = cells[3].text_content().strip() if len(cells) > 3 else ""
        
        try:
            grade = int(grade_cell) if grade_cell.isdigit() else grade_map.get(grade_cell, 0)
            gpa = float(gpa_cell) if gpa_cell else 0.0
        except Exception:
            grade, gpa = 0, 0.0
            
        courses.append({
            "course_name": name,
            "grade": grade,
            "gpa": gpa
        })
    
    avg_gpa = sum(c["gpa"] for c in courses) / len(courses) if courses else 0
    return {
        "courses": courses,
        "average_gpa": round(avg_gpa, 2)
    }

def a() -> Dict[str, Any]:
    """主抓取逻辑"""
    url = "http://zhjw.qfnu.edu.cn/jsxsd/kscj/cjcx_list"  # 补充URL
    payload = {
        "kksj": "",
        "kcxz": "", 
        "kcmc": "",
        "xsfs": "all"
    }
    
    print("🔐 正在登录教务系统 ...")
    session = jwxtdl.deng(STU_ID, STU_PWD)
    print("🌐 正在抓取成绩页面 ...")
    resp = session.post(url, data=payload)
    
    if "未查询到数据" in resp.text:
        print("❌ 未查询到成绩")
        return {}
    
    print("📑 正在解析成绩数据 ...")
    result = suan(resp.text)
    print("🔍 正在对比历史成绩 ...")
    
    old = load_last()
    if diff_and_notify(old, result):
        save_current(result)
        print("💾 成绩有变化，已保存")
    else:
        print("💤 成绩无变化，不落盘")
    
    return result

# ---------- 入口 ---------- 
if __name__ == "__main__":
    a()
