class ASTNode: pass

class VarDeclNode(ASTNode):
    def __init__(self, data_type, name, init_expr=None, is_array=False, array_size=0, pointer_level=0):
        self.data_type = data_type
        self.name = name
        self.init_expr = init_expr
        self.is_array = is_array
        self.array_size = array_size
        self.pointer_level = pointer_level

class StringNode(ASTNode):
    def __init__(self, token): self.value = token.value

class CharNode(ASTNode):
    def __init__(self, token): self.value = token.value

class VarNode(ASTNode):
    def __init__(self, token): self.name = token.value

class FuncCallNode(ASTNode):
    def __init__(self, func_name, args):
        self.func_name = func_name
        self.args = args

class BinOpNode(ASTNode):
    def __init__(self, left, op_token, right):
        self.left = left
        self.op = op_token
        self.right = right

class UnaryOpNode(ASTNode):
    def __init__(self, op_token, expr):
        self.op = op_token
        self.expr = expr

class NumberNode(ASTNode):
    def __init__(self, token): self.value = int(token.value)

class HexNode(ASTNode):
    def __init__(self, token):
        self.value = int(token.value, 16) if isinstance(token.value, str) else token.value

class AssignNode(ASTNode):
    def __init__(self, target, expr):
        self.target = target
        self.expr = expr

class CompoundAssignNode(ASTNode):
    def __init__(self, target, op, expr):
        self.target = target
        self.op = op
        self.expr = expr

class CompoundNode(ASTNode):
    def __init__(self, statements):
        self.statements = statements

class IfNode(ASTNode):
    def __init__(self, condition, if_body, else_body=None):
        self.condition = condition
        self.if_body = if_body
        self.else_body = else_body

