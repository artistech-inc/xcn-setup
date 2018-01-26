# XCN Framework Setup

Setup Scripts for XCN/EMANE Framework

## Requirements

- Ubuntu Linux 16.04 LTS

## Install

```sh
cd install_scripts
./setup_env_apt.sh
./install-emane.sh
./install-oslrd.sh
./install-docker.sh
```

Installing docker updates the current user to be in the docker group, log out and back in to have this change take effect.

## Run Simulation

For now, only the 'cnr' simulatin is published.

```sh
cd cnr
./cnr.scn
./run_bridge_fcfs.sh
```

FCFS is First-Come, First-Serve for pairing IP addresses from CNR to XCN. The `run_bridge_fcfs.sh` script will check for and download the cnr-bridge software and build if necessary. This script will also run the necessary `emane_client.sh` scripts on each node.

## End Simulation

```sh
CTRL+C to kill the running bridge processes.
./kill.sh
```

# Configuration

The number of nodes is calculated from the number of lines in the `cnr.eel` file.  This file can be auto-generated using the `generate_connected_eel.sh` script and passing in the number of nodes to configure.  This will create a fully-connected 1-hop network configuration.

```sh
./generate_connected_eel.sh 3 > cnr.eel
````
