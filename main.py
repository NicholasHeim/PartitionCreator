from itertools import permutations
from bisect import bisect_right
from math import factorial
from numpy import prod

import multiprocessing as mp

def readFile(filename):
   #with open(filename + ".csv") as file:
   with open("p2.csv") as file:
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
      else: return [], dims
   return partition, dims

def d3Hooks(partition):
   # Determine shape of each level for the hook length calculation
   # This is done using the count of remaining heights in the original
   partitionCopy = partition[:] # Copy because we will need the original
   regPart = []
   for level in range(partition[0][0]):
      regPart.append([len(x) for x in partitionCopy if len(x) > 0])
      partitionCopy = [[height-1 for height in tower if (height - 1) > 0] for tower in partitionCopy]
   
   # Find the inverse of each individual level for hook length calculation
   invPartition = [[len(regPart[level]) - bisect_right(regPart[level][::-1], i) for i in range(regPart[level][0])] for level in range(len(regPart))]

   # Calculate hook lengths of the whole plane partition one level at a time
   hooks = [[[(regPart[level][i] - j + invPartition[level][j] - i - 2) + (partition[i][j] - level) for j in range(regPart[level][i])] for i in range(len(regPart[level]))] for level in range(len(regPart))]

   print("Hook Lengths:")
   for i, s in enumerate(hooks):
      print("Level", i + 1)
      for t in s:
         print(*t)
   return hooks

def calcHooks(partition, dimension):
   invPartition = []

   if(dimension == 2):
      print("Partition:", *partition)

      # Find the inverse of the partition (swap rows and columns)
      invPartition = [len(partition) - bisect_right(partition[::-1], i) for i in range(partition[0])]
      hooks = [[(partition[i] - j + invPartition[j] - i - 1) for j in range(partition[i])] for i in range(len(partition))]
      
      # Print hook length results to console
      print("Hook lengths:")
      for s in hooks: print(*s)
   elif(dimension == 3):
      print("Partition:")
      for s in partition: print(*s)

      hooks = d3Hooks(partition)
   else:
      print("No recognized partition dimension.")
      return
   return hooks

def verifySYT(syt):
   for row in range(len(syt)):
      for col in range(len(syt[row])):
         try:
            # Determine if right square value is larger
            if syt[row][col] > syt[row][col + 1]:
               return 0
         # All exceptions will be an out of bounds error
         # Ignore them to save time on checks because they are a minimal case
         except: pass

         try:
            # Determine if down square value is larger
            if syt[row][col] > syt[row + 1][col]:
               return 0
         # All exceptions will be an out of bounds error
         # Ignore them to save time on checks because they are a minimal case
         except: pass
   return 1

def countSYT(partition):
   # Standard is to work with (1, ... , n), add 1 to i to preserve this
   numbers = [i + 1 for i in range(sum(len(row) for row in partition))]

   # Copy the partition to avoid destructive behavior
   syt = partition[:]
   count = 0
   
   for perm in permutations(numbers):
      # Break if the first number is not 1, lowers to (n-1)! options
      if(perm[0] != 1): break

      # Copy the partition to avoid destructive behavior
      pIter = iter(perm)

      # Overwrite all values in syt with values from current perm
      syt = [[next(pIter) for __ in row] for row in syt]
      count += verifySYT(syt)
   
   return count

def verifyPSYT(psyt):
   for level in range(len(psyt)):
      for row in range(len(psyt[level])):
         for col in range(len(psyt[level][row])):
            try:
               # Determine if right square value is larger
               if psyt[level][row][col] > psyt[level][row][col + 1]:
                  return 0
            # All exceptions will be an out of bounds error
            # Ignore them to save time on checks because they are a minimal case
            except: pass

            try:
               # Determine if down square value is larger
               if psyt[level][row][col] > psyt[level][row + 1][col]:
                  return 0
            # All exceptions will be an out of bounds error
            # Ignore them to save time on checks because they are a minimal case
            except: pass

            try:
               # Determine if above box value is larger
               if psyt[level][row][col] > psyt[level + 1][row][col]:
                  return 0
            # All exceptions will be an out of bounds error
            # Ignore them to save time on checks because they are a minimal case
            except: pass
   return 1

def countPSYT(partition):
   # Standard is to work with (1, ... , n), add 1 to i to preserve this
   numbers = [i + 1 for i in range(sum(sum(len(row) for row in level) for level in partition))]

   # Copy the partition to avoid destructive behavior
   psyt = partition[:]
   count = 0

   for perm in permutations(numbers):
      # Break if the first number is not 1, lowers to (n-1)! options
      if(perm[0] != 1): break 
      pIter = iter(perm)

      # Overwrite all values in psyt with values from perm
      psyt = [[[next(pIter) for __ in row] for row in level] for level in psyt]
      count += verifyPSYT(psyt)

   return count
   
def main():
   partition, dimension = readFile(input("Enter the name of the CSV file without the extension: "))
   hooks = calcHooks(partition, dimension)

   if(dimension == 2):
      # Output the calculated number of SYT:
      count = factorial(sum(partition)) / prod([i for sub in hooks for i in sub])
      print("   Expected count:", int(count))

      # Brute force the number of partitions, meant as a check for correctness
      count = countSYT(hooks)
      print("Brute force count:", count)

   if(dimension == 3):
      count = countPSYT(hooks)
      print("Count:", count)
   
main()