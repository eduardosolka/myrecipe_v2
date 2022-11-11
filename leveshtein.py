import numpy
class Levenshtein_string:
    def printDistances(distances, token1Length, token2Length):
        print((distances[(token1Length)][(token2Length)]), end=" ")
        print()


    def levenshteinDistanceDP(token1, token2):
        distances = numpy.zeros((len(token1) + 1, len(token2) + 1))
        
        for t1 in range(len(token1) + 1):
            distances[t1][0] = t1

        for t2 in range(len(token2) + 1):
            distances[0][t2] = t2
        #cria a matriz vazia com estes indexs t1 e t2, 
        #cada token na string 1 são x linhas(t1) e cada token da string 2 são y colunas(t2)
        a = 0
        b = 0
        c = 0
        for t1 in range(1, len(token1) + 1):
            for t2 in range(1, len(token2) + 1):                
                if (token1[t1-1] == token2[t2-1]):
                    distances[t1][t2] = distances[t1 - 1][t2 - 1]
                else:
                    a = distances[t1][t2 - 1]
                    b = distances[t1 - 1][t2]
                    c = distances[t1 - 1][t2 - 1]
                    
                    if (a <= b and a <= c):
                        distances[t1][t2] = a + 1
                    elif (b <= a and b <= c):
                        distances[t1][t2] = b + 1                    
                    else:
                        distances[t1][t2] = c + 1
                    
        distancia = distances[len(token1)][len(token2)]
        if distancia < 1:
            peso = 1
        if distancia == 1:
            peso = 0.7
        if distancia == 2:
            peso = 0.5
        if distancia > 2:
            peso = 0.1

        return peso


    print(levenshteinDistanceDP("hl", "hello"))
    #print(printDistances(5, 3, 2))