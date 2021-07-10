# Stegowav

A project exploring WAV-steganography (hiding information in the byte data of a .wav file). 
It allows encoding text information in a .wav file either via a CLI interface or as a 
Python library. 

![StegoWav-Logo](logo.png)

# Usage

## Installation

```
git clone https://github.com/robert461/cyber-security
pip3 install -r requirements.txt
```

## CLI

List all commands:

```
$ ./stegowav.py --help
positional arguments:
  input                 input file path

optional arguments:
  -h, --help              show this help message and exit
  -e, --encode ENCODE     encode given text message into wav file
  -d, --decode            decode a text message from wav file if possible
  -o, --output OUTPUT     output file path to be written to
  --overwrite             if the file specified as output should be overwritten
  -t, --encryption_type ENCRYPTION_TYPE
                          encryption type as number to use (0: NONE, 1: FERNET, 2: AES, 3: RSA). 
  -r, --redundant_bits REDUNDANT_BITS
                          number of redundant bits for hamming code
  -l, --lsb LSB           number of least significant bits to use while encoding
  -f, --fill              fill entire file by repeating data
  -s, --spectrogram       display a spectrogram of the given file
  -p, --play              play the file (if -e provided, it will play after encoding, to hear the noise)
```

For example to encode the message `My secret!` in a file called `audio.wav`:

```
$ ./stegowav.py audio.wav --encode "My secret!" --output audio_with_secret.wav
```

Some example 1 second .wav files are provided with keywords which can be used for 
testing: `sine`, `square`, `sawtooth` and `hello`. So the above command can use `hello` like this, instead of
`audio.wav` if you do not have a wav file ready:

```
$ ./stegowav.py hello --encode "My secret!" --output audio_with_secret.wav
```

To decode the message from the file add the `--decode` flag:

```
$ ./stegowav.py audio_with_secret.wav --decode
Decoded message (len=10):
My secret!
```

To compare how the audio has changed you can add a `--play` flag, if combined with the `--encode` flag
it will play the audio file after encoding. Alternatively, a spectrogram can be created with a before
and after. For example, here the file is filled with repeating the letter `a` (`--fill` flag). 
By doing this a very clear line can be seen at 12 kHz:

```
$ ./stegowav.py hello --encode a --fill --spectrogram --lsb 1
```

![](media/hello_spectrogram.png)

This is clearly audible. To avoid such an issue, encryption can be used by adding the `--encryption-type 2` 
flag to randomize the data (1: FERNET, 2: AES, 3: RSA, AES is recommended). 

To get an impression of the audibility of encoded messages the degradation_eval.py script located 
in the evaluation folder can be executed. 

```
$ ./evaluation/degredation_eval.py
```

This script generates a test case for each of the files located in audio/1_min_files and tasks the 
user to choose in which file(s) he detects audible degradation. The created test reports are saved 
in evaluation/eval_reports/.


All generated evaluation reports can be analyzed by executing eval_report_analysis.py located in 
the evaluation directory. 

```
$ ./evaluation/eval_report_analysis.py
```

This creates graphs for each of the used samples, which option the users 
chose for a specific sample, and aggregates if the user was right or wrong with his decision.



## As a library

Basics:
```python
from wav_steganography.wav_file import WAVFile

wav_file = WAVFile("wav_file_path.wav")
wav_file.encode("My secret message")
wav_file.decode()  # "My secret message"
```

Encode takes mostly the same parameters as the CLI above, here the default parameters are shown. 
See the CLI section above for an explanation for each one.

```python
from wav_steganography.wav_file import WAVFile
from security.encryption_provider import EncryptionProvider
from security.enums.encryption_type import EncryptionType

wav_file = WAVFile("wav_file_path.wav")
wav_file.encode(
    "My secret message",
    least_significant_bits=2,
    redundant_bits=0,
    every_nth_byte=1,
    encryptor=EncryptionProvider.get_encryptor(EncryptionType.NONE),  # e.g. for AES: EncryptionType.AES
    repeat_data=False,
)
# To display the spectrogram
wav_file.spectrogram()

# Plays the sound
wav_file.play()

# Writes the possibly encoded wav_file to the given path
wav_file.write("encoded_wav_file_path.wav")
```


# About
This is the repository for the Cyber-Security project of group 3.


