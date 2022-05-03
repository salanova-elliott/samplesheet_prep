#!/usr/bin/env python3

import sys
import argparse
import string
import csv
from datetime import date

# Argument parser
parser = argparse.ArgumentParser(description = "Creates a sample sheet for Illumina amplicon sequencing. Outputs to run-name.csv")
parser.add_argument("-r", "--run-name", metavar="runname", dest="runname", type=str, 
                    help="Name of the sequencing run", required=True)
parser.add_argument("-w", "--workflow", metavar="workflow", dest="workflow", choices = ["A", "B"],
                    help="Type of workflow Choice of 'A' (MiSeq) or 'B' (MiniSeq, NextSeq) ", required=True)
parser.add_argument("-i", "--indices", metavar="indices", dest="indices",
                    type=str, help="CSV document containing the indices for the appropraite workflow", required=True)
parser.add_argument("-l", "--library-names", metavar="libnames", dest="libnames",
                    type=str, help="CSV document containing only library name and index ID on each line", required=True)
args = parser.parse_args()

# Descriptions for output
descript_dict = {
    "A" : "The Index 2 Read is performed before Read 2 resynthesis, so the Index 2 (i5) adapter is sequenced on the forward strand. "
            "Workflow A is performed on the NovaSeq, MiSeq, HiSeq 2500, and HiSeq 2000.",
    "B" : "The Index 2 Read is performed after Read 2. Workflow B is performed on the MiniSeq, NextSeq, HiSeq 4000, and HiSeq 3000."
}

# Reminder for workflow choice
print(f"REMINDER: You have chosen workflow {args.workflow}. Make sure you have input the corresponding indices.", file=sys.stderr)

# Dictionary of indices {UDI_index: [well_coord, index, index2]}
index_dict = {}

# Library list [[libname, UDI_index], ...]
library_list = []

# Today's date in correct format
today_date = date.today().strftime("%Y.%m.%d")

# Sample ID counter
sampleID_counter = 1

# Accepted characters for sample names
accepted_chars = set(string.ascii_lowercase + string.ascii_uppercase + "_0123456789")

# Checks that sample name is kosher
def name_check(sample_name):
    assert set(sample_name) <= accepted_chars, f"{sample_name} contains invalid characters"

# Populates dictionary of indices
with open(args.indices) as index_f:
    csv_reader = csv.reader(index_f, delimiter=",")
    for row in csv_reader:
        if row[4].startswith("UDI"):
            index_dict[row[4]] = [row[3], row[5], row[7]]

# Loads sample names into library_dict
with open(args.libnames) as lib_f:
    csv_reader = csv.reader(lib_f, delimiter=",")
    # Checks library names
    for n in csv_reader:
        name_check(n[0])
        library_list.append(n)

# OUTPUT
with open(f"{args.runname}.csv", "w") as output_f:
    outputwriter = csv.writer(output_f, delimiter=",")

    outputwriter.writerow([args.runname])
    outputwriter.writerow(["Date", today_date])
    outputwriter.writerow(["Workflow", "GenerateFASTQ"])
    outputwriter.writerow(["Assay", "TruSeq HT"])
    outputwriter.writerow(["Index Kit", "IDT-ILMN TruSeq DNA-RNA UD 96 Indexes"])
    outputwriter.writerow(["Description", descript_dict[args.workflow]])
    outputwriter.writerow(["Chemistry", "Amplicon"])

    outputwriter.writerows([[], ["[Reads]"], ["151"], ["151"], []])

    outputwriter.writerows([
        ["[Settings]"],
        ["Adapter", "AGATCGGAAGAGCACACGTCTGAACTCCAGTCA"],
        ["AdapaterRead2", "AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGT"],
        []
    ])

    outputwriter.writerow(["[Data]"])
    outputwriter.writerow([
        "Sample_ID", 
        "Sample_Name", 
        "Index_Plate_Well", 
        "I7_Index_ID", 
        "index", 
        "I5_Index_ID", 
        "index2", 
        "Sample_Project", 
        "Description"
    ])

    for library in library_list:
        outputwriter.writerow([
            sampleID_counter, 
            library[0], 
            index_dict[library[1]][0],
            library[1],
            index_dict[library[1]][1],
            library[1],
            index_dict[library[1]][2],
            "Project",
            "Description"
        ])
        sampleID_counter += 1