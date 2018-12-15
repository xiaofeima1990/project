from pathos.threading import ThreadPool
import time
pool = ThreadPool(nodes=4)

# do a blocking map on the chosen function
print(pool.map(pow, [1,2,3,4], [5,6,7,8]))

# do a non-blocking map, then extract the results from the iterator
results = pool.imap(pow, [1,2,3,4], [5,6,7,8])
print("...")
print(list(results))


# do an asynchronous map, then get the results
results = pool.amap(pow, [1,2,3,4], [5,6,7,8])
while not results.ready():
    time.sleep(5)
    print(".")

print(results.get())


# do one item at a time, using a pipe

print(pool.pipe(pow, 1, 5))
print(pool.pipe(pow, 2, 6))

# do one item at a time, using an asynchronous pipe

result1 = pool.apipe(pow, 1, 5)
result2 = pool.apipe(pow, 2, 6)
print(result1.get())
print(result2.get())


print("hello world")



