# kevin_bacon
Solving the 6 Degrees of Kevin Bacon Problem using Python 3 &amp; SPARQL

This script is fully described in the blog post at: 

https://www.winwaed.com/blog/2019/07/29/solving-the-six-degrees-of-kevin-bacon-problem/

Script to solve the Six Degrees of Kevin Bacon problem Finds the number of hops from the specified actor to
Kevin Bacon, stopping at 6. Uses DBpedia's SPARQL interface to query actors in films.

Usage:

python3 find_bacon.py < actor >

< actor > must be the DBpedia identifier for the label without a namespace
eg. "Gillian_Anderson" (no quotes)
