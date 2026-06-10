class Symbol:
    def __init__(self, name, data_type, address, size, is_array=False, is_pointer=False):
        self.name = name
        self.data_type = data_type
        self.address = address
        self.size = size
        self.is_array = is_array
        self.pointer_level = 1 if is_pointer else 0

class SymbolTable:
    def __init__(self):
        self.global_scope = {}
        self.local_stack = []  # 本地作用域棧

    @property
    def local_scope(self):
        """返回當前（最頂層）的本地作用域"""
        return self.local_stack[-1] if self.local_stack else None

    def add_symbol(self, name, data_type, address, size):
        if self.local_stack:
            # 添加到本地作用域
            scope = self.local_stack[-1]
        else:
            # 添加到全局作用域
            scope = self.global_scope
        symbol = Symbol(name, data_type, address, size)
        scope[name] = symbol

    def lookup(self, name):
        # 從棧頂向下查找本地作用域
        for scope in reversed(self.local_stack):
            if name in scope:
                return scope[name]
        # 查找全局作用域
        if name in self.global_scope:
            return self.global_scope[name]
        return None

    def enter_function(self):
        """進入函數，推送新的本地作用域"""
        self.local_stack.append({})

    def exit_funnction(self):  # 保留拼寫錯誤以兼容舊代碼
        """退出函數，彈出本地作用域"""
        if self.local_stack:
            self.local_stack.pop()

    def reset(self):
        self.global_scope = {}
        self.local_stack = []
