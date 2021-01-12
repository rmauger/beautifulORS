nbsp = u'\xa0'


def error_save(func):
    # TODO implement error handling decorator
    def inner_function(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            err_msg = f'{func.__name__} fed: {args} {kwargs} & returned error: {e}'
            print(err_msg)
            logger('err', err_msg, True)
        return inner_function


def logger_list(fn, line, append=True):
    logger(fn, f'{line[0]}: {line[1]}{nbsp}', True)


def logger(fn, txt, append=True):
    if append:
        try:
            with open(fn+'-log.txt', 'r+') as log:
                log.write(txt)
            return
        except Exception as e:
            print(f'Err. {e} Could not open file. Writing new file instead.')
    with open(fn+'-log.txt',  'w') as log:
        log.write(txt)


def print_err(err, context):
    error_msg = f'{err}: {context}{nbsp}'
    print(error_msg)
    logger('err', error_msg, True)
