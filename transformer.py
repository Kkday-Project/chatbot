import os
import sys
import numpy as np
import pandas as pd

import torch
from transformers import AutoTokenizer, AutoModel

class Bert():
    def __init__(self, bert_name="hfl/chinese-bert-wwm-ext", max_len=20):
        self.max_len = max_len
        self.prod_embedding = None
        self.tokenizer = AutoTokenizer.from_pretrained(bert_name)
        self.bert_model = AutoModel.from_pretrained(bert_name)
        self.cos = torch.nn.CosineSimilarity(dim=1)

    def sent_padding(self, sent_token):
        padding = [sent_token[:self.max_len-1] + [102]] if len(sent_token) >= self.max_len \
                else [sent_token + [0] * (self.max_len - len(sent_token))]
        masks = [[float(value > 0) for value in values] for values in padding]
        return torch.tensor(padding), torch.tensor(masks)

    def get_embedding(self, sent, show_info=False):
        sent_token = self.tokenizer.encode(sent)
        sent_padding, masks = self.sent_padding(sent_token)
        embedded, _ = self.bert_model(sent_padding, attention_mask=masks)
        word_vec = embedded[:, 0, :].detach().numpy()

        if show_info is True:
            print("sent:", sent)
            print("sent_token:", sent_token)
            print("sent_padding:", sent_padding)
            print("masks:", masks)
            print("embedded shape:", embedded.shape)

        return word_vec

    def predict(self, sent, embedding_dir = "./product_embedding.npy"):

        if self.prod_embedding is None:
            try:
                self.prod_embedding = np.load(embedding_dir, allow_pickle=True)
            except FileNotFoundError:
                print("{}檔案不存在".format(embedding_dir))
                sys.exit(1)
            except IsADirectoryError:
                print("{}是一個目錄".format(embedding_dir))
                sys.exit(1)

        best_prod = -1
        max_score = -100
        emb_vec = self.get_embedding(sent)

        for prod in self.prod_embedding:
            prod_id = prod[0]
            prod_emb = prod[1]
            score = float(self.cos(torch.tensor(emb_vec), torch.tensor(prod_emb)))
            if score > max_score:
                max_score = score
                best_prod = prod_id

        print(max_score)
        return best_prod