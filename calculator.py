def split_expr(expr:str):
    expr = expr.replace(' ', '')
    expr = expr.replace('+', ' + ')
    expr = expr.replace('-', ' - ')
    expr = expr.replace('*', ' * ')
    expr = expr.replace('/', ' / ')
    return expr.split()    


def calculate(expr):

    add = lambda a,b: a+b
    sub = lambda a,b: a-b
    mul = lambda a,b: a*b
    div = lambda a,b: a/b

    operations = {
        '+':add,
        '-':sub,
        '*':mul,
        '/':div

    }

    ops = split_expr(expr)

    if not ops:
        return None
    res = 0
    cur_op = add
    for op in ops:
        if op.isdigit():
            el = float(op)
            res = cur_op(res, el)
        elif op in operations:
            cur_op = operations[op]
        else:
            raise ValueError('Неожиданный параметр', op)
    return res


def simple_test(expr):
    try:
        print(expr, '=', calculate(expr))
    except ZeroDivisionError:
        print(expr, ' can\'t devide by zero')

if __name__ == '__main__':
    simple_test('1+1')
    simple_test('1 + 1')
    simple_test('5-4')
    simple_test('4-5')
    simple_test('3*2*5')
    simple_test('2+6')
    simple_test('5*7')
    simple_test('5/7')
    simple_test('5/0')