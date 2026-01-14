**曲师大教务成绩自动监控 & 钉钉推送机器人** 🎓🤖

一个用 GitHub Actions 实现的**零成本、自动、加密、安全**的成绩监控+钉钉推送工具

### ✨ 核心功能

- 每小时自动登录教务系统抓取成绩
- 只推送**新出现的成绩**（增量对比）
- **AES-256-GCM + RSA-2048** 混合加密，仓库里只存密文
- 即使仓库被黑/泄露也无法解密成绩
- 完全免费，无需自己买服务器/云函数
- 支持钉钉群推送 / 钉钉私聊推送

### 🚀 3分钟极速部署流程

1. **先把项目拿下来**

```bash
git clone https://github.com/a6b6c6d6/QFNUSorcerRemind.git
cd QFNUSorcerRemind
# 或者直接在网页上点 Fork 也行
```

2. **生成 RSA 2048 密钥对**（只需做一次）

```bash
# 生成私钥
openssl genrsa -out private.pem 2048

# 导出公钥
openssl rsa -in private.pem -pubout -out public.pem
```

3. **把密钥转成一行字符串**（很重要！GitHub Secrets 要单行）

Linux/macOS:

```bash
awk 'NF {printf "%s\\n", $0}' public.pem   # 复制输出
awk 'NF {printf "%s\\n", $0}' private.pem  # 复制输出
```

PowerShell (Windows):

```powershell
(Get-Content public.pem -Raw) -replace "`r?`n", "\n"
(Get-Content private.pem -Raw) -replace "`r?`n", "\n"
```

4. **在 GitHub 仓库设置 6 个 Secrets**（必须全填）

| 变量名              | 说明                            | 示例值                              |
|---------------------|---------------------------------|-------------------------------------|
| `STU_ID`            | 教务系统学号                    | 2023123456                         |
| `STU_PWD`           | 教务系统密码                    | Abcd123!@#                         |
| `DING_TOKEN`        | 钉钉机器人 access_token         | SEC...长串字符                      |
| `DING_SECRET`       | 钉钉加签密钥（没开加签可不填）  | 空 或 SEC...                       |
| `RSA_PUBLIC_PEM`    | 公钥（单行，含\n）              | -----BEGIN PUBLIC KEY-----\nMIIB... |
| `RSA_PRIVATE_PEM`   | 私钥（单行，含\n）              | -----BEGIN RSA PRIVATE KEY-----\nMII... |

5. **开启仓库 Actions 写权限**（非常重要！）

仓库 → Settings → Actions → General  
→ Workflow permissions → 选 **Read and write permissions** → Save

6. **手动触发一次测试**

Actions → 成绩监控 → Run workflow → Run workflow  
成功后会：
- 生成加密的成绩快照 `data/encrypted.json`
- 推第一条测试消息到钉钉（如果有成绩）

### 快速自定义修改对照表

想要改什么            | 去改哪个文件                          | 大概位置/说明
-----------------------|---------------------------------------|-------------------------------
改抓取频率             | `.github/workflows/gpa.yml`           | 第4行 `cron: '0 * * * *'`
改成企业微信/飞书推送  | 把 `ding.py` 换成对应平台的推送脚本   | 替换 send_message 函数
不想用混合加密         | `crypto_util.py`                      | 改成纯RSA或纯AES
想加打码平台识别验证码 | `jwxtdl.py`                           | 改 `recognize_captcha()` 函数
想本地调试             | `gpa.py` 最上面                       | 直接硬编码学号密码运行

### 常见问题速查

现象                         | 可能原因 & 解决办法
-----------------------------|--------------------------------------
Actions 提交失败 403         | 没开 Read&Write permissions
钉钉一条消息都收不到         | token错 / 群里没加机器人 / 加签开了但没填secret
一直验证码识别失败           | 自动重试3次还不行→考虑接打码平台
成绩没更新但其实出了新成绩   | 可能是教务系统延迟，先手动跑一次看看

祝大家早日看到心仪的成绩～
