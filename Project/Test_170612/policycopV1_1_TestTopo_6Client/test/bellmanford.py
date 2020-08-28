import sys
import numpy
import copy
import math
import optparse
import csv

def BellmanFord(weight,source):
	distance=[999999999]*len(weight)
	distance[source]=0
	parent=[0]*len(weight)
	parent[source]=source
	
	for i in range(0,len(weight)):
		for a in range(0,len(weight)):
			for b in range(0,len(weight)):
				if distance[a] != 999999999 and weight[a][b] != 999999999:
					if (distance[a] + weight[a][b]) < distance[b]:
						distance[b] = distance[a] + weight[a][b]
						parent[b] = a
	for a in range(0,len(weight)):
		for b in range(0,len(weight)):
			if distance[a] + weight[a][b] < distance[b]:
				sys.exit("Graph contains a negative-weight cycle")

	return (distance,parent)

def MakeForwardingTable(weight):
	table=numpy.zeros(shape=(len(weight),len(weight)))
	distance=numpy.zeros(shape=(len(weight),len(weight)))
	parent=numpy.zeros(shape=(len(weight),len(weight)))
	for i in range(0,len(weight)):
		distance[i] , parent[i] = BellmanFord(weight,i)

	for i in range(0,len(weight)):
		for j in range(0,len(weight)):
			parentNode=j
			while parent[i][parentNode] != i:
				parentNode = parent[i][parentNode]
			table[i][j]=parentNode
	return table
def readweight(weightfile):
    """
    read the weight from "weight.csv"
    """
    inner = csv.reader(open(weightfile))

    weight = []

    for line in inner:
        if len(line) == 0: continue
        #print (line)
        line = [s.strip(',') for s in line]
        weight.append(line[:])

    return weight
weight = [
	[0,1,1,999999999,999999999,999999999],
	[1,0,1,1,1,999999999],
	[1,1,0,1,1,999999999],
	[999999999,1,1,0,1,1],
	[999999999,1,1,1,0,1],
	[999999999,999999999,999999999,1,1,0]
	]

parser = optparse.OptionParser(usage="usage: %prog weight_csv")
(options, args) = parser.parse_args()
if len(args) < 1:
	table = MakeForwardingTable(weight)
else:
	weight_str = readweight(args[0])
	
	weight_list=numpy.zeros(shape=(len(weight_str),len(weight_str)))
	#print weight_str
	for i in range(0,len(weight_str)):
		for j in range(0,len(weight_str)):
			weight_list[i][j]=int(weight_str[i][j])/1
	#print weight_list
	
	table = MakeForwardingTable(weight_list)
	

for i in range(0,len(table)):
		for j in range(0,len(table)):
			table[i][j]+=1
print table
