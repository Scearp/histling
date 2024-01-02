import sys

import pandas as pd
import numpy as np

from Levenshtein import distance
from sklearn.cluster import AgglomerativeClustering
from scipy.spatial.distance import squareform
from scipy.spatial import distance_matrix


def word_distance(a, b):
    x = a[0]
    y = b[0]
    return distance(x, y) / max(len(x), len(y))
    return 2 * distance(x, y) / (len(x) + len(y))


def main():
    df = pd.read_csv("./words.csv")
    df['gloss'] = df['gloss'].str.replace("\xa0", " ")
    df['ipa'] = df['ipa'].str.replace('tʃ', 'ʧ')

    pdf = pd.pivot_table(df, values='ipa', index='gloss',
                         columns='language', aggfunc=lambda x: x)

    langs = pdf.columns

    rows = []
    for gloss, *reflexes in pdf.itertuples():
        temp = list(zip(reflexes, langs))
        ls = [gloss]
        for e in temp:
            if isinstance(e[0], str):
                ls.append(e)
            elif isinstance(e[0], np.ndarray):
                for i in e[0]:
                    ls.append((i, e[1]))
        if len(ls) > 2:
            rows.append(ls)

    candidates = []

    for row in rows:
        refl = row[1:]
        l = len(refl)
        dm = np.ndarray((l, l))
        for x in range(l):
            for y in range(l):
                dm[x, y] = word_distance(refl[x], refl[y])

        c = AgglomerativeClustering(
            n_clusters=None,
            metric='precomputed',
            linkage='single',
            distance_threshold=0.5).fit_predict(dm)

        sets = {i: [] for i in set(c)}
        counts = {i: 0 for i in sets}

        if max(c) < l - 1:
            for tup in zip(row[1:], c):
                sets[tup[1]].append((tup[0][0], row[0], tup[0][1]))
                counts[tup[1]] += 1

        for s in sets:
            if counts[s] > 1:
                candidates.append(sets[s])

    for cand in candidates:
        print(cand)

    print(len(candidates))


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
