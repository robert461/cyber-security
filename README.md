# Stegowav

A project exploring WAV-steganography (hiding information in the byte data of a .wav file). 
It allows encoding text information in a .wav file either via a CLI interface or as a 
Python library. 

![StegoWav-Logo](logo.png)

# Usage

## CLI

List all commands:

`./stegowav.py -h`

## As a library

Basics:
```python
from wav_steganography.wav_file import WAVFile

wav_file = WAVFile("wav_file_path.wav")
wav_file.encode("My secret message")
wav_file.decode()  # "My secret message"
```

```python
from wav_steganography.wav_file import WAVFile
from security.encryption_provider import EncryptionProvider
from security.enums.encryption_type import EncryptionType

EncryptionProvider.get_encryptor(EncryptionType.AES)
wav_file = WAVFile("wav_file_path.wav")
wav_file.encode("My secret message", least_significant_bits=4, redundant_bits=16)
wav_file.decode()  # "My secret message"
```


# About
This is the repository for the Cyber-Security project of group 3.


