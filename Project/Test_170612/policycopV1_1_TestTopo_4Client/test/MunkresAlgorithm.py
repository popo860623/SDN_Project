from munkres import Munkres, print_matrix

matrix = [[1,1,1,1,1,100],
	[2,2,3,2,2,1],
	[2,2,3,2,2,1],
	[1,2,3,1,2,1],
	[3,3,3,3,3,1],
	[3,2,3,3,2,1]]



m = Munkres()
indexes = m.compute(matrix)
print_matrix(matrix, msg='Lowest cost through this matrix:')
total = 0
print indexes

for row, column in indexes:
    value = matrix[row][column]
    total += value
    print '(%d, %d) -> %d' % (row, column, value)
print 'total cost: %d' % total
