import pandas as pd
import numpy as np
from numpy.linalg import norm

import torch
from transformers import AutoTokenizer, AutoModel

class Bert():
    def __init__(self, bert_name="hfl/chinese-bert-wwm-ext", max_len=10):
        self.max_len = max_len
        self.tokenizer = AutoTokenizer.from_pretrained(bert_name)
        self.bert_model = AutoModel.from_pretrained(bert_name)
        self.proc_df = pd.read_csv('all_product_info.csv', encoding = 'utf-8')
        self.proc_embbeding = np.load("product_embedding.npy", allow_pickle=True)

    def sent_padding(self, sent_token):
        padding = [sent_token[:self.max_len]] if len(sent_token) >= self.max_len \
                else [sent_token + [0] * (self.max_len - len(sent_token))]
        masks = [[float(value > 0) for value in values] for values in padding]
        return torch.tensor(padding), torch.tensor(masks)

    def get_embedding(self, sent):
        sent_token = self.tokenizer.encode(sent)
        sent_padding, masks = self.sent_padding(sent_token)
        embedded, _ = self.bert_model(sent_padding, attention_mask=masks)
        word_vec = embedded[:, 0, :].detach().numpy()
        return word_vec

    def get_cos_sim(self, a, b):
        return np.inner(a, b) / (norm(a) * norm(b))

    def predict(self, sent):
        emb_vec = self.get_embedding(sent)
        max_score = -100
        best_proc = -1

        for proc in self.proc_embbeding:
            proc_id = proc[0]
            proc_emb = proc[1]
            score = self.get_cos_sim(emb_vec, proc_emb)
            if score > max_score:
                max_score = score
                best_proc = proc_id

        best_proc_title = self.proc_df[self.proc_df["product_id"] == best_proc]["title"].to_numpy()[0]
        #print(max_score)
        return best_proc_title