import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]

def calc_genes(person, one_gene, two_genes):
    """
    Function to determine the number of genes for a person
    Inputs:
        person, string
        one_gene, set of persons carrying one gene
        two_genes, set of persons carrying two genes
    Returns: an integer of the number of genes
    """
    if person in one_gene:
        return 1
    elif person in two_genes:
        return 2
    else:
        return 0

def inherits_gene(genes_parent, from_parent):
    """
    Function to determine probability a child inherits genes from parents
    Inputs:
        genes_parent, integer of how many genes parent has
        from_parent, boolean value if child inherits gene from parent
    Return: probability value child inherits gene from parent
    """
    # If parent has 0 genes
    if genes_parent == 0:
        # If child inherits from parent, must be via mutation 
        # ==> P(inherits) = P(mutation)
        if from_parent:
            return PROBS["mutation"]
        # Else, P(not inherits) = P(not mutation)
        else:
            return 1 - PROBS["mutation"]
    # If parent has 1 gene, equal likelihood for child to inherit, not inherit
    elif genes_parent == 1:
        return 0.5
    # If parent has 2 genes
    elif genes_parent == 2:
        # Child won't inherit if mutation
        # P(not inherits) = P(mutation)
        if not from_parent:
            return PROBS["mutation"]
        # P(inherits) = 1 - P(mutation)
        else:
            return 1 - PROBS["mutation"]
    
def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    # For every person, init dictionary to store gene and trait probabilities
    person_values = {
        person: {
            "n_genes": None,
            "p_gene": None,
            "p_trait": None
        }
        for person in people
    }
    # Determine which people are parents/children
    children = []
    parents = []
    for person in people:
        # If person has a mother or father ==> child
        if (people[person]["mother"] or people[person]["father"]):
            children.append(person)
        # Else are a parent
        else:
            parents.append(person)
    
    # Implement parent logic
    for parent in parents:
        # Calculate number of genes, store value
        num_genes = calc_genes(parent, one_gene, two_genes)
        person_values[parent]["n_genes"] = num_genes
        # Assign probabilities
        person_values[parent]["p_gene"] = PROBS["gene"][num_genes]
        person_values[parent]["p_trait"] = PROBS["trait"][num_genes][parent in have_trait]
    
    # Implement child logic which considers parent genes and mutation
    for child in children:
        # Determine child's genes, store value
        num_genes = calc_genes(child, one_gene, two_genes)        
        person_values[child]["n_genes"] = num_genes
        # Determine number of parent genes
        mother = people[child]["mother"]
        father = people[child]["father"]
        genes_mother = person_values[mother]["n_genes"]
        genes_father = person_values[father]["n_genes"]
        # Calculate gene probability for child, given parent info
        # If child has 0 genes
        if num_genes == 0:
            # Assume 0 genes from each parent ie. P(not mother, not father) 
            # ==> P(not mother)*P(not father)
            p_gene = inherits_gene(genes_mother, False) * inherits_gene(genes_father, False)
        # If child has 1 gene
        elif num_genes == 1:
            # Can inherit 1 gene from either parent ie. P(mother, not father) or P(father, not mother) 
            # ==> P(mother)*P(not father) + P(father)*P(not mother)
            p_gene = inherits_gene(genes_mother, True) * inherits_gene(genes_father, False) \
                + inherits_gene(genes_mother, False) * inherits_gene(genes_father, True)
        # If child has 2 genes
        elif num_genes == 2:
            # Assume 1 gene from each parent ie. P(mother, father) 
            # ==> P(mother)*P(father)
            p_gene = inherits_gene(genes_mother, True) * inherits_gene(genes_father, True)
        # Store gene probability for child
        person_values[child]["p_gene"] = p_gene
        # Trait probability
        person_values[child]["p_trait"] = PROBS["trait"][num_genes][child in have_trait]
    # Calculate the joint probability
    joint_prob = 1
    for person in person_values:
        joint_prob *= person_values[person]["p_gene"]*person_values[person]["p_trait"]
    
    return joint_prob

def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities:
        # Calculate number of genes
        num_genes = calc_genes(person, one_gene, two_genes)
        # Assign gene probability
        probabilities[person]["gene"][num_genes] = p
        # Asign trait probability
        probabilities[person]["trait"][person in have_trait] = p

def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities:
        # Determine gene normalisation factor: 1/sum(gene values)
        gene_factor = 1/(probabilities[person]["gene"][0] + probabilities[person]["gene"][1] + probabilities[person]["gene"][2])
        # Determine trait normalisation factor: 1/sum(trait values)
        trait_factor = 1/(probabilities[person]["trait"][True] + probabilities[person]["trait"][False])
        # Normalise gene probabilities
        for gene in probabilities[person]["gene"]:
            probabilities[person]["gene"][gene] *= gene_factor
        # Normalise trait probabilities
        for trait in probabilities[person]["trait"]:
            probabilities[person]["trait"][trait] *= trait_factor

    return probabilities

if __name__ == "__main__":
    main()
