from bisect import bisect_right
import pandas as pd
import numpy

def readFile(filename):
   file = open(filename + ".csv")
   # Read in the dimension number
   dims = int(file.readline())

   if(dims == 2):
      # Read in partition data, strip for safety
      partition = list(map(int, file.readline().strip().split(',')))
      # Ensure that the partition is in standard form for return
      partition.sort(reverse = True)
   elif(dims == 3):
      # Each number on a line is the stack height of the plane partition
      partition = list()
      while True:
         line = file.readline()
         if not line:
            break
         partition.append(list(map(int, line.strip().split(','))))

   file.close()
   return partition, dims
   
def main():
   partition, dimension = readFile(input("Enter the name of the CSV file without the extension: "))
   print(partition)

   if(dimension == 2):
      # Find the inverse of the partition
      invPartition = [len(partition) - bisect_right(partition[::-1], i) for i in range(partition[0])]
      hooks = [[(partition[i] - j + invPartition[j] - i - 1) for j in range(partition[i])] for i in range(len(partition))]
      print(hooks)
