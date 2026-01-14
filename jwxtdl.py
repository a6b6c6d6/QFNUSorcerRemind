import requests, base64, ddddocr, logging, time
from PIL import Image
from io import BytesIO

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def _ocr(image: Image.Image) -> str:
    """OCR 识别验证码"""
    ocr = ddddocr.DdddOcr(show_ad=False)
    buf = BytesIO()
    image.save(buf, format="PNG")
    return ocr.classification(buf.getvalue())

def _get_captcha(session: requests.Session) -> str:
    """下载并识别验证码，失败返回空串"""
    url = "http://zhjw.qfnu.edu.cn/jsxsd/verifycode.servlet"
    try:
        resp = session.get(url, timeout=10)
        resp.raise_for_status()
        image = Image.open(BytesIO(resp.content))
        return _ocr(image)
    except Exception as e:
        logger.warning("验证码获取/识别失败: %s", e)
        return ""

def deng(stu_id: str, stu_pwd: str, max_retry: int = 3) -> requests.Session:
    """带重试的登录"""
    login_url = "http://zhjw.qfnu.edu.cn/jsxsd/xk/LoginToXkLdap"
    encoded = (base64.b64encode(stu_id.encode()).decode() + "%%%" +
               base64.b64encode(stu_pwd.encode()).decode())

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })

    for i in range(1, max_retry + 1):
        try:
            # 拿首页 Cookie
            session.get("http://zhjw.qfnu.edu.cn/jsxsd/", timeout=10)
            code = _get_captcha(session)
            if not code:
                continue

            payload = {
                "userAccount": "",
                "userPassword": "",
                "RANDOMCODE": code,
                "encoded": encoded
            }
            resp = session.post(login_url, data=payload, timeout=10)
            resp.raise_for_status()
            # 简单判断：登录失败一般跳回登录页
            if "xk/LoginToXkLdap" not in resp.url and "用户登录" not in resp.text:
                logger.info("登录成功")
                return session
            logger.warning("第 %d 次登录失败，重试...", i)
        except Exception as e:
            logger.warning("第 %d 次登录异常: %s", i, e)
        time.sleep(1)

    raise RuntimeError("登录失败，请检查账号/密码/验证码")