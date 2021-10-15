
SIZE_METRIC = [ 'BB', 'KB', 'MB', 'GB', 'TB' ]

def translate_capacity(capacity:str):
    # converts from supported storage capacity to capacity in bytes
    return int(float(capacity[:-2]) * ( 1024 ** (SIZE_METRIC.index( capacity[-2:] )) ))
