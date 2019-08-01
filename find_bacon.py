# Copyright 2019 Winwaed Software Technology LLC>
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following
# conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following 
# disclaimer in the documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, 
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE 
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, 
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; 
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, 
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Script to solve the Six Degrees of Kevin Bacon problem
# Finds the number of hops from the specified actor to
# Kevin Bacon, stopping at 6.
# Uses DBpedia's SPARQL interface to query actors in films.
#
# Usage:
#
# python3 find_bacon.py <actor>
#
# <actor> must be the DBpedia identifier for the label without a namespace
# eg. "Gillian_Anderson" (no quotes)

import csv
import re
import string
import sys
import time


from SPARQLWrapper import SPARQLWrapper, JSON

FilmsVisited = set()
ActorsVisited = set()

# Queries all statements with this property
# entity is either subject (bEntityIsSubj=true) or object
# Returns list of tuples: (obj, label, IsPastTense)
# List is of max length: MAX_STATEMENTS_PER_PROPERTY
# Property may have http://www.wikidata.org/entity/ prefix.
#   if so, this is replaced by wdt: prefix
# Set req_label to False if no label is required
def QueryFilmActors(sparql, prev_actor):
    time.sleep(0.1)
    
    sparql.setQuery("""
    SELECT DISTINCT ?film, ?actor
WHERE
{
?film dbo:starring <http://dbpedia.org/resource/%s> .
?film dbo:starring ?actor .
}
    """ % (prev_actor, ) )

    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    result_tuples = []
    
    for result in results["results"]["bindings"]:
        film = result["film"]["value"]
        actor = result["actor"]["value"]
        # remove namespace
        film = film.split("/").pop()
        actor = actor.split("/").pop()
        result_tuples.append( (film,actor) )

    # return the result (might be an empty list)
    return result_tuples


######################################

# Find all new actors who have acted with this actor
# Returns a list of the new paths
def FindActorsForPath( sparql, path, actor):
    global FilmsVisited, ActorsVisited
    
    new_path_list = [ ]
    reached_destination = [ ]
    candidates = QueryFilmActors(sparql, actor)
    for (new_film, new_actor) in candidates:
        if not new_film in FilmsVisited:
            if not new_actor in ActorsVisited:
                ActorsVisited.add(new_actor)
                new_path = list(path)
                new_path.append( (new_film, new_actor ) )
                new_path_list.append(new_path)
                if new_actor == "Kevin_Bacon":
                    reached_destination.append(new_path)
                
    # 2nd pass because we do not want to prematurely exclude actors/films
    for (new_film, new_actor) in candidates:
        if not new_film in FilmsVisited:
            FilmsVisited.add(new_film)

    return (new_path_list, reached_destination)

    
# The main (command line) call   
if __name__ == "__main__":
    # Get the entity parameter
    actor = sys.argv[1]

    sparql = SPARQLWrapper("http://dbpedia.org/sparql")

    # First iteration is with one call
    
    ActorsVisited.add(actor)

    all_paths = [ [] ]
    reached_dest = []
    for step in range(0,6):
        # New step level
        next_new_paths = [ ]
        for this_path in all_paths:
            if len(this_path) == 0:
                this_actor = actor
            else:
                # last actor of this path
                this_actor = this_path[-1][1]

            (new_paths, reached_dest) = FindActorsForPath(sparql, this_path, this_actor)
            next_new_paths += new_paths
            
            if len(reached_dest) > 0:  
                # We've found Kevin Bacon!
                break

        if len(reached_dest) > 0:
            break
        # save the new paths read for the next iteration
        all_paths = next_new_paths
        # loop around to the next step or hop

    # do we have a result?
    if len(reached_dest) > 0:
        num_hops = len(reached_dest[0])
        print("Kevin Bacon found in {} hops:".format(num_hops) )
        for route in reached_dest:
            print("Route:")
            for (film,actor) in route:
                print("  Film: {};  Actor: {}".format(film,actor) )
    else:
        print("Kevin Bacon was not found")
        
    
