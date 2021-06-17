import sys

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
        # For each var in domains {var: set(words)}
        for var in self.domains:
            # Keep track of words which violate unary constraint
            non_unary = set()
            # For each word in set(words)
            for word in self.domains[var]:
                # If length of word != variable.length
                if len(word) != var.length:
                    # Add word to set
                    non_unary.add(word)
            # Iterate and remove non_unary words
            for word in non_unary:
                self.domains[var].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        flag = False
        overlap = self.crossword.overlaps[x,y]
        # If there is no point of overlap then the variables are arc consistent and there is no point of conflict
        if overlap != None:
            # ith value in x == jth value in y
            i,j = overlap
            # List of y_j chars
            y_j = [word[j] for word in self.domains[y]]
            # Set of words which fail binary constraints
            non_binary = set()
            # For each ith letter in word_x, check for overlapping letter in y_j
            for word_x in self.domains[x]:
                if word_x[i] not in y_j:
                    # Add to non_binary set
                    non_binary.add(word_x)
            # if there are inconsistent words
            if len(non_binary) != 0:
                # For each non_binary word in x (ie. that does not have a consistent word in y)
                for word in non_binary:
                    # Remove word from domain_x
                    self.domains[x].remove(word)
                flag = True
        
        return flag

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # Arcs are the edges between different variables
        if arcs == None:
            # Create list of all arcs
            arcs = []
            for v1 in self.crossword.variables:
                for v2 in self.crossword.variables:
                    # Cannot have an edge/arc between the same variable
                    if v1 != v2:
                        arcs.append((v1, v2))
        
        # Create a queue (FIFO)
        queue = arcs
        # While there are arcs in the queue
        while queue:
            # Take the first item
            x,y = queue.pop(0)
            # If domain x is revised
            if self.revise(x,y):
                # Check domain is not now empty
                if len(self.domains[x]) == 0:
                    return False
                # Since the domain has changed, add the neighbouring (connected) edges to the queue to check they still satisfy arc constraints
                for neighbour in self.crossword.neighbors(x):
                    if neighbour != y:
                        queue.append((neighbour, x))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        # For all crossword variables
        for var in self.crossword.variables:
            # If variable does not have an assigned value, break
            if var not in assignment:
                return False
            # Else check if var has 0 or >1 vales assigned
            if not assignment[var]:
                # Then not complete
                return False
        # Otherwise all variables have one assigned value --> complete
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # For all the values in the assignment dict
        vals = list(assignment.values())
        # If a value occurs more than once ie. not distinct--> inconsistent
        for val in vals:
            if vals.count(val) > 1:
                return False
        # For all variables in assignment
        for var in assignment:
            # If a variable length != the length of the assigned value --> inconsistent
            if var.length != len(assignment[var]):
                return False
            # Check conflicts with neighbouring variables
            # Find all neighbours of the variable, var
            neighbours = self.crossword.neighbors(var)
            # For every neighbour of var
            for neighbour in neighbours:
                if neighbour in assignment:
                    # Check the point of overlap (i,j) between var and neighbour
                    # As neighbours, assume overlap != None
                    i,j = self.crossword.overlaps[var,neighbour]
                    # If ith letter of var value != jth value of neighbour value in the assignment --> inconsistent
                    if assignment[var][i] != assignment[neighbour][j]:
                        return False
        
        # Otherwise, all assignments are consistent
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # Dictionary to track {word: n} for how many n a word eliminates
        eliminated_vals = {}
        # Possible words/values for var
        words = self.domains[var]
        # All neighbours for var
        neighbours = self.crossword.neighbors(var)
        # For each word in the domain of var
        for word in words:
            n = 0
            # For each neighbour of var
            for neighbour in neighbours:
                # If neighbour hasn't been assigned a value
                if neighbour not in assignment:
                    # Find neighbour's possible values
                    neighbour_words = self.domains[neighbour]
                    # For the words in the neighbours domain
                    for neighbour_word in neighbour_words:
                        # Check if var and neighbour overlap
                        i,j = self.crossword.overlaps[var, neighbour]
                        # If the words don't satisfy and overlap, increment counter
                        if word[i] != neighbour_word[j]:
                            n += 1
            # Store n count against word
            eliminated_vals[word] = n
        
        sorted_dict = dict(sorted(eliminated_vals.items(), key=lambda item: item[1]))
        sorted_vars = list(sorted_dict.keys())
         
        return sorted_vars

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        # Set of all variables in crossword
        all_vars = self.crossword.variables
        # Set of all assigned variables
        assigned = set(assignment.keys())
        # Set difference 
        unassigned  = all_vars - assigned
        # Minimum remaining value heuristic
        mrv = {var:len(self.domains[var]) for var in unassigned}
        # Sort lowest to highest
        mrv_sorted = dict(sorted(mrv.items(), key=lambda item: item[1]))
        # List of keys, values (lowest to highest)
        mrv_vars = list(mrv_sorted.keys())
        mrv_vals = list(mrv_sorted.values())
        # Check if lowest value has ties
        mrv_min = mrv_vals[0]
        n = mrv_vals.count(mrv_min)
        # If single minimum
        if n == 1:
            # Return first var in dict
            return mrv_vars[0]
        # Else if tied mrv
        else:
            # Calculate degree of lowest n vars
            ldh = {}
            for var in mrv_vars[0:n]:
                ldh[var] = len(self.crossword.neighbors(var))
            # Sort by highest degree value, as list of tuples
            ldh_max = sorted(ldh.items(), key=lambda item: item[1], reverse=True)
            # Return var with largest degree -- first item of first tuple in list
            return ldh_max[0][0]          

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # If the assignment is complete, return
        if self.assignment_complete(assignment):
            return assignment

        # var = Select-Unassigned-Var(assignment, csp)
        var = self.select_unassigned_variable(assignment)
        
        # for value in Domain-Values(var, assignment, csp):
        for val in self.order_domain_values(var, assignment):
            # if value consistent with assignment:            
            if self.consistent(assignment):
            # add {var = value} to assignment
                assignment[var] = val
                # inferences = Inference(assignment, csp)
                # if inferences ≠ failure:
                # add inferences to assignment
                # result = Backtrack(assignment, csp)
                result = self.backtrack(assignment)
                # if result ≠ failure:
                if result is not None:
                    # return result
                    return result
                # remove {var = value} and inferences from assignment
                else:
                    assignment.pop(var)
            # return failure
            return None

def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

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


if __name__ == "__main__":
    main()
