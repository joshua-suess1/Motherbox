from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium_stealth import stealth
import time
import firebase_admin
from firebase_admin import credentials, storage
import requests
import datetime
import sys
import csv
import subprocess

#*************************************** LOAD SETTINGS ***************************************#
instanceID = subprocess.check_output(["hostname"])
userName = subprocess.check_output(["whoami"])
print(instanceID)
time.sleep(30)
driverPath = "C:\\Users\\{}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\chromedriver".format(userName)
chromeDir = "C:\\Users\\{}\\AppData\\Local\\Google\\Chrome\\User Data".format(userName) 

#************************************ FIND MATCHING VIDEO ************************************#
cred = credentials.Certificate("cred.json")
firebase_admin.initialize_app(cred,{'storageBucket': 'motherbox-4ae00.appspot.com'}) 

videoName = ""
videoURL = ""
expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
bucket = storage.bucket()
for blob in bucket.list_blobs():
  if(blob.name[:blob.name.index(".")] == instanceID):
    videoName = blob.name
    videoURL = blob.generate_signed_url(expiration)
if videoName == "":
  sys.exit("VIDEO NOT FOUND")

#*************************************** DOWNLOAD VIDEO ***************************************#
response = requests.get(videoURL)
with open(f"{videoName}", "wb") as file:
  file.write(response.content)

#**************************************** UPLOAD VIDEO ****************************************#
options = webdriver.ChromeOptions()
options.add_argument("start-maximized")
options.add_argument(f"user-data-dir={chromeDir}")
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )

url = "https://www.tiktok.com/upload?lang=en"
driver.get(url)

JS_DROP_FILE = """
    var target = arguments[0],
        offsetX = arguments[1],
        offsetY = arguments[2],
        document = target.ownerDocument || document,
        window = document.defaultView || window;

    var input = document.createElement('INPUT');
    input.type = 'file';
    input.onchange = function () {
      var rect = target.getBoundingClientRect(),
          x = rect.left + (offsetX || (rect.width >> 1)),
          y = rect.top + (offsetY || (rect.height >> 1)),
          dataTransfer = { files: this.files };

      ['dragenter', 'dragover', 'drop'].forEach(function (name) {
        var evt = document.createEvent('MouseEvent');
        evt.initMouseEvent(name, !0, !0, window, 0, 0, 0, x, y, !1, !1, !1, !1, 0, null);
        evt.dataTransfer = dataTransfer;
        target.dispatchEvent(evt);
      });

      setTimeout(function () { document.body.removeChild(input); }, 25);
    };
    document.body.appendChild(input);
    return input;
"""
def drag_and_drop_file(drop_target, path):
    _driver = drop_target.parent
    file_input = _driver.execute_script(JS_DROP_FILE, drop_target, 0, 0)
    file_input.send_keys(path)

time.sleep(15)
iFrame = driver.find_element(By.CSS_SELECTOR, "iframe")
driver.switch_to.frame(iFrame)
time.sleep(5)
upload_area = driver.find_element(By.CSS_SELECTOR,"div[class*='upload-card']")
drag_and_drop_file(upload_area, f"{videoName}")
time.sleep(20)
caption = driver.find_element(By.CSS_SELECTOR,"div[class*='notranslate public-DraftEditor-content']")
caption.clear()
caption.send_keys(description)
time.sleep(5)
buttons = driver.find_element(By.CSS_SELECTOR,"div[class*='btn-post']")
buttons.click()
time.sleep(30)

driver.quit()

