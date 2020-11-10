#!/bin/bash
#SBATCH -p geo,glados12,glados16
#SBATCH --ntasks=1
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --array=1-282
#SBATCH --output="outslurm/slurm-%A_%a.out"

#file=$(sed -n "${SLURM_ARRAY_TASK_ID}p" family_files.list)
file=$(sed -n "${SLURM_ARRAY_TASK_ID}p" templates.list)
echo $file

python create_events_from_detections.py $file
python templates2stream.py $file
