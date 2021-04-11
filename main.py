from itertools import permutations
from bisect import bisect_right
from math import factorial
from numpy import prod
import csv

GENERATE_3D_PARTITIONS  = True   # Determine whether or not the program will generate all partitions of size MIN_GENERATION_SIZE <= n <= MAX_GENERATION_SIZE
MIN_GENERATION_SIZE     = 1      # Expected to be greater than 0
MAX_GENERATION_SIZE     = 5      # Expected to be greater than the min
GENERATE_RESULTS        = False  # Requires that GENERATE_3D_PARTITIONS has been run up to and through MAX_GENERATION_SIZE
CONFIRM_RESULTS         = False  # Run through each file and check that the conjecture holds
CLI_OUTPUT              = False  # Set to true to see some extra outputs to the CLI


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

   if(CLI_OUTPUT):
      print("Hook Lengths:")
      for i, s in enumerate(hooks):
         print("Level", i + 1)
         for t in s:
            print(*t)
   return hooks


def calcHooks(partition):

   # Create the inverse partition
   invPartition = []

   if(CLI_OUTPUT):
      print("Partition:")
      for s in partition: print(*s)

      hooks = d3Hooks(partition)
   return hooks


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


def genPartitions(size):
   
   # Safety in ensuring it is an integer
   size = int(size)

   # Create (size) x (size) list, fill with zeros
   initialPart = [[0 for __ in range(size)] for __ in range(size)]
   
   # Set this position to zero as we assume that we begin with a "tower" and move one block at a time
   initialPart[0][0] = size

   # Store as a tuple for set item comparison later (hashability for sets)
   initialPart = tuple(tuple(i) for i in initialPart)

   # Create and initialize the set to contain all unique partitions
   uniqueParts = set()
   uniqueParts.add(initialPart)

   newUnique = set()

   i = 0
   usedPartitions = set()
   while i < len(uniqueParts):
      for partition in uniqueParts.difference(usedPartitions):
         usedPartitions.add(partition)
         newUnique.update(findLegalBlock(partition))
      
      uniqueParts.update(newUnique)
      newUnique.clear()
      i += 1
   
   savePartitions(size, uniqueParts)

   return len(uniqueParts)


def findLegalBlock(partition):

   newUnique = set()

   # Steps to find a movable block:
   #  Loop through every (i, j) in the partition
   #  If, at (i, j), the following are true:
   #     1. partition[i + 1][j] < partition[i][j]
   #     2. partition[i][j + 1] < partition[i][j]
   # Note that both conditions must be true.
   # Then we call findLegalPositions
   for i, row in enumerate(partition):
      for j, __ in enumerate(row):
         checks = [False, False]
         
         try:
            if partition[i + 1][j] >= partition[i][j]: continue
            
            checks[0] = True
         # All exceptions will be an out of bounds error
         # They only mean that we do not have to check a value here
         except: pass

         try:
            if partition[i][j + 1] >= partition[i][j]: continue
            
            checks[1] = True
         # All exceptions will be an out of bounds error
         # They only mean that we do not have to check a value here
         except: pass

         if checks[0] == True and checks[1] == True:
            newUnique.update(findLegalPositions(partition, i, j))

   return newUnique


def findLegalPositions(partition, i, j):

   newParts = set()

   # Convert the tuple partition into a list for editing
   listPart = [list(row) for row in partition]

   # Decrement the height at position (i, j)
   listPart[i][j] -= 1

   # Find all legal movements of the block by checking the following conditions:
   #     1. listPart[x - 1][y] > listPart[x][y]
   #     2. listPart[x][y - 1] > listPart[x][y]
   # Note that both conditions must be true.
   for x, row in enumerate(listPart):
      for y, __ in enumerate(row):
         checks = [False, False]
         
         if(x == 0):
            checks[0] = True

            if listPart[x][y - 1] <= listPart[x][y]:
               continue
            checks[1] = True
         elif(y == 0):
            if listPart[x - 1][y] <= listPart[x][y]: 
               continue
            checks[0] = True

            checks[1] = True
         else:
            if listPart[x - 1][y] <= listPart[x][y]:
               continue
            checks[0] = True

            if listPart[x][y - 1] <= listPart[x][y]:
               continue
            checks[1] = True

         if checks[0] == True and checks[1] == True:
            listPart[x][y] += 1
            tPart = tuple([tuple(row) for row in listPart])
            newParts.add(tPart)
            listPart[x][y] -= 1
   
   return newParts


def savePartitions(size, partitions):

   # Save all generated partitions to a file
   with open(f"partition_shapes\size{size}parts.csv", "w") as file:
      for partition in partitions:
         for row in partition:

            # Reset string variable that will hold each row
            toWrite = ""
            for height in row:
               
               # Remove zeros from the resulting document for later reading
               if height == 0:
                  break
               toWrite += f"{height},"

            # Avoid extra spaces in the resulting document
            if len(toWrite) != 0:
               file.write(toWrite[:-1] + "\n")
         
         # Add a newline after each partition
         file.write("\n")


def generateResults():

   # Loop through all files of size i up to the MAX_GENERATION_SIZE
   for i in range(MIN_GENERATION_SIZE, MAX_GENERATION_SIZE + 1):

      # Setup a list to hold the collected partitions
      loadedParts = list()
      with open(f"partition_shapes\size{i}parts.csv", "r") as file:
         
         # Reset the line string to not be empty after finishing a file read
         line = " "
         while line:

            # Setup a list to hold values while reconstructing a partition
            partition = list()

            # Each number on a line is the stack height of the plane partition
            while True:
               line = file.readline()
               if not line or line == "\n":
                  break
               partition.append(list(map(int, line.strip().split(','))))
            if len(partition) > 0: 
               loadedParts.append(partition)

      # Test all partitions we have collected from file i
      results = list()
      for part in loadedParts:
         hooks = calcHooks(part)

         # Find the "naive" count of PSYT (2D formula)
         # Take the factorial of n, the size of the partition. Calculated by summing across all heights
         numerator = factorial(sum([i for col in part for i in col]))
         
         # Converts the hook length 3D list into a 1D list and then multiplies all of the values together
         denominator = prod([i for row in hooks for col in row for i in col])

         results.append((countPSYT(hooks), numerator/denominator))
      
      # Store the results in a file named accordingly
      with open(f"results\size{i}.csv", "w") as f:
         save = csv.writer(f)
         save.writerows(results)


def main():

   # Generate partitions for use in the program.
   if(GENERATE_3D_PARTITIONS):
      for i in range(MIN_GENERATION_SIZE, MAX_GENERATION_SIZE + 1):
         genPartitions(i)
   
   if(GENERATE_RESULTS):
      generateResults()

   if(CONFIRM_RESULTS):

      # Loop through all files of size i up to the MAX_GENERATION_SIZE
      for i in range(1, MAX_GENERATION_SIZE + 1):
         print(i)
         with open(f"partition_shapes\size{i}parts.csv", "r") as file:
            line = file.readline()
            if(line[0] < line[1]):
               print("Conjecture is False")
               print(f"{i}: {line}")
   
   return


main()
