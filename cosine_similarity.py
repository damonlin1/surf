# Program to measure the similarity between 
# two sentences using cosine similarity.
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# X = input("Enter first string: ").lower()
# Y = input("Enter second string: ").lower()
X = """Germaine Marthe NEVEU fone- t ionnaire de la Mairie du 2,° Arrondissement de Paris, officier de 1 'état civil par délégation du ***** Maire. l'ADJOTNT AU MAIRE ÓFFICIER' DE L'ÉTAT-CIVIL
Germaine Marthe NEVEU, fonctionnaire de la Mairie du 2° Arrondissement de Paris, Officier * de 1 'état civil par délégat ion du Maire. L'ADJOINT All MATHE GFFICERR L'ÉTAT-CIVIL"""
Y = "Germaine Marthe NEVEU , fonctionnaire de la Mairie du 2° rrondissement de Paris, officier de l'état civil par délégation du Maire. L'ADJOTNT AU MATRE OFFICIER DE L'ÉTAT-CINIL "

# tokenization
X_list = word_tokenize(X)
Y_list = word_tokenize(Y)

# sw contains the list of stopwords
sw = stopwords.words('english')
l1 = []
l2 = []

# remove stop words from the string
X_set = {w for w in X_list if not w in sw}
Y_set = {w for w in Y_list if not w in sw}

# form a set containing keywords of both strings 
rvector = X_set.union(Y_set)
for w in rvector:
    if w in X_set:
        l1.append(1)  # create a vector
    else:
        l1.append(0)
    if w in Y_set:
        l2.append(1)
    else:
        l2.append(0)
c = 0

# cosine formula 
for i in range(len(rvector)):
    c += l1[i] * l2[i]
cosine = c / float((sum(l1) * sum(l2)) ** 0.5)
print("similarity: ", cosine)
