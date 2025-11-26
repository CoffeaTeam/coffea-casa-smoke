#!/bin/bash

python make_input.py
text2workspace.py datacard.txt -o workspace.root
combine -M MultiDimFit --algo fixed --fixedPointPOIs r=0 --setParameterRanges r=0,20 -n _fit0 -d workspace.root --verbose 3
combine -M MultiDimFit --algo fixed --fixedPointPOIs r=0 --setParameters r=0 --setParameterRanges r=0,20 -n _r0fit0 -d workspace.root -t 1000 --toysFrequentist --bypassFrequentistFit
python plot_pval.py higgsCombine_fit0.MultiDimFit.mH120.root higgsCombine_r0fit0.MultiDimFit.mH120.123456.root pval_r0fit0.png


