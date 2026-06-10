[README (1).md](https://github.com/user-attachments/files/28806526/README.1.md)
# Small-C Interactive Interpreter 🖥️

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Status](https://img.shields.io/badge/status-Complete-brightgreen)
![Tests](https://img.shields.io/badge/tests-11%2F11%20passed-brightgreen)

> 一個完整實現的 Small-C 語言互動式解譯器，支持詞法分析、語法分析、語義執行等完整編譯過程。

## 📸 功能演示

```
$ python3 main.py
Small-C Interpreter REPL
輸入 HELP 查看指令
sc> int x = 10;
程式回傳: 0

sc> printf("x = %d\n", x);
x = 10
程式回傳: 0

sc> ABOUT
╔════════════════════════════════════════════════════════════════════╗
║                   Small-C 互動式解譯器                            ║
║  【版本號】Version 1.0 (Release)                                   ║
║  【作者】Yenbi (顏比)                                              ║
║  【課程】系統軟體 (Spring 2026)                                   ║
╚════════════════════════════════════════════════════════════════════╝

sc> HELP VARS
指令：VARS
功能：列出所有全域變數
用法：VARS
說明：顯示當前全域作用域中的所有變數...

sc> LOAD tests/test01_arithmetic.sc
✓ 已載入 test01_arithmetic.sc (10 行)

sc> RUN
a + b = 13
a - b = 7
a * b = 30
a / b = 3
a % b = 1
程式回傳: 0
```

---

## ✨ 核心功能

### 語言特性

| 功能 | 支持 |
|------|------|
| **資料型別** | `int`, `char`, 指標 (`*`), 陣列 (`[]`) |
| **運算子** | 13 級優先級運算符（算術、邏輯、位元、關係） |
| **控制結構** | `if/else`, `while`, `for`, `do-while`, `break`, `continue` |
| **函式** | 定義、呼叫、遞歸、參數傳遞 |
| **前處理器** | `#define` 常數定義 |
| **註解** | `//` 和 `/* */` |

### 編譯過程

```
源代碼 → 詞法分析 → 語法分析 → 語義執行 → 輸出結果
         (Lexer)   (Parser)   (Interpreter)
```

### REPL 環境

**17 個互動式指令：**

| 分類 | 指令 |
|------|------|
| **程式管理** | `APPEND`, `LIST`, `INSERT`, `DELETE`, `EDIT`, `SAVE`, `LOAD`, `NEW` |
| **執行與除錯** | `RUN`, `CHECK`, `TRACE`, `VARS`, `FUNCS` |
| **系統** | `HELP`, `ABOUT`, `CLEAR`, `QUIT`, `EXIT` |

### 內建函數

**24 個函數：**

```python
# 輸入輸出
printf, scanf, putchar, getchar, puts

# 字串操作
strlen, strcpy, strcmp, strcat

# 數學運算
abs, max, min, pow, sqrt, mod

# 轉換函數
atoi, itoa, sizeof_int, sizeof_char

# 其他
rand, srand, memset, exit
```

---

## 🚀 快速開始

### 必要條件

- Python 3.10+
- 無第三方依賴

### 安裝

```bash
# 克隆倉庫
git clone https://github.com/yenbi/smaltc.git
cd smaltc

# 執行解譯器
python3 main.py
```

### 基本用法

#### 直接執行代碼

```bash
sc> int x = 5;
程式回傳: 0

sc> int y = 10;
程式回傳: 0

sc> printf("x + y = %d\n", x + y);
x + y = 15
程式回傳: 0
```

#### 多行輸入

```bash
sc> APPEND
進入多行輸入模式，輸入 '.' 結束
1> int main() {
2>     printf("Hello, Small-C!\n");
3>     return 0;
4> }
5> .
✓ 已添加 4 行

sc> RUN
Hello, Small-C!
程式回傳: 0
```

#### 載入測試程式

```bash
sc> LOAD tests/test01_arithmetic.sc
✓ 已載入 test01_arithmetic.sc (10 行)

sc> RUN
a + b = 13
a - b = 7
a * b = 30
a / b = 3
a % b = 1
程式回傳: 0
```

#### 查看幫助

```bash
sc> HELP              # 顯示所有指令
sc> HELP VARS         # 查看 VARS 詳細說明
sc> HELP APPEND       # 查看 APPEND 詳細說明
sc> HELP RUN          # 查看 RUN 詳細說明
```

#### 查看解譯器資訊

```bash
sc> ABOUT
# 顯示版本、作者、課程資訊等
```

---

## 📚 文件結構

```
smaltc/
├── 【核心解譯器】
│   ├── main.py                    # 進入點
│   ├── mylexer.py                 # 詞法分析器
│   ├── parser.py                  # 語法分析器
│   ├── interpreter.py             # 語義執行引擎
│   ├── symtable.py                # 符號表管理
│   ├── memory.py                  # 記憶體管理
│   ├── builtins.py                # 內建函數庫
│   └── repl.py                    # 互動式環境
│
├── 【測試程式集】
│   └── tests/
│       ├── test01_arithmetic.sc      # 基本算術
│       ├── test02_variables.sc       # 變數操作
│       ├── test03_if_else.sc         # 條件控制
│       ├── test04_loops.sc           # 迴圈控制
│       ├── test05_function.sc        # 函式定義
│       ├── test06_fibonacci.sc       # 遞迴函式
│       ├── test07_array.sc           # 陣列操作
│       ├── test08_pointer.sc         # 指標操作
│       ├── test09_string.sc          # 字串操作
│       ├── test10_error_division.sc  # 錯誤檢查
│       ├── test11_error_array_bounds.sc # 邊界檢查
│       └── README.md
│
├── 【文檔】
│   ├── Technical_Report.md           # 技術報告
│   ├── HELP_AND_ABOUT_DEMO.md        # 新功能演示
│   ├── RECORDING_GUIDE.md            # 錄影指南
│   ├── QUICK_REFERENCE.md            # 快速參考
│   └── README.md (本檔案)
│
└── 【其他】
    ├── .gitignore
    └── LICENSE
```

---

## 🧪 測試

### 運行所有測試

```bash
python3 verify_tests.py
```

### 測試結果

```
✅ Test 01 - 基本算術: PASS
✅ Test 02 - 變數操作: PASS
✅ Test 03 - if/else 控制: PASS
✅ Test 04 - for/while 迴圈: PASS
✅ Test 05 - 函式定義: PASS
✅ Test 06 - 遞迴函式: PASS
✅ Test 07 - 陣列操作: PASS
✅ Test 08 - 指標操作: PASS
✅ Test 09 - 字串與字符: PASS
✅ Test 10 - 錯誤檢查（除以零）: PASS
✅ Test 11 - 錯誤檢查（陣列越界）: PASS

測試結果：11/11 通過 (100%)
```

---

## 💻 系統架構

### 三層編譯器架構

```
┌─────────────────────────────────────────┐
│      互動式環境 (REPL)                  │
│  (repl.py - 用戶界面與命令處理)        │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│   詞法分析 → 語法分析 → 語義分析        │
│ (mylexer)   (parser)   (interpreter)    │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│      執行階段 (Execution)                │
│ (記憶體管理、符號表、內建函數)         │
└──────────────────────────────────────────┘
```

### 記憶體模型

```
┌─────────────────────────────┐
│  起始位址：1000              │
├─────────────────────────────┤
│  變數 x (int, 4 bytes)      │
│  位址: 1000-1003            │
├─────────────────────────────┤
│  變數 y (int, 4 bytes)      │
│  位址: 1004-1007            │
├─────────────────────────────┤
│  陣列 arr[10] (40 bytes)    │
│  位址: 1008-1047            │
├─────────────────────────────┤
│  其他變數...                 │
└─────────────────────────────┘
```

---

## 📊 統計

| 指標 | 數值 |
|------|------|
| **代碼行數** | 2,200+ |
| **模組數** | 8 個 |
| **測試程式** | 11 個 |
| **測試通過率** | 100% |
| **REPL 指令** | 17 個 |
| **內建函數** | 24 個 |
| **支持功能** | 100% |

---

## 🎓 課程信息

| 項目 | 內容 |
|------|------|
| **課程名稱** | 系統軟體 (System Software) |
| **修課學期** | 2026 年春季學期 |
| **實現語言** | Python 3.10+ |
| **完成日期** | 2026-06-11 |

---

## 📝 範例程式

### 例 1：基本算術

```c
int main() {
    int a = 10;
    int b = 3;
    printf("a + b = %d\n", a + b);
    printf("a * b = %d\n", a * b);
    return 0;
}
```

輸出：
```
a + b = 13
a * b = 30
程式回傳: 0
```

### 例 2：遞迴函式（Fibonacci）

```c
int fib(int n) {
    if (n <= 0) return 0;
    if (n == 1) return 1;
    return fib(n - 1) + fib(n - 2);
}

int main() {
    int i;
    printf("Fibonacci: ");
    for (i = 0; i < 7; i = i + 1) {
        printf("%d ", fib(i));
    }
    printf("\n");
    return 0;
}
```

輸出：
```
Fibonacci: 0 1 1 2 3 5 8 
程式回傳: 0
```

### 例 3：指標操作

```c
void swap(int *a, int *b) {
    int temp;
    temp = *a;
    *a = *b;
    *b = temp;
}

int main() {
    int x = 5;
    int y = 10;
    printf("Before: x = %d, y = %d\n", x, y);
    swap(&x, &y);
    printf("After: x = %d, y = %d\n", x, y);
    return 0;
}
```

輸出：
```
Before: x = 5, y = 10
After: x = 10, y = 5
程式回傳: 0
```

---

## 🔧 進階功能

### 錯誤偵測

解譯器支持多種執行期錯誤偵測：

```bash
# 除以零
sc> int result = 10 / 0;
❌ 執行錯誤: division by zero

# 陣列越界
sc> int arr[3];
sc> arr[5] = 20;
❌ 執行錯誤: Runtime error: array index out of bounds (index 5, size 3).

# Null 指標
sc> int *ptr = 0;
sc> *ptr = 10;
❌ 執行錯誤: Null pointer dereference
```

### 追蹤模式

```bash
sc> TRACE ON
✓ 追蹤模式已啟用

sc> RUN
[line 1] <statement>
[line 2] <expression>
...
```

### 語法檢查

```bash
sc> APPEND
1> int main() {
2>     int x = 10
3>     return 0;
4> }
5> .

sc> CHECK
✗ 語法錯誤: Expected ';' at line 2
```

---

## 🛠️ 開發過程

### 主要困難及解決方案

1. **模組循環依賴**
   - 解決：使用動態導入

2. **符號表作用域管理**
   - 解決：棧式作用域管理

3. **全域變數跨執行保留**
   - 解決：條件性初始化

4. **陣列邊界檢查**
   - 解決：運行時邊界檢查

5. **#define 常數支持**
   - 解決：前期注入符號表

---

## 🤝 貢獻

本項目為課程作業，歡迎提出建議和反饋。

### 如何報告問題

```
1. 檢查是否已有相同 Issue
2. 提供詳細的錯誤信息
3. 包含重現步驟
4. 提供環境信息（Python 版本等）
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 作者

**Yenbi (顏比)**
- 📧 Email: student@university.edu.tw
- 🔗 GitHub: [@yenbi](https://github.com/yenbi)

---

## 📚 參考資料

- Ron Cain (1980) - A small C compiler
- James Hendrix (1984) - The Small-C handbook
- Robert Nystrom (2021) - Crafting Interpreters

---

## ⭐ 致謝

感謝課程教授提供的指導和作業規範。

---

## 📞 聯繫方式

有問題或建議？請通過以下方式聯繫：
- GitHub Issues
- 電子郵件：student@university.edu.tw
- GitHub Discussions

---

## 🎉 項目狀態

| 項目 | 狀態 |
|------|------|
| 核心功能 | ✅ 完成 |
| 測試驗證 | ✅ 完成 |
| 文檔編寫 | ✅ 完成 |
| 展示影片 | ✅ 完成 |
| 規則符合 | ✅ 100% |

**專案完成度：100% ✅**

---

**最後更新**：2026-06-11  
**版本**：1.0 (Release)  
**狀態**：完成並驗證

---

<div align="center">

Made with ❤️ for System Software Course  
© 2026 Yenbi. All rights reserved.

</div>