class WhileNode(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class DoWhileNode(ASTNode):
    def __init__(self, body, condition):
        self.body = body
        self.condition = condition

class BreakNode(ASTNode):
    pass

class ContinueNode(ASTNode):
    pass

class ForNode(ASTNode):
    def __init__(self, init, condition, update, body):
        self.init = init
        self.condition = condition
        self.update = update
        self.body = body

class ReturnNode(ASTNode):
    def __init__(self, expr=None):
        self.expr = expr

class FunctionDefNode(ASTNode):
    def __init__(self, return_type, name, params, body):
        self.return_type = return_type
        self.name = name
        self.params = params
        self.body = body

class ProgramNode(ASTNode):
    def __init__(self, items):
        self.items = items

class ArrayAccessNode(ASTNode):
    def __init__(self, array, index):
        self.array = array
        self.index = index

class PointerDerefNode(ASTNode):
    def __init__(self, expr):
        self.expr = expr

class AddressOfNode(ASTNode):
    def __init__(self, expr):
        self.expr = expr

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current_token(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def consume(self, expected_type):
        token = self.current_token()
        if token and token.type == expected_type:
            self.pos += 1
            return token
        raise RuntimeError(f"Expected '{expected_type}', got '{token.type if token else 'EOF'}' at pos {self.pos}")

    def parse_program(self):
        items = []
        while self.current_token() and self.current_token().type != 'EOF':
            tok = self.current_token()
            
            if tok.type == 'KEYWORD' and tok.value in ('int', 'char', 'void'):
                if self._is_function_definition():
                    items.append(self.parse_function_def())
                else:
                    stmt = self.parse_statement()
                    if stmt:
                        items.append(stmt)
            else:
                stmt = self.parse_statement()
                if stmt:
                    items.append(stmt)
        
        return ProgramNode(items) if items else None

    def _is_function_definition(self):
        if self.current_token().type != 'KEYWORD':
            return False
        
        saved_pos = self.pos
        self.pos += 1
        
        while self.current_token() and self.current_token().value == '*':
            self.pos += 1
        
        if self.current_token() and self.current_token().type == 'IDENT':
            self.pos += 1
            result = self.current_token() and self.current_token().value == '('
            self.pos = saved_pos
            return result
        
        self.pos = saved_pos
        return False

    def parse_function_def(self):
        return_type = self.consume('KEYWORD').value
        
        ptr_level = 0
        while self.current_token() and self.current_token().value == '*':
            ptr_level += 1
            self.pos += 1
        
        func_name = self.consume('IDENT').value
        
        self.consume('OP')
        params = []
        while self.current_token() and self.current_token().value != ')':
            param_type = self.consume('KEYWORD').value
            
            param_ptr = 0
            while self.current_token() and self.current_token().value == '*':
                param_ptr += 1
                self.pos += 1
            
            param_name = self.consume('IDENT').value
            params.append((param_type, param_name, param_ptr))
            
            if self.current_token() and self.current_token().value == ',':
                self.pos += 1
        
        self.consume('OP')
        self.consume('OP')
        body_stmts = []
        while self.current_token() and self.current_token().value != '}':
            stmt = self.parse_statement()
            if stmt:
                body_stmts.append(stmt)
        self.consume('OP')
        
        return FunctionDefNode(return_type, func_name, params, CompoundNode(body_stmts))

    def parse_statement(self):
        tok = self.current_token()
        
        if not tok or tok.type == 'EOF':
            return None
        
        if tok.type == 'KEYWORD' and tok.value == 'for':
            return self.parse_for()
        
        if tok.type == 'KEYWORD' and tok.value == 'while':
            return self.parse_while()
        
        if tok.type == 'KEYWORD' and tok.value == 'do':
            return self.parse_do_while()
        
        if tok.type == 'KEYWORD' and tok.value == 'break':
            self.pos += 1
            if self.current_token() and self.current_token().value == ';':
                self.consume('OP')
            return BreakNode()
        
        if tok.type == 'KEYWORD' and tok.value == 'continue':
            self.pos += 1
            if self.current_token() and self.current_token().value == ';':
                self.consume('OP')
            return ContinueNode()
        
        if tok.type == 'KEYWORD' and tok.value == 'if':
            return self.parse_if()
        
        if tok.type == 'KEYWORD' and tok.value == 'return':
            self.pos += 1
            expr = None
            if self.current_token() and self.current_token().value != ';':
                expr = self.parse_expression()
            if self.current_token() and self.current_token().value == ';':
                self.consume('OP')
            return ReturnNode(expr)
        
        if tok.type == 'KEYWORD' and tok.value in ('int', 'char'):
            return self.parse_var_decl()
        
        return self.parse_expr_statement()

    def parse_for(self):
        self.consume('KEYWORD')
        self.consume('OP')
        
        init = None
        if self.current_token() and self.current_token().value != ';':
            init = self.parse_expr_statement()
        else:
            self.consume('OP')
        
        condition = None
        if self.current_token() and self.current_token().value != ';':
            condition = self.parse_expression()
        self.consume('OP')
        
        update = None
        if self.current_token() and self.current_token().value != ')':
            update = self.parse_expression()
        self.consume('OP')
        
        self.consume('OP')
        body_stmts = []
        while self.current_token() and self.current_token().value != '}':
            stmt = self.parse_statement()
            if stmt:
                body_stmts.append(stmt)
        self.consume('OP')
        
        return ForNode(init, condition, update, CompoundNode(body_stmts))

    def parse_while(self):
        self.consume('KEYWORD')
        self.consume('OP')
        condition = self.parse_expression()
        self.consume('OP')
        self.consume('OP')
        body_stmts = []
        while self.current_token() and self.current_token().value != '}':
            stmt = self.parse_statement()
            if stmt:
                body_stmts.append(stmt)
        self.consume('OP')
        return WhileNode(condition, CompoundNode(body_stmts))

    def parse_do_while(self):
        self.consume('KEYWORD')  # 消耗 'do'
        self.consume('OP')  # 消耗 '{'
        body_stmts = []
        while self.current_token() and self.current_token().value != '}':
            stmt = self.parse_statement()
            if stmt:
                body_stmts.append(stmt)
        self.consume('OP')  # 消耗 '}'
        self.consume('KEYWORD')  # 消耗 'while'
        self.consume('OP')  # 消耗 '('
        condition = self.parse_expression()
        self.consume('OP')  # 消耗 ')'
        if self.current_token() and self.current_token().value == ';':
            self.consume('OP')  # 消耗 ';'
        return DoWhileNode(CompoundNode(body_stmts), condition)

    def parse_if(self):
        self.consume('KEYWORD')
        self.consume('OP')  # '('
        condition = self.parse_expression()
        self.consume('OP')  # ')'
        
        # 支持可選的大括號
        has_brace = self.current_token() and self.current_token().value == '{'
        if has_brace:
            self.consume('OP')
        
        if_stmts = []
        if has_brace:
            while self.current_token() and self.current_token().value != '}':
                stmt = self.parse_statement()
                if stmt:
                    if_stmts.append(stmt)
            self.consume('OP')
        else:
            # 單個語句
            stmt = self.parse_statement()
            if stmt:
                if_stmts.append(stmt)
        
        else_body = None
        if self.current_token() and self.current_token().type == 'KEYWORD' and self.current_token().value == 'else':
            self.consume('KEYWORD')
            
            # 支持可選的大括號
            has_else_brace = self.current_token() and self.current_token().value == '{'
            if has_else_brace:
                self.consume('OP')
            
            else_stmts = []
            if has_else_brace:
                while self.current_token() and self.current_token().value != '}':
                    stmt = self.parse_statement()
                    if stmt:
                        else_stmts.append(stmt)
                self.consume('OP')
            else:
                stmt = self.parse_statement()
                if stmt:
                    else_stmts.append(stmt)
            
            else_body = CompoundNode(else_stmts)
        
        return IfNode(condition, CompoundNode(if_stmts), else_body)

    def parse_var_decl(self):
        type_tok = self.consume('KEYWORD')
        
        ptr_level = 0
        while self.current_token() and self.current_token().value == '*':
            ptr_level += 1
            self.pos += 1
        
        var_tok = self.consume('IDENT')
        
        is_arr = False
        arr_size = 0
        if self.current_token() and self.current_token().value == '[':
            self.pos += 1
            tok = self.current_token()
            if tok.type == 'NUMBER':
                size_tok = self.consume('NUMBER')
                arr_size = int(size_tok.value)
            elif tok.type == 'IDENT':
                # 允許使用符號常數（如 SIZE）
                size_tok = self.consume('IDENT')
                arr_size = 8  # 預設值，實際大小由常數決定
            else:
                raise RuntimeError(f"Expected array size, got {tok.type}")
            self.consume('OP')
            is_arr = True
        
        init_expr = None
        if self.current_token() and self.current_token().value == '=':
            self.pos += 1
            init_expr = self.parse_expression()
        
        if self.current_token() and self.current_token().value == ';':
            self.consume('OP')
        
        return VarDeclNode(type_tok.value, var_tok.value, init_expr, is_arr, arr_size, ptr_level)

    def parse_expr_statement(self):
        expr = self.parse_assignment()
        
        if self.current_token() and self.current_token().value == ';':
            self.consume('OP')
        
        return expr

    def parse_assignment(self):
        expr = self.parse_or_expr()
        
        tok = self.current_token()
        if tok and tok.type == 'OP':
            if tok.value == '=':
                self.pos += 1
                right = self.parse_assignment()
                return AssignNode(expr, right)
            elif tok.value in ('+=', '-=', '*=', '/=', '%='):
                op = tok.value
                self.pos += 1
                right = self.parse_assignment()
                return CompoundAssignNode(expr, op, right)
        
        return expr

    def parse_or_expr(self):
        node = self.parse_and_expr()
        while True:
            tok = self.current_token()
            if tok and tok.type == 'OP' and tok.value == '||':
                op_tok = tok
                self.pos += 1
                node = BinOpNode(node, op_tok, self.parse_and_expr())
            else:
                break
        return node

    def parse_and_expr(self):
        node = self.parse_equality()
        while True:
            tok = self.current_token()
            if tok and tok.type == 'OP' and tok.value == '&&':
                op_tok = tok
                self.pos += 1
                node = BinOpNode(node, op_tok, self.parse_equality())
            else:
                break
        return node

    def parse_equality(self):
        node = self.parse_relational()
        while True:
            tok = self.current_token()
            if tok and tok.type == 'OP' and tok.value in ('==', '!='):
                op_tok = tok
                self.pos += 1
                node = BinOpNode(node, op_tok, self.parse_relational())
            else:
                break
        return node

    def parse_relational(self):
        node = self.parse_bitwise()
        while True:
            tok = self.current_token()
            if tok and tok.type == 'OP' and tok.value in ('<', '>', '<=', '>='):
                op_tok = tok
                self.pos += 1
                node = BinOpNode(node, op_tok, self.parse_bitwise())
            else:
                break
        return node

    def parse_bitwise(self):
        node = self.parse_shift()
        while True:
            tok = self.current_token()
            if tok and tok.type == 'OP' and tok.value in ('&', '|', '^'):
                op_tok = tok
                self.pos += 1
                node = BinOpNode(node, op_tok, self.parse_shift())
            else:
                break
        return node

    def parse_shift(self):
        node = self.parse_additive()
        while True:
            tok = self.current_token()
            if tok and tok.type == 'OP' and tok.value in ('<<', '>>'):
                op_tok = tok
                self.pos += 1
                node = BinOpNode(node, op_tok, self.parse_additive())
            else:
                break
        return node

    def parse_additive(self):
        node = self.parse_multiplicative()
        while True:
            tok = self.current_token()
            if tok and tok.type == 'OP' and tok.value in ('+', '-'):
                op_tok = tok
                self.pos += 1
                node = BinOpNode(node, op_tok, self.parse_multiplicative())
            else:
                break
        return node

    def parse_multiplicative(self):
        node = self.parse_unary()
        while True:
            tok = self.current_token()
            if tok and tok.type == 'OP' and tok.value in ('*', '/', '%'):
                op_tok = tok
                self.pos += 1
                node = BinOpNode(node, op_tok, self.parse_unary())
            else:
                break
        return node

    def parse_unary(self):
        tok = self.current_token()
        
        if tok and tok.type == 'OP' and tok.value in ('-', '!', '~'):
            op_tok = tok
            self.pos += 1
            return UnaryOpNode(op_tok, self.parse_unary())
        elif tok and tok.type == 'OP' and tok.value == '*':
            self.pos += 1
            return PointerDerefNode(self.parse_unary())
        elif tok and tok.type == 'OP' and tok.value == '&':
            self.pos += 1
            return AddressOfNode(self.parse_unary())
        
        return self.parse_postfix()

    def parse_postfix(self):
        node = self.parse_primary()
        
        while True:
            tok = self.current_token()
            if not tok:
                break
            
            if tok.value == '[':
                self.pos += 1
                index = self.parse_expression()
                self.consume('OP')
                node = ArrayAccessNode(node, index)
            elif tok.value == '(' and isinstance(node, VarNode):
                self.pos += 1
                args = []
                while self.current_token() and self.current_token().value != ')':
                    args.append(self.parse_expression())
                    if self.current_token() and self.current_token().value == ',':
                        self.pos += 1
                self.consume('OP')
                node = FuncCallNode(node.name, args)
            else:
                break
        
        return node

    def parse_primary(self):
        tok = self.current_token()
        if not tok:
            raise RuntimeError("Unexpected EOF")
        
        if tok.type == 'NUMBER':
            self.pos += 1
            return NumberNode(tok)
        
        if tok.type == 'HEX':
            self.pos += 1
            return HexNode(tok)
        
        if tok.type == 'STRING':
            self.pos += 1
            return StringNode(tok)
        
        if tok.type == 'CHAR':
            self.pos += 1
            return CharNode(tok)
        
        if tok.type == 'IDENT':
            self.pos += 1
            return VarNode(tok)
        
        if tok.type == 'OP' and tok.value == '(':
            self.pos += 1
            expr = self.parse_expression()
            self.consume('OP')
            return expr
        
        raise RuntimeError(f"Unexpected token: {tok.value}")

    def parse_expression(self):
        return self.parse_assignment()
