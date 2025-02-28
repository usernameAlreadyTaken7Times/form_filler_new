# FormFiller 表格填充助手
(替代原[form_filler](https://github.com/usernameAlreadyTaken7Times/form_filler)(已弃用))

## 项目简介
本项目旨在实现根据当前复制字段自动在剪贴板填充对应文字的功能。通过该项目，可以在诸如为大量人物、填充表格内重复字段等场景提高操作效率。

## 功能特点
- 快速调用 Excel 内数据并在指定位置粘贴
- 可在程序内快速查看和编辑信息

## 技术栈
- python == 3.12
- GUI：PysimpleGUI
- Database: 使用 xlsx 文件

## 使用方式
在 Release 中下载编译好的 windows 执行文件，并确保文件目录下存在 config.json 配置文件。修改配置文件内数据文件目录，保存后执行程序。

打开程序后，可以使用程序内的 Modifier 修改人物条目和条目别称。关闭程序后修改内容会自动同步到数据文件。也可以手动在 xlsx 文件中修改内容。

执行程序时，先使用 Run/Terminate 按键或 Ctrl+R/Ctrl+T 快捷键启动或终止键盘快捷键监听服务。服务运行时，使用键盘上下键切换人物，左右键切换字段。对应人物和字段的值会自动同步到剪贴板；也可以先上下键确认人物后，选中屏幕字段，并按 Ctrl+C 进行检索。若对应字段匹配当前任务的数据库内某一条目，则将对应的值复制入剪贴板，随后可按 Ctrl+V 粘贴。


## 构建方法

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
```bash
# 工作表路径和名称
'input_data_xlsx_filepath': '$PATH'
'input_data_sheet_name': '$SHEETNAME'
```

5. 运行项目：

```bash
python main.py
```

## 实现原理和架构

- 程序分为三个线程。主线程运行 ui 模块，两个子线程运行 Keyboard 和 Business 模块。其中：

    - ui 模块负责用户界面的渲染，采用 PysimpleGUI 作为解决方案；
    - keyboard 模块通过 keyboard 包监听键盘输入，并通过 pyperclip 读取和写入剪贴板相关内容；
    - Business 模块从 data 模块中读取信息，并处理相关程序业务逻辑。

- 不同线程之间通过额外的消息队列 shared_queue 进行通讯。为了保证不同线程均可将各自消息写入队列并消费消息，存在三个消息队列，每个新消息发布时都会复制一份进入消息队列。

- 程序内置了两个 Modifier。其中：
    - data_modifier 可用来编辑人物和对应的键/值，键名不应重复，且所有人物都应有相同的键/值；
    - alias_modifier 可用来编辑键可能的别称，键可能有多个别称，但别称不应重复。

- data 模块处理信息的输入和输出。它读取 xlsx 文件内容，并在程序加载时写入程序内便于操作。为了实现人物 - 键值和键值 - 别称的要求，xlsx 文件内应包含两个工作表，分别储存对应信息。示例工作表可在目录/assets/下找到。
