# ase24_ETEM

This is ETEM, a compiler bug isolation method proposed in the paper "Compiler Bug Isolation via Enhanced Test Program Mutation". This repository provides the source code of ETEM, the datasets used in experiments, and the experimental results.

## File Organization and Dataset

- ./run: Source code of ETEM.

- ./mutator: Feature mutators defined by ETEM.
    - ./mutator/exefile: Executable files of feature mutators.
    - ./mutator/srcfile: Source code of feature mutators.
    - ./mutator/testFile: Compiler test suite, serving as the library of program elements inserted by add-type mutators.

- ./benchmark: Datasets used in the experiments, including 60 real bugs on GCC (based on SVN repository) and 60 real bugs on LLVM (based on GitHub repository). 
    - The overall bug list is in benchmark/[gcc/llvm]bugs_all.txt, Each line in file is like:
        ```shell
        [bug id], [buggy compiler version], [passing configuration], [failing configuration], [bug type], [install type]
        ```
        - For buggy compiler version, it is a github hashcode for llvm bugs, or a svn reversion number for gcc bugs.
        - For bug types, we only distinguish whether it was a crash bug (checkIsPass_zeroandcrush), all other categories are just hints to the user.
        
    - Each bug contains:
        - benchmark/[gcc/llvm]bugs/[bug id]/fail.c: The failing test.
        - benchmark/[gcc/llvm]bugs/[bug id]/locations: Buggy locations
     
    - The GCC part is the same as prior compiler bug isolation work (such as RecBi[https://github.com/haoyang9804/RecBi])
    - The LLVM part is newly collected by our work from LLVM's GitHub Issue page.
    - If you want to isolated your own bugs, just add a line in [gcc/llvm]bugs_all.txt and create benchmark/[gcc/llvm]bugs/[your bug id]/, fill in your failing test fail.c

- ./experimental_result: Experimental results. Within ./experimental_result/[ETEM, ODFL, RecBi, DiWi]/.../[gccbugs, llvmbugs], the results of [ETEM, ODFL, RecBi, DiWi] on [gcc, llvm] datasets are stored.
    - Data in the paper: The experimental results in the paper can be found directly in [gccbugs, llvmbugs]/eval.txt.
    - Detailed rank list: Each method's bug isolation result rank list is in [gccbugs, llvmbugs]/rankFile-[bugid].

- ./ODFL-src: Source code of ODFL. Based on their paper and the provided ODFL code for GCC, we implemented ODFL for LLVM.

- other: The source code of DiWi and RecBi is the same as that in their GitHub repository: https://github.com/JunjieChen/DiWi and https://github.com/haoyang9804/RecBi

## Setup Environment

- Linux System with GPU
- python
- torch, numpy
- cmake
- other requirments for building GCC/LLVM compilers (such as cmake and GMP/MPFR/MPC/flex/gcc-multilib)

We provide a script to automatically install those requirements.


## Usage

1. Clone this repository and set up the environment

```shell
sudo ./set-up-env.sh
```

2. Modify ./run/benchmark/[gcc/llvm]bugs_summary.txt

You can isolate the any bug in ./run/benchmark/[gcc/llvm]bugs_all.txt by pasting the corresponding line into the ./run/benchmark/[gcc/llvm]bugs_summary.txt

We already provide an example in ./run/benchmark/[gcc/llvm]bugs_summary.txt

3. Run ETEM

```shell
cd run
sudo python3 ./[gcc/llvm]-setup.py # Setup folder, install compilers, and run ETEM step 1 (Optimization Configuration Simplification)
sudo python3 ./[gcc/llvm]-run.py # Run ETEM step 2 (Test Generation)
sudo python3 ./[gcc/llvm]-get-res.py # Run ETEM step 3 (Suspicion Calculation). Get the bug isolation result rank lists, the rank list is default in ./workplace/[gcc/llvm]bugs/rankFile-[bugid]
sudo python3 ./[gcc/llvm]-eval.py # Eval ETEM and print Top-n/MFR/MAR to the shell
```

Since install compiler(each bug 30 minutes) and test generation(each bug one hour) is time consuming, we provide 5 llvm bugs' intermediate results, you can just run ./llvm-get-res.py and ./llvm-eval.py to quickly get rank lists and Top-n/MFR/MAR for those 5 bugs.
