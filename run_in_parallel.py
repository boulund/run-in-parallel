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
    slurm.add_argument("-J", 
        default="sbatch",
        help="""Name for the job allocation, note that at most 8 characters are seen 
                in the squeue listings [%(default)s].""")

    program_parser = parser.add_argument_group("PROGRAM", "Command to run in parallel.")
    program_parser.add_argument("--call", required=True,
        default="",
        help="""Program and arguments in a single quoted string,
                e.g. 'blat dbfile.fasta {query} -t=dnax q=prot {query}.blast8'.
                {query} is substituted for the filenames specified on
                as arguments to run_in_parallel.py (one file per Slurm job).""")
    program_parser.add_argument("--stack", type=int, metavar="N",
        default=1,
        help="""Stack N calls on each node. Remember to end your
                command with '&' so the commands are run simultaneously 
                [%(default)s].""")
    program_parser.add_argument("query", nargs="+", metavar="FILE",
        default="",
        help="Query file(s).")

    if len(argv)<2:
        parser.print_help()
        exit()

    options = parser.parse_args()
    return options



def generate_sbatch_scripts(options):
    """Generate sbatch scripts.
    """

    while options.query:
        query_files_in_script = []
        sbatch_script = ["#!/usr/bin/env bash",
            "#SBATCH -N {N}".format(N=options.N),
            "#SBATCH -p {p}".format(p=options.p),
            "#SBATCH -A {A}".format(A=options.A),
            "#SBATCH -t {t}".format(t=options.t),
            "#SBATCH -J {J}".format(J=options.J)]
        if options.C:
            sbatch_script.append("#SBATCH -C {C}".format(C=options.C))
        
        for query_file in options.query[0:options.stack]:
            options.query.pop(0)
            query_files_in_script.append(query_file)
            call = options.call.format(query=query_file)
            sbatch_script.append(call)

        yield "\n".join(sbatch_script), query_files_in_script



def call_sbatch(sbatch_script):
    """Run sbatch in a subprocess.
    """

    sbatch = Popen("sbatch", stdin=PIPE, stdout=PIPE, stderr=PIPE)
    out, err = sbatch.communicate(sbatch_script)
    if err:
        raise Exception("sbatch error: {}".format(err))



if __name__ == "__main__":
    options = parse_commandline()
    for sbatch_script, query_files in generate_sbatch_scripts(options):
        call_sbatch(sbatch_script)
        if len(query_files) > 1:
            print "Submitted stacked Slurm job for {} files: '{}'".format(len(query_files), "', '".join(query_files))
        else:
            print "Submitted Slurm job for: '{}'".format(query_files[0])
