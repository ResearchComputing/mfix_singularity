#!/bin/bash
#SBATCH --nodes 9
#SBATCH --exclusive
#SBATCH --account ucb1_summit1
#SBATCH --time 04:00:00
##SBATCH --output normal.out
##SBATCH --reservation bench-bandwidth

ml singularity/2.4.2 gcc/6.1.0

export MFIX=/app/mfix/build/mfix/mfix
export WD=/scratch/summit/holtat/hcs_80k_large_weak_scaling
export IMAGE=/scratch/summit/holtat/singularity/holtat-mfix_full:latest.simg
export MPIRUN=/projects/holtat/spack/opt/spack/linux-rhel7-x86_64/gcc-6.1.0/openmpi-2.1.2-foemyxg2vl7b3l57e7vhgqtlwggubj3a/bin/mpirun

## Formatting for output files
## Latest commit date, format: 2018-02-19 12:44:03 -0800
singularity exec $IMAGE bash -c "cd /app/mfix; git log -n 1 --pretty=format:'%ai'" > info.txt
echo '' >> info.txt
## Shortened latest commit hash, format: b119a72
singularity exec $IMAGE bash -c "cd /app/mfix; git log -n 1 --pretty=format:'%h'" >> info.txt
echo '' >> info.txt
## Nodelist
echo $SLURM_NODELIST >> info.txt
## Modules
ml 2>&1 | grep 1 >> info.txt

export DATE=$(sed '1q;d' info.txt | awk '{print $1;}')
export HASH=$(sed '2q;d' info.txt)
echo $DATE
echo $HASH
echo $SLURM_NODELIST

## Save info
cp info.txt /projects/holtat/CICD/results/hcs_80k_large_weak_scaling/metadata/${DATE}_${HASH}.txt

for dir in {np_00001,np_00008,np_00027,np_00064,np_00125,np_00216}; do

    # Make directory if needed
    mkdir -p $WD/$dir
    cd $WD/$dir
    pwd
    # Get np from dir
    np=${dir:(-5)}
    np=$((10#$np))
    $MPIRUN -np $np singularity exec $IMAGE bash -c "cd $WD/$dir; $MFIX inputs >> ${DATE}_${HASH}_${dir}"

done


## Copy results to projects
cd $WD
for dir in {np_00001,np_00008,np_00027,np_00064,np_00125,np_00216}; do
    cp ${dir}/${DATE}_${HASH}* /projects/holtat/CICD/results/hcs_80k_large_weak_scaling/${dir}
done

#for ii in np_*; do cp -v $ii/2018* /projects/holtat/CICD/results/weak_scaling_small/${ii}/; done