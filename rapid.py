import requests
from bs4 import BeautifulSoup
import time
import re
import os
import threading
from datetime import datetime

# ANSI color codes
GREEN = "\033[1;92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
WHITE = "\033[1;97m"
RESET = "\033[0m"
BOLD = "\033[1m"

def print_banner():
    print(f"{GREEN}")
    print("███████╗ █████╗ ██╗   ██╗ ██████╗███████╗████████╗")
    print("██╔════╝██╔══██╗██║   ██║██╔════╝██╔════╝╚══██╔══╝")
    print("█████╗  ███████║██║   ██║██║     █████╗     ██║   ")
    print("██╔══╝  ██╔══██║██║   ██║██║     ██╔══╝     ██║   ")
    print("██║     ██║  ██║╚██████╔╝╚██████╗███████╗   ██║   ")
    print("╚═╝     ╚═╝  ╚═╝ ╚═════╝  ╚═════╝╚══════╝   ╚═╝   ")
    print(f"{YELLOW}MOD by ANDRE Jendela Semesta{RESET}")
    print(f"{WHITE}NO APIKEY + ON 24JAM NONSTOP{RESET}")
    print(f"{RESET}")

def get_email():
    email_file = "rapidfun.txt"
    if os.path.exists(email_file):
        try:
            with open(email_file, "r") as f:
                email = f.read().strip()
                if email:
                    print(f"{CYAN}[i] Found saved email: {email}{RESET}")
                    return email
        except:
            pass
    print(f"{YELLOW}[!] No saved email found.{RESET}")
    email = input(f"{CYAN}[?] Enter your email: {RESET}").strip()
    try:
        with open(email_file, "w") as f:
            f.write(email)
        print(f"{GREEN}[✓] Email saved to {email_file}{RESET}")
    except:
        print(f"{RED}[✗] Failed to save email{RESET}")
    return email

def extract_sweetalert(html):
    soup = BeautifulSoup(html, "html.parser")
    scripts = soup.find_all("script")
    for script in scripts:
        text = script.string if script.string else ""
        if "Swal.fire" in text and "success" in text:
            html_match = re.search(r"html:\s*['\"]([^'\"]+)['\"]", text)
            if html_match:
                msg = html_match.group(1).strip()
                if "faucetpay account" in msg.lower():
                    nominal = re.search(r"\d+\.\d+\s+USDT", msg)
                    val = nominal.group(0) if nominal else ""
                    return f"{val} Dikirim ke FaucetPay!"
                return msg
    return None

def print_success(msg, site=""):
    prefix = f"[{site}] " if site else ""
    print(f"{GREEN}{BOLD}[✓] {prefix}{msg}{RESET}")

def print_error(msg, site=""):
    prefix = f"[{site}] " if site else ""
    print(f"{RED}{BOLD}[✗] {prefix}{msg}{RESET}")

def print_info(msg, site=""):
    prefix = f"[{site}] " if site else ""
    print(f"{CYAN}[i] {prefix}{msg}{RESET}")

def print_info_white(msg, site=""):
    prefix = f"[{site}] " if site else ""
    print(f"{WHITE}[i] {prefix}{msg}{RESET}")

def print_warn(msg, site=""):
    prefix = f"[{site}] " if site else ""
    print(f"{YELLOW}[!] {prefix}{msg}{RESET}")

