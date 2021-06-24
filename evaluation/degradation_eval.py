import pathlib
import random
import csv
import simpleaudio as sa
from datetime import datetime


ONE_MINUTE_FILES_DIRECTORY_NAME = 'audio/1min_files'
AUDIO_FILES_DIRECTORY_NAME = 'audio/evaluation_samples'
EVAL_REPORTS_DIRECTORY_NAME = 'eval_reports'
EVAL_REPORT_FILE_STRING = 'eval_report_'


def process_examples():
    print(audio_file_path)
    for test_set in audio_file_path.glob('*'):
        for audio_example in test_set.glob('*'):
            process_example_pair(audio_example)


def process_example_pair(audio_example):
    audio_sample_list = []
    # add the modified file to the sample list
    audio_sample_list.append((audio_example, True))

    # get the corresponding unmodified file name to the modified file
    one_min_file_name = str(audio_example.name).replace('modified_', '')
    print(f'\nNow evaluating examples of {one_min_file_name}')
    # get the file path of the one minute file
    one_min_file_path = unmodified_audio_files_path.joinpath(one_min_file_name)
    print(one_min_file_path)
    # add the unmodified file to the sample list
    audio_sample_list.append((one_min_file_path, False))

    # randomize item order in list
    randomized_sample_list = random.sample(audio_sample_list, len(audio_sample_list))
    example_name = f'{audio_example.parent.name}_{one_min_file_name}'
    print(example_name)
    play_sounds(randomized_sample_list, example_name)


def play_sounds(randomized_sample_list, example_name):
    for iteration, (sample, modified) in enumerate(randomized_sample_list):
        print(f'Now playing sample {iteration + 1}')
        wave_obj = sa.WaveObject.from_wave_file(str(sample))
        play_obj = wave_obj.play()
        while play_obj.is_playing():
            if input('Press \'s\' to end playback and go to next file') == 's':
                play_obj.stop()
                play_obj.wait_done()
    process_user_evaluation(randomized_sample_list, example_name)


def process_user_evaluation(randomized_sample_list, example_name):
    choice = input('Which audio file shows degradation? File 1(1), file 2(2), both(b) or none(n)? If you want to '
                   'repeat the audio playback press (r)')
    if choice == '1':
        append_eval_report(randomized_sample_list, "1", example_name)
        print('You chose file 1.')
    elif choice == '2':
        print('You chose file 2.')
        append_eval_report(randomized_sample_list, "2", example_name)
    elif choice == 'b':
        print('You detected audio degradation in both files.')
        append_eval_report(randomized_sample_list, "b", example_name)
    elif choice == 'n':
        print('You were not able to detect any audio degradation.')
        append_eval_report(randomized_sample_list, "n", example_name)
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
    file_1_modified = randomized_sample_list[0][1]
    file_2_modified = randomized_sample_list[1][1]

    if (user_choice == '1' and file_1_modified) or \
            (user_choice == '2' and file_2_modified) or \
            (user_choice == 'b' and file_1_modified and file_2_modified) or \
            (user_choice == 'n' and not file_1_modified and not file_2_modified):
        eval_result = True
    else:
        eval_result = False
    eval_report.writerow([example_name, file_1_modified, file_2_modified, user_choice, eval_result])


audio_file_path = pathlib.Path(__file__).absolute().parents[1].joinpath(AUDIO_FILES_DIRECTORY_NAME)
unmodified_audio_files_path = pathlib.Path(__file__).absolute().parents[1].joinpath(ONE_MINUTE_FILES_DIRECTORY_NAME)
eval_report_path = pathlib.Path(__file__).absolute().parent.joinpath(EVAL_REPORTS_DIRECTORY_NAME)
eval_report_path.mkdir(parents=True, exist_ok=True)
eval_report = init_eval_report()
process_examples()
