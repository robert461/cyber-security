import pathlib
import random
import csv
import os
from simpleaudio import WaveObject
from datetime import datetime


ONE_MINUTE_FILES_DIRECTORY_NAME = 'audio/1min_files'
AUDIO_FILES_DIRECTORY_NAME = 'audio/evaluation_samples'
EVAL_REPORTS_DIRECTORY_NAME = 'eval_reports'
EVAL_REPORT_FILE_STRING = 'eval_report_'


def process_examples():
    for one_min_sample in unmodified_audio_files_path.glob('*'):
        audio_sample_list = select_rand_test_variant(one_min_sample)
        process_example_pair(audio_sample_list, one_min_sample.name)


def select_rand_test_variant(one_min_sample):
    audio_sample_list = []
    test_variant = random.randint(0, 19)

    # unmodified/unmodified
    if test_variant == 0:
        for i in range(2):
            audio_sample_list.append((one_min_sample, 0))

    # modified/modified
    elif test_variant == 1:
        for i in range(2):
            degr_directory = random.choice(os.listdir(audio_file_path))
            sample = get_audio_file_by_example_name(one_min_sample.name, degr_directory)
            audio_sample_list.append((sample, sample.parent.name.replace('lsb_', '')))

    # unmodified/modified
    else:
        audio_sample_list.append((one_min_sample, 0))
        degr_directory = random.choice(os.listdir(audio_file_path))
        sample = get_audio_file_by_example_name(one_min_sample.name, degr_directory)
        audio_sample_list.append((sample, sample.parent.name.replace('lsb_', '')))
    return audio_sample_list


def get_audio_file_by_example_name(name, directory):
    directory = audio_file_path.joinpath(directory)
    for file in directory.glob('*'):
        if name in file.name:
            return file


def process_example_pair(audio_sample_list, example_name):
    # randomize item order in list
    randomized_sample_list = random.sample(audio_sample_list, len(audio_sample_list))
    print(f'Testing sample {example_name}')
    play_sounds(randomized_sample_list, example_name)


def play_sounds(randomized_sample_list, example_name):
    for iteration, (sample, modified) in enumerate(randomized_sample_list):
        print(f'Playing sample {iteration + 1}')
        wave_obj = WaveObject.from_wave_file(str(sample))
        play_obj = wave_obj.play()
        while play_obj.is_playing():
            if input('Type \'s\' to end playback and go to next file') == 's':
                play_obj.stop()
                play_obj.wait_done()
    process_user_evaluation(randomized_sample_list, example_name)


def process_user_evaluation(randomized_sample_list, example_name):
    choice = input('Which audio file showed degradation? File 1(1), file 2(2), both(b) or none(n)? If you want to '
                   'repeat the audio playback press (r)')
    if choice == '1':
        append_eval_report(randomized_sample_list, "First", example_name)
        print('You chose file 1.')
    elif choice == '2':
        print('You chose file 2.')
        append_eval_report(randomized_sample_list, "Second", example_name)
    elif choice == 'b':
        print('You detected audio degradation in both files.')
        append_eval_report(randomized_sample_list, "Both", example_name)
    elif choice == 'n':
        print('You were not able to detect any audio degradation.')
        append_eval_report(randomized_sample_list, "None", example_name)
    elif choice == 'r':
        print('Repeating examples...')
        play_sounds(randomized_sample_list, example_name)
    else:
        print('Undefined command.')
        process_user_evaluation(randomized_sample_list, example_name)


def init_eval_report():
    time_now = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
    file = open(eval_report_path.joinpath(EVAL_REPORT_FILE_STRING + time_now + '.csv'), 'w', newline='')
    csv_writer = csv.writer(file, delimiter=';')
    csv_writer.writerow(['Example Name', 'File 1 modified', 'File 2 modified', 'User choice', 'Eval result'])
    return csv_writer


def append_eval_report(randomized_sample_list, user_choice, example_name):
    file_1_modified = True if randomized_sample_list[0][1] != 0 else False
    file_2_modified = True if randomized_sample_list[1][1] != 0 else False

    if (user_choice == 'First' and file_1_modified) or \
            (user_choice == 'Second' and file_2_modified) or \
            (user_choice == 'Both' and file_1_modified and file_2_modified) or \
            (user_choice == 'None' and not file_1_modified and not file_2_modified):
        eval_result = True
    else:
        eval_result = False
    print(eval_result)
    eval_report.writerow([example_name, file_1_modified, file_2_modified, user_choice, eval_result])


audio_file_path = pathlib.Path(__file__).absolute().parents[1].joinpath(AUDIO_FILES_DIRECTORY_NAME)
unmodified_audio_files_path = pathlib.Path(__file__).absolute().parents[1].joinpath(ONE_MINUTE_FILES_DIRECTORY_NAME)
eval_report_path = pathlib.Path(__file__).absolute().parent.joinpath(EVAL_REPORTS_DIRECTORY_NAME)
eval_report_path.mkdir(parents=True, exist_ok=True)
eval_report = init_eval_report()
process_examples()
