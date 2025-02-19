# FormFiller 表格填充助手
(替代原[form_filler](https://github.com/usernameAlreadyTaken7Times/form_filler)(已弃用))

## 项目简介
本项目旨在实现根据当前复制字段自动在剪贴板填充对应文字的功能。通过该项目，可以在填充表格等重复性较高的场景提高操作效率。

## 功能特点
- 快速调用 Excel 内数据并在指定位置粘贴
- 可在程序内快速查看和编辑信息

## 技术栈
- python == 3.12
- GUI：PysimpleGUI
- Database: 使用 xlsx 文件

## 使用方法

### 前提条件
- python == 3.12

### 安装步骤
1. 克隆本项目到本地或直接下载 ZIP 包：

```bash
git clone https://github.com/usernameAlreadyTaken7Times/form_filler_new
```

2. 进入项目目录：

```bash
cd form_filler_new/
```

3. 构建并启动 conda 或 venv 虚拟环境，并从 requirements.txt 安装依赖。

```bash
# 新建并使用venv虚拟环境
python -m venv .venv
.\.venv\Scripts\Activate.ps1 (Windows)
```

```bash
# 安装依赖
pip install -r requirements.txt
```

4. 回到目录，确保 main.py 所在位置有 config.json 配置文件，且配置文件内包含了正确的输入/输出和备份文件地址。
```config
# 工作表路径和名称
'input_data_xlsx_filepath': '$PATH'
'input_data_sheet_name': '$SHEETNAME'
```

5. 运行项目：

```bash
python main.py
```

## 实现原理
- 通过 keyboard 监听 Ctrl+C 复制键，通过 pyperclip 读写剪贴板和键值
- 使用另一个工作表储存键可能的其他名称，并在键未匹配时尝试寻找

