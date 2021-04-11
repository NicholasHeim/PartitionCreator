from itertools import permutations
from bisect import bisect_right
from math import factorial
from numpy import prod
import csv

GENERATE_3D_PARTITIONS  = True   # Determine whether or not the program will generate all partitions of size MIN_GENERATION_SIZE <= n <= MAX_GENERATION_SIZE
MIN_GENERATION_SIZE     = 1      # Expected to be greater than 0
MAX_GENERATION_SIZE     = 5      # Expected to be greater than the min
DIMENSIONS              = 3     
GENERATE_RESULTS     = False  # Requires that GENERATE_3D_PARTITIONS has been run up to and through MAX_GENERATION_SIZE
CONFIRM_RESULTS         = False  # Run through each file and check that the conjecture holds
CLI_OUTPUT              = False  # Set to true to see some extra outputs to the CLI

def readFile(filename):

   global DIMENSIONS

   #with open(filename + ".csv") as file:
   with open("p3.csv") as file:

      if(DIMENSIONS == 2):
         # Read in partition data, strip for safety
         partition = list(map(int, file.readline().strip().split(',')))
         # Ensure that the partition is in standard form for return
         partition.sort(reverse = True)
      elif(DIMENSIONS == 3):
         # Each number on a line is the stack height of the plane partition
         partition = list()
         while True:
            line = file.readline()
            if not line:
               break
            partition.append(list(map(int, line.strip().split(','))))
      else: return []
   return partition


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

   if(DIMENSIONS == 2):
      if(CLI_OUTPUT): 
         print("Partition:", *partition)

      # Find the inverse of the partition (swap rows and columns)
      invPartition = [len(partition) - bisect_right(partition[::-1], i) for i in range(partition[0])]
      hooks = [[(partition[i] - j + invPartition[j] - i - 1) for j in range(partition[i])] for i in range(len(partition))]
      
      # Print hook length results to console
      print("Hook lengths:")
      for s in hooks: print(*s)
   elif(DIMENSIONS == 3):
      if(CLI_OUTPUT):
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


def plane_partition_num ( n ):

   #*****************************************************************************80
   #
   ## PLANE_PARTITION_NUM returns the number of plane partitions of the integer N.
   #
   #  Discussion:
   #
   #    A plane partition of a positive integer N is a partition of N in which
   #    the parts have been arranged in a 2D array that is nonincreasing across
   #    rows and columns.  There are six plane partitions of 3:
   #
   #      3   2 1   2   1 1 1   1 1   1
   #                1           1     1
   #                                  1
   #
   #  First Values:
   #
   #     N PP(N)
   #     0    1
   #     1    1
   #     2    3
   #     3    6
   #     4   13
   #     5   24
   #     6   48
   #     7   86
   #     8  160
   #     9  282
   #    10  500
   #
   #  Licensing:
   #
   #    This code is distributed under the GNU LGPL license.
   #
   #  Modified:
   #
   #    27 April 2014
   #
   #  Author:
   #
   #    John Burkardt
   #
   #  Reference:
   #
   #    Frank Olver, Daniel Lozier, Ronald Boisvert, Charles Clark,
   #    NIST Handbook of Mathematical Functions,
   #    Cambridge University Press, 2010,
   #    ISBN: 978-0521140638,
   #    LC: QA331.N57.
   #    
   #  Parameters:
   #
   #    Input, integer N, the number, which must be at least 0.
   #
   #    Output, integer VALUE, the number of plane partitions of N.
   #
   import numpy as np

   if ( n < 0 ):
      print ( '' )
      print ( 'PLANE_PARTITION_NUM - Fatal error!' )
      print ( '  0 <= N is required.' )

   pp = np.zeros ( n + 1 )

   nn = 0
   pp[nn] = 1

   nn = 1
   if ( nn <= n ):
      pp[nn] = 1

   for nn in range ( 2, n + 1 ):
      for j in range ( 1, nn + 1 ):
         s2 = 0
         for k in range ( 1, j + 1 ):
            if ( ( j % k ) == 0 ):
               s2 = s2 + k * k
         pp[nn] = pp[nn] + pp[nn-j] * s2
      pp[nn] = pp[nn] / nn

   value = pp[n]

   return int(value)


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

   if(DIMENSIONS == 2):

      partition = readFile(input("Enter the name of the CSV file without the extension: "))
      hooks = calcHooks(partition)
      
      # Output the calculated number of SYT:
      count = factorial(sum(partition)) / prod([i for sub in hooks for i in sub])
      print("Count:", int(count))

   if(DIMENSIONS == 3):
      
      # Generate partitions for use in the program.
      if(GENERATE_3D_PARTITIONS):
         for i in range(MIN_GENERATION_SIZE, MAX_GENERATION_SIZE + 1):
            genPartitions(i)
      
      if(GENERATE_RESULTS):
         generateResults

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
