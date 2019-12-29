def split_expr(expr:str, level):
    expr = expr.replace(' ', '')

    if level == 1:
        expr = expr.replace('+', ' + ')
        expr = expr.replace('-', ' - ')
    elif level == 2:
        expr = expr.replace('*', ' * ')
        expr = expr.replace('/', ' / ')
    
    return expr.split()    

def calculate_operation(list_op_operators):
    
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

    res = 0
    cur_op = add
    for oparator in list_op_operators:
        if oparator in operations:
            cur_op = operations[oparator]
        else:
            res = cur_op(res, float(oparator))
    return res


def calculate(expr):

    operators_level1 = split_expr(expr, level=1)
    
    for index,operator in enumerate(operators_level1):

        if operator in '+-':
            continue
        else:
            operators_level1[index] = calculate_operation(split_expr(operator, level=2))

    return calculate_operation(operators_level1)


def simple_test(expr):
    print(expr, '=', calculate(expr))
    

if __name__ == '__main__':
    simple_test('2/0.5')
    simple_test('1+1 * 2 -2/0.5 + 4+ 4 -3/2')
    