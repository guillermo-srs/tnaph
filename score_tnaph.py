import sys
import tnaph as tn
from ast import literal_eval

if __name__ == '__main__':
    ln = len(sys.argv)
    if ln != 2:
        print("Format: score_tnaph.py <array_of_scores>")
        raise TypeError("One arguments were expected, but it received "
                        + str(ln - 1))

    exercises_score = literal_eval(sys.argv[1])
    TN = tn.tnaph(f='./data.csv')
    err = tn.set_score_values(TN.data, exercises_score, pond=10, key="EJ")
    print(tn.apply_score(TN.data, err, 1))

