import pathlib
import random
import csv
from datetime import datetime
from playsound import playsound

AUDIO_FILES_DIRECTORY_NAME = 'audio/evaluation_samples'
TEST_REPORTS_DIRECTORY_NAME = 'eval_reports'
TEST_REPORT_FILE_STRING = 'eval_report_'


def process_examples():
    print(audio_file_path)
    for audio_example_pair in audio_file_path.glob('*'):
        print(f'\nNow testing example at {audio_example_pair}')
        process_example_pair(audio_example_pair)


def process_example_pair(audio_example_pair):
    audio_sample_list = []
    for audio_example in audio_example_pair.glob('*'):
        print(audio_example)
        modified = "modified" in str(audio_example)
        audio_sample_list.append((audio_example, modified))

    # randomize item order in list
    randomized_sample_list = random.sample(audio_sample_list, len(audio_sample_list))
    play_sounds(randomized_sample_list)
    process_user_input(randomized_sample_list)


def play_sounds(randomized_sample_list):
    for iteration, (sample, modified) in enumerate(randomized_sample_list):
        print(f'Now playing sample {iteration + 1}')
        playsound(str(sample))


def process_user_input(randomized_sample_list):
    choice = input('Which audio file shows degradation? File 1(1), file 2(2), both(b) or none(n)? If you want to '
                   'repeat the audio playback press (r)')
    if choice == '1':
        append_test_report(randomized_sample_list, "1")
        print('You chose file 1.')
    elif choice == '2':
        print('You chose file 2.')
        append_test_report(randomized_sample_list, "2")
    elif choice == 'b':
        print('You detected audio degradation in both files.')
        append_test_report(randomized_sample_list, "b")
    elif choice == 'n':
        print('You were not able to detect any audio degradation.')
        append_test_report(randomized_sample_list, "n")
    elif choice == 'r':
        print('Repeating examples...')
        play_sounds(randomized_sample_list)
        process_user_input(randomized_sample_list)
    else:
        print('Undefined command.')
        process_user_input(randomized_sample_list)


def init_test_report():
    time_now = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
    file = open(test_report_path.joinpath(TEST_REPORT_FILE_STRING + time_now + '.csv'), 'w', newline='')
    csv_writer = csv.writer(file, delimiter=';')
    csv_writer.writerow(['Example Name', 'File 1 modified', 'File 2 modified', 'User choice', 'Test result'])
    return csv_writer


def append_test_report(randomized_sample_list, user_choice):
    example_name = randomized_sample_list[0][0].parents[0].name
    file_1_modified = randomized_sample_list[0][1]
    file_2_modified = randomized_sample_list[1][1]

    if (user_choice == '1' and file_1_modified) or \
            (user_choice == '2' and file_2_modified) or \
            (user_choice == 'b' and file_1_modified and file_2_modified) or \
            (user_choice == 'n' and not file_1_modified and not file_2_modified):
        test_result = True
    else:
        test_result = False

    test_report.writerow([example_name, file_1_modified, file_2_modified, user_choice, test_result])


audio_file_path = pathlib.Path(__file__).absolute().parents[1].joinpath(AUDIO_FILES_DIRECTORY_NAME)
test_report_path = pathlib.Path(__file__).absolute().parent.joinpath(TEST_REPORTS_DIRECTORY_NAME)
test_report_path.mkdir(parents=True, exist_ok=True)
test_report = init_test_report()
process_examples()
