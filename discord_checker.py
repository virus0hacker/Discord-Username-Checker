import aiohttp
import asyncio
import aiofiles
import random
import json
import sys
from datetime import datetime

class DiscordChecker:
    def __init__(self):
        self.available_count = 0
        self.taken_count = 0
        self.error_count = 0
        
    def print_banner(self):
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║               
║                                                              ║
║         ████▄  ██ ▄█████ ▄█████ ▄████▄ █████▄  ████▄         ║
║         ██  ██ ██ ▀▀▀▄▄▄ ██     ██  ██ ██▄▄██▄ ██  ██        ║
║         ████▀  ██ █████▀ ▀█████ ▀████▀ ██   ██ ████▀         ║
║                                                              ║
║                                                              ║
║              DISCORD USERNAME CHECKER v1.0                   ║
║                   by ViRuS - HaCkEr                          ║
║                   Twitter: @h3fq1                            ║
╚══════════════════════════════════════════════════════════════╝
        """
        print("\033[38;5;33m" + banner + "\033[0m")
    
    def print_stats(self):
        stats = f"""
┌─────────────────────────────────────────────┐
│  \033[38;5;82mSTATISTICS\033[0m                                 │
│                                             │
│  Available: \033[38;5;82m{self.available_count}\033[0m                    │
│  Taken: \033[38;5;196m{self.taken_count}\033[0m                      │
│  Errors: \033[38;5;214m{self.error_count}\033[0m                      │
│                                             │
└─────────────────────────────────────────────┘
        """
        print(stats)
    
    def print_header(self):
        header = f"""
\033[38;5;33m┌─────────────────────────────────────────────────────┐\033[0m
\033[38;5;33m│  Starting check at {datetime.now().strftime('%H:%M:%S')}          │\033[0m
\033[38;5;33m└─────────────────────────────────────────────────────┘\033[0m
        """
        print(header)
    
    def print_result(self, username, status):
        colors = {
            "AVAILABLE": "\033[38;5;82m",
            "TAKEN": "\033[38;5;196m",
            "ERROR": "\033[38;5;214m",
            "RATE_LIMITED": "\033[38;5;226m",
            "UNKNOWN": "\033[38;5;141m"
        }
        
        reset = "\033[0m"
        
        if status == "AVAILABLE":
            print(f"{colors['AVAILABLE']}[✓] {username}{reset}")
            self.available_count += 1
        elif status == "TAKEN":
            print(f"{colors['TAKEN']}[✗] {username}{reset}")
            self.taken_count += 1
        elif status.startswith("ERROR"):
            print(f"{colors['ERROR']}[!] {username} - {status}{reset}")
            self.error_count += 1
        elif status == "RATE_LIMITED":
            print(f"{colors['RATE_LIMITED']}[⚠] {username} - Rate Limited{reset}")
        else:
            print(f"{colors['UNKNOWN']}[?] {username} - {status}{reset}")
    
    async def check_username(self, session, username, available_file):
        url = "https://discord.com/api/v9/unique-username/username-attempt-unauthed"
        
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Origin": "https://discord.com",
            "Referer": "https://discord.com/register",
            "X-Debug-Options": "bugReporterEnabled",
            "X-Discord-Locale": "en-US",
            "X-Super-Properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEyMC4wLjAuMCBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTIwLjAuMC4wIiwib3NfdmVyc2lvbiI6IjEwIiwicmVmZXJyZXIiOiIiLCJyZWZlcnJpbmdfZG9tYWluIjoiIiwiY2xpZW50X2J1aWxkX251bWJlciI6MjUzODUwLCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsfQ=="
        }
        
        payload = {"username": username}
        
        try:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if "taken" in data:
                        if not data["taken"]:
                            async with aiofiles.open(available_file, 'a', encoding='utf-8') as f:
                                await f.write(f"{username}\n")
                            self.print_result(username, "AVAILABLE")
                            return True
                        else:
                            self.print_result(username, "TAKEN")
                    else:
                        self.print_result(username, f"UNKNOWN: {data}")
                elif response.status == 429:
                    retry_after = int(response.headers.get('Retry-After', random.randint(5, 10)))
                    self.print_result(username, "RATE_LIMITED")
                    await asyncio.sleep(retry_after)
                    return await self.check_username(session, username, available_file)
                else:
                    self.print_result(username, f"ERROR {response.status}")
                    return False
        except Exception as e:
            self.print_result(username, f"EXCEPTION: {str(e)}")
            return False
        
        return False
    
    async def main(self):
        self.print_banner()
        
        username_file = input("\033[38;5;33m┌─[\033[0mUsername file path\033[38;5;33m]─>\033[0m ").strip()
        available_file = "available.txt"
        
        self.print_header()
        
        async with aiohttp.ClientSession() as session:
            try:
                async with aiofiles.open(username_file, 'r', encoding='utf-8') as f:
                    usernames = [line.strip() for line in await f.readlines()]
            except FileNotFoundError:
                print(f"\033[38;5;196m[!] File '{username_file}' not found\033[0m")
                return
            
            total = len(usernames)
            print(f"\033[38;5;33mTotal usernames to check: {total}\033[0m")
            
            tasks = []
            for idx, username in enumerate(usernames):
                if username:
                    task = self.check_username(session, username, available_file)
                    tasks.append(task)
                    
                    if len(tasks) >= 3:
                        await asyncio.gather(*tasks)
                        tasks = []
                        await asyncio.sleep(random.uniform(1.5, 3.0))
                    
                    if (idx + 1) % 10 == 0:
                        print(f"\033[38;5;33mProgress: {idx + 1}/{total}\033[0m")
            
            if tasks:
                await asyncio.gather(*tasks)
        
        self.print_stats()
        
        print(f"\033[38;5;33m┌─────────────────────────────────────────────────────┐\033[0m")
        print(f"\033[38;5;33m│  Results saved to: {available_file}                  │\033[0m")
        print(f"\033[38;5;33m│  Credits: @h3fq1                                    │\033[0m")
        print(f"\033[38;5;33m│  Finished at: {datetime.now().strftime('%H:%M:%S')}          │\033[0m")
        print(f"\033[38;5;33m└─────────────────────────────────────────────────────┘\033[0m")

if __name__ == "__main__":
    checker = DiscordChecker()
    asyncio.run(checker.main())
