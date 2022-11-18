import os
import librosa
import argparse
import soundfile as sf

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument("--in_path", default="./tsukuyomi_raw", required=True)
  parser.add_argument("--out_path", default="./tsukuyomi" ,required=True)

  args = parser.parse_args()

  os.makedirs(out_path, exist_ok=True)
  filenames = os.listdir(in_path)
  for filename in filenames:
      print(in_path+filename)
      y, sr = librosa.core.load(in_path+filename, sr=22050, mono=True)
      sf.write(out_path+filename, y, sr, subtype="PCM_16")
