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


logger_list(fn, list, append=True)
    




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
