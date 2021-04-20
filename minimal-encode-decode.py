import wave

# Read file
in_file = wave.open('./audio/sine_mono_110hz.wav', 'rb')
frames = [in_file.readframes(1) for _ in range(in_file.getnframes())]

# Encode message
message = b'hello world'
m = ''.join(map(lambda c: format(c, '#010b')[2:], message))
print(f"Encoding message: {message} => {m}")
frames[:len(m)] = [bytes([b1^int(lsb)^b1&1, b2]) for lsb, (b1, b2) in zip(m, frames)]

# Save file
out_file = wave.open('encoded.wav', 'wb')
out_file.setparams(in_file.getparams())
out_file.writeframes(b''.join(frames))

# Decode
res = wave.open('encoded.wav', 'rb')
dec = [sum((res.readframes(1)[0]&1) << (7-c) for c in range(8)) for _ in range(len(message))]
print(f"Decoded message: {''.join(map(chr, dec))}")
