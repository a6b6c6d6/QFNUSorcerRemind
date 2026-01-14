QFNUSorcerRemind  

> 曲师大教务成绩自动监控 & 钉钉推送机器人 🎓🤖  

---

功能一览  
- ✅ 每小时自动登录教务系统抓取最新成绩  
- ✅ 发现新成绩立即加密落盘，并推送到钉钉群/私聊  
- ✅ AES-256-GCM + RSA-2048 混合加密，仓库只存密文，丢失也解不开  
- ✅ GitHub Actions 零成本托管，无需服务器  
- ✅ 增量对比，只推送「新出现的成绩」  

---

快速上手（3 分钟部署）

1. Fork / 克隆本仓库

```bash
git clone https://github.com/a6b6c6d6/QFNUSorcerRemind.git
cd QFNUSorcerRemind
```

2. 生成 RSA 密钥对（仅一次）

```bash
openssl genrsa -out private.pem 2048
openssl rsa -in private.pem -pubout -out public.pem
# Windows 可用 Git Bash 或 Python 脚本生成
```

把换行变成 `\n` 后得到一行字符串：

```powershell
(Get-Content public.pem -Raw) -replace "`r?`n", "\n"
(Get-Content private.pem -Raw) -replace "`r?`n", "\n"
```

3. 设置 GitHub Secret
进入仓库 Settings → Secrets and variables → Actions → New repository secret 添加以下 6 项：

变量名	说明	示例	
`STU_ID`	教务系统学号  `123456`	
`STU_PWD`	教务系统密码	`123456!`	
`DING_TOKEN`	钉钉机器人 access_token	`你的access_token`	
`DING_SECRET`	机器人加签密钥（未开启可留空）	`你的`	
`RSA_PUBLIC_PEM`	公钥一行字符串（含 `\n`）	`-----BEGIN PUBLIC KEY-----\nMkiGEF...AQAB\n-----END PUBLIC KEY-----`	
`RSA_PRIVATE_PEM`	私钥一行字符串（含 `\n`）	`-----BEGIN RSA PRIVATE KEY-----\nMBAA...-----END RSA PRIVATE KEY-----`	

4. 启用 Actions 写权限
仓库 → Settings → Actions → General → Workflow permissions → 勾选 "Read and write permissions" → Save。

5. 手动触发一次
进入 Actions 页面 → 选择「成绩监控」→ Run workflow → 运行成功后能看到 `data/encrypted.json` 被自动提交，且钉钉收到第一条测试推送（如已有成绩）。

---

自定义

需求	修改位置	
调整抓取间隔	`.github/workflows/gpa.yml` 第 4 行 `cron: "0 * * * *"`	
推送渠道	替换 `ding.py` 为企业微信/飞书/Server 酱等	
加密方式	把 `crypto_util.py` 换成纯 RSA 或纯 AES 均可	

---

常见问题

现象	解决	
Actions 403 无法 push	确认已勾选「Read and write permissions」；workflow 已带 `token: ${{ secrets.GITHUB_TOKEN }}`	
验证码识别失败	重试 3 次自动重登；如仍失败可换打码平台	
钉钉收不到消息	检查 TOKEN/SECRET 是否正确；机器人是否开启「加签」	
想本地测试	把账号密码直接写在 `gpa.py` 顶部即可运行	

---

项目结构

```
.
├── .github/workflows/gpa.yml     # GitHub Actions 定时任务
├── gpa.py                        # 主程序：抓取→加密→推送
├── jwxtdl.py                     # 登录+验证码识别
├── crypto_util.py                # AES-GCM + RSA 混合加密
├── ding.py                       # 钉钉 Markdown 推送
├── requirements.txt              # 依赖列表
└── data/encrypted.json           # 加密后的成绩快照（自动生成）
```

---

免责声明
本项目仅供学习交流，请勿用于商业或非法用途。使用即视为同意自行承担全部风险。

---

⭐ 如果帮到你，给个 Star 让我知道！
