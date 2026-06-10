class Interpreter:
    def __init__(self, memory, symtable, builtins):
        self.memory = memory
        self.symtable = symtable
        self.builtins = builtins
        self.trace_mode = False
        self.functions = {}
        self.return_value = None
        self.should_return = False
        self.should_break = False
        self.should_continue = False

    def visit(self, node):
        if node is None:
            return None
        
        if self.trace_mode:
            print(f"DEBUG: Visiting {type(node).__name__}")
            
        node_type = type(node).__name__

        if node_type == 'ProgramNode':
            for item in node.items:
                if type(item).__name__ == 'FunctionDefNode':
                    self.functions[item.name] = item
            
            result = None
            for item in node.items:
                if type(item).__name__ != 'FunctionDefNode':
                    result = self.visit(item)
            
            if 'main' in self.functions:
                result = self._call_function('main', [])
                print(f"程式回傳: {result}")
            
            return result

        if node_type == 'NumberNode':
            return node.value
            
        elif node_type == 'HexNode':
            return node.value
        
        elif node_type == 'CharNode':
            return node.value
            
        elif node_type == 'UnaryOpNode':
            val = self.visit(node.expr)
            op = node.op.value
            if op == '-': 
                return -val
            elif op == '!': 
                return 1 if val == 0 else 0
            elif op == '~': 
                return ~val
            return None
                
        elif node_type == 'BinOpNode':
            op_sign = node.op.value
            
            if op_sign == '&&':
                left_val = self.visit(node.left)
                if left_val == 0: 
                    return 0
                right_val = self.visit(node.right)
                return 1 if right_val != 0 else 0
            
            elif op_sign == '||':
                left_val = self.visit(node.left)
                if left_val != 0: 
                    return 1
                right_val = self.visit(node.right)
                return 1 if right_val != 0 else 0
            
            left_val = self.visit(node.left)
            right_val = self.visit(node.right)
            
            if op_sign == '+': 
                return left_val + right_val
            elif op_sign == '-': 
                return left_val - right_val
            elif op_sign == '*': 
                return left_val * right_val
            elif op_sign == '/':
                if right_val == 0: 
                    raise RuntimeError("division by zero")
                return int(left_val / right_val)
            elif op_sign == '%':
                if right_val == 0: 
                    raise RuntimeError("division by zero")
                return left_val % right_val
            elif op_sign == '&': 
                return left_val & right_val
            elif op_sign == '|': 
                return left_val | right_val
            elif op_sign == '^': 
                return left_val ^ right_val
            elif op_sign == '<<': 
                return left_val << right_val
            elif op_sign == '>>': 
                return left_val >> right_val
            elif op_sign == '>': 
                return 1 if left_val > right_val else 0
            elif op_sign == '<': 
                return 1 if left_val < right_val else 0
            elif op_sign == '==': 
                return 1 if left_val == right_val else 0
            elif op_sign == '!=': 
                return 1 if left_val != right_val else 0
            elif op_sign == '>=': 
                return 1 if left_val >= right_val else 0
            elif op_sign == '<=': 
                return 1 if left_val <= right_val else 0

        elif node_type == 'StringNode':
            str_len = len(node.value) + 1
            addr = self.memory.allocate(str_len)
            self.builtins.write_str(addr, node.value)
            return addr 
            
        elif node_type == 'VarNode':
            symbol = self.symtable.lookup(node.name)
            if symbol is None: 
                raise RuntimeError(f"Runtime error: Undefined variable '{node.name}'")
            
            # 對於數組，返回數組地址；對於普通變數，讀取值
            is_array = getattr(symbol, 'is_array', False)
            if is_array:
                return symbol.address
            
            if symbol.data_type == 'char':
                return self.memory.read_char(symbol.address)
            else:
                return self.memory.read_int(symbol.address)

        elif node_type == 'PointerDerefNode':
            addr = self.visit(node.expr)
            if addr == 0:
                raise RuntimeError("Runtime error: Null pointer dereference")
            return self.memory.read_int(addr)

        elif node_type == 'AddressOfNode':
            if type(node.expr).__name__ == 'VarNode':
                symbol = self.symtable.lookup(node.expr.name)
                if symbol is None:
                    raise RuntimeError(f"Runtime error: Undefined variable '{node.expr.name}'")
                return symbol.address
            elif type(node.expr).__name__ == 'ArrayAccessNode':
                array = self.visit(node.expr.array)
                index = self.visit(node.expr.index)
                offset = index * 4
                return array + offset
            else:
                raise RuntimeError("Runtime error: Cannot take address of this expression")

        elif node_type == 'ArrayAccessNode':
            array = self.visit(node.array)
            index = self.visit(node.index)
            
            # 獲取陣列符號以檢查邊界
            array_var_name = None
            if type(node.array).__name__ == 'VarNode':
                array_var_name = node.array.name
                symbol = self.symtable.lookup(array_var_name)
                if symbol and getattr(symbol, 'is_array', False):
                    array_size = symbol.size // 4  # int 佔 4 字節
                    if index < 0 or index >= array_size:
                        raise RuntimeError(f"Runtime error: array index out of bounds (index {index}, size {array_size}).")
            
            offset = index * 4
            return self.memory.read_int(array + offset)

        elif node_type == 'VarDeclNode':
            # 檢查變數是否已經存在（全域範圍）
            existing_symbol = None
            if not self.symtable.local_stack:  # 在全域範圍
                existing_symbol = self.symtable.lookup(node.name)
            
            if existing_symbol and not self.symtable.local_stack:
                # 全域變數已存在，只更新值
                addr = existing_symbol.address
                if node.init_expr:
                    val = self.visit(node.init_expr)
                    if node.data_type == 'char': 
                        self.memory.write_char(addr, val)
                    else: 
                        self.memory.write_int(addr, val)
            else:
                # 新建變數
                type_size = 4 if node.data_type == 'int' else 1
                
                if node.pointer_level > 0:
                    alloc_size = 4
                elif node.is_array:
                    alloc_size = type_size * node.array_size
                else:
                    alloc_size = type_size
                    
                addr = self.memory.allocate(alloc_size)
                self.symtable.add_symbol(node.name, node.data_type, addr, alloc_size)
                
                # 設置數組標記
                symbol = self.symtable.lookup(node.name)
                if symbol:
                    symbol.is_array = node.is_array
                    symbol.pointer_level = node.pointer_level
                
                if node.init_expr:
                    val = self.visit(node.init_expr)
                    if node.data_type == 'char': 
                        self.memory.write_char(addr, val)
                    else: 
                        self.memory.write_int(addr, val)
            return None

        elif node_type == 'AssignNode':
            target_type = type(node.target).__name__
            val = self.visit(node.expr)
            
            if target_type == 'VarNode':
                symbol = self.symtable.lookup(node.target.name)
                if symbol is None:
                    raise RuntimeError(f"Runtime error: Undefined variable '{node.target.name}'")
                if symbol.data_type == 'char':
                    self.memory.write_char(symbol.address, val)
                else:
                    self.memory.write_int(symbol.address, val)
            elif target_type == 'PointerDerefNode':
                addr = self.visit(node.target.expr)
                if addr == 0:
                    raise RuntimeError("Runtime error: Null pointer dereference")
                self.memory.write_int(addr, val)
            elif target_type == 'ArrayAccessNode':
                array = self.visit(node.target.array)
                index = self.visit(node.target.index)
                
                # 檢查陣列邊界
                array_var_name = None
                if type(node.target.array).__name__ == 'VarNode':
                    array_var_name = node.target.array.name
                    symbol = self.symtable.lookup(array_var_name)
                    if symbol and getattr(symbol, 'is_array', False):
                        array_size = symbol.size // 4  # int 佔 4 字節
                        if index < 0 or index >= array_size:
                            raise RuntimeError(f"Runtime error: array index out of bounds (index {index}, size {array_size}).")
                
                offset = index * 4
                self.memory.write_int(array + offset, val)
            else:
                raise RuntimeError(f"Runtime error: Cannot assign to {target_type}")
            
            return val

        elif node_type == 'CompoundAssignNode':
            target_type = type(node.target).__name__
            
            if target_type == 'VarNode':
                symbol = self.symtable.lookup(node.target.name)
                if symbol is None:
                    raise RuntimeError(f"Runtime error: Undefined variable '{node.target.name}'")
                current_val = self.memory.read_int(symbol.address)
            elif target_type == 'PointerDerefNode':
                addr = self.visit(node.target.expr)
                if addr == 0:
                    raise RuntimeError("Runtime error: Null pointer dereference")
                current_val = self.memory.read_int(addr)
            elif target_type == 'ArrayAccessNode':
                array = self.visit(node.target.array)
                index = self.visit(node.target.index)
                
                # 檢查陣列邊界
                if type(node.target.array).__name__ == 'VarNode':
                    array_var_name = node.target.array.name
                    symbol = self.symtable.lookup(array_var_name)
                    if symbol and getattr(symbol, 'is_array', False):
                        array_size = symbol.size // 4  # int 佔 4 字節
                        if index < 0 or index >= array_size:
                            raise RuntimeError(f"Runtime error: array index out of bounds (index {index}, size {array_size}).")
                
                offset = index * 4
                current_val = self.memory.read_int(array + offset)
            else:
                raise RuntimeError(f"Runtime error: Cannot compound assign to {target_type}")
            
            expr_val = self.visit(node.expr)
            op = node.op[:-1]
            
            if op == '+':
                new_val = current_val + expr_val
            elif op == '-':
                new_val = current_val - expr_val
            elif op == '*':
                new_val = current_val * expr_val
            elif op == '/':
                if expr_val == 0:
                    raise RuntimeError("Runtime error: division by zero.")
                new_val = int(current_val / expr_val)
            elif op == '%':
                if expr_val == 0:
                    raise RuntimeError("Runtime error: division by zero.")
                new_val = current_val % expr_val
            else:
                new_val = current_val
            
            if target_type == 'VarNode':
                self.memory.write_int(symbol.address, new_val)
            elif target_type == 'PointerDerefNode':
                self.memory.write_int(addr, new_val)
            elif target_type == 'ArrayAccessNode':
                self.memory.write_int(array + offset, new_val)
            
            return new_val
            
        elif node_type == 'CompoundNode':
            for stmt in node.statements:
                self.visit(stmt)
                if self.should_return or self.should_break:
                    break
            return None

        elif node_type == 'IfNode':
            if self.visit(node.condition):
                self.visit(node.if_body)
            elif node.else_body:
                self.visit(node.else_body)
            return None

        elif node_type == 'WhileNode':
            while self.visit(node.condition) != 0:
                self.visit(node.body)
                if self.should_continue:
                    self.should_continue = False
                    continue
                if self.should_return or self.should_break:
                    break
            self.should_break = False
            return None

        elif node_type == 'ForNode':
            if node.init:
                self.visit(node.init)
            
            while node.condition is None or self.visit(node.condition) != 0:
                self.visit(node.body)
                if self.should_continue:
                    self.should_continue = False
                    if node.update:
                        self.visit(node.update)
                    continue
                if self.should_break:
                    break
                if self.should_return:
                    break
                if node.update:
                    self.visit(node.update)
            
            self.should_break = False
            return None

        elif node_type == 'DoWhileNode':
            while True:
                self.visit(node.body)
                if self.should_continue:
                    self.should_continue = False
                if self.should_break:
                    self.should_break = False
                    break
                if self.should_return:
                    break
                if self.visit(node.condition) == 0:
                    break
            return None

        elif node_type == 'BreakNode':
            self.should_break = True
            return None

        elif node_type == 'ContinueNode':
            self.should_continue = True
            return None

        elif node_type == 'ReturnNode':
            if node.expr:
                self.return_value = self.visit(node.expr)
            else:
                self.return_value = 0
            self.should_return = True
            return self.return_value

        elif node_type == 'FuncCallNode':
            if node.func_name in ('strcpy', 'strcat', 'strcmp', 'strlen', 'scanf'):
                args_vals = []
                for i, arg in enumerate(node.args):
                    arg_type = type(arg).__name__
                    
                    need_address = False
                    if node.func_name in ('strcpy', 'strcat', 'strcmp', 'strlen') and i == 0:
                        need_address = True
                    elif node.func_name == 'scanf' and i > 0:
                        need_address = True
                    
                    if need_address and arg_type == 'VarNode':
                        symbol = self.symtable.lookup(arg.name)
                        args_vals.append(symbol.address)
                    elif need_address and arg_type == 'StringNode':
                        str_len = len(arg.value) + 1
                        addr = self.memory.allocate(str_len)
                        self.builtins.write_str(addr, arg.value)
                        args_vals.append(addr)
                    else:
                        args_vals.append(self.visit(arg))
            else:
                args_vals = [self.visit(arg) for arg in node.args]
            
            if node.func_name in self.functions:
                return self._call_function(node.func_name, args_vals)
            
            if hasattr(self.builtins, node.func_name):
                func = getattr(self.builtins, node.func_name)
                try:
                    result = func(*args_vals)
                    return result if result is not None else 0
                except Exception as e:
                    raise RuntimeError(f"Runtime error in function '{node.func_name}': {e}")
            else:
                raise RuntimeError(f"Runtime error: Unknown function '{node.func_name}'")
                
        raise RuntimeError(f"Runtime error: Unknown AST node type '{node_type}'.")

    def _call_function(self, func_name, args):
        func_def = self.functions[func_name]
        
        self.symtable.enter_function()
        
        try:
            for i, param_info in enumerate(func_def.params):
                if i < len(args):
                    if len(param_info) == 3:
                        param_type, param_name, param_ptr = param_info
                    else:
                        param_type, param_name = param_info
                        param_ptr = 0
                    
                    if param_ptr > 0:
                        addr = self.memory.allocate(4)
                        self.symtable.add_symbol(param_name, param_type, addr, 4)
                        self.memory.write_int(addr, args[i])
                    else:
                        addr = self.memory.allocate(4 if param_type == 'int' else 1)
                        self.symtable.add_symbol(param_name, param_type, addr, 4 if param_type == 'int' else 1)
                        if param_type == 'char':
                            self.memory.write_char(addr, args[i])
                        else:
                            self.memory.write_int(addr, args[i])
            
            self.should_return = False
            self.return_value = 0
            
            self.visit(func_def.body)
            
            result = self.return_value
            return result
        
        finally:
            self.symtable.exit_funnction()
            self.should_return = False
            self.return_value = 0
