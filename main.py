from datetime import datetime
import json
import logging
import os
import subprocess
import time
from retry import retry
from urllib.parse import urlparse

# from line_profiler import LineProfiler
from memory_profiler import profile

from flask import Flask, request
from flask_httpauth import HTTPBasicAuth

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import SessionNotCreatedException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
auth = HTTPBasicAuth()

users = {
    os.getenv('BASIC_USER'): os.getenv('BASIC_PASSWORD')
}
    
@auth.get_password
def get_password(username):
    if username in users:
        return users.get(username)
    return None

@app.route('/')
def index():
    return 'index'

@app.route('/get_contents', methods=['GET'])
@auth.login_required
@profile(precision=3)
def get_contents():
    pid = str(os.getpid())
    now = datetime.now()
    start_time = time.time()
    logger.info(pid + ' START ' + now.strftime("%Y/%m/%d %H:%M:%S"))
    
    url = request.args.get('url', '')
    if url == '':
        logger.info(pid + ' CHECK POINT 005')
        return '', 200
    
    logger.info(pid + ' TARGET URL : ' + url)

    try:
        res = subprocess.check_output(['ps', '-C', 'chrome', '-o', 'pid'])
        logger.info(pid + ' ' + str(res))
        for chrome_pid in str(res).split('\\n'):
            logger.info(pid + ' ' + chrome_pid.strip())
            if chrome_pid.strip().isdecimal() == True:
                try:
                    res = subprocess.check_output(['kill', '-9', chrome_pid.strip()])
                except Exception as e:
                    logger.info(pid + ' ' + str(e))
    except Exception as e:
        logger.info(pid + ' ' + str(e))

    res = subprocess.check_output(['ps', 'aux'])
    logger.info(pid + ' ' + str(res))
    
    caps = DesiredCapabilities.CHROME
    caps['goog:loggingPrefs'] = {"performance": "ALL"}
    logger.info(pid + ' CHECK POINT 010')

    options = Options()
    
    options.add_argument('--allow-running-insecure-content')
    options.add_argument('--blink-settings=imagesEnabled=false')
    options.add_argument('--disable-desktop-notifications')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-web-security')
    options.add_argument('--headless')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--lang=ja')
    options.add_argument('--no-sandbox')
    # options.add_argument('--proxy-server="direct://"')
    # options.add_argument('--proxy-bypass-list=*')
    options.add_argument('--proxy-server="http://dummy.local/"')
    options.add_argument('--proxy-bypass-list=' + os.getenv('PROXY_BYPASS_LIST'))
    options.add_argument('--start-maximized')
    # options.add_argument('--host-rules=' + os.getenv('HOST_RULES'))
    options.add_argument('--user-agent=' + os.getenv('USER_AGENT'))
    
    options.page_load_strategy = 'eager'
    
    # logger.info(pid + ' HOST_RULES : ' + os.getenv('HOST_RULES'))
    logger.info(pid + ' CHECK POINT 020')

    driver = get_webdriver(options, caps)
    
    if driver is None:
        return '', 500
    
    logger.info(pid + ' CHECK POINT 030')
    driver.implicitly_wait(10)
    
    logger.info(pid + ' CHECK POINT 040')
    
    request_start_time = time.time()
    driver.get(url)
    try:
        logger.info(pid + ' CHECK POINT 050')
        logger.info(pid + ' CLASS_NAME : ' + os.getenv('CLASS_NAME'))
        logger.info(pid + ' CHECK POINT 060')
        element = WebDriverWait(driver, 15).until(
            expected_conditions.visibility_of_element_located((By.CLASS_NAME, os.getenv('CLASS_NAME')))
        )
    except TimeoutException as e:
        logger.info(pid + ' TimeoutException : ' + str(e))
        logger.info(pid + ' ' + driver.page_source)
        # driver.quit();
        # return '', 500
    except Exception as e:
        logger.info(pid + ' Exception : ' + str(e))
        driver.quit();
        return '', 500
    
    http_status = ''
    logs = driver.get_log('performance')
    for log in logs:
        message = json.loads(log['message'])['message']
        # logger.info(pid + ' ' + str(message))
        if message['method'] == 'Network.responseReceived':
            logger.info(pid + ' ' + message['params']['response']['url'] + ' ' + str(datetime.fromtimestamp(message['params']['response'].get('responseTime', 0) / 1000)))
            if message['params']['response']['url'] == url:
                http_status = str(message['params']['response']['status'])
    logger.info(pid + ' ' + http_status + ' [' + str(time.time() - request_start_time)[:5] + 'sec] ' + urlparse(url).netloc)
    
    logger.info(pid + ' CHECK POINT 070')
    logger.info(pid + ' RESULT URL : ' + driver.current_url)
    res = driver.page_source
    logger.info(pid + ' CHECK POINT 080')

    driver.quit()
    logger.info(pid + ' CHECK POINT 090')
    
    logger.info(pid + ' FINISH ' + str(time.time() - start_time)[:5] + 'sec')
    return res, 200

@retry(SessionNotCreatedException, tries=3)
@profile(precision=3)
def get_webdriver(options_, caps_):
    pid = str(os.getpid())
    logger.info(pid + ' START get_webdriver')
    try:
        logger.info(pid + ' CHECK POINT 022')
        driver = webdriver.Chrome(options=options_, desired_capabilities=caps_)
        logger.info(pid + ' CHECK POINT 024')
    except SessionNotCreatedException as e:
        logger.info(pid + ' ' + str(e))
        driver = None
        raise e
    except Exception as e:
        logger.info(pid + ' ' + str(e))
        driver = None

    return driver

if __name__ == '__main__':
    app.run()
