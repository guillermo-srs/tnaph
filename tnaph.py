import numpy as np
import pandas as pd
from difflib import get_close_matches as cls
import re
import os
import sys


class tnaph():
    """
    Class to handle a pandas of code errors and score them

    ...

    Attributes
    ----------
    data : pandas
        Pandas object which columns and indexes, represent the filename and
        error names, respectively.

    Methods
    -------

    add_name(self, name)
        Adds a name (row) to the pandas

    add_problem(self, problem)
        Checks and adds a problem (column) to the pandas

    update(self, name, problem, val)
        Updates the value of [name, problem] to '1' regardless
        of its previous value

    find(self, string, problem=True)
        Finds the closets problem or name (column or row) in the pandas

    get_name(self, name)
        Gets a name from the pandas

    def save(self, f='data.csv')
        Saves the pandas into a csv file
    """

    def __init__(self, f=''):
        if f != '':
            self.data = pd.read_csv(f, index_col=[0])
        else:
            self.data = pd.DataFrame()

    def add_name(self, name):
        if name in self.find(name, problem=False):
            print('Error: Name already exists')
        else:
            self.__add_name__(name)

    def __add_name__(self, name):
        """Private function to add a name to the pandas"""
        x = self.data.columns
        y = np.array([name])
        frame = [self.data,
                 pd.DataFrame(np.zeros([1, len(x)]), index=y, columns=x)]
        self.data = pd.concat(frame)

    def add_problem(self, problem):
        if problem in self.find(problem):
            print('Error: Problem already exists')
        else:
            self.__add_problem__(problem)

    def __add_problem__(self, problem):
        """Private function to add a problem to the pandas"""
        self.data.insert(len(self.data.columns), problem, 0)

    def update(self, name, problem, val):
        self.data.loc[[name], [problem]] = val

    def find(self, string, problem=True):
        if problem is True:
            # find problem
            return cls(string, self.data.columns.values)
        else:
            # find name
            return cls(string, self.data.index.values.astype(str))

    def get_name(self, name):
        scores = self.data.transpose()
        return np.array(scores[name][(scores[name] == 1)].index)

    def save(self, f='data.csv'):
        self.data.to_csv(f)


def set_score_values(data, sc_ej, score=10, key="EX"):
    """Sets the score values for each problem found in the pandas (data)

    The input is performed over an command line input.

    Parameters
    ----------
    data : pandas object
         Pandas from the tnaph object
    sc_ej : Array-like
        Array of percentages with the weight for each exercise
    score : int (default is 10)
        The total score if the file
    key : str (default is 'EX')
        Key used to identify each exercise

    Return
    ------

    score_err : dictionary
        Dictionary with the name of the problems and score
    """
    if np.sum(sc_ej) > 1.:
        print("Warning: The sum of the scores is greater" //
              + "than the total score")
    err = data.columns
    score_err = {}
    for i in range(len(sc_ej)):
        r = re.compile('.*'+key+str(i+1)+'[0-9]*-.*')
        print("Exercise " + str(i+1) + "; Points :" + str(sc_ej[i]*score))
        vmatch = np.vectorize(lambda x: bool(r.match(x)))
        err_aux = err[vmatch(err)]
        for elem in err_aux:
            value = float(input("Score : '"+str(elem)+"' :")) * sc_ej[i]
            score_err.update({str(elem): value})
    return score_err


def add_comments(data, nm, dcom, fout):
    """Function that parses the problems and comments of a dictionary,
    into a data structure and output tex file.

    Parameters
    ----------
    data : tnaph object
         Tnaph object where the extracted data will be stored
    nm : string
        Name of the file
    dcom : dictionary
        Dictionary with the extracted data (problems and comments)
    fout : str
        Name of the output file (tex)

    """

    fh = open(fout, "a")
    for pname, [code, comment] in sorted(dcom.items()):

        lst = data.find(pname)
        if pname not in lst:
            data.add_problem(pname)
        data.update(nm, pname, 1)
        fh.write("\subsection{" + pname + "}\n")
        fh.write("\\begin{lstlisting}[frame=single,tabsize=2]\n")
        for text in code:
            fh.write(text)
        fh.write("\end{lstlisting}\n")
        for text in comment:
            fh.write(text[2:])
    fh.write("\end{document}\n")
    fh.close()


def apply_score(data, err_d, scr_stl):
    """Function that applies the problems' score to each name on data

    This function is a complementary function to set_score_values(...)

    Parameters
    ----------
    data : pandas object
         pandas object where the data will be imported from
    err_d : dictionary
         dictionary with the scores of each problem
    scr_stl : array-like
         Array with the score of each exercise

    Return
    ------
    res : dictionary
        Dictionary with the final score of each name in data

    """

    notas = data.transpose()
    res = {}
    for pareja in notas.columns:
        pr = np.array(notas[pareja][(notas[pareja] == 1)].index)
        a = 10
        for elem in pr:
            a -= err_d[elem]
        a = a * scr_stl
        res.update({pareja: a})
    return res


def parse_file(data, nm, fin, fout, language="Lisp"):
    """Function that parses a file into a tnaph object and a output tex file.

    Parameters
    ----------
    data : object
         Tnaph object where the data will be stored
    nm : string
        Name used to identify the file from now on
    fin : str
        Name of the input file
    fout : str
        Name of the output file (tex)

       Return
    ------
    res : dictionary
        Dictionary with the final score of each name in data

    """

    fh = open(fout, "w")
    fh.write("\\documentclass{article}\n\\usepackage{color}\\usepackage{listings}\n\\begin{document}\n\\lstset{breaklines,numbers=left,numberstyle=\\tiny,numbersep=5pt,language=" + language + ",basicstyle=\\ttfamily\\footnotesize,showstringspaces=false,keywordstyle=\\ttfamily\\color{blue},stringstyle=\\ttfamily\\tiny\\ttfamily\\color{red},commentstyle=\\ttfamily\\color{red}}\n\n\n\section{Name: " + nm[1:] + "}")
    fh.close()
    dcom = get_comments(fin)
    lst = data.find(nm, problem=False)
    if nm not in lst:
        data.add_name(nm)
    return add_comments(data, nm, dcom, fout)


def get_comments(fname):
    """Auxiliary function of parse_file, that extracts comments from fname
    into a dictionary"""
    data = {}
    with open(fname, 'r+') as f:
        flag = False
        buffer = []
        cbuffer = []
        comment_name = ''

        for line in f:
            if line.startswith(";#end"):
                data.update({comment_name: [buffer, cbuffer]})
                buffer = np.array([])
                cbuffer = np.array([])
                flag = False
            elif flag:
                if line.startswith(";%"):
                    cbuffer = np.append(cbuffer, line)
                elif line.startswith(";"):
                    continue
                else:
                    buffer = np.append(buffer, line)
            elif line.startswith(";#ini"):
                ini = line.find('name=')
                comment_name = line[ini+5:].upper().strip()
                flag = True
    return data


if __name__ == '__main__':
    ln = len(sys.argv)
    if ln != 4:
        print("Format: tnaph.py <directory> <language> <termination" //
              + " (e.g. .py)>")
        raise TypeError("Three arguments were expected, but it received "
                        + str(ln - 1))

    directory, language, termination = sys.argv[1:]
    TN = tnaph(f='./data.csv')
    for filename in os.listdir(directory):
        if filename.endswith(termination):
            name = filename.split('-')[0]
            parse_file(TN, name, directory+'/'+filename, name+'.tex')
    TN.save()
