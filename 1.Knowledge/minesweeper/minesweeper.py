import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        # A cell = a mine when there is a 1:1 knowledge of cells to mines
        # i.e. # cells == # mines
        if len(self.cells) == self.count:
            return self.cells
        else:
            return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        # A cell is safe when the mine count = 0, and the cell exists in the knowledge
        if (self.count == 0 and len(self.cells) != 0):
            return self.cells
        else:
            return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        # If cell is a mine and in list of cells, remove from set of cells and -1 from count
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        # If cell is safe and in list of cells, remove from the set
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)
    
    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.
        """
        # 1) Mark the cell as a move that has been made
        self.moves_made.add(cell)

        # 2) Mark the cell as safe using mark_safe method
        self.mark_safe(cell)

        # 3) Add a new sentence to the AI's knowledge base using the value of `cell` and `count`
        # Find neighbours of the cell
        cell_neighbours = self.find_neighbours(cell)
        # Check if state of neighbour is already known, if so then remove 
        known_neighbours = set()        
        for neighbour in cell_neighbours:
            if neighbour in self.mines:
                known_neighbours.add(neighbour)
                count -= 1
            elif neighbour in self.safes:
                known_neighbours.add(neighbour)
        cell_neighbours -= known_neighbours
        # Create new Sentence instance using unknown neighbours and count
        new_knowledge = Sentence(cell_neighbours,count)
        # Add new Sentence to the knowledge base
        self.knowledge.append(new_knowledge)

        # 4) Mark any additional cells as safe or as mines based on the AI's knowledge base
        add_mines = set()
        add_safes = set()
        # For each Sentence instance in the AI's KB
        for sentence in self.knowledge:
            # If the knowledge is empty, remove sentence
            if len(sentence.cells) == 0:
                self.knowledge.remove(sentence)
            # Else, for each knowledge Sentence, check known mines and safes and add to AI's list
            else:
                for mine in sentence.known_mines():
                    add_mines.add(mine)
                for safe in sentence.known_safes():
                    add_safes.add(safe)
        # AI mark mines
        for mine in add_mines:
            self.mark_mine(mine)
        # AI mark safes
        for safe in add_safes:
            self.mark_safe(safe)
        
        # 5) Add any new knowledge if it can be inferred from existing knowledge
        # Compare sentences in the KB against each other (but not the same sentence) for subsets
        infered_knowledge = Sentence(set(),0)
        for sentence1 in self.knowledge:
            for sentence2 in self.knowledge:
                if sentence1 != sentence2:
                    infered_knowledge = self.knowledge_subset(sentence1,sentence2)
        # Add infered knowledge, if it exists, to the AI's KB
        self.knowledge.append(infered_knowledge)

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        # Set of safe moves which have not been made yet
        unmade_safes = self.safes.difference(self.moves_made)
        # If no safe move, return None
        if len(unmade_safes) == 0:
            return None
        # Else pick a move which is safe and not yet made
        else:
            return unmade_safes.pop()

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        all_moves = set()
        for i in range(self.height):
            for j in range(self.width):
                all_moves.add((i,j))
        # Set of allowed moves
        allowed_moves = all_moves - self.mines - self.moves_made
        # If no allowed moves, return None
        if len(allowed_moves) == 0:
            return None
        # Else select random move
        else:
            return allowed_moves.pop()
    
    def find_neighbours(self, cell):
        """
        For cell (i,j), find immediate neighbours
        """
        i,j = cell
        neighbours = set()
        for n in range(i-1,i+2):
            for m in range(j-1,j+2):
                if (n,m) != (i,j):  # exclude the safe cell
                    if 0 <= n < self.height and 0 <= m < self.width: # check row falls within the height,width of grid
                        neighbours.add((n,m))
        return neighbours

    def knowledge_subset(self,sentence1,sentence2):
        set1 = sentence1.cells
        set2 = sentence2.cells
        infered_cells = set()
        infered_count = 0
        # If cells are a subset
        if set1.issubset(set2):
            # Subtract to get the remaining cells
            infered_cells = set2.difference(set1)
            # Subtract the count difference
            infered_count = sentence2.count - sentence1.count
        # Create new knowledge Sentence using infered cells and count
        infered_knowledge = Sentence(infered_cells,infered_count)
        return infered_knowledge