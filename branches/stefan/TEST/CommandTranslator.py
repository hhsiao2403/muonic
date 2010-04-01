'''
Provide simple functions that generate QuarkNet DAQ commands
'''

def disable_counters():
    return 'CD'

def enable_counters():
    return 'CE'

def display_scalars():
    return 'CS'

def reset():
    '''Reset scalars and TMC only'''
    return 'RB'

def reset_everything():
    '''Reset everything including setup parameters'''
    return 'RE'

def get_thermometer():
    return 'TH'

def display_gps():
    return 'DG'

def get_airpressure():
    return 'BA'

def set_threshold(channel,thresh):
    return 'TL %i %i'%(channel,thresh)
