# Job Hunter — 客户端试运行测试指南 (Client Trial Release)

欢迎使用 **Job Hunter** 试运行测试包！本文档面向第一次拿到项目的工程师，旨在帮助您在个人电脑环境中快速完成环境验证、依赖安装、安全自检与最小启动测试。

---

## 1. 项目用途

* **Job Hunter 是什么**：Job Hunter 是一套本地运行的自动化求职决策与拟真投递系统。核心采用纯本地 Python 确定性规则引擎与五维评估算法，实现精准、可解释且零 Token 消耗的岗位匹配与筛选。
* **当前版本主要功能**：支持自动化岗位抓取与解析、三层资格规则过滤（薪资底线/作息硬拦截/公司排查）、五维加权打分（技术30%/职业方向30%/经验15%/文化15%/地点10%）、防风控拟真自动化投递、SQLite 全流程状态追踪与失败归因。
* **包含的平台与组件**：当前版本主要支持主流招聘平台（BOSS直聘主入口、前程无忧 51job、猎聘），包含规则评估引擎、风控熔断机制与本地 SQLite 审计数据库。
* **当前版本阶段**：本项目处于**交付试运行阶段 (Client Trial Release)**。所有核心算法与投递链路已固化封板，本次交付专门用于甲方工程师验证自身宿主机环境的兼容性与可运行性。

---

## 2. 最低环境要求

根据项目源码与实际运行依赖严格核定：

| 配置项 | 最低要求 | 推荐配置 | 说明依据 |
| :--- | :--- | :--- | :--- |
| **操作系统** | macOS 11+, Linux, Windows 10/11 | macOS 13+ / Ubuntu 22.04+ | 跨平台 Python 标准环境与 Chrome 支持 |
| **Python 版本** | **Python 3.9+** | **Python 3.10 或 3.11** | 核心依赖及测试套件已验证兼容 Python 3.9+ |
| **Node.js / npm** | **无需安装** | 无 | 项目为纯 Python 架构，无前端打包或 Node 依赖 |
| **Chrome 浏览器** | Google Chrome (稳定版) | 最新稳定版 Chrome | 自动化投递需通过 CDP (Chrome DevTools Protocol) 驱动 |
| **必要浏览器组件** | Chrome Remote Debugging | 端口 9223 | 无需安装额外驱动（DrissionPage 原生支持 CDP 协议） |
| **内存建议** | 最低 4GB | 8GB 及以上 | 保证 Chrome 独立用户实例与 Python 进程稳定常驻 |
| **磁盘空间** | 500MB 可用空间 | 1GB+ | 虚拟环境依赖占用 ~150MB，浏览器缓存占用 ~200MB |
| **网络要求** | 基础外网连通 | 宽带/蜂窝均可 | 需能访问招聘平台主站，投递请求流量极低 |

---

## 3. 极速上手最短路径

从零启动只需 4 步：

```text
安装依赖 ──> 环境自检 (client_env_check) ──> 安全启动演练 (dry-run) ──> 正式运行
```

### 第一步：创建虚拟环境并安装依赖

进入项目根目录：

```bash
# 1. 创建干净的 Python 虚拟环境（推荐命名为 .venv）
python3 -m venv .venv

# 2. 激活虚拟环境
# macOS / Linux:
source .venv/bin/activate
# Windows (PowerShell):
# .venv\Scripts\Activate.ps1

# 3. 升级 pip 并安装核心依赖（仅 3 个轻量基础包）
pip install --upgrade pip
pip install -r requirements.txt
```

> **依赖说明**：`requirements.txt` 仅声明项目必需的三方库：
> * `DrissionPage>=4.0`：基于 CDP 协议的轻量拟真浏览器自动化控制库；
> * `httpx`：异步与同步 HTTP 网络通信库；
> * `PyYAML>=6.0`：候选人策略与调度配置解析库。

---

### 第二步：运行客户端环境自检

项目内置了无害的只读自检脚本，用于检测本地 Python、依赖包、Chrome 及网络状态：

```bash
python3 scripts/client_env_check.py
```

**预期输出效果**：
```text
============================================================
       Job Hunter 客户端运行环境自检 (Client Env Check)      
============================================================

[1/6] 检查 Python 运行环境:
[PASS] Python 3.x.x

[2/6] 检查核心依赖包:
[PASS] DrissionPage (4.1.1.4)
[PASS] httpx (0.28.1)
[PASS] PyYAML (6.0.3)

[3/6] 检查 Chrome 浏览器环境:
[PASS] Chrome detected: Google Chrome xxx (/path/to/chrome)

[4/6] 检查本地目录读写权限:
[PASS] 项目目录可读写权限

[5/6] 检查网络基础连通性:
[PASS] 网络基础连通性正常

[6/6] 检查项目配置文件:
[PASS] 模板配置 config.example.json 存在

============================================================
Environment check: PASS
您的本地环境完全满足 Job Hunter 的基础运行要求！
============================================================
```

如果出现 `[MISSING]`，脚本会精确指引缺失的软件包或 Chrome 安装路径，修复后重新运行即可。

---

### 第三步：执行最小安全演练测试 (Dry-Run)

在首次运行前，**严禁直接进行真实投递**。请先执行安全启动演练：

```bash
python3 scripts/client_dry_run.py
```

