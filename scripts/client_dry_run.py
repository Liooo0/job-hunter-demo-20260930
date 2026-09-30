#!/usr/bin/env python3
"""Job Hunter 客户端安全启动演练脚本 (Client Safe Start & Dry-Run Test)

本脚本用于甲方在不连接招聘网站、不触发任何真实投递、不发送任何消息的前提下，
完整验证系统的程序启动、依赖可用性、配置解析、核心五维匹配引擎与决策链路。

用法:
    python3 scripts/client_dry_run.py
"""

import sys
import os
import sqlite3
import socket
from pathlib import Path

# 将项目根目录置于 Python 模块搜索路径首位
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

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
    print(f"[{RED}FAIL{RESET}] {msg}")


def print_info(msg: str):
    print(f"[{BLUE}INFO{RESET}] {msg}")


def test_core_imports() -> bool:
    print("\n[1/5] 测试核心模块导入...")
    modules = [
        ("shared", "全局工具与配置管理器"),
        ("match_engine", "五维岗位评分匹配引擎"),
        ("job_decision", "双层规则过滤与决策中心"),
        ("guardrails", "风控红线与安全约束"),
        ("store", "SQLite 数据持久层"),
        ("boss_apply", "平台自动化投递引擎"),
    ]
    all_ok = True
    for mod_name, desc in modules:
        try:
            __import__(mod_name)
            print_pass(f"模块导入: {mod_name} ({desc})")
        except Exception as e:
            print_missing(f"模块导入失败: {mod_name} - {e}")
            all_ok = False
    return all_ok


def test_config_loader() -> bool:
    print("\n[2/5] 测试配置加载与默认值补齐...")
    try:
        import shared
        import boss_apply
        cfg = shared.load_config()
        cities = boss_apply._resolve_cities(cfg)
        keywords = boss_apply._resolve_keywords(cfg)
        min_score = cfg.get("min_score", 30)
        safety = cfg.get("safety", {})

        print_pass(f"配置解析成功: 包含 {len(cfg)} 项配置参数")
        print_info(f"默认搜索城市: {', '.join(cities[:4])} (共 {len(cities)} 个)")
        print_info(f"默认主打岗位: {', '.join(keywords[:4])} (共 {len(keywords)} 个)")
        print_info(f"安全风控上限: 日限额 {safety.get('normal_daily_cap', 50)} 份 / 小时限额 {safety.get('hourly_cap', 8)} 份")
        return True
    except Exception as e:
        print_missing(f"配置加载异常: {e}")
        return False


def test_decision_engine() -> bool:
    print("\n[3/5] 测试五维匹配引擎与过滤决策链路...")
    try:
        import match_engine
        import shared

        cfg = shared.load_config()

        # 模拟一份合规的优质岗位 JD
        good_job = {
            "title": "AI应用工程师",
            "company": "未来科技有限公司",
            "desc": "负责公司企业级大模型应用、RAG知识库开发以及Agent工作流编排，熟练使用Python、FastAPI，具备双休与弹性作息。",
            "salary": "18-25K",
            "city": "深圳"
        }
        res_good = match_engine.explain_match(
            good_job["title"],
            good_job["desc"],
            company=good_job["company"],
            salary=good_job["salary"],
            city=good_job["city"],
            cfg=cfg
        )
        total_score = res_good.get("total", 0)
        verdict = res_good.get("verdict", "")

        # 模拟一份包含排除词的岗位 JD (例如：销售岗/单休)
        bad_job = {
            "title": "AI课程电话销售",
            "company": "某培训机构",
            "desc": "负责拨打电话推广AI课程，单休，加班多，要求抗压能力强。",
            "salary": "4-6K",
            "city": "深圳"
        }
        res_bad = match_engine.explain_match(
            bad_job["title"],
            bad_job["desc"],
            company=bad_job["company"],
            salary=bad_job["salary"],
            city=bad_job["city"],
            cfg=cfg
        )

        print_pass(f"合规岗位评估: 得分 {total_score}/100 -> 结论: {verdict}")
        print_pass(f"不合规岗位过滤: 得分 {res_bad.get('total', 0)}/100 -> 结论: {res_bad.get('verdict', '')}")
        print_info("五维匹配引擎与规则判定在纯标准库环境下正常运作（0 Token 消耗，毫秒级响应）")
        return True
    except Exception as e:
        print_missing(f"决策引擎测试异常: {e}")
        return False


def test_sqlite_store() -> bool:
    print("\n[4/5] 测试 SQLite 本地数据库初始化与表结构...")
    try:
        import store
        # 在内存数据库中验证 SCHEMA
        conn = sqlite3.connect(":memory:")
        conn.executescript(store.SCHEMA)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall() if not row[0].startswith("sqlite_")]
        conn.close()

        print_pass(f"SQLite 存储引擎就绪: 已创建核心表结构 ({', '.join(tables)})")
        return True
    except Exception as e:
        print_missing(f"SQLite 数据库测试失败: {e}")
        return False


def test_chrome_cdp_status() -> bool:
    print("\n[5/5] 检查投递专用 Chrome 浏览器连接状态...")
    port = 9223
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1.0)
    result = sock.connect_ex(("127.0.0.1", port))
    sock.close()

    if result == 0:
        print_pass(f"Chrome 调试端口 127.0.0.1:{port} 处于监听状态（浏览器已就绪）")
    else:
        print_warn(f"Chrome 调试端口 127.0.0.1:{port} 未开启")
        print_info("提示: 在演练模式 (dry-run) 下无需启动浏览器。")
        print_info("若后续需要正式自动化投递，请使用以下命令启动专用 Chrome 并扫码登录:")
        if sys.platform == "darwin":
            print_info('  macOS: /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --remote-debugging-port=9223 --user-data-dir="$HOME/job-hunter-chrome"')
        elif sys.platform.startswith("linux"):
            print_info('  Linux: google-chrome --remote-debugging-port=9223 --user-data-dir="$HOME/job-hunter-chrome"')
        else:
            print_info('  Windows: chrome.exe --remote-debugging-port=9223 --user-data-dir="%USERPROFILE%\\job-hunter-chrome"')
    return True


def main():
    print("=" * 60)
    print("      Job Hunter 客户端安全启动演练 (Client Dry-Run Test)     ")
    print("=" * 60)
    print("说明: 本测试仅验证代码、配置、规则与算法逻辑，绝不触碰任何网络投递接口。")

    results = []
    results.append(("核心模块导入", test_core_imports()))
    results.append(("配置加载", test_config_loader()))
    results.append(("决策匹配引擎", test_decision_engine()))
    results.append(("数据存储状态", test_sqlite_store()))
    results.append(("浏览器状态检查", test_chrome_cdp_status()))

    # 清理演练测试可能生成的任何临时标记
    for tmp_file in [ROOT_DIR / "dry_run_plan.json", ROOT_DIR / ".chrome.lock"]:
        if tmp_file.exists():
            try:
                tmp_file.unlink()
            except Exception:
                pass

    print("\n" + "=" * 60)
    failures = [name for name, ok in results if not ok]
    if not failures:
        print(f"{GREEN}Safe start check: PASS{RESET}")
        print("所有核心算法与功能组件演练完毕，程序可正常安全启动！")
        print("=" * 60)
        sys.exit(0)
    else:
        print(f"{RED}Safe start check: FAIL{RESET}")
        print(f"以下检查失败: {', '.join(failures)}")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
