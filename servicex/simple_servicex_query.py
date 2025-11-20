from servicex import query, dataset, deliver
# we need to unset BEARER_TOKEN_FILE environment variable for now
import os
del os.environ['BEARER_TOKEN_FILE']

spec = {
    "Sample": [
        {
            "Name": "UprootRaw_Dictcms1",
            "Dataset": dataset.FileList(
                [
                    #"root://xcache.cmsaf-dev.flatiron.hollandhpc.org//store/mc/RunIISummer20UL18NanoAODv9/DYJetsToLL_M-50_HT-100to200_TuneCP5_PSweights_13TeV-madgraphMLM-pythia8/NANOAODSIM/106X_upgrade2018_realistic_v16_L1v1-v1/70000/92DF66B4-2A9E-4A49-8B43-A1B2F4B24379.root",  # noqa: E501
                    "root://cmsxrootd.fnal.gov//store/mc/RunIISummer20UL18NanoAODv9/DYJetsToLL_M-50_HT-100to200_TuneCP5_PSweights_13TeV-madgraphMLM-pythia8/NANOAODSIM/106X_upgrade2018_realistic_v16_L1v1-v1/70000/92DF66B4-2A9E-4A49-8B43-A1B2F4B24379.root"
                ]
            ),
            "Query": query.UprootRaw(
                [
                    {
                        "treename": "Events",
                        "filter_name": "MET_pt",
                    }
                ]
            ),
        }
    ]
}

print(f"Files: {deliver(spec)}")
