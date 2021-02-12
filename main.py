from bisect import bisect_right
from math import factorial
from numpy import prod

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

def verifySYT(partition, syt):
   # Determine if partition is a legal SYT
   for row in range(len(partition)):
      for col in range(partition[row]):
         # Check existence of right square
         if (col + 1) < partition[row]:
            # Determine if right square value is larger
            if syt[row][col] > syt[row][col + 1]:
               return 0
         # Ensure no out of range check
         if row < len(partition) - 1:
            # Check existence of down square
            if col < partition[row + 1]:
               # Determine if down square value is larger
               if syt[row][col] > syt[row + 1][col]:
                  return 0
   return 1

# Definition adapted from https://docs.python.org/3/library/itertools.html#itertools.permutations
def permutations(iterable, r=None):
    # permutations('ABCD', 2) --> AB AC AD BA BC BD CA CB CD DA DB DC
    # permutations(range(3)) --> 012 021 102 120 201 210
    pool = tuple(iterable)
    n = len(pool)
    r = n if r is None else r
    if r > n:
        return
    indices = list(range(n))
    cycles = list(range(n, n-r, -1))
    yield tuple(pool[i] for i in indices[:r])
    while n:
        for i in reversed(range(r)):
            cycles[i] -= 1
            if cycles[i] == 0:
                indices[i:] = indices[i+1:] + indices[i:i+1]
                cycles[i] = n - i
            else:
                j = cycles[i]
                indices[i], indices[-j] = indices[-j], indices[i]
                yield tuple(pool[i] for i in indices[:r])
                break
        else:
            return

def countSYT(partition):
   # Standard is to work with (1, ... , n), add 1 to i to preserve this
   numbers = [i + 1 for i in range(sum(partition))]
   # Find all permutations
   perms = list(permutations(numbers))
   # Remove permutations where 1 is not the first number
   # These are false by definition, reduces calculation time
   perms = [i for i in perms if i[0] == 1]
   # Convert each permutation into the form defined by the partition
   # This needs to be done before sending it to verifySYT
   # We currently do not care what each correct one is, only the number of them
   count = 0
   for p in perms:
      syt = [p[sum(partition[:pos]):sum(partition[:pos]) + cols] for pos, cols in enumerate(partition)]
      count += verifySYT(partition, syt)
   print("Brute force count:", count)


def main():
   partition, dimension = readFile(input("Enter the name of the CSV file without the extension: "))
   hooks = calcHooks(partition, dimension)

   # Output the calculated number of SYT:
   count = factorial(sum(partition)) / prod([i for sub in hooks for i in sub])
   print("   Expected count:", int(count))

   countSYT(partition)

   #print("       SYT Result:", verifySYT(partition, syt))

   # Start with a 2D partition for brute force
   #print("Brute force count:", bruteForce(partition, dimension))
   
main()