**安全演练验证内容**：
* 验证所有核心模块能否正常 `import`；
* 验证配置解析器与默认策略兜底机制；
* 离线模拟测试真实岗位 JD 通过五维匹配引擎（毫秒级计算，0 外部网络调用，0 真实申请）；
* 离线验证 SQLite 本地持久化表结构；
* 检测 Chrome 调试端口就绪状态。

也可以直接运行主入口的演练模式验证参数输出：
```bash
python3 boss_apply.py --dry-run
```
> **提示**：演练模式下不会连接任何在线招聘账号，绝不修改账号状态，绝不发送求职信，安全无害。

---

### 第四步：零依赖体验五维匹配打分引擎

Job Hunter 的评分引擎 `match_engine.py` 为纯 Python 标准库编写，可在终端中直接对任意职位描述进行五维打分评估：

```bash
python3 match_engine.py "AI应用工程师" \
  --desc "负责企业大模型应用开发、RAG知识库与Agent工作流编排，熟练使用Python与FastAPI，双休弹性" \
  --salary "18-25K" \
  --city "深圳"
```

终端将实时打印包含总分档位、五维明细柱状图与命中依据的评估卡片。

---

## 4. 配置说明

项目支持**零配置开箱即用**：如果不创建任何配置文件，程序会自动加载内置的安全策略与默认词表。

如需按自身需求自定义投递目标，请复制模板生成 `config.json`：

```bash
cp config.example.json config.json
```

### 关键配置项说明

| 配置键名 | 类型 | 必须/可选 | 说明与示例 |
| :--- | :--- | :---: | :--- |
| `skills` | 列表 | 可选 | 候选人核心技能词（如 `["Python", "FastAPI", "Agent"]`），命中加分 |
| `target_roles` | 列表 | 可选 | 期望目标岗位名称（如 `["AI应用工程师", "测试开发"]`） |
| `exclude_keywords` | 列表 | 可选 | 岗位标题硬排除词（如 `["销售", "总监", "实习"]`，命中直接过滤） |
| `body_exclude_keywords` | 列表 | 可选 | 岗位正文硬排除词（如 `["大小周", "单休", "夜班", "外包"]`） |
| `salary_filter` | 对象 | 可选 | 城市分级薪资底线设置（如低于 8K 自动跳过） |
| `min_score` | 整数 | 可选 | 最低投递分数线（默认 `60`） |
| `safety` | 对象 | 可选 | 风控护栏：日投递上限 (`normal_daily_cap: 50`)，小时上限 (`hourly_cap: 8`)，夜间禁投窗口等 |

### API Key / 凭据说明

* **核心决策与匹配引擎**：**无需任何 API Key**。全部过滤与打分均由本地纯规则引擎计算，零成本运行。
* **招聘平台账号**：无需在配置文件中填写账号密码。投递采用本地浏览器登录态复用方式，操作人员通过调试端口手动登录即可。
* **可选功能凭据**：
  * 若需启用可选的 AI 辅助草拟 HR 消息功能，可通过环境变量传入任意 OpenAI 兼容的 API Key（如 `export COMMANDCODE_API_KEY="your-api-key"`）；若未配置，系统会自动采用预设模板话术。
  * 若需启用移动端消息提醒，可通过环境变量配置 `WXPUSHER_APP_TOKEN` 与 `WXPUSHER_UID`；若未配置，所有结果在终端和本地日志中完整呈现。

---

## 5. 正式启动自动化投递（可选）

当上述环境自检与演练测试均通过，且甲方工程师需要测试完整的浏览器自动化流程时：

1. **以调试模式启动专用 Chrome 实例**：
   * **macOS**:
     ```bash
     /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
       --remote-debugging-port=9223 --user-data-dir="$HOME/job-hunter-chrome"
     ```
   * **Linux**:
     ```bash
     google-chrome --remote-debugging-port=9223 --user-data-dir="$HOME/job-hunter-chrome"
     ```
   * **Windows**:
     ```cmd
     chrome.exe --remote-debugging-port=9223 --user-data-dir="%USERPROFILE%\job-hunter-chrome"
     ```
2. **在打开的 Chrome 中登录招聘网站**（例如访问 `https://www.zhipin.com` 扫码登录）。
3. **运行主投递入口**：
   ```bash
   python3 boss_apply.py --cities "深圳" --jobs "AI应用工程师" --count 5
   ```

> 🛡️ **安全提示**：系统内置全天候风控保护。默认在夜间时段（22:00 - 08:00）处于安全禁投保护状态；如遇非工作时段测试，可优先使用 `--dry-run` 模式进行全流程验证。

---

## 6. 常见问题排查

* **Q: 运行提示 `Chrome 未启动或调试端口 (9223) 不可用`？**
  * A: 确保已使用上述第 5 节的命令启动了 Chrome，并且传入了 `--remote-debugging-port=9223` 参数。
* **Q: 提示 `当前处于夜间禁投时段`？**
  * A: 为防止平台封控账号，系统内置了夜间禁投护栏。在非工作时段验证请添加 `--dry-run` 参数。
* **Q: 如何检查投递历史与本地审计记录？**
  * A: 本地投递记录统一存放在 SQLite 数据库（`ab_experiment.db`），可通过 `python3 -m unittest` 运行单元测试套件或使用 SQLite 客户端只读查看。
