class BuildINFunction:
    def __init__(self, memory):
        self.memory = memory

    def write_str(self, address, string):
        for i, ch in enumerate(string):
            self.memory.write_char(address + i, ord(ch))
        self.memory.write_char(address + len(string), 0)

    def read_str(self, address):
        result = []
        i = 0
        while True:
            ch = self.memory.read_char(address + i)
            if ch == 0:
                break
            result.append(chr(ch))
            i += 1
        return ''.join(result)

    def printf(self, *args):
        if not args:
            return 0
        fmt_addr = args[0]
        fmt_str = self.read_str(fmt_addr)
        
        arg_idx = 1
        result = []
        i = 0
        while i < len(fmt_str):
            if fmt_str[i] == '%' and i + 1 < len(fmt_str):
                spec = fmt_str[i + 1]
                if spec == 'd':
                    if arg_idx < len(args):
                        result.append(str(args[arg_idx]))
                        arg_idx += 1
                    i += 2
                elif spec == 'c':
                    if arg_idx < len(args):
                        result.append(chr(args[arg_idx]))
                        arg_idx += 1
                    i += 2
                elif spec == 's':
                    if arg_idx < len(args):
                        result.append(self.read_str(args[arg_idx]))
                        arg_idx += 1
                    i += 2
                elif spec == 'x':
                    if arg_idx < len(args):
                        result.append(hex(args[arg_idx])[2:])
                        arg_idx += 1
                    i += 2
                elif spec == '%':
                    result.append('%')
                    i += 2
                else:
                    result.append(fmt_str[i])
                    i += 1
            elif fmt_str[i] == '\\' and i + 1 < len(fmt_str):
                next_ch = fmt_str[i + 1]
                if next_ch == 'n':
                    result.append('\n')
                    i += 2
                elif next_ch == 't':
                    result.append('\t')
                    i += 2
                else:
                    result.append(fmt_str[i])
                    i += 1
            else:
                result.append(fmt_str[i])
                i += 1
        
        print(''.join(result), end='')
        return len(''.join(result))

    def scanf(self, *args):
        if not args:
            return 0
        fmt_addr = args[0]
        fmt_str = self.read_str(fmt_addr)
        
        try:
            if '%d' in fmt_str and len(args) > 1:
                val = int(input())
                self.memory.write_int(args[1], val)
                return 1
            elif '%c' in fmt_str and len(args) > 1:
                val = input()[0]
                self.memory.write_char(args[1], ord(val))
                return 1
            return 0
        except:
            return 0

    def strlen(self, *args):
        if not args:
            return 0
        addr = args[0]
        length = 0
        while self.memory.read_char(addr + length) != 0:
            length += 1
        return length

    def strcpy(self, *args):
        if len(args) < 2:
            return 0
        dest = args[0]
        src = args[1]
        i = 0
        while True:
            ch = self.memory.read_char(src + i)
            self.memory.write_char(dest + i, ch)
            if ch == 0:
                break
            i += 1
        return dest

    def strcmp(self, *args):
        if len(args) < 2:
            return 0
        s1 = self.read_str(args[0])
        s2 = self.read_str(args[1])
        if s1 == s2:
            return 0
        return 1 if s1 > s2 else -1

    def strcat(self, *args):
        if len(args) < 2:
            return 0
        dest = args[0]
        src = args[1]
        
        i = 0
        while self.memory.read_char(dest + i) != 0:
            i += 1
        
        j = 0
        while True:
            ch = self.memory.read_char(src + j)
            self.memory.write_char(dest + i + j, ch)
            if ch == 0:
                break
            j += 1
        return dest

    def getchar(self, *args):
        try:
            return ord(input()[0])
        except:
            return 0

    def putchar(self, *args):
        if args:
            print(chr(args[0]), end='')
        return 0

    def puts(self, *args):
        if args:
            print(self.read_str(args[0]))
        return 0

    def exit(self, *args):
        code = args[0] if args else 0
        print(f"程式回傳: {code}")
        import sys
        sys.exit(code)

    def max(self, *args):
        if len(args) < 2:
            return 0
        return max(args[0], args[1])

    def min(self, *args):
        if len(args) < 2:
            return 0
        return min(args[0], args[1])

    def abs(self, *args):
        if not args:
            return 0
        return abs(args[0])

    def pow(self, *args):
        if len(args) < 2:
            return 0
        return int(args[0] ** args[1])

    def sqrt(self, *args):
        if not args:
            return 0
        val = args[0]
        if val < 0:
            raise RuntimeError("sqrt: argument cannot be negative")
        return int(val ** 0.5)

    def mod(self, *args):
        if len(args) < 2:
            return 0
        return args[0] % args[1]
    
    def atoi(self, *args):
        """將字符串轉換為整數"""
        if not args:
            return 0
        string = self.read_str(args[0])
        try:
            return int(string)
        except:
            return 0
    
    def itoa(self, *args):
        """將整數轉換為十進制字符串"""
        if len(args) < 2:
            return 0
        value = args[0]
        str_addr = args[1]
        string = str(value)
        self.write_str(str_addr, string)
        return str_addr
    
    def rand(self, *args):
        """返回 0 到 32767 之間的隨機數"""
        import random
        return random.randint(0, 32767)
    
    def srand(self, *args):
        """使用種子初始化隨機數生成器"""
        import random
        if args:
            random.seed(args[0])
        return 0
    
    def memset(self, *args):
        """將 ptr 所指向的記憶體區域之前 size 個位元組設定為 value"""
        if len(args) < 3:
            return 0
        ptr = args[0]
        value = args[1]
        size = args[2]
        for i in range(size):
            self.memory.write_char(ptr + i, value & 0xFF)
        return ptr
    
    def sizeof_int(self, *args):
        """回傳 int 型別的位元組數（固定為 4）"""
        return 4
    
    def sizeof_char(self, *args):
        """回傳 char 型別的位元組數（固定為 1）"""
        return 1
