from timeit import default_timer as timer
start = timer()
fullstart = start
x = 40
for i in range(10000000):
    x = i
    # x < 20

end = timer()

print("Total time : %.1f ms" % (1000 * (end - fullstart)))
