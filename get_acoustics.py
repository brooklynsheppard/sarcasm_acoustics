import parselmouth
from scipy.special import eval_legendre
import scipy.stats
import cmudict
import numpy as np
import os
import math
import statistics
import tgt

# Load cmudict. Used to get number of syllables and word rate
pron_dict = cmudict.dict()

def to_sound(wav_path):
    """
    Convert wav file to Praat sound object
    :param wav_path: full path to wav file
    :return: wav file as sound object
    """
    return parselmouth.Sound(wav_path)

# Get intensity and pitch contours
def get_contours(sound, start_time, end_time, keep_zeros):
    """
    Extract F0 and intensity contours from wav file, within a given time frame
    :param wav_path: Full path to a single wav file
    :param keep_zeros: True if you want to keep zeros of F0 contour (i.e., keep spaces without an F0 measurement)
    :return: the F0 and intensity contours as lists
    """
    sound_interval = sound.extract_part(from_time=start_time, to_time=end_time)
    try: # This deals with if the extracted part is shorter than the window length
        pitch_contour = sound_interval.to_pitch().selected_array['frequency']
        intensity_contour = sound_interval.to_intensity().values[0]
    except parselmouth.PraatError:
        intensity_contour = [np.nan, np.nan] # this is of length 2 just to avoid errors from statistics functions
        pitch_contour = [np.nan, np.nan]
    if not keep_zeros:
        pitch_contour = [i for i in pitch_contour if i !=0]

    if len(pitch_contour) < 2:
        pitch_contour = [np.nan, np.nan]
    if len(intensity_contour) <2:
        intensity_contour = [np.nan, np.nan]

    return pitch_contour, intensity_contour

# Convert hz to semitones
def f2st(f0_contour,reference_f0):
    """
    Convert Hz to Semitones. Used for Speaker Normalization
    :param f0_contour: list of F0 values
    :param reference_f0: In the case of speaker normalization, this is the mean F0 of the speaker
    :return: List of F0 values in semitones
    """
    return [12*math.log(i/reference_f0,2) for i in f0_contour]

# Convert db to z-scores
def norm_intensity(intensity_contour):
    """
    Conver dB to z-scores. Used for speaker normalization
    :param intensity_contour: Intensity values in dB
    :return: intensity contours in z-scores
    """
    return scipy.stats.zscore(intensity_contour)

def get_mean(contour):
    return statistics.mean(contour)

def get_range(contour):
    return max(contour) - min(contour)

def get_sd(contour):
    return statistics.stdev(contour)

# Speaking Rate (as syllables per second- use cmudict to get canonical number of syllables of each word)
def get_speak_rate(word, start, end):
    """
    Get speaking rate as syllables per second
    :param word: String, all lowercase word. Must be in CMU dict
    :param start: start time of the word
    :param end: end time of the word
    :return: float of speaking rate in sylls/sec
    """
    try:
        phones = pron_dict[word][0]  # grab first pronunciation of the word, this is a simplifying assumption
    except IndexError:
        return np.nan, np.nan
    dur = end-start
    word_syll_count = sum([1 for phone in phones if phone[-1].isdigit()]) # count all syllables in a single word
    rate = word_syll_count/dur
    return float(rate)

def get_times_from_textgrid(path_to_textgrid, tier_name):
    """
    Extract bounadary times for each interval and its annotation
    :param path_to_textgrid: full path to the textgrid file
    :param tier_name: the tier you want to extract annotations from
    :return: List of lists: each list if os the form [annotation, start_time, end_time] for each interval in the textgrid
    """
    textgrid = tgt.io.read_textgrid(path_to_textgrid)
    tier = textgrid.get_tier_by_name(tier_name)
    intervals = []
    for interval in tier:
        curr_interval = []
        curr_interval.append(interval.text)
        curr_interval.append(interval.start_time)
        curr_interval.append(interval.end_time)
        intervals.append(curr_interval)
    return intervals

# Use Legendre polynomials to model pitch and intensity
def get_legendres(contour, n=3): # This operates at word-level. Get a legendre for each word
    """
    Perform Legendre poplynomial expansion on a contour of any acoustic measure
    :param contour: A list of values representing the contour (e.g., pitch or intensity) you want Legendre coefficients for
    :param n: order of legendre polynomials you want coefficients for
    :return: List of n legendre coefficients (i.e. list[0] = 0th legendre coefficient)
    """
    all_legendres = []

    num_xs_contour = len(contour)
    x_vals_contour = np.linspace(-1, 1, num_xs_contour)
    contour_sampled_legendres = [eval_legendre(i, x_vals_contour) for i in range(n)]
    fitted_contours = [2*np.dot(contour, contour_sampled_legendres[i])/num_xs_contour for i in range(len(contour_sampled_legendres))]
    all_legendres += fitted_contours
    return all_legendres

# Helper function to find specific file in a given diretory
def find_file(filename, search_path):
   for root, dir, files in os.walk(search_path):
       if filename in files:
          result=os.path.join(root, filename)
          return result

