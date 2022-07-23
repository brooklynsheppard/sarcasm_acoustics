# Extract Basic Acoustics from Wav Files

This repository contains code to automatically extract some simple F0 and intensity 
acoustic measures as well as approximate F0 and intensity contours using Legendre 
polynomial expansion.

##Dependencies:
```
numpy==1.21.3
pandas==1.4.3
praat-parselmouth==0.4.1
scipy==1.8.1
cmudict==1.0.2
tgt==1.4.4
```


##Example Usage:
```
python main.py --data_dir $PATH_TO_DATA_DIRECTORY --out_path $PATH_TO_OUTFILE
```
where the data directory is a directory of wav and their associated TextGrid files
and the outfile is a csv file.

##Options:
`--tier_name`: specify the name of the tier from the textgrids. Default is 'words'

`--legendre_order`: specify to what order you want to extract Legendre coefficients. Default is 3.

`--no-keep_zeros`: add this argument to ignore values of zero for pitch measurements

`--no-legendre_only`: add this argument to calculate all statistics, not just legendres





