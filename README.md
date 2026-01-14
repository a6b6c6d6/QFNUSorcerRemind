🎓🤖 QFNUSorcerRemind

曲师大教务成绩自动监控 & 钉钉推送机器人

基于 GitHub Actions 的零成本成绩监控方案
成绩一出，立即 加密存储并推送到钉钉

---

✨ 功能一览

· ✅ 自动监控：每小时自动登录教务系统，抓取最新成绩
· ✅ 即时推送：发现新成绩立即加密落盘，并推送到钉钉群/私聊
· ✅ 安全加密：AES-256-GCM + RSA-2048 混合加密，仓库仅存密文
· ✅ 零成本托管：基于 GitHub Actions，无需服务器
· ✅ 智能对比：仅推送「新出现的成绩」，避免重复提醒

---

🚀 快速上手（3 分钟部署）

1️⃣ 获取项目代码

```bash
git clone https://github.com/a6b6c6d6/QFNUSorcerRemind.git
cd QFNUSorcerRemind
```

2️⃣ 生成密钥对（仅需一次）

```bash
# 生成 RSA 私钥
openssl genrsa -out private.pem 2048

# 生成对应公钥
openssl rsa -in private.pem -pubout -out public.pem
```

转换为单行字符串（用于 GitHub Secrets）

Windows PowerShell：

```powershell
(Get-Content public.pem -Raw) -replace "`r?`n", "\n"
(Get-Content private.pem -Raw) -replace "`r?`n", "\n"
```

Linux / macOS：

```bash
awk 'NF {printf "%s\\n", $0}' public.pem
awk 'NF {printf "%s\\n", $0}' private.pem
```

3️⃣ 配置 GitHub Secrets

进入仓库：Settings → Secrets and variables → Actions → New repository secret

添加以下 6 个变量：

变量名 说明 示例
STU_ID 教务系统学号 123456
STU_PWD 教务系统密码 123456!
DING_TOKEN 钉钉机器人 access_token xxxxxxxx（只要后面ID的内容）
DING_SECRET 钉钉机器人加签密钥（未开启可留空） SECxxxxx
RSA_PUBLIC_PEM 公钥（单行，含 \n） -----BEGIN PUBLIC KEY-----\nMIIBI...\n-----END PUBLIC KEY-----
RSA_PRIVATE_PEM 私钥（单行，含 \n） -----BEGIN RSA PRIVATE KEY-----\nMIIEp...\n-----END RSA PRIVATE KEY-----

4️⃣ 启用 Actions 写权限

进入：Settings → Actions → General

在 Workflow permissions 中选择：

☑️ Read and write permissions

点击 Save

5️⃣ 手动触发测试

1. 打开仓库的 Actions 页面
2. 选择 成绩监控 工作流
3. 点击 Run workflow

运行成功后将会：

· 自动提交 data/encrypted.json
· 钉钉收到测试推送（若存在新成绩）

---

⚙️ 自定义配置

需求 修改位置
调整抓取间隔 .github/workflows/gpa.yml 中的 cron
更换推送渠道 替换 ding.py（可改为企业微信 / 飞书 / Server 酱）
修改加密方式 修改 crypto_util.py（纯 RSA / 纯 AES）

---

❓ 常见问题

问题 解决方案
Actions 403 无法 push 确认已开启 Read and write permissions，并使用 ${{ secrets.GITHUB_TOKEN }}
验证码识别失败 程序自动重试 3 次，可替换为打码平台
钉钉收不到消息 检查 TOKEN / SECRET，确认是否开启「加签」
本地测试运行 在 gpa.py 顶部直接填写账号密码

---

📁 项目结构

```
.
├── .github/workflows/
│   └── gpa.yml              # GitHub Actions 定时任务
├── gpa.py                   # 主程序：抓取 → 加密 → 推送
├── jwxtdl.py                # 登录模块 + 验证码识别
├── crypto_util.py           # AES-GCM + RSA 混合加密
├── ding.py                  # 钉钉 Markdown 推送
├── requirements.txt         # Python 依赖
└── data/
    └── encrypted.json       # 加密后的成绩快照
```

---

⚠️ 免责声明

本项目仅供 学习与技术交流 使用。
请遵守所在学校相关规章制度，使用者需自行承担全部风险。
作者不对因使用本项目造成的任何直接或间接损失负责。

---

⭐ 如果这个项目对你有帮助，欢迎 Star 支持！
