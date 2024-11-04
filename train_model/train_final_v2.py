# !pip install transformers
# !pip install datasets
# !pip install evaluate
# !pip install seqeval

import json
import pandas as pd
from sklearn.model_selection import train_test_split
from datasets import Dataset, DatasetDict
from transformers import BertTokenizerFast, BertForTokenClassification, TrainingArguments, Trainer
# from transformers import T5ForTokenClassification, T5Tokenizer
from transformers import AutoModelForTokenClassification, AutoTokenizer
from transformers import DataCollatorForTokenClassification
from datasets import load_metric
import numpy as np
from transformers import PreTrainedTokenizerFast

# Загрузка данных из JSON
def load_json_data(filename):
    with open(filename, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)
    return data

# Загрузка токенизатора из файла JSON
def load_custom_tokenizer(tokenizer_dir):
    return PreTrainedTokenizerFast.from_pretrained(tokenizer_dir)

# Преобразование данных в pandas DataFrame
def convert_to_dataframe(data):
    rows = []
    for entry in data:
        tokens = entry['tokens']
        tags = entry['tags']
        rows.append({'tokens': tokens, 'tags': tags})
    return pd.DataFrame(rows)


# Функция для токенизации и выравнивания меток
def tokenize_and_align_labels(examples, tokenizer, label2id, max_length):
    # Токенизация входных данных
    tokenized_inputs = tokenizer(
        examples['tokens'], 
        truncation=True, 
        is_split_into_words=True, 
        padding='max_length', 
        max_length=max_length
    )

    # Выравнивание меток
    labels = []
    for i, label_list in enumerate(examples['tags']):
        word_ids = tokenized_inputs.word_ids(batch_index=i)
        label_ids = [
            label2id.get(label_list[word_idx], label2id['O']) if word_idx is not None else -100
            for word_idx in word_ids
        ]
        
        # Пометить последний токен [SEP] как -100
        if tokenizer.sep_token_id in tokenized_inputs['input_ids'][i]:
            sep_index = tokenized_inputs['input_ids'][i].index(tokenizer.sep_token_id)
            label_ids[sep_index] = -100
        
        labels.append(label_ids)

    tokenized_inputs['labels'] = labels
    return tokenized_inputs

def compute_metrics(p, metric, id2label):
    predictions, labels = p
    predictions = np.argmax(predictions, axis=2)

    true_labels = []
    pred_labels = []

    for prediction, label in zip(predictions, labels):
        true_label = []
        pred_label = []
        for p, l in zip(prediction, label):
            if l != -100:
                true_label.append(id2label[l])
                pred_label.append(id2label[p])
        true_labels.append(true_label)
        pred_labels.append(pred_label)

    results = metric.compute(predictions=pred_labels, references=true_labels)
    return results

# Определение уникальных меток
def define_labels(df):
    label_list = list()
    for i in range(df.shape[0]):
        label_list.extend((list(df.tags.iloc[i])))

    label_list = set(label_list)
    print('label_list =', label_list)

    return label_list

# 'DeepPavlov/rubert-base-cased', 'alexyalunin/RuBioBERT',
# annotations = ['BIO_mark_sent_v2.json', 'mark_sent_2.json']
# model_names = ['DeepPavlov/rubert-base-cased', 'alexyalunin/RuBioBERT', 'cointegrated/rut5-base', 'cointegrated/rut5-base-multitask']

def train_model(annotation, model_name, custom_tokenizer=None, num_epoch=3, test_size=0.15, max_length=512, train_batch_size=8, eval_batch_size=8):
    
    # Загрузка данных из JSON в формат Hugging Face Dataset
    data = load_json_data(annotation)
    dataset = Dataset.from_pandas(pd.DataFrame(convert_to_dataframe(data)))
    dataset = dataset.train_test_split(test_size=test_size)
    
    # Определение уникальных меток
    label_list = define_labels(pd.DataFrame(convert_to_dataframe(data)))
    label2id = {label: i for i, label in enumerate(label_list)}
    id2label = {i: label for i, label in enumerate(label_list)}

    # Загрузка модели и токенизатора
    model = AutoModelForTokenClassification.from_pretrained(model_name, num_labels=len(label_list), trust_remote_code=True)
    tokenizer = custom_tokenizer or AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    
    model.config.label2id = label2id
    model.config.id2label = id2label
    
    def preprocess_data(example):
        return tokenize_and_align_labels(example, tokenizer, label2id, max_length)
    
    tokenized_datasets = dataset.map(preprocess_data, batched=True)

    data_collator = DataCollatorForTokenClassification(tokenizer)

    metric = load_metric("seqeval", trust_remote_code=True)

    training_args = TrainingArguments(
        output_dir="./results",
        evaluation_strategy="epoch",
        learning_rate=2e-5,
        per_device_train_batch_size=train_batch_size,
        per_device_eval_batch_size=eval_batch_size,
        num_train_epochs=num_epoch,
        weight_decay=0.01,
        fp16=True  # Mixed precision training
    )

    for param in model.parameters():
        if not param.is_contiguous():
            param.data = param.data.contiguous()

    trainer = Trainer(
        model=model,
        args=training_args,
        data_collator=data_collator,
        compute_metrics=lambda p: compute_metrics(p, metric, id2label),
        train_dataset=tokenized_datasets['train'],
        eval_dataset=tokenized_datasets['test']
    )

    trainer.train()
    
    # Сохранение модели
    name_file = f'./saved_model_with_custom_tokenizer_{train_batch_size}_{annotation.replace("content/", "").split(".")[0]}_{model_name.split("/")[-1]}_{num_epoch}'
    model.save_pretrained(name_file)
    tokenizer.save_pretrained(name_file)

    # Оценка модели
    results = trainer.evaluate()
    print(results)


# Параметры
annotation = 'content/mark_sent_2.json'
model_name = 'DeepPavlov/rubert-base-cased'
custom_tokenizer = 'content/my_tokenizer_zero.json'
#num_epoch = 3
test_size = 0.15
max_length = 512

# Запуск тренировки
for num_epoch in range(5, 7):
    for batch_size in range(16, 28, 4):
        train_model(annotation, model_name,
                    custom_tokenizer = load_custom_tokenizer(custom_tokenizer),
                    train_batch_size = batch_size,
                    eval_batch_size = batch_size,
                    num_epoch = num_epoch
                    )
print('Работа программы успешно завершена!')