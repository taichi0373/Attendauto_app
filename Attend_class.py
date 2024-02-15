from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
import datetime, random


class Attend():
    def __init__(self, student_id, password, course_name):
        self.student_id = student_id
        self.password = password
        self.course_name = course_name

    def syusseki(self):
        options = Options()
        options.add_argument('--headless')
        options.add_argument("--no-sandbox")
        browser = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        sec = random.uniform(1, 5)
        sleep(sec)
        
        
        #アクセス
        url = ''
        browser.implicitly_wait(10)
        browser.get(url)
        
        #ユーザID、パスワード入力
        USER = "g" +self.student_id
        element = browser.find_element("id","username")
        element.clear()
        sleep(sec)
        element.send_keys(USER)

        PASS = self.password
        element = browser.find_element("id","password")
        element.clear()
        sleep(sec)
        element.send_keys(PASS)

        #login
        element = browser.find_element("id","LoginBtn")
        sleep(1)
        element.click()
        

        list_course = browser.find_elements(By.PARTIAL_LINK_TEXT, str(self.course_name))
        if len(list_course) == 1:
            list_course.clear()
            print("該当する講義名がありました。")

            sleep(sec)
            element = browser.find_element(By.PARTIAL_LINK_TEXT, str(self.course_name))
            element.click()
            
            sec = random.uniform(1, 6) 
            sleep(sec)
            element = browser.find_element(By.XPATH, '/html/body/header/nav/div[2]/div/ul[3]/li[5]/a')
            element.click()
            
            #出席日
            sleep(sec)
            dt = datetime.date.today()
            list_day = browser.find_elements(By.PARTIAL_LINK_TEXT, str(dt.strftime("%Y/%m/%d")))
            
            if len(list_day) > 0:
                list_day.clear()
                element = browser.find_element(By.PARTIAL_LINK_TEXT, str(dt.strftime("%Y/%m/%d")))
                element.click()
                
                #ポップアップはframeなのでbrowserの向き先を切り替える
                sleep(sec)
                frame = browser.find_element(By.NAME, "contentsInfo")
                browser.switch_to.frame(frame)
                
                #開始ボタンが有効かどうか
                list_start = browser.find_elements(By.NAME, "next")
                
                if len(list_start) > 0:
                    list_start.clear()
                    print("開始ボタンが有効です。")
                    element = browser.find_element(By.NAME, "next")
                    element.click()
                    
                    sleep(sec)
                    frame = browser.find_element(By.NAME, "answer")
                    browser.switch_to.frame(frame)
                    
                    #出席データするにチェック
                    sleep(sec)
                    element = browser.find_element("id","1_1")
                    element.click()
                    
                    #出席データを送信するをクリック
                    sec = random.uniform(2, 5) 
                    sleep(sec)
                    browser.implicitly_wait(10)
                    element = browser.find_element("id","GradeBtn")
                    element.click()
                    print("出席データを送信しました。")
                else:
                    print("出席時間外です。\n 講義名：" + str(self.course_name))
                    sleep(1)
                    browser.implicitly_wait(10)
                    element = browser.find_element(By.NAME, "giveup")
                    element.click()
            else:
                print("出席日ではありません。\n 講義名：" + str(self.course_name))
        elif len(list_course) > 1:
            list_course.clear()
            print("該当する講義名が複数あります。")
        else:
            print("該当する講義名がありません。")
        
        print("ブラウザを終了します")
        browser.quit()
