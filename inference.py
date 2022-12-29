import torch
import commons
import utils

from models import SynthesizerTrn
from text.symbols import symbols
from text import text_to_sequence

import numpy as np
from scipy.io.wavfile import write
from target_phonemizer import AccentuatedPhonemizer

speakers = {'ermil': 0, 'malchhik': 1, 'omazh': 2, 'andrey': 3, 'vasiliy': 4, 'irina': 5, 'marusa': 6, 'valeriy': 7,
            'filipp': 8, 'oksana': 9, 'regina': 10, 'nikita': 11, 'zahar': 12, 'jane': 13, 'roman': 14,
            'mishka': 15, 'saveliy': 16, 'alena': 17, 'zhenya': 18, 'elena': 19, 'tatyana2': 20, 'tatyana1': 21}


def get_text(text, hps):
    text_norm = text_to_sequence(text, hps.data.text_cleaners)
    if hps.data.add_blank:
        text_norm = commons.intersperse(text_norm, 0)
    text_norm = torch.LongTensor(text_norm)
    return text_norm


hps = utils.get_hparams_from_file("configs/ljs_mb_istft_vits.json")


net_g = SynthesizerTrn(
    len(symbols),
    hps.data.filter_length // 2 + 1,
    hps.train.segment_size // hps.data.hop_length,
    **hps.model).cuda()
_ = net_g.eval()

_ = utils.load_checkpoint("logs/ljs_mb_istft_vits_multi/G_670000.pth", net_g, None)


phonemizer = AccentuatedPhonemizer.from_config()

text = 'Привет'

phoneme = get_text(phonemizer.process(text), hps)

speaker: int = speakers.get('ermil')
noise_scale: float = .667
noise_scale_w: float = 0.8
length_scale: float = 1

with torch.no_grad():
    x = phoneme.cuda().unsqueeze(0)
    x_length = torch.LongTensor([phoneme.size(0)]).cuda()
    sid = torch.LongTensor([speaker]).cuda()
    audio = net_g.infer(
        x,
        x_length,
        sid=sid,
        noise_scale=noise_scale,
        noise_scale_w=noise_scale_w,
        length_scale=length_scale)[0][0, 0].data.cpu().float().numpy()
    audio *= 32767 / max(0.01, np.max(np.abs(audio))) * 0.6
    audio = np.clip(audio, -32767.0, 32767.0)
    write(f'test_ms.wav', 22050, audio.astype(np.int16))