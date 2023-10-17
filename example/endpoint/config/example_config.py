from parsl.addresses import address_by_interface
from parsl.launchers import SrunLauncher
from parsl.providers import SlurmProvider

from globus_compute_endpoint.endpoint.utils.config import Config
from globus_compute_endpoint.executors import HighThroughputExecutor


user_opts = {
    'delta': {
        'worker_init': 'conda activate custom-image-builder-py-3.9',
        'scheduler_options': '#SBATCH --account=bbmi-delta-cpu',
    }
}

config = Config(
    executors=[
        HighThroughputExecutor(
            max_workers_per_node=10,
            address=address_by_interface('hsn0'),
            scheduler_mode='soft',
            worker_mode='singularity_reuse',
            container_type='singularity',
            container_cmd_options="",
            provider=SlurmProvider(
                partition='cpu',
                launcher=SrunLauncher(),

                # string to prepend to #SBATCH blocks in the submit
                # script to the scheduler eg: '#SBATCH --constraint=knl,quad,cache'
                scheduler_options=user_opts['delta']['scheduler_options'],
                worker_init=user_opts['delta']['worker_init'],
                # Command to be run before starting a worker, such as:
                # 'module load Anaconda; source activate parsl_env'.

                # Scale between 0-1 blocks with 2 nodes per block
                nodes_per_block=1,
                init_blocks=0,
                min_blocks=0,
                max_blocks=1,

                # Hold blocks for 30 minutes
                walltime='00:30:00'
            ),
        )
    ],
)
