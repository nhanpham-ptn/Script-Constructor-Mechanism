from prefixspan import PrefixSpan

db = [
    [0, 1, 2, 3, 4],
    [1, 1, 1, 3, 4],
    [2, 1, 2, 2, 0],
    [1, 1, 1, 2, 2],
]

ps = PrefixSpan(db)

print(ps.frequent(2))
#So from what I can understand, PrefixSpan splits the 

#So from what I can understand, PrefixSpan partitions each component or each list in a list of lists into smaller lists 
#and count how many time they appear.
#For pattern recognition like this, this algorithm is fitted for picking out repeated patterns.