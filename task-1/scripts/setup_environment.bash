

"${SHELL}" <(curl -L micro.mamba.pm/install.sh)

micromamba create -n oscars-pan-finder-task-1 -f oscars-pan-finder-environment.yaml -c conda-forge

sudo apt install -y jq ffmpeg libavif13 libgstreamer-plugins-bad1.0-0

micromamba install playwright-python

micromamba run -n oscars-pan-finder-task-1 playwright install

