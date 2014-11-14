#!/usr/bin/env python
# Fredrik Boulund (c) 2014
# Run a program on multiple data files on C3SE Glenn

from sys import argv, exit
from subprocess import Popen, PIPE
import argparse


def parse_commandline():
    """Parse commandline.
    """

    desc="""Run in parallel on C3SE Glenn using Slurm sbatch. Fredrik Boulund (c) 2014"""

    parser = argparse.ArgumentParser(description=desc)

    slurm = parser.add_argument_group("SLURM", "Set slurm parameters.")
    slurm.add_argument("-N", type=int,
        default=1,
        help="Number of nodes. Change if you're running MPI [%(default)s].")
    slurm.add_argument("-p", 
        default="glenn",
        help="Slurm partition [%(default)s].")
    slurm.add_argument("-A", 
        default="SNIC2014-1-183",
        help="Slurm account [%(default)s].")
    slurm.add_argument("-t", 
        default="01:00:00",
        help="Max runtime per job [%(default)s].")
    slurm.add_argument("-C", choices=["SMALLMEM", "BIGMEM", "HUGEMEM"],
        default="",
        help="Specify node memory size [default let Slurm decide].")

    program_parser = parser.add_argument_group("PROGRAM", "Command to run in parallel.")
    program_parser.add_argument("--call", 
        default="",
        help="Program and arguments in a single quoted string, "+\
            "e.g. 'blat dbfile.fasta {query} -t=dnax q=prot {query}.blast8'. "+\
            "{query} is substituted for the filenames specified on "+\
            "as arguments to run_in_parallel.py (one file per Slurm job).")
    program_parser.add_argument("query", nargs="+", metavar="FILE",
        default="",
        help="Query file(s).")

    if len(argv)<2:
        parser.print_help()
        exit()

    options = parser.parse_args()
    return options



def generate_sbatch_script(options, query_file):
    """Generate sbatch script.
    """

    sbatch_script = ["#!/usr/bin/env bash",
        "#SBATCH -N {N}".format(N=options.N),
        "#SBATCH -p {p}".format(p=options.p),
        "#SBATCH -A {A}".format(A=options.A),
        "#SBATCH -t {t}".format(t=options.t)]

    if options.C:
        sbatch_script.append("#SBATCH -C {C}".format(C=options.C))

    call = options.call.format(query=query_file)
    sbatch_script.append("{call}".format(call=call))

    return "\n".join(sbatch_script)



def call_sbatch(sbatch_script):
    """Run sbatch in a subprocess.
    """

    sbatch = Popen("sbatch", stdin=PIPE, stdout=PIPE, stderr=PIPE)
    out, err = sbatch.communicate(sbatch_script)
    if err:
        raise Exception("sbatch error: {}".format(err))



if __name__ == "__main__":
    options = parse_commandline()
    for query_file in options.query:
        sbatch_script = generate_sbatch_script(options, query_file)
        call_sbatch(sbatch_script)
        print "Submitted Slurm job for '{}'".format(query_file)
