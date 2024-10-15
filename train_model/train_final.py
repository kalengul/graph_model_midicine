# !pip install transformers
# !pip install datasets
# !pip install evaluate
# !pip install seqeval

import json
import pandas as pd
from sklearn.model_selection import train_test_split
from datasets import Dataset, DatasetDict
from transformers import BertTokenizerFast, BertForTokenClassification, TrainingArguments, Trainer
from transformers import AutoModelForTokenClassification, AutoTokenizer
from transformers import DataCollatorForTokenClassification
from datasets import load_metric
import numpy as np

# Загрузка данных из JSON
def load_json_data(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

# Преобразование данных в pandas DataFrame
def convert_to_dataframe(data):
    rows = []
    for entry in data:
        tokens = entry['tokens']
        tags = entry['tags']
        rows.append({'tokens': tokens, 'tags': tags})
    return pd.DataFrame(rows)


# Функция для токенизации и выравнивания меток
def tokenize_and_align_labels(examples):
    global max_length
    tokenized_inputs = tokenizer(examples['tokens'], truncation=True, is_split_into_words=True, padding='max_length', max_length=max_length)
    labels = []
    for i, label in enumerate(examples['tags']):
        word_ids = tokenized_inputs.word_ids(batch_index=i)
        # previous_word_idx = None
        label_ids = []
        for word_idx in word_ids:
            if word_idx is None:
                label_ids.append(-100)  # Ignored token
            else:
                label_ids.append(label2id.get(label[word_idx], label2id['O']))
            #     label_ids.append(label2id.get(label[word_idx], label2id['O']))  # Default to 'O'
            
            # elif word_idx != previous_word_idx:
            #     label_ids.append(label2id.get(label[word_idx], label2id['O']))  # Default to 'O'
            # else:
            #     label_ids.append(-100)  # For sub-tokens
            # previous_word_idx = word_idx

        # Пометить последний токен [SEP] как -100
        if tokenizer.sep_token_id:
            sep_index = tokenized_inputs['input_ids'][i].index(tokenizer.sep_token_id)
            label_ids[sep_index] = -100
        
        labels.append(label_ids)

    tokenized_inputs['labels'] = labels
    return tokenized_inputs

def compute_metrics(p):
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

# 'DeepPavlov/rubert-base-cased', 'alexyalunin/RuBioBERT',
annotations = [#'BIO_mark_sent_v2.json', 
               'content/mark_sent_3.json']
model_names = ['DeepPavlov/rubert-base-cased', 
               #'alexyalunin/RuBioBERT', 
               #'cointegrated/rut5-base', 
               #'cointegrated/rut5-base-multitask'
               ]

start = 6
finish = 7


for annotation in annotations:
    data = load_json_data(annotation)
    df = convert_to_dataframe(data)

    # Разделение данных на обучающий и тестовый наборы
    train_df, test_df = train_test_split(df, test_size=0.15)

    label_list = list()
    for i in range(df.shape[0]):
        label_list.extend((list(df.tags.iloc[i])))

    label_list = set(label_list)
    print('label_list =', label_list)
    # Пример меток
    #label_list = ['O', 'B-noun', "I-noun", 'B-glag', 'I-glag']
    label2id = {label: i for i, label in enumerate(label_list)}
    id2label = {i: label for i, label in enumerate(label_list)}


    # Конвертация в формат Dataset
    train_dataset = Dataset.from_pandas(train_df)
    test_dataset = Dataset.from_pandas(test_df)
    dataset_dict = DatasetDict({
        'train': train_dataset,
        'test': test_dataset
    })

    for model_name in model_names:
        # Загрузка токенизатора и модели
        if 't5' in model_name.lower():
            max_length = 512
            tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
            model = AutoModelForTokenClassification.from_pretrained(model_name, num_labels=len(label_list), trust_remote_code=True)
        elif 'bert' in model_name.lower():
            max_length = 512
            tokenizer = BertTokenizerFast.from_pretrained(model_name, trust_remote_code=True)
            model = BertForTokenClassification.from_pretrained(model_name, num_labels=len(label_list), trust_remote_code=True)

        model.config.label2id = label2id
        model.config.id2label = id2label

        tokenized_datasets = dataset_dict.map(tokenize_and_align_labels, batched=True)

        data_collator = DataCollatorForTokenClassification(tokenizer)

        # Загрузка метрики
        metric = load_metric("seqeval", trust_remote_code=True)

        # Обновленная функция для вычисления метрик

        for num_epoch in range(start, finish):
            # Настройки для тренировки
            training_args = TrainingArguments(
                output_dir="./results",
                evaluation_strategy="epoch",
                learning_rate=2e-5,
                per_device_train_batch_size=16,
                per_device_eval_batch_size=16,
                num_train_epochs=num_epoch,
                weight_decay=0.01,
            )


            for param in model.parameters():
                if not param.is_contiguous():
                    param.data = param.data.contiguous()
            print(f'обучение модели {model_name}  с {num_epoch} эпох')
            
            trainer = Trainer(
                model=model,
                args=training_args,
                data_collator=data_collator,
                compute_metrics=compute_metrics,
                train_dataset=tokenized_datasets['train'],
                eval_dataset=tokenized_datasets['test']
            )

            trainer.train()
            
            # Сохранение модели
            annotation_name = annotation.split('.')[0]
            model.save_pretrained('./saved_model' + '_' + annotation_name.replace('content/', '') + '_' + model_name.split('/')[-1] + '_' + str(num_epoch))
            tokenizer.save_pretrained('./saved_model' + '_' + annotation_name.replace('content/', '') + '_' + model_name.split('/')[-1] + '_' + str(num_epoch))

            # Оценка модели
            results = trainer.evaluate()
            print(results)

    
print('Работа программы успешно завершина!')