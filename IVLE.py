import os
import shutil
import getpass
from selenium import webdriver 
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ModuleNotFoundError(Exception):
    pass
        
class FileNotFoundError(Exception):
    pass

class ModuleURLNotFoundError(Exception):
    pass

class FolderURLNotFoundError(Exception):
    pass

class NoSuchWindowError(Exception):
    pass

class IVLE():
    def __init__(self, url, username, password, browser, download_path, default_download_path, count):
        self.user = username
        self.password = password
        self.browser = browser
        self.url = url
        self.count = count
        self.path = download_path
        self.default = default_download_path
        self.modules = {}
        self.windows = {}
        self.login()
        
    def login(self):
        self.browser.get(self.url)
        self.browser.maximize_window()
        self.windows[self.count] = self.browser.window_handles[0]
        self.count += 1
        print("Proceeding to login to IVLE...")
        username_input = WebDriverWait(self.browser, 30).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='ctl00_ctl00_ContentPlaceHolder1_userid']")))
        username_input.send_keys(self.user)
        password_input = WebDriverWait(self.browser, 30).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='ctl00_ctl00_ContentPlaceHolder1_password']")))
        password_input.send_keys(self.password)
        sign_in_button = WebDriverWait(self.browser, 30).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='ctl00_ctl00_ContentPlaceHolder1_btnSignIn']")))
        sign_in_button.click()
        print("Successfully login!")
        self.update()
        
    def update(self):
        try:
            self.retrieve_module()
            self.access_module()
        except ModuleURLNotFoundError as error:
            print(error)
        
        print("All files successfully updated!")
        self.end()
    
    def check_folder(self, *args):
        if len(args) == 1:
            path = self.path + "\\" + args[0]
        elif len(args) == 2:
            path = args[0] + "\\" + args[1] 
        if not os.path.exists(path):
            os.mkdir(path)
        return path
    
    def retrieve_module(self):
        for mod in self.browser.find_elements_by_xpath("//*[@id='collapseTwo']/div/div/div/div/div/strong/u/a"):
            if "SCI" not in mod.text:
                module_path = self.check_folder(mod.text)
                module_folder_url = mod.get_attribute("href")
                
                if module_folder_url != None:
                    if mod.text not in self.modules:
                        self.modules[mod.text] = {}
                    self.modules[mod.text]["url"] = module_folder_url
                    self.modules[mod.text]["path"] = module_path
                else:
                    raise ModuleURLNotFoundError(mod.text + " URL not found!")
            else:
                break
            
    def open_new_window(self, url):
        if self.count not in self.windows:
            self.browser.execute_script("window.open('" + url + "')")
            self.windows[self.count] = self.browser.window_handles[len(self.windows)]
            self.browser.switch_to.window(self.windows[self.count])
            self.count += 1
        else:
            self.browser.switch_to.window(self.windows[self.count])
            self.browser.get(url)
            
    def access_module(self):
        for module in self.modules:
            self.open_new_window(self.modules[module]["url"])
            try:                    
                self.access_files_folder(module)
                self.update_folders(module, self.modules[module]["path"])
            except FileNotFoundError as error:
                print(error)
            except NoSuchWindowError as error:
                print(error)
                
    def access_files_folder(self, module):
        files_button = None
        for item in self.browser.find_elements_by_xpath("//*[@id='ctl00_ctl00_ctl00_ContentPlaceHolder1_ContentPlaceHolder1_divSideMenu']/ul/li/a"):
            if "Files" in item.text:
                files_button = item
        
        if files_button != None:
            print("Accessing " + module + " files...")
            files_button.click()
        else:
            raise FileNotFoundError(module + " files not found!")
     
    def update_folders(self, folder, path):
        try:
            WebDriverWait(self.browser, 5).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='mainTable']/tbody/tr/td/a")))
        except:
            print(folder + " does not have any items!")
            self.browser.close()
            self.count -= 1
            del self.windows[self.count]
            self.browser.switch_to.window(self.windows[self.count - 1])
            return
        
        for element in self.browser.find_elements_by_xpath("//*[@id='mainTable']/tbody/tr/td/a"):
            if element.text != "Student Submission":
                if element.get_attribute("class") == "fName":
                    new_path = self.check_folder(path, element.text)
                    folder_url = element.get_attribute("href")
                    
                    if folder_url != None:
                        new_folder = folder + "\\" + element.text
                        self.open_new_window(folder_url)
                        self.update_folders(new_folder, new_path) 
                    else:
                        raise FolderURLNotFoundError(element.text + " URL not found!")
                elif element.get_attribute("class") == "fileName":
                    ls = [item for item in os.listdir(path)]
                    if element.text not in ls:
                        self.download_file(folder, path, element.get_attribute("href"), element.text)
                    
        self.browser.close()
        self.count -= 1
        del self.windows[self.count]
        
        if self.count >= 2:
            self.browser.switch_to.window(self.windows[self.count - 1])
        else:
            raise NoSuchWindowError("No more available tabs!")
        return
    
    def download_file(self, module, path, url, file_name):
        os.chdir(self.default)
        self.browser.get(url)
        while file_name not in os.listdir():
            continue
        shutil.move(self.default + "\\" + file_name, path)
        print(file_name + " has been downloaded into " + module + " folder!")
                
    def end(self):
        self.browser.close()
'''
def create_path(path):
    if   
'''
if __name__ == "__main__":
    print("This IVLE Python Program was built using Python 3.6 and runs only on Windows OS\n")
    print("This program will login to the user's NUS IVLE account and download all possible updates.")
    print("The user only needs to provide an absolute path to store all the downloads and the program will create the necessary folders to store the files, if there is any.\n")
    print("Lastly, this program also works as an updater. If this program had successfully ran on the computer, by providing the old absolute download path, this program will only check and download new files.\n")
    print("------------------------------------------------------------------------------------------")
    print("Please make sure you satisfy the following conditions before proceeding:")
    print("1) Running this program on Windows OS")
    print("2) Have already installed Python 3.x")
    print("3) Have already installed the Python Module Selenium")
    print("4) Have already downloaded Chromedriver.exe (2.4.1) for Selenium")
    print("------------------------------------------------------------------------------------------\n")
    
    while True:
        condition = input("Have you satisfied the above conditions: [Y(es)/N(o)] ")
        if condition == "Y":
            username = input("Enter NUS IVLE Username: ")
            password = getpass.getpass("Enter NUS IVLE Password: ")
            print("A windows absolute path is of this form: C:\\xxxx\\xxxx\\xxxx")
            download_path = input("Enter the absolute download path where you would like to store the files in: ")
            default_download_path = input("Enter the default download path: ")
            while not os.path.exists(default_download_path):
                default_download_path = input("Default download path does not exist! Please check and enter the correct default download path: ")
            chromedriver_path = input("Enter the absolute path where chromedriver.exe is stored in: ")
            os.chdir(chromedriver_path)
            chromedriver = chromedriver_path + "\\chromedriver.exe"
            opts = Options()
            opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36")
            chrome = webdriver.Chrome(chromedriver, chrome_options=opts)
            count = 1
            ivle = IVLE("https://ivle.nus.edu.sg", username, password, chrome, download_path, default_download_path, count)
            break
        elif condition == "N":
            print("Goodbye!")
            break
        else:
            print("Wrong input! Only enter Y/N.")

        
        