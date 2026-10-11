import ast#用于解析表达式
import operator#用于操作符
import math#用于数学函数如sqrt、sin、cos等
from hello_agents import ToolRegistry

def my_calculate(expression:str) -> str:
    """简单的数学计算函数"""
    if not expression.strip():
        return "计算表达式不能为空"

    #支持的基本运算
    operators = {
        ast.Add:operator.add,
        ast.Sub:operator.sub,
        ast.Mult:operator.mul,
        ast.Div:operator.truediv
    }

    #支持的基本函数
    functions = {
        'sqrt':math.sqrt,#平方根
        'pi':math.pi,#圆周率
    }

    try:
        node = ast.parse(expression,mode='eval')#解析表达式 mode='eval'表示解析为可评估的表达式
        result= _eval_node(node.body,operators,functions)
        return str(result)
    except:
        return "计算失败，请检查表达式格式"

def _eval_node(node,operators,functions):
    """简化的表达式求值"""
    if isinstance(node,ast.Constant):#常量直接返回
        return node.value
    elif isinstance(node,ast.BinOp):#二元运算符
        left=_eval_node(node.left,operators,functions)
        right=_eval_node(node.right,operators,functions)
        op = operators.get(type(node.op))#获取运算符函数
        return op(left,right)
    elif isinstance(node,ast.Call):#函数调用
        func_name = node.func.id#获取函数名
        if func_name in functions:
            args = [_eval_node(arg,operators,functions) for arg in node.args]#递归求值参数
            return functions[func_name](*args)

    elif isinstance(node,ast.Name):#变量引用
        if node.id in functions:
            return functions[node.id]

def create_calculator_registry():
    """创建包含计算器的工具注册表"""
    registry = ToolRegistry()

    #注册计算器函数
    registry.register_function(
        name='my_calculator',
        description="简单的数学计算工具，支持基本运算（+，-，*，/）和函数（sqrt、pi）",
        func=my_calculate
    )

    return registry


    