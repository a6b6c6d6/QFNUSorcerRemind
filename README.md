QFNUSorcerRemind

曲师大教务成绩自动监控 & 钉钉推送机器人 🎓🤖

✨ 功能一览

- ✅ 自动监控：每小时自动登录教务系统，抓取最新成绩
- ✅ 即时推送：发现新成绩立即加密落盘，并推送到钉钉群/私聊
- ✅ 安全加密：采用 AES-256-GCM + RSA-2048 混合加密，仓库只存储密文，即使数据丢失也无法解密
- ✅ 零成本托管：基于 GitHub Actions，无需额外服务器
- ✅ 智能对比：增量对比，只推送「新出现的成绩」

🚀 快速上手（3分钟部署）

1. 获取项目代码

Fork 或克隆本仓库：

git clone https://github.com/a6b6c6d6/QFNUSorcerRemind.git
cd QFNUSorcerRemind

2. 生成密钥对（仅需一次）

# 生成RSA私钥
openssl genrsa -out private.pem 2048
# 生成对应公钥
openssl rsa -in private.pem -pubout -out public.pem

Windows 用户可使用 Git Bash 或运行项目内的 Python 脚本生成。
转换格式（将换行符替换为 
"\n"）：

PowerShell：

(Get-Content public.pem -Raw) -replace "`r?`n", "\n"
(Get-Content private.pem -Raw) -replace "`r?`n", "\n"

Linux/macOS：

awk 'NF {printf "%s\\n", $0}' public.pem
awk 'NF {printf "%s\\n", $0}' private.pem

3. 配置 GitHub Secrets

进入仓库 Settings → Secrets and variables → Actions → New repository secret，添加以下 6 个变量：

变量名 说明 示例

"STU_ID" 教务系统学号 
"123456"

"STU_PWD" 教务系统密码 
"123456!"

"DING_TOKEN" 钉钉机器人 access_token 
"你的access_token"

"DING_SECRET" 机器人加签密钥（未开启可留空） 
"你的密钥"

"RSA_PUBLIC_PEM" 公钥一行字符串（含 
"\n"） 
"-----BEGIN PUBLIC KEY-----\nMIIBI...AQAB\n-----END PUBLIC KEY-----"

"RSA_PRIVATE_PEM" 私钥一行字符串（含 
"\n"） 
"-----BEGIN RSA PRIVATE KEY-----\nMIIEp...Q==\n-----END RSA PRIVATE KEY-----"

4. 启用 Actions 写权限

进入仓库 Settings → Actions → General，找到 Workflow permissions，勾选 "Read and write permissions"，然后保存。

5. 手动触发测试

进入仓库的 Actions 页面，选择 「成绩监控」 工作流，点击 Run workflow。运行成功后，系统会自动提交 
"data/encrypted.json" 文件，并在钉钉收到第一条测试推送（如果已有成绩记录）。

⚙️ 自定义配置

需求 修改位置
调整抓取间隔 
".github/workflows/gpa.yml" 第 4 行 
"cron: "0 * * * *""
更换推送渠道 替换 
"ding.py" 为企业微信/飞书/Server 酱等接口
修改加密方式 替换 
"crypto_util.py" 为纯 RSA 或纯 AES 实现

❓ 常见问题

现象 解决方案
Actions 403 无法 push 确认已开启「Read and write permissions」；检查 workflow 中是否包含 
"token: ${{ secrets.GITHUB_TOKEN }}"
验证码识别失败 程序自动重试 3 次；如持续失败可替换为打码平台接口
钉钉收不到消息 检查 TOKEN/SECRET 是否正确；确认机器人已开启「加签」选项
本地测试运行 将账号密码直接写入 
"gpa.py" 顶部变量即可本地执行

📁 项目结构

.
├── .github/workflows/
│   └── gpa.yml              # GitHub Actions 定时任务配置
├── gpa.py                   # 主程序：抓取 → 加密 → 推送
├── jwxtdl.py               # 登录模块 + 验证码识别
├── crypto_util.py          # AES-GCM + RSA 混合加密工具
├── ding.py                 # 钉钉 Markdown 消息推送
├── requirements.txt        # Python 依赖列表
└── data/                   # 数据目录（自动生成）
    └── encrypted.json      # 加密后的成绩快照

⚠️ 免责声明

本项目仅供学习与技术交流使用，请勿用于商业或非法用途。使用者应遵守所在学校相关规章制度，并自行承担使用风险。作者不对因使用本项目而产生的任何直接或间接损失负责。

如果这个项目对你有帮助，欢迎点个 ⭐ Star 支持！
