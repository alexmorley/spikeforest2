# Full analysis (for the website)

Here we provide instructions for running the SpikeForest analysis from start to finish.

## Step 0. Configure security tokens to connect to the SpikeForest storage system (kbucket)
You need to add two key files containing security tokens. Contact Jeremy Magland to obtain tokens.
- Create a file `~/.mountaintools/kachery_tokens`
  - Add a line `spikeforest.kbucket upload XXXX`
  - Add a line `spikeforest.kbucket download YYYY`
  - Add a line `spikeforest.public upload XXXX`
  
- Create a file `~/.mountaintools/pairio_tokens`
  - Add a line `spikeforest XXXXXX`


## Step 1. Prepare the studies and recordings

Raw data for the SpikeForest website is hosted on a kbucket share. Scripts for assembling study and recording information into JSON objects are found in the `working/prepare_recordings` directory.

For example, to prepare the recordings for the visapy_synth study set, do the following:

```
cd working/prepare_recordings
./prepare_visapy_synth_recordings.py
```

If you have proper authorization, this will save the information to:

`key://pairio/spikeforest/spikeforest_recording_group.visapy_synth.json`

You can then view these recordings (from any computer) using ForestView

```
forestview key://pairio/spikeforest/spikeforest_recording_group.visapy_synth.json
```

To prepare all, run `./prepare_all.sh`

## Step 2. Run the main analysis

The SpikeForest processing is split into multiple `analysis.*.json` files found in the `working/main_analysis` directory. These files specify the input files (recordings prepared above), the spike sorters and parameters to run, compute resources to use, and where to put the output. For example, to run the visapy_synth analysis (authorization is required):

```
cd working/main_analysis
./spikeforest_analysis analysis.visapy_synth.json
```

If successful, the results of this analysis can be viewed (from any computer) using ForestView:

```
forestview key://pairio/spikeforest/spikeforest_analysis_results.visapy_synth.json
```

To run all, see the `run_all_*.sh` scripts.

## Step 3. Assemble data for the website

Scripts for preparing the data for the website are found in the `working/website` directory. To prepare data prior to loading into the website's database, run the following script after removing the website_data directory:

```
cd working/website
./do_assemble_website_data.sh
```

It is also possible to assemble only a portion of the data. See the `--help` for the `assemble_website_data.py` script.

## Step 4. Load data into website database

In order to load data into the website database, you will need to clone the [spike-front](https://github.com/flatironinstitute/spike-front) repo and follow the installation instructions. In order to utilize the convenience script below, you should place the `spike-front` directory adjacenty to the `spikeforest` directory.

To load the data into a local (development) database, you should install mongodb locally, and then run the following:

```
cd working/website
./load_data_into_local_database.sh website_data
```

where `website_data` contains the .json files created in the previous step.

You can the launch a local development version of the website via:

```
cd spike-front
DATBASE=mongodb://localhost:27017/spikefront yarn dev
```

Similarly, to upload the the data to the remote database, you can run the following command after setting up the proper admin tokens:

```
cd working/website
./load_data_into_remote_database.sh website_data
```