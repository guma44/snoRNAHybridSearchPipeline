#!/usr/bin/env python
"""
Generate fasta file from snoRNA input
"""

__date__ = "2015-02-20"
__author__ = "Rafal Gumienny"
__email__ = "r.gumienny@unibas.ch"
__license__ = "GPL"

# imports
import sys
import os
file_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(file_dir, ".."))
import time
from modules.snoRNA import CD_snoRNA, WrongCDBoxPlacementException, IncompatibleStrandAndCoordsException
import pandas as pd
from collections import defaultdict
from argparse import ArgumentParser, RawTextHelpFormatter

class WrongTypeException(Exception): pass

parser = ArgumentParser(description=__doc__, formatter_class=RawTextHelpFormatter)
parser.add_argument("-v",
                    "--verbose",
                    dest="verbose",
                    action="store_true",
                    default=False,
                    help="Be loud!")
parser.add_argument("--input",
                    dest="input",
                    required=True,
                    help="Input file in tab format.")
parser.add_argument("--output",
                    dest="output",
                    help="Output file in fasta format.")
parser.add_argument("--type",
                    dest="type",
                    required=True,
                    choices=("CD", "HACA"),
                    help="Type of snoRNA")
parser.add_argument("--switch-boxes",
                    dest="switch_boxes",
                    action="store_true",
                    default=False,
                    help="If the CD box is located wrongly it will try to relabel it")
parser.add_argument("--length",
                    dest="length",
                    type=int,
                    default=20,
                    help="Length of interaction element (seed) to be extracted, defaults to 20")


# redefine a functions for writing to stdout and stderr to save some writting
syserr = sys.stderr.write
sysout = sys.stdout.write


def main(options):
    """Main logic of the script"""
    names = ["chrom",
             "start",
             "end",
             "snor_id",
             "mod_type",
             "strand",
             "sequence",
             "box_d",
             "box_c",
             "box_h",
             "box_aca",
             "alias",
             "gene_name",
             "accession",
             "mod_site",
             "host_gene",
             "host_id",
             "organization",
             "organism",
             "note"]
    snoRNAs = pd.read_table(options.input, names=names)
    if len(set(snoRNAs.mod_type)) != 1:
        WrongTypeException("More than one type of snoRNAs detected: %s" % str(set(snoRNAs.mod_type)))
    counter = 0
    if options.type == "CD":
        families = defaultdict(list)
        for ind, snor in snoRNAs.iterrows():
            try:
                s = CD_snoRNA(snor_id=snor.snor_id,
                              organism=snor.organism,
                              chrom=snor.chrom,
                              start=snor.start,
                              end=snor.end,
                              strand=snor.strand,
                              sequence=snor.sequence,
                              snor_type=snor.mod_type,
                              d_boxes=snor.box_d,
                              c_boxes=snor.box_c,
                              switch_boxes=options.switch_boxes,
                              alias=snor.alias,
                              gene_name=snor.gene_name,
                              accession=snor.accession,
                              modified_sites=snor.mod_site,
                              host_id=snor.host_id,
                              organization=snor.organization,
                              note=snor.note)
                families[str(s.get_d_interaction_region(options.length))].append(s.snor_id)
            except WrongCDBoxPlacementException, e:
                syserr(str(e) + "\n")
            except IncompatibleStrandAndCoordsException, e:
                syserr(str(e) + "\n")
            except TypeError, e:
                syserr(str(e) + "\n")
        for key, val in families.iteritems():
            print key, val
        print "Found %s families" % len(families.keys())
    elif options.type == "HACA":
        raise NotImplementedError("This function has not been implemented yet")
    else:
        raise Exception("Unknown type of snoRNA")

if __name__ == '__main__':
    try:
        try:
            options = parser.parse_args()
        except Exception, e:
            parser.print_help()
            sys.exit()
        if options.verbose:
            start_time = time.time()
            start_date = time.strftime("%d-%m-%Y at %H:%M:%S")
            syserr("############## Started script on %s ##############\n" %
                   start_date)
        main(options)
        if options.verbose:
            syserr("### Successfully finished in %i seconds, on %s ###\n" %
                   (time.time() - start_time,
                    time.strftime("%d-%m-%Y at %H:%M:%S")))
    except KeyboardInterrupt:
        syserr("Interrupted by user after %i seconds!\n" %
               (time.time() - start_time))
        sys.exit(-1)
