import os
import re
import glob
import shutil
import numpy as np

import torch
from torch.autograd import Variable
'''
Construct the vocabulary
'''
def construct_vocab(file_, max_size=200000, mincount=5):
    vocab2id = {'<s>': 2, '</s>': 3, '<pad>': 1, '<unk>': 0}
    id2vocab = {2: '<s>', 3: '</s>', 1: '<pad>', 0: '<unk>'}
    word_pad = {'<s>': 2, '</s>': 3, '<pad>': 1, '<unk>': 0}
    
    cnt = 4
    with open(file_, 'r') as fp:
        for line in fp:
            arr = re.split('\s', line[:-1])
            if arr[0] == ' ':
                continue
            if arr[0] in word_pad:
                continue
            if int(arr[1]) >= mincount:
                vocab2id[arr[0]] = cnt
                id2vocab[cnt] = arr[0]
                cnt += 1
            if len(vocab2id) == max_size:
                break
    
    return vocab2id, id2vocab
'''
Split the corpus into batches.
'''
def create_batch_file(path_, fkey_, file_, batch_size, clean=False):
    file_name = os.path.join(path_, file_)
    folder = os.path.join(path_, 'batch_'+fkey_+'_'+str(batch_size))
    
    if os.path.exists(folder):
        batch_files = glob.glob(os.path.join(folder, '*'))
        if len(batch_files) > 0 and clean==False:
            return len(batch_files)
    
    try:
        shutil.rmtree(folder)
        os.mkdir(folder)
    except:
        os.mkdir(folder)
    
    fp = open(file_name, 'r')
    cnt = 0
    for line in fp:
        try:
            arr.append(line)
        except:
            arr = [line]
        if len(arr) == batch_size:
            fout = open(os.path.join(folder, str(cnt)), 'w')
            for itm in arr:
                fout.write(itm)
            fout.close()
            arr = []
            cnt += 1
    
    if len(arr) > 0:
        fout = open(os.path.join(folder, str(cnt)), 'w')
        for itm in arr:
            fout.write(itm)
        fout.close()
        arr = []
        cnt += 1
        fp.close()
    
    return cnt
'''
Process the minibatch.
'''
def process_minibatch(batch_id, path_, fkey_, batch_size, vocab2id, max_lens=[400, 100]):
    file_ = os.path.join(path_, 'batch_'+fkey_+'_'+str(batch_size), str(batch_id))
    fp = open(file_, 'r')
    src_arr = []
    trg_arr = []
    src_lens = []
    trg_lens = []
    for line in fp:
        arr = re.split('<sec>', line[:-1])
        dabs = re.split('\s', arr[0])
        dabs = filter(None, dabs)
        trg_lens.append(len(dabs))
        
        dabs2id = [
            vocab2id[wd] if wd in vocab2id
            else vocab2id['<unk>']
            for wd in dabs
        ]
        trg_arr.append(dabs2id)
                
        dart = re.split('\s', arr[1])
        dart = filter(None, dart)
        src_lens.append(len(dart))
        dart2id = [
            vocab2id[wd] if wd in vocab2id
            else vocab2id['<unk>']
            for wd in dart
        ]
        src_arr.append(dart2id)
    fp.close()
    
    src_max_lens = max_lens[0]
    trg_max_lens = max_lens[1]
            
    src_arr = [itm[:src_max_lens] for itm in src_arr]
    trg_arr = [itm[:trg_max_lens] for itm in trg_arr]

    src_arr = [
        itm + [vocab2id['<pad>']]*(src_max_lens-len(itm))
        for itm in src_arr
    ]
    trg_input_arr = [
        itm[:-1] + [vocab2id['<pad>']]*(1+trg_max_lens-len(itm))
        for itm in trg_arr
    ]
    trg_output_arr = [
        itm[1:] + [vocab2id['<pad>']]*(1+trg_max_lens-len(itm))
        for itm in trg_arr
    ]
    
    src_var = Variable(torch.LongTensor(src_arr))
    trg_input_var = Variable(torch.LongTensor(trg_input_arr))
    trg_output_var = Variable(torch.LongTensor(trg_output_arr))
    
    return src_var, trg_input_var, trg_output_var

