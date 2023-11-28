import requests
import time
import smtplib
from concurrent import futures
from email.mime.text import MIMEText
from email.header import Header
# 监测的网站地址列表
URLS = ["http://114.55.245.176:60/","http://47.99.92.71:12/","http://yousonic.com.cn/","http://yousonicai.fun/"]

# 监测频率
FREQUENCY = 20 * 60 # 10分钟

# 设置阈值
RESPONSE_TIME_THRESHOLD = 3 # 页面响应时间阈值，单位为秒
HTTP_STATUS_CODE_THRESHOLD = 400 # HTTP 状态码阈值

# 邮件相关配置
EMAIL_HOST = 'smtp.163.com'
EMAIL_PORT = 25
EMAIL_FROM = 'YousonicMonitor@163.com' # 发件人邮箱
#EMAIL_PASSWORD = 'yousonic@ROOT' # 发件人邮箱密码
EMAIL_PASSWORD = 'BKJVJGVTVTURCMFY'
EMAIL_TO = ['735682329@qq.com','hongkun.liu@yousonicai.fun','xiangdong.zhang@yousonicai.fun','su.shen@yousonicai.fun'] # 收件人邮箱

# 记录已发送的异常通知
sent_notifications = set()

def check_website(url):
    start_time = time.time()
    try:
        response = requests.get(url)
        response.raise_for_status()
        status_code = response.status_code
    except requests.exceptions.RequestException as e:
        print("网站异常")
        send_email('网站异常', str(e))
    else:
        end_time = time.time()
        if end_time - start_time > RESPONSE_TIME_THRESHOLD:
            send_email(f'{url} 响应缓慢', '响应时间超时')
        elif status_code >= HTTP_STATUS_CODE_THRESHOLD:
            send_email(f'{url} 异常', f'HTTP 状态码为 {status_code}')
        else:
            sent_notifications.discard(url)  # 移除已发送的通知，确保下次异常时能够再次发送邮件

def send_email(subject, message):
    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as smtp:
            smtp.login(EMAIL_FROM, EMAIL_PASSWORD)
            email = f"""\
                From: {EMAIL_FROM}
                To: {','.join(EMAIL_TO)}
                Subject: {subject}

                {message}"""
                
            msg = MIMEText(email, 'plain', 'utf-8')  # 内容主题
            msg['From'] = Header(EMAIL_FROM)  # 发件人
            msg['To'] = Header( '; '.join(EMAIL_TO), "utf-8")   # 收件人
            msg['Subject'] = Header("网站异常！", 'utf-8')   # 主题
            smtp.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
            print("邮件发送成功")
    except Exception as e:
        print(f"邮件发送失败: {str(e)}")
    finally:
        smtp.quit()

if __name__ == '__main__':
    while True:
        with futures.ThreadPoolExecutor(max_workers=10) as executor:
            executor.map(check_website, URLS)
        time.sleep(FREQUENCY)