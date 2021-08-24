import sys
import operator
import time 

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for variable in self.domains:
            word_to_remove = set()
            for word in self.domains[variable]:
                if len(word) != variable.length:
                    word_to_remove.add(word)
            self.domains[variable] = self.domains[variable] - word_to_remove

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
        if not self.crossword.overlaps[x,y]:
            return revised

        #store the position of overlap
        overlap = self.crossword.overlaps[x,y]
        word_to_remove = set()

        for wordx in self.domains[x]:
            change = False
            for wordy in self.domains[y]:
                #if we find a word in y's domain that satisfies constraint for (x,y) 
                if wordx[overlap[0]] == wordy[overlap[1]]:
                    change = True
                    revised = True
                    break
            if change == False:
                word_to_remove.add(wordx)
            self.domains[x] = self.domains[x] - word_to_remove 

        return revised


    def initialize_arcs(self):
        all_arcs = []
        for var1 in self.domains:
            for var2 in self.crossword.neighbors(var1):
                if ((var1,var2)) not in all_arcs and ((var2,var1)) not in all_arcs:
                    all_arcs.append((var1,var2))
        return all_arcs
    

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs == None:
            arcs = self.initialize_arcs()
        while len(arcs) != 0:
            arc = arcs.pop(0)
            x = arc[0]
            y = arc[1]
            #if a modification has been made
            if self.revise(x,y):
                #if we find an arc no consistent than the problem has no solution
                if len(self.domains[x])==0:
                    return False
                #We have delete some element in X's domain so we add all the arcs starting to x 
                #to the queue
                for z in (self.crossword.neighbors(x) - {y}):
                        arcs.append((z,x))
        return True

    
    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        if len(assignment) == len(self.domains):
            return True
        return False


    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # Unary contraint
        for variable in assignment:
            if len(assignment[variable]) != variable.length and assignment[variable]:
                return 0
        
        # Binary constraint
        for variable, word in assignment.items():
            for neighbor in self.crossword.neighbors(variable).intersection(assignment.keys()):
                overlap = self.crossword.overlaps[variable, neighbor]
                if word[overlap[0]] != assignment[neighbor][overlap[1]]:
                    return False

        # Additional constraint all word must be different
        for variable1 in assignment:
            occurrence = 0
            for variable2 in assignment:
                if variable1 == variable2:
                    occurrence+=1
            if occurrence > 1:
                return 2
        return True
    
    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        dico = dict((word,0) for word in self.domains[var])
        for word in self.domains[var]:
            count = 0
            variable_to_check = [variable for variable in self.crossword.neighbors(var) if variable not in assignment]
            for variable in variable_to_check:
                for wordbis in self.domains[variable]:
                    overlap = self.crossword.overlaps[var,variable]
                    i = overlap[0]
                    j = overlap[1]
                    if word[i] != wordbis[j]:
                        count += 1
            dico[word] = count
        dico = dict(sorted(dico.items(), key=lambda item: item[1]))
        return [*dico]

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassigned_variable = [variable for variable in self.domains if variable not in assignment]
        dico = dict((var,len(self.domains[var])) for var in unassigned_variable)
        dico = dict(sorted(dico.items(), key=operator.itemgetter(1)))
        
        if len(dico) == 1 or [*dico.values()][0] != [*dico.values()][1]:
            return [*dico][0]

        else:
            num_degrees = dict((var, len(self.crossword.neighbors(var))) for var in unassigned_variable)
            dico_bis = dict(sorted(num_degrees.items(), key=operator.itemgetter(1)),reverse = True)
            return [*dico_bis][0]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        var = self.select_unassigned_variable(assignment)
        for word in self.order_domain_values(var,assignment):
            # add var to assignment dictionnary
            assignment[var] = word
            if self.consistent(assignment):
                result = self.backtrack(assignment)
                if result:
                    return result
            del assignment[var]
        return None

def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")
    
    start_time = time.time()

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)
    print("%s seconds" % (time.time() - start_time))

if __name__ == "__main__":
    main()
   