class FaucetClaimer:
    def __init__(self, name, base_url, login_url, faucet_url, verify_url, email):
        self.name = name
        self.base_url = base_url
        self.login_url = login_url
        self.faucet_url = faucet_url
        self.verify_url = verify_url
        self.email = email
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/126.0.0.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "*/*",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        })
        self.running = True
        self.claim_count = 0

    def login(self):
        try:
            print_info(f"Fetching login page...", self.name)
            resp = self.session.get(self.base_url, timeout=15)
            soup = BeautifulSoup(resp.text, "html.parser")
            csrf_input = soup.find("input", {"name": "csrf_token_name"})
            csrf_token = csrf_input.get("value") if csrf_input else None
            print_info(f"Logging in as: {self.email}", self.name)
            login_data = {"wallet": self.email, "csrf_token_name": csrf_token}
            login_resp = self.session.post(self.login_url, data=login_data, timeout=15, allow_redirects=True)
            if login_resp.status_code == 200:
                print_success(f"Login successful!", self.name)
                return True
            else:
                print_error(f"Login failed! Status: {login_resp.status_code}", self.name)
                return False
        except Exception as e:
            print_error(f"Login error: {str(e)}", self.name)
            return False

    def claim_loop(self):
        if not self.login():
            return
        while self.running:
            self.claim_count += 1
            try:
                faucet_resp = self.session.get(self.faucet_url, timeout=15)
                if faucet_resp.status_code != 200:
                    print_error(f"Failed to load faucet page: {faucet_resp.status_code}", self.name)
                    time.sleep(10)
                    continue
                soup_faucet = BeautifulSoup(faucet_resp.text, "html.parser")
                verify_form = soup_faucet.find("form", {"id": "verify"})
                if not verify_form:
                    verify_form = soup_faucet.find("form", action=lambda x: x and "verify/usdt" in x)
                auto_faucet_token, csrf_token_claim, token = None, None, None
                if verify_form:
                    for inp in verify_form.find_all("input"):
                        name = inp.get("name")
                        value = inp.get("value")
                        if name == "auto_faucet_token": auto_faucet_token = value
                        elif name == "csrf_token_name": csrf_token_claim = value
                        elif name == "token": token = value
                if not all([auto_faucet_token, csrf_token_claim, token]):
                    print_error("Could not extract all form tokens!", self.name)
                    time.sleep(10)
                    continue
                
                timer_script = soup_faucet.find("script", string=lambda x: x and "let timer" in x)
                if timer_script:
                    timer_match = re.search(r"let\s+timer\s*=\s*(\d+)", timer_script.string)
                    if timer_match:
                        total_time = int(timer_match.group(1))
                        for i in range(total_time, 0, -1):
                            percent = ((total_time - i) / total_time) * 100
                            print(f"{WHITE}[i] {self.name}: {percent:.1f}% progress ({i}s left){RESET}", end="\r")
                            time.sleep(1)
                        print() 
                    else: time.sleep(11)
                else: time.sleep(11)

                claim_data = {"auto_faucet_token": auto_faucet_token, "csrf_token_name": csrf_token_claim, "token": token}
                claim_resp = self.session.post(self.verify_url, data=claim_data, timeout=15, allow_redirects=True)
                if claim_resp.status_code == 200:
                    sweet_msg = extract_sweetalert(claim_resp.text)
                    if sweet_msg: print_success(f"SUKSES! {sweet_msg}", self.name)
                    else:
                        if "success" in claim_resp.text.lower() and "usdt" in claim_resp.text.lower():
                            print_success("SUKSES! Claim submitted successfully!", self.name)
                        else: print_warn("Claim response received but no clear success message", self.name)
                else: print_error(f"Claim failed! Status: {claim_resp.status_code}", self.name)
                print_warn("Next Claim Tunggu 10 Detik bos...", self.name)
                time.sleep(10)
            except Exception as e:
                print_error(f"Error in claim loop: {str(e)}", self.name)
                time.sleep(10)

    def stop(self):
        self.running = False

def run_claimer(claimer):
    claimer.claim_loop()

print_banner()
EMAIL = get_email()
rapid = FaucetClaimer(name="Rapid", base_url="https://rapidgame.fun/", login_url="https://rapidgame.fun/auth/login", faucet_url="https://rapidgame.fun/faucet/currency/usdt", verify_url="https://rapidgame.fun/faucet/verify/usdt", email=EMAIL)
flash = FaucetClaimer(name="Flash", base_url="https://flashpost.online/", login_url="https://flashpost.online/auth/login", faucet_url="https://flashpost.online/faucet/currency/usdt", verify_url="https://flashpost.online/faucet/verify/usdt", email=EMAIL)

print_info("Starting claimers for both websites...")
thread1 = threading.Thread(target=run_claimer, args=(rapid,))
thread2 = threading.Thread(target=run_claimer, args=(flash,))
thread1.start()
thread2.start()

try:
    while thread1.is_alive() or thread2.is_alive():
        time.sleep(1)
except KeyboardInterrupt:
    print_info("\nStopping claimers...")
    rapid.stop()
    flash.stop()
    thread1.join()
    thread2.join()
    print_success("Both claimers stopped.")
