import numpy as np
import pandas as pd
import sys

V = ['a', 'e', 'ɛ', 'o', 'u', 'y', 'i', 'ø', 'ə', 'ɐ', 'ɔ', 'j', 'l', 'w']
N = ['m', 'n', '.', 'ŋ', 'ɲ']
A = ['s', 't', 'ʃ', 'd', 'z', 'ʒ', 'ð', 'θ', 'ʧ']
VE = ['g', 'k', 'ɣ', 'x', 'ŋ']
S = ['l', 'r', 'ɾ', 'ʁ', 'ʎ', 'w', 'j']

CLASSES = [V, N, A, VE, S]

distances = {}

BIG = 0.5
SMALL = BIG


def sub_cost(a, b):

    cost = 1

    tup = tuple(sorted([a, b]))
    a = tup[0]
    b = tup[1]

    if tup in distances:
        return distances[tup]

    for c in CLASSES:
        if a in c and b in c:
            cost -= BIG
            distances[tup] = cost
            return cost

    return cost


def distance(a: str, b: str, threshold=0.3):
    '''Levenstein edit distance'''
    m = len(b)
    n = len(a)

    if n > m:
        return distance(b, a)

    if (m - n) / (2 * n) > threshold:
        return False

    diff = 0

    while len(a) < m:
        a += " "
        diff += 1

    m += 1

    matrix = np.zeros(m ** 2)

    for i in range(1, m):
        matrix[i] = matrix[i - 1] + 1
        matrix[i * m] = matrix[(i-1) * m] + 1
    for i in range(1, m):
        for j in range(1, m - diff):
            if a[i - 1] != b[j - 1]:
                matrix[i + j * m] = min(
                    matrix[i - 1 + j * m] + 1,
                    matrix[i + (j - 1) * m] + 1,
                    matrix[i - 1 + (j - 1) * m] + sub_cost(a[i-1], b[j-1]))
            else:
                matrix[i + j * m] = matrix[i - 1 + (j - 1) * m]

    for i in range(1, diff + 1):
        if b[-i] in V or b[-i] == ".":
            matrix[-1] -= 0.5

    return matrix[m + (m - diff - 1) * m - 1] / (m - 1) <= threshold


def main():
    df = pd.read_csv("./words.csv")

    df = df[df['ipa'].apply(lambda x: len(x) > 3)]

    langs = df['language'].drop_duplicates()
    df['ipa'] = df['ipa'].str.replace('tʃ', 'ʧ')
    df['gloss'] = df['gloss'].str.replace('\xa0', ' ')

    pairs = []
    dist = []

    for l_1 in langs:
        for l_2 in langs:
            if l_1 == l_2:
                break
            print(l_1, l_2)
            df_1 = df[df['language'] == l_1]
            df_2 = df[df['language'] == l_2]

            for f in df_1.itertuples():
                for p in df_2.itertuples():
                    if f.gloss == p.gloss:
                        pairs.append(
                            (distance(f.ipa, p.ipa), f.ipa, f.gloss, p.ipa, p.gloss, l_1, l_2))
                    else:
                        pairs.append(
                            (distance(f.ipa, p.ipa, threshold=0.2), f.ipa, f.gloss, p.ipa, p.gloss, l_1, l_2))

    ndf = pd.DataFrame(pairs)
    ndf = ndf.loc[ndf[0]].sort_values(by=2).reset_index(drop=True)

    ndf.to_csv("out.csv")

    print(ndf.reset_index(drop=True).to_string())

    '''pairs = []

    for idx, row in ndf.iterrows():
        pairs.append(((row.iat[1], row.iat[2], row.iat[5]),
                     (row.iat[3], row.iat[4], row.iat[6])))

    pool = set(map(frozenset, pairs))
    groups = []

    while pool:
        group = set()
        groups.append([])
        while True:
            for candidate in pool:
                if not group or group & candidate:
                    group |= candidate
                    groups[-1].append(tuple(candidate))
                    pool.remove(candidate)
                    break
            else:
                break

    for c_set in groups:
        print(c_set)'''


if __name__ == "__main__" and sys.argv[-1] == 'p':
    import cProfile
    from pstats import Stats

    pr = cProfile.Profile()
    pr.enable()

    main()

    pr.disable()
    stats = Stats(pr)
    stats.sort_stats('tottime').print_stats(10)

elif __name__ == '__main__':
    main()
