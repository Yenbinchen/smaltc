import os
import sys
import mylexer as lexer
from importlib import import_module

# 確保當前目錄在 sys.path 中
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 動態導入避免名稱衝突
import importlib.util
parser_spec = importlib.util.spec_from_file_location("parser_module", os.path.join(current_dir, "parser.py"))
parser_module = importlib.util.module_from_spec(parser_spec)
parser_spec.loader.exec_module(parser_module)
Parser = parser_module.Parser

interpreter_spec = importlib.util.spec_from_file_location("interpreter_module", os.path.join(current_dir, "interpreter.py"))
interpreter_module = importlib.util.module_from_spec(interpreter_spec)
interpreter_spec.loader.exec_module(interpreter_module)
Interpreter = interpreter_module.Interpreter

class REPL:
    def __init__(self, memory=None, symtable=None, builtins_module=None):
        if memory is None or symtable is None or builtins_module is None:
            # 若未提供，自己建立
            from memory import SystemMemory
            from symtable import SymbolTable
            import importlib.util as util
            builtins_spec = util.spec_from_file_location("custom_builtins", os.path.join(current_dir, "builtins.py"))
            custom_builtins = util.module_from_spec(builtins_spec)
            builtins_spec.loader.exec_module(custom_builtins)
            
            self.memory = SystemMemory()
            self.symtable = SymbolTable()
            self.builtins = custom_builtins.BuildINFunction(self.memory)
        else:
            # 使用外部提供的物件
            self.memory = memory
            self.symtable = symtable
            self.builtins = builtins_module
        
        self.buffer = []
        self.buffer_modified = False
        self.trace_mode = False
        self.interpreter = None

    def run(self):
        print("Small-C Interpreter REPL")
        print("輸入 HELP 查看指令")
        while True:
            try:
                cmd = input("sc> ").strip()
                if not cmd:
                    continue
                self.process_command(cmd)
            except KeyboardInterrupt:
                print("\n再見！")
                break
            except Exception as e:
                print(f"❌ 錯誤: {e}")

    def start(self):
        """別名，與 run() 相同"""
        self.run()

    def process_command(self, cmd):
        parts = cmd.split(maxsplit=1)
        if not parts:
            return
        
        command = parts[0].upper()
        arg = parts[1] if len(parts) > 1 else None
        
        # 檢查是否是有效的 REPL 命令
        valid_commands = {'APPEND', 'LIST', 'INSERT', 'DELETE', 'EDIT', 'SAVE', 'LOAD', 'NEW', 'RUN', 'CHECK', 'TRACE', 'VARS', 'FUNCS', 'HELP', 'ABOUT', 'CLEAR', 'QUIT', 'EXIT'}
        
        if command not in valid_commands:
            # 如果不是有效命令，嘗試作為單行程式執行
            self._execute_direct(cmd)
            return
        
        if command == 'APPEND': self._append_buffer()
        elif command == 'LIST': self._list_buffer(arg)
        elif command == 'INSERT': self._insert_buffer(arg)
        elif command == 'DELETE': self._delete_buffer(arg)
        elif command == 'EDIT': self._edit_buffer(arg)
        elif command == 'SAVE': self._save_buffer(arg)
        elif command == 'LOAD': self._load_buffer(arg)
        elif command == 'NEW': self._new_buffer()
        elif command == 'RUN': self._run_program()
        elif command == 'CHECK': self._check_syntax()
        elif command == 'TRACE': self._set_trace(arg)
        elif command == 'VARS': self._list_variables()
        elif command == 'FUNCS': self._list_functions()
        elif command == 'HELP': self._show_help(arg)
        elif command == 'ABOUT': self._show_about()
        elif command == 'CLEAR': self._clear_screen()
        elif command in ('QUIT', 'EXIT'): self._quit()
        else: print(f"❌ 未知指令: {command}\n")

    def _append_buffer(self):
        print("進入多行輸入模式，輸入 '.' 結束")
        start_line = len(self.buffer)
        while True:
            s = input(f"{len(self.buffer) + 1}> ")
            if s.strip() == ".": break
            self.buffer.append(s)
        self.buffer_modified = True
        print(f"✓ 已添加 {len(self.buffer) - start_line} 行\n")

    def _list_buffer(self, arg):
        if not self.buffer:
            print("(空緩衝區)\n")
            return
        
        if arg:
            if '-' in arg:
                # LIST 1-3 格式
                parts = arg.split('-')
                start = int(parts[0]) - 1  # 轉換為 0-indexed
                end = int(parts[1])  # end 是 exclusive
            else:
                # LIST 2 格式 - 顯示第 2 行
                line_num = int(arg)
                if line_num < 1 or line_num > len(self.buffer):
                    print(f"⚠️  行號 {line_num} 超出範圍（共 {len(self.buffer)} 行）\n")
                    return
                start = line_num - 1  # 轉換為 0-indexed
                end = line_num  # 只顯示這一行
        else:
            # LIST（無參數）- 顯示全部
            start, end = 0, len(self.buffer)
        
        for i in range(start, min(end, len(self.buffer))):
            print(f"{i+1:4}: {self.buffer[i]}")
        print()

    def _insert_buffer(self, arg):
        if not arg:
            print("用法: INSERT <line_number>\n")
            return
        line_num = int(arg) - 1
        print("進入插入模式，輸入 '.' 結束")
        while True:
            s = input(f"{line_num + 1}> ")
            if s.strip() == ".": break
            self.buffer.insert(line_num, s)
            line_num += 1
        self.buffer_modified = True
        print(f"✓ 已插入\n")

    def _delete_buffer(self, arg):
        if not arg:
            print("用法: DELETE <line> 或 DELETE <start>-<end>\n")
            return
        
        if '-' in arg:
            start, end = map(int, arg.split('-'))
            del self.buffer[start-1:end]
        else:
            del self.buffer[int(arg)-1]
        
        self.buffer_modified = True
        print("✓ 已刪除\n")

    def _edit_buffer(self, arg):
        if not arg:
            print("用法: EDIT <line_number>\n")
            return
        
        line_num = int(arg) - 1
        print(f"原內容: {self.buffer[line_num]}")
        new_line = input(f"編輯第 {line_num + 1} 行> ")
        
        if new_line:
            self.buffer[line_num] = new_line
            self.buffer_modified = True
            print("✓ 已編輯\n")

    def _save_buffer(self, filename):
        if not filename:
            print("用法: SAVE <filename>\n")
            return
        
        with open(filename, 'w') as f:
            f.write('\n'.join(self.buffer))
        
        self.buffer_modified = False
        num_lines = len(self.buffer)
        print(f"✓ 已保存到 {filename} ({num_lines} 行)\n")

    def _load_buffer(self, filename):
        if not filename:
            print("用法: LOAD <filename>\n")
            return
        
        if self.buffer_modified:
            confirm = input("有未保存的變更，確定要載入嗎? (y/n): ")
            if confirm.lower() != 'y':
                print()
                return
        
        with open(filename, 'r') as f:
            self.buffer = f.read().strip().split('\n')
        
        self.buffer_modified = False
        num_lines = len(self.buffer)
        print(f"✓ 已載入 {filename} ({num_lines} 行)\n")

    def _new_buffer(self):
        if self.buffer_modified:
            confirm = input("有未保存的變更，確定要清除嗎? (y/n): ")
            if confirm.lower() != 'y':
                print()
                return
        
        self.buffer = []
        self.buffer_modified = False
        self.memory.reset()
        self.symtable.reset()
        self.interpreter = None
        print("✓ 緩衝區已清除\n")

    def _run_program(self):
        code = "\n".join(self.buffer)
        if not code.strip():
            print("(空程式碼)\n")
            return
        
        try:
            lex = lexer.Lexer(code)
            tokens = lex.tokenize()
            defines = lex.defines
            
            ast = Parser(tokens).parse_program()
            
            if ast:
                self.memory.reset()
                self.symtable.reset()
                
                # 注入 #define 常數
                for const_name, const_value in defines.items():
                    const_addr = self.memory.allocate(4)
                    self.memory.write_int(const_addr, const_value)
                    self.symtable.add_symbol(const_name, 'int', const_addr, 4)
                
                self.interpreter = Interpreter(self.memory, self.symtable, self.builtins)
                self.interpreter.trace_mode = self.trace_mode
                result = self.interpreter.visit(ast)
                print()
            else:
                print("(空程式碼)\n")
        except Exception as e:
            print(f"❌ 執行錯誤: {e}\n")

    def _check_syntax(self):
        code = "\n".join(self.buffer)
        if not code.strip():
            print("(空程式碼)\n")
            return
        
        try:
            lex = lexer.Lexer(code)
            tokens = lex.tokenize()
            ast = Parser(tokens).parse_program()
            print("✓ 語法檢查通過 - No errors found\n")
        except Exception as e:
            print(f"✗ 語法錯誤: {e}\n")

    def _set_trace(self, arg):
        if not arg:
            print("用法: TRACE ON/OFF\n")
            return
        
        if arg.upper() == 'ON':
            self.trace_mode = True
            print("✓ 追蹤模式已啟用\n")
        elif arg.upper() == 'OFF':
            self.trace_mode = False
            print("✓ 追蹤模式已關閉\n")

    def _list_variables(self):
        if not self.interpreter:
            print("未執行程式，無變數資訊\n")
            return
        
        scope = self.interpreter.symtable.global_scope
        if not scope:
            print("(無變數)\n")
            return
        
        print("\n全域變數：")
        for name, symbol in scope.items():
            addr = symbol.address
            
            if getattr(symbol, 'is_array', False):
                print(f"  {name} ({symbol.data_type}[{symbol.size // (4 if symbol.data_type == 'int' else 1)}]) @ {addr}")
            elif getattr(symbol, 'pointer_level', 0) > 0:
                print(f"  {name} ({symbol.data_type}*) @ {addr}")
            elif symbol.data_type == 'char':
                val = self.memory.read_char(addr)
                print(f"  {name} (char) = '{chr(val) if 32 <= val < 127 else '?'}' (ASCII {val}) @ {addr}")
            else:
                val = self.memory.read_int(addr)
                print(f"  {name} (int) = {val} @ {addr}")
        
        print()

    def _list_functions(self):
        print("\n" + "="*80)
        print("函式清單")
        print("="*80)
        print(f"{'函式名':<18} {'回傳型別':<12} {'參數':<45} {'標記':<15}")
        print("-"*80)
        
        # 顯示用戶定義的函數
        if self.interpreter and hasattr(self.interpreter, 'functions'):
            for func_name in sorted(self.interpreter.functions.keys()):
                func_def = self.interpreter.functions[func_name]
                ret_type = func_def.return_type
                
                # 格式化參數列表
                if func_def.params:
                    params = []
                    for param in func_def.params:
                        if len(param) == 3:
                            ptype, pname, pptr = param
                            if pptr > 0:
                                params.append(f"{'*' * pptr}{pname}")
                            else:
                                params.append(pname)
                        else:
                            ptype, pname = param
                            params.append(pname)
                    param_str = ', '.join(params)
                else:
                    param_str = 'void'
                
                print(f"{func_name:<18} {ret_type:<12} {param_str:<45} [user-defined]")
        
        print()
        
        # 顯示內建函數
        builtins = [
            ('abs', 'int', 'int x'),
            ('atoi', 'int', 'char *s'),
            ('exit', 'void', 'int code'),
            ('getchar', 'int', 'void'),
            ('itoa', 'void', 'int value, char *str'),
            ('max', 'int', 'int a, int b'),
            ('memset', 'void', 'char *ptr, int val, int size'),
            ('min', 'int', 'int a, int b'),
            ('mod', 'int', 'int a, int b'),
            ('pow', 'int', 'int base, int exp'),
            ('printf', 'int', 'const char *format, ...'),
            ('putchar', 'int', 'int ch'),
            ('puts', 'int', 'char *s'),
            ('rand', 'int', 'void'),
            ('scanf', 'int', 'const char *format, ...'),
            ('sizeof_char', 'int', 'void'),
            ('sizeof_int', 'int', 'void'),
            ('sqrt', 'int', 'int x'),
            ('srand', 'void', 'int seed'),
            ('strcat', 'int', 'char *dest, char *src'),
            ('strcmp', 'int', 'char *s1, char *s2'),
            ('strcpy', 'int', 'char *dest, const char *src'),
            ('strlen', 'int', 'const char *str'),
        ]
        
        for name, ret_type, params in builtins:
            print(f"{name:<18} {ret_type:<12} {params:<45} [built-in]")
        
        print("="*80 + "\n")

    def _show_help(self, cmd):
        if not cmd:
            print("""
========== Small-C Interpreter - 指令幫助 ==========
【程式管理】
  APPEND              進入多行輸入模式，輸入 '.' 結束
  LIST [n] [n1-n2]    列出程式碼（可指定行數）
  INSERT <n>          在第n行前插入代碼
  DELETE <n>/<n1-n2>  刪除行（支持範圍刪除）
  EDIT <n>            編輯第n行的內容
  SAVE <file>         保存程式碼到文件
  LOAD <file>         從文件載入程式碼
  NEW                 清除緩衝區（重新開始）

【執行與除錯】
  RUN                 執行緩衝區中的程式
  CHECK               檢查程式語法（不執行）
  TRACE ON/OFF        開啟/關閉執行追蹤模式
  VARS                列出所有全域變數及其值
  FUNCS               列出所有函式（用戶定義+內建）

【系統】
  HELP [cmd]          顯示幫助（可指定指令詳細說明）
  ABOUT               關於本解譯器
  CLEAR               清除終端機畫面
  QUIT/EXIT           退出程式

輸入 'HELP <指令名稱>' 查看特定指令的詳細說明
例如：HELP VARS      查看 VARS 指令的詳細說明
""")
        else:
            # 詳細的幫助文本
            helps = {
                'APPEND': """
指令：APPEND
功能：進入多行輸入模式
用法：APPEND
說明：
  進入多行輸入模式，可以輸入多行程式碼。
  每行代碼前會顯示行號。
  輸入 '.' 單獨成行可結束輸入。
  
範例：
  sc> APPEND
  進入多行輸入模式，輸入 '.' 結束
  1> int main() {
  2>     printf("Hello\\n");
  3>     return 0;
  4> }
  5> .
  ✓ 已添加 4 行
""",
                'LIST': """
指令：LIST
功能：列出程式碼緩衝區
用法：
  LIST              列出全部程式碼
  LIST n            列出第 n 行
  LIST n1-n2        列出第 n1 到 n2 行

說明：
  顯示當前緩衝區中的程式碼，每行左側顯示行號。
  可以指定行號或範圍來查看特定部分。

範例：
  sc> LIST
  sc> LIST 5
  sc> LIST 1-10
""",
                'INSERT': """
指令：INSERT
功能：在指定行前插入新代碼
用法：INSERT <n>
說明：
  在第 n 行前插入新的代碼行。
  進入插入模式後，輸入 '.' 結束。

範例：
  sc> INSERT 3
  進入插入模式，輸入 '.' 結束
  3> int x = 10;
  3> .
  ✓ 已插入
""",
                'DELETE': """
指令：DELETE
功能：刪除指定行
用法：
  DELETE n          刪除第 n 行
  DELETE n1-n2      刪除第 n1 到 n2 行

說明：
  從程式碼緩衝區刪除指定的行。
  支持刪除單行或範圍內的多行。

範例：
  sc> DELETE 5
  sc> DELETE 1-5
""",
                'EDIT': """
指令：EDIT
功能：編輯指定行
用法：EDIT <n>
說明：
  編輯第 n 行的內容。
  顯示原內容後，輸入新內容替換。

範例：
  sc> EDIT 3
  原內容: int x = 10;
  編輯第 3 行> int x = 20;
  ✓ 已編輯
""",
                'SAVE': """
指令：SAVE
功能：保存程式碼到文件
用法：SAVE <filename>
說明：
  將當前程式碼緩衝區保存到指定文件。
  文件名稱通常以 .sc 為副檔名。

範例：
  sc> SAVE myprogram.sc
  ✓ 已保存到 myprogram.sc (15 行)
""",
                'LOAD': """
指令：LOAD
功能：從文件載入程式碼
用法：LOAD <filename>
說明：
  從指定文件載入程式碼到緩衝區。
  若有未保存的變更，會提示確認。

範例：
  sc> LOAD myprogram.sc
  ✓ 已載入 myprogram.sc (15 行)
""",
                'NEW': """
指令：NEW
功能：清除程式碼緩衝區
用法：NEW
說明：
  清除當前程式碼緩衝區並重置狀態。
  若有未保存的變更，會提示確認。
  同時重置所有全域變數和函數。

範例：
  sc> NEW
  ✓ 緩衝區已清除
""",
                'RUN': """
指令：RUN
功能：執行緩衝區中的程式碼
用法：RUN
說明：
  對緩衝區中的 Small-C 程式進行詞法分析、
  語法分析、語義檢查，最後執行。
  如遇錯誤會顯示詳細的錯誤訊息。

範例：
  sc> RUN
  Hello, World!
  程式回傳: 0
""",
                'CHECK': """
指令：CHECK
功能：檢查程式碼語法
用法：CHECK
說明：
  對緩衝區中的程式碼進行語法檢查。
  不執行程式碼，只檢查是否有語法錯誤。

範例：
  sc> CHECK
  ✓ 語法檢查通過 - No errors found
""",
                'TRACE': """
指令：TRACE
功能：啟用或禁用執行追蹤模式
用法：TRACE <ON|OFF>
說明：
  開啟追蹤模式後，執行程式時會顯示
  詳細的執行步驟和各節點的訪問過程。
  用於除錯和理解程式執行流程。

範例：
  sc> TRACE ON
  ✓ 追蹤模式已啟用
  sc> RUN
  [line 1] <statement>
  [line 2] <expression>
  ...
""",
                'VARS': """
指令：VARS
功能：列出所有全域變數
用法：VARS
說明：
  顯示當前全域作用域中的所有變數。
  對於每個變數，顯示：
    - 變數名稱
    - 資料型別（int, char, 陣列, 指標）
    - 目前值（如適用）
    - 記憶體位址

範例：
  sc> VARS
  
  全域變數：
    x (int) = 25 @ 1000
    y (int) = -18 @ 1004
    ch (char) = 'Z' (ASCII 90) @ 1070
""",
                'FUNCS': """
指令：FUNCS
功能：列出所有函式
用法：FUNCS
說明：
  顯示所有已定義的函式（用戶定義和內建）。
  對於每個函式，顯示：
    - 函式名稱
    - 回傳型別
    - 參數列表
    - 標記（用戶定義或內建）

範例：
  sc> FUNCS
  
  ================================================================================
  函式清單
  ================================================================================
  函式名              回傳型別     參數                            標記
  ================================================================================
  swap                void         int *a, int *b                 [user-defined]
  main                int          void                           [user-defined]
  abs                 int          int x                          [built-in]
  printf              int          const char *format, ...        [built-in]
  ...
""",
                'HELP': """
指令：HELP
功能：顯示幫助訊息
用法：
  HELP              顯示所有指令的概述
  HELP <cmd>        顯示特定指令的詳細說明

說明：
  獲取指令的使用說明。可以查看單個指令的詳細用法。

範例：
  sc> HELP
  sc> HELP VARS
""",
                'ABOUT': """
指令：ABOUT
功能：顯示解譯器資訊
用法：ABOUT
說明：
  顯示解譯器的名稱、版本、作者與課程資訊。

範例：
  sc> ABOUT
""",
                'CLEAR': """
指令：CLEAR
功能：清除終端機畫面
用法：CLEAR
說明：
  清除終端機中的所有輸出內容，保持清潔的工作環境。

範例：
  sc> CLEAR
""",
                'QUIT': """
指令：QUIT 或 EXIT
功能：退出解譯器
用法：QUIT 或 EXIT
說明：
  終止解譯器程式。
  若有未保存的變更，會提示確認。

範例：
  sc> QUIT
  再見！
""",
            }
            
            cmd_upper = cmd.upper()
            if cmd_upper in helps:
                print(helps[cmd_upper])
            else:
                print(f"❌ 未知指令: {cmd}\n")
                print("輸入 'HELP' 查看所有指令說明\n")

    def _show_about(self):
        print("""

Small-C 互動式解譯器    
作者 陳彥斌B1329021
修課學期 2026 SPRING                        
版本 3.0

""")

    def _clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def _quit(self):
        if self.buffer_modified:
            confirm = input("有未保存的變更，確定要退出嗎? (y/n): ")
            if confirm.lower() != 'y':
                return
        print("再見！")
        exit()

    def _execute_direct(self, code):
        """直接執行單行程式碼 - 保留全域變數狀態"""
        try:
            # 代碼作為全域層級執行，不包裝在 main 中，允許變數跨執行保留
            wrapped_code = code + "\nint main() { return 0; }"
            
            lex = lexer.Lexer(wrapped_code)
            tokens = lex.tokenize()
            defines = lex.defines
            
            ast = Parser(tokens).parse_program()
            
            if ast:
                # 第一次執行時才建立和重置環境
                if self.interpreter is None:
                    self.memory.reset()
                    self.symtable.reset()
                    
                    # 注入 #define 常數
                    for const_name, const_value in defines.items():
                        const_addr = self.memory.allocate(4)
                        self.memory.write_int(const_addr, const_value)
                        self.symtable.add_symbol(const_name, 'int', const_addr, 4)
                    
                    self.interpreter = Interpreter(self.memory, self.symtable, self.builtins)
                else:
                    # 後續執行：只注入新的 #define
                    for const_name, const_value in defines.items():
                        if self.symtable.lookup(const_name) is None:
                            const_addr = self.memory.allocate(4)
                            self.memory.write_int(const_addr, const_value)
                            self.symtable.add_symbol(const_name, 'int', const_addr, 4)
                
                self.interpreter.trace_mode = self.trace_mode
                result = self.interpreter.visit(ast)
                print()
            else:
                print("(空程式碼)\n")
        except Exception as e:
            print(f"❌ 執行錯誤: {e}\n")

if __name__ == '__main__':
    repl = REPL()
    repl.run()
