from pathlib import Path

from wav_steganography.wav_file import WAVFile


def test_loading_and_plotting_wav_file():
    audio_path = Path("audio")
    for audio_file in audio_path.glob("*.wav"):
        print(f"Loading audio file {audio_file}")
        file = WAVFile(audio_file)
        plots_path = audio_path / 'plots'
        plots_path.mkdir(exist_ok=True)
        file.plot(filename=plots_path / audio_file.name.replace(".wav", ".png"))
