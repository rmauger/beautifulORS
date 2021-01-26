nbsp = u'\xa0'
hr = u'\x0d'


def error_save(func):
    # TODO implement error handling decorator better
    def inner_function(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            # todo I think next line is breaking this, but haven't debugged any.
            err_msg = f'{func.__name__} fed: {args} {kwargs} & returned error: {e}'
            print(err_msg)
            logger('err', err_msg, True)
        return inner_function


def logger_list(fn, aline, append=True):
    myline = f'{aline[0]}: {aline[1]}{hr}'
    logger(fn, myline, True)


def logger(fn, txt, append=True):
    if append:
        try:
            with open(f'log-{fn}.txt', 'a+') as log:
                log.write(txt)
            return
        except Exception as e:
            print(f'Err. {e} Could not open file. Writing new file instead.')
    with open(f'log-{fn}.txt',  'w') as log:
        log.write(txt)


def print_err(err, context):
    error_msg = f'{err}: {context}{nbsp}'
    print(error_msg)
    logger('err', error_msg, True)
