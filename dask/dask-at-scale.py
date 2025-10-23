from dask.distributed import Client
client = Client("tls://localhost:8786")  # update as needed

import dask.bag
import numpy as np
import time

NUM_TASKS = 2000  # change to control tree size

x = np.linspace(1, NUM_TASKS, NUM_TASKS)
b = dask.bag.from_sequence(x, npartitions=len(x))

def my_function(num):
    time.sleep(5)
    return num

futures = b.map(my_function)  # apply the function to each entry of the bag
task = futures.fold(lambda x,y: x+y, split_every=4)  # parallel reduction pattern
dask.compute(task)
