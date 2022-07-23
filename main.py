import argparse
import os
import pandas as pd
import get_acoustics


parser = argparse.ArgumentParser()
parser.add_argument('--data_dir')
parser.add_argument('--out_path')
parser.add_argument('--tier_name', default='words')
parser.add_argument('--legendre_order', default=int(3))

# These booleans default to true. To make false, just add "no-" preceding the argument (e.g., --no-legendre_only)
parser.add_argument('--keep_zeros', action=argparse.BooleanOptionalAction)
parser.add_argument('--legendre_only', action=argparse.BooleanOptionalAction)


args = parser.parse_args()


def main():
    filename_list = []
    word_list = []
    pitch_legendre_0_list = []
    pitch_legendre_1_list = []
    pitch_legendre_2_list = []
    intensity_legendre_0_list = []
    intensity_legendre_1_list = []
    intensity_legendre_2_list = []

    mean_pitch_list = []
    pitch_range_list = []
    pitch_sd_list = []
    mean_intensity_list = []
    intensity_range_list =[]
    speak_rate_list = []

    for root, dirs, files in os.walk(args.data_dir):
        for file in files:
            filename = file.split('.')[0]
            filetype = file.split('.')[1]

            if filetype =='TextGrid': # This is so that it only calculates statistics once per Textgrid/wav pair
                # Get full path to textgrid and wav file
                tgt_path = os.path.join(root,filename+'.TextGrid')
                wav_path = os.path.join(root,filename+'.wav')
                print(filename)
                # Get word boundaries from textgrid
                boundaries = get_acoustics.get_times_from_textgrid(tgt_path,args.tier_name)

                # Load wav file
                sound = get_acoustics.to_sound(wav_path)

                # Go thru boundaries from textgrid file
                for interval in boundaries:
                    word = interval[0]
                    start_time = interval[1]
                    end_time = interval[2]
                    pitch_contour, intensity_contour = get_acoustics.get_contours(sound, start_time, end_time, args.keep_zeros)
                    filename_list.append(filename)
                    word_list.append(word)

                    # Get legendres
                    intensity_legendres = get_acoustics.get_legendres(intensity_contour)
                    pitch_legendres = get_acoustics.get_legendres(pitch_contour)
                    pitch_legendre_0_list.append(pitch_legendres[0])
                    pitch_legendre_1_list.append(pitch_legendres[1])
                    pitch_legendre_2_list.append(pitch_legendres[2])
                    intensity_legendre_0_list.append(intensity_legendres[0])
                    intensity_legendre_1_list.append(intensity_legendres[1])
                    intensity_legendre_2_list.append(intensity_legendres[2])

                    # Get rest of acoustics if not legendre only
                    if args.legendre_only == False:
                        mean_pitch_list.append(get_acoustics.get_mean(pitch_contour))
                        pitch_range_list.append(get_acoustics.get_range(pitch_contour))
                        pitch_sd_list.append(get_acoustics.get_sd(pitch_contour))
                        mean_intensity_list.append(get_acoustics.get_mean(intensity_contour))
                        intensity_range_list.append(get_acoustics.get_range(intensity_contour))
                        speak_rate_list.append(get_acoustics.get_speak_rate(word, start_time, end_time))


    if args.legendre_only:
        data_dict = {'filename': filename_list,
                     'word': word_list,
                     'f0_legendre_0':pitch_legendre_0_list,
                     'f0_legendre_1':pitch_legendre_1_list,
                     'f0_legendre_2':pitch_legendre_2_list,
                     'intensity_legendre_0': intensity_legendre_0_list,
                     'intensity_legendre_1': intensity_legendre_1_list,
                     'intensity_legendre_2': intensity_legendre_2_list}

    else:
        data_dict = {'filename': filename_list,
                     'word': word_list,
                     'f0_legendre_0': pitch_legendre_0_list,
                     'f0_legendre_1': pitch_legendre_1_list,
                     'f0_legendre_2': pitch_legendre_2_list,
                     'intensity_legendre_0': intensity_legendre_0_list,
                     'intensity_legendre_1': intensity_legendre_1_list,
                     'intensity_legendre_2': intensity_legendre_2_list,
                     'mean_pitch': mean_pitch_list,
                     'pitch_range': pitch_range_list,
                     'pitch_sd': pitch_sd_list,
                     'mean_intensity':mean_intensity_list,
                     'intensity_range': intensity_range_list,
                     'speak_rate': speak_rate_list}

    df = pd.DataFrame.from_dict(data_dict)
    df.to_csv(args.out_path)



if __name__ == '__main__':
    main()







