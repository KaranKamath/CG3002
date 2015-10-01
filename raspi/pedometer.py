import time
import sys
from Database.db import DB
foo = DB()


def dedup_data(foo):
    prev_val = [0, 0, 0, 0, 0, 0]
    current = int(time.time()*1000)
    while True:
        data = foo.fetch(since=current, sid=1)
        if data:
            data = data[-1]
            if prev_val != data[2][:3]:
                prev_val = data[2][:3]
                yield sum(data[2][:3])/3.0
            current = data[0]
    
regs = []    
def init_filter(data):
    sum_val = sum(regs)
    del regs[0]
    regs.append(data)
    return sum_val


counter = 0
max_val = float("-inf") 
min_val = float("inf")
threshold = None
sample_new = None
sample_old = None
precision = 100
steps = 0
for d in dedup_data(foo):
    while len(regs) < 4:
        regs.append(d)
    filtered_data = init_filter(d)
    counter += 1
    if max_val < filtered_data:
        max_val = filtered_data
    if min_val > filtered_data:
        min_val = filtered_data
    if counter == 10:
        print min_val, max_val, (min_val + max_val) / 2.0
        threshold = (min_val + max_val) / 2.0
        min_val = float('inf')
        max_val = float('-inf')
        counter = 0
    sample_old = sample_new
    if sample_new is None or abs(filtered_data - sample_new) > precision:
        sample_new = filtered_data
    print sample_new, sample_old, sample_new < sample_old, sample_new < threshold, sample_old > threshold
    if sample_new and sample_old and sample_new < sample_old and sample_new < threshold and sample_old > threshold:
        steps += 1
        print steps
        
    
    
    

    # sys.stdout.flush()
    # sys.stdout.write("A: %s M: %s %s  \r" % (a, m, flag))
