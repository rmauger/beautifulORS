def error_save(func):
    # TODO implement error handling decorator
    def inner_function(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            err_msg = f'{func.__name__} fed: {args} {kwargs} & returned error: {e}'
            print_err(e, err_msg)
            logger('err', err_msg, True)
        return inner_function


def print_err(err, context):
    print(f'ERR: {err} -- {context}')


def logger_list(fn, alist):
    num = 0
    unpacked = ''
    for item in alist:
        if num == 0:
            unpacked += item
            num += 1
        else:
            unpacked += item + '\n'
    logger(fn, unpacked, True)


def logger(fn, txt, append=True):
    if append:
        try:
            with open(fn+'-log.txt', 'a') as log:
                log.write(txt)
            return
        except Exception as e:
            print_err(e, f'Could not open {fn}-log.txt. Writing new.')
    with open(fn+'-log.txt',  'w') as log:
        log.write(txt)
