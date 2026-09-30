#!/usr/bin/env python3
"""Job Hunter 客户端运行环境自检脚本 (Client Environment Self-Check)

本脚本用于甲方在自身电脑上验证环境是否满足 Job Hunter 的运行要求。
完全基于只读与本地探测，严禁访问任何真实业务数据或个人求职记录。

用法:
    python3 scripts/client_env_check.py
"""

import sys
import os
import shutil
import subprocess
import urllib.request
import json
from pathlib import Path

# ANSI 颜色定义
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
RESET = "\033[0m"


def print_pass(msg: str):
    print(f"[{GREEN}PASS{RESET}] {msg}")


def print_warn(msg: str):
    print(f"[{YELLOW}WARN{RESET}] {msg}")


def print_missing(msg: str):
    print(f"[{RED}MISSING{RESET}] {msg}")


def print_info(msg: str):
    print(f"[{BLUE}INFO{RESET}] {msg}")


def check_python_version() -> bool:
    v = sys.version_info
    ver_str = f"{v.major}.{v.minor}.{v.micro}"
    if v.major < 3 or (v.major == 3 and v.minor < 9):
        print_missing(f"Python 版本: 当前为 {ver_str}，要求 Python >= 3.9（推荐 3.10+）")
        return False
    elif v.major == 3 and v.minor == 9:
        print_pass(f"Python {ver_str} (满足运行要求 >= 3.9，推荐升级至 3.10+)")
        return True
    else:
        print_pass(f"Python {ver_str}")
        return True


def check_python_packages() -> bool:
    packages = {
        "DrissionPage": ("DrissionPage", ">=4.0"),
        "httpx": ("httpx", "通用"),
        "yaml": ("PyYAML", ">=6.0"),
    }
    all_ok = True
    for mod_name, (display_name, req_ver) in packages.items():
        try:
            mod = __import__(mod_name)
            ver = getattr(mod, "__version__", "已安装")
            print_pass(f"{display_name} ({ver})")
        except ImportError:
            print_missing(f"{display_name} 未安装（要求 {req_ver}，运行: pip install -r requirements.txt）")
            all_ok = False
    return all_ok


def detect_chrome() -> tuple:
    """探测系统 Chrome 安装路径及版本"""
    candidates = [
        # macOS 常见路径
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        os.path.expanduser("~/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
        # Linux / Windows PATH
        shutil.which("google-chrome"),
        shutil.which("google-chrome-stable"),
        shutil.which("chromium"),
        shutil.which("chromium-browser"),
        shutil.which("chrome"),
        # Windows 默认安装路径
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    ]
    for c in candidates:
        if c and os.path.exists(c):
            # 获取版本
            try:
                res = subprocess.check_output([c, "--version"], stderr=subprocess.STDOUT, text=True, timeout=5)
                return True, c, res.strip()
            except Exception:
                return True, c, "版本获取失败(可执行文件存在)"
    return False, None, None


def check_chrome() -> bool:
    found, path, ver = detect_chrome()
    if found:
        print_pass(f"Chrome detected: {ver} ({path})")
        return True
    else:
        print_missing("Google Chrome 浏览器未检测到。自动投递功能需要 Chrome (推荐最新稳定版)")
        print("         安装指引: https://www.google.cn/chrome/")
        return False


def check_directory_permissions(root_dir: Path) -> bool:
    test_file = root_dir / ".perm_check_tmp"
    try:
        test_file.write_text("ok", encoding="utf-8")
        test_file.unlink()
        print_pass("项目目录可读写权限")
        return True
    except Exception as e:
        print_missing(f"项目目录写入失败: {e}，请检查目录权限")
        return False


def check_network_connectivity() -> bool:
    # 检查基本外网连通性
    urls = [
        ("https://www.zhipin.com", "BOSS直聘网络连通"),
        ("https://www.baidu.com", "基础互联网连通"),
    ]
    ok_count = 0
    for url, desc in urls:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=4) as resp:
                if resp.status in (200, 301, 302, 403):  # 403 也是可达，仅被 WAF 拦截 UA
                    ok_count += 1
        except Exception:
            pass

    if ok_count > 0:
        print_pass("网络基础连通性正常")
        return True
    else:
        print_warn("网络连通检测超时（请确认能否正常访问求职平台网站）")
        return False


def check_configuration_files(root_dir: Path) -> bool:
    config_file = root_dir / "config.json"
    example_file = root_dir / "config.example.json"

    if config_file.exists():
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                json.load(f)
            print_pass("配置文件 config.json 存在且 JSON 格式有效")
            return True
        except Exception as e:
            print_missing(f"配置文件 config.json 格式错误: {e}")
            return False
    elif example_file.exists():
        print_pass("模板配置 config.example.json 存在（项目支持缺省配置直接启动，正式运行请执行 cp config.example.json config.json）")
        return True
    else:
        print_missing("未找到 config.json 或 config.example.json")
        return False


def check_environment_variables() -> None:
    # 环境变量均为可选扩展项（非必须），打印当前就绪状态
    llm_env = os.environ.get("JOBHUNTER_LLM_KEY_ENV", "COMMANDCODE_API_KEY")
    llm_key = os.environ.get(llm_env) or os.environ.get("OPENCODE_GO_API_KEY")
    if llm_key:
        print_info(f"LLM API Key: 已配置 ({llm_env} 可用于 HR 自动回复草拟)")
    else:
        print_info("LLM API Key: 未配置（可选：纯规则决策引擎零依赖 LLM，仅 HR 消息自动草拟需提供）")

    wx_token = os.environ.get("WXPUSHER_APP_TOKEN")
    if wx_token:
        print_info("移动端通知 (WxPusher): 已配置")
    else:
        print_info("移动端通知 (WxPusher): 未配置（可选：投递结果将在本地终端与日志完整展示）")


def main():
    print("=" * 60)
    print("       Job Hunter 客户端运行环境自检 (Client Env Check)      ")
    print("=" * 60)

    root_dir = Path(__file__).resolve().parent.parent

    results = []

    print("\n[1/6] 检查 Python 运行环境:")
    results.append(("Python 版本", check_python_version()))

    print("\n[2/6] 检查核心依赖包:")
    results.append(("核心依赖包", check_python_packages()))

    print("\n[3/6] 检查 Chrome 浏览器环境:")
    results.append(("Chrome 浏览器", check_chrome()))

    print("\n[4/6] 检查本地目录读写权限:")
    results.append(("目录读写权限", check_directory_permissions(root_dir)))

    print("\n[5/6] 检查网络基础连通性:")
    results.append(("网络连通性", check_network_connectivity()))

    print("\n[6/6] 检查项目配置文件:")
    results.append(("配置文件检查", check_configuration_files(root_dir)))

    print("\n[可选组件状态]:")
    check_environment_variables()

    print("\n" + "=" * 60)
    failures = [name for name, ok in results if not ok]
    if not failures:
        print(f"{GREEN}Environment check: PASS{RESET}")
        print("您的本地环境完全满足 Job Hunter 的基础运行要求！")
        print("下一步建议：执行安全演练测试 -> python3 scripts/client_dry_run.py")
        print("=" * 60)
        sys.exit(0)
    else:
        print(f"{RED}Environment check: FAIL{RESET}")
        print(f"以下检查未通过: {', '.join(failures)}")
        print("请根据上方提示修复缺失依赖或组件后再试。")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
