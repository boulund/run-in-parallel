# README #

Download this script and run it on e.g. C3SE Glenn to start running simple
command lines in parallel on several nodes in a simple way.

* [Research group wiki](http://bioinformatics.math.chalmers.se/wiki) 

## Overview of features ##

 * Run single command on one node per file:
 ``` run_in_parallel.py --call 'echo {query}' file1 file2 file3 ```. 
 This submits three batch jobs via Slurm.

 * Stack single command for N files per node:
 ``` run_in_parallel.py --call 'echo {query}&' --stack 2 file1 file2 file3 ```. 
 This submits two batch jobs via Slurm, where the first runs the command on
 file1 and file2 simultaneously, and the second node only runs on file3. 

 * Run composite command on one node per file:
 ``` run_in_parallel.py --call 'cp ~/database.fasta $TMPDIR; cd $TMPDIR; heavy_processing {query} -out={query}.output; cp {query}.output ~/results' file1 file2 file3 ```. 
 This copies a big database to the $TMPDIR on each one, then changes dir to the
 $TMPDIR and runs heavy_processing in the $TMPDIR, then copies the results back
 to the user home dir.

Note that the script is stupid, makes a lot of assumptions and has no error
correction---so make sure you spell the command correctly. Also note that this
script does not help you optimally use the resources of the node. You are
responsible for making sure you use the nodes to their full capacity.

## Quick-start instructions ##
Run the script and give any number of files as command line arguments. The call
should be enclosed in single quotes. Example:

```
#!bash
$ ls sequence_files
reads1.fasta reads2.fasta reads3.fasta something_else.txt annotation.gff
$ run_in_parallel.py --call 'blat ~/databases/bacterial_genomes.fasta {query} -out=blast8 {query}.blast8' sequence_files/*.fasta
Submitted Slurm job for 'reads1.fasta'
Submitted Slurm job for 'reads2.fasta'
Submitted Slurm job for 'reads3.fasta'
(... wait for jobs to be allocated and run)
$ ls 
sequence_files reads1.fasta.blast8 reads2.fasta.blast8 reads3.fasta.blast8 
slurm-6132412.out slurm-6132413.out slurm-6132414.out 
```

There is command line help available. Run without arguments, -h or --help to
display the help text. Remember to set the -p and -A flags (Slurm partition and
account) to whatever is relevant for your application. Always specify a
reasonable wall clock time (-t), so that your job is allocated as soon as
possible.


## Long instructions for use on C3SE Glenn ##

### Load a Python module in the C3SE environment ###
You need to have the Python interpreter loaded to run the script. I prefer to
use the clean Python module with virtualenv that is available:
```
#!bash
$ module load virtualenv/1.11.4
```

### Get the script ###
Clone the repository and symlink the run_in_parallel.py script in your ~/bin
folder:
```
#!bash
$ hg clone https://bitbucket.org/chalmersmathbioinformatics/run_in_parallel
$ ln -s ./run_in_parallel/run_in_parallel.py ~/bin
```

### Run things in parallel! ###
Call the script from wherever (since you have a symlink in ~/bin) and give it
many files as command line arguments. The call is a simple hello world in this
example.
```
#!bash
$ ls files_to_run
job1 job2 job3
$ run_in_parallel.py --call 'echo "Hello from {query}!"' files_to_run/*
Submitted Slurm job for 'job1'
Submitted Slurm job for 'job2'
Submitted Slurm job for 'job3'
```

### Check the results ###
Most of the time you probably write the results to some files somewhere. Here
we just see the printout in the stdout from the nodes which are available in
the call directory after job completion.
```
#!bash
$ cat slurm*.out 
Hello from job2!
Hello from job1!
Hello from job3!
```