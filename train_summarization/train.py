import pandas as pd
from datasets import Dataset
from transformers import T5Tokenizer, T5ForConditionalGeneration, Seq2SeqTrainer, Seq2SeqTrainingArguments

# Чтение .parquet файлов с помощью pandas
train_df    = pd.read_parquet("data\\train-00000-of-00002.parquet")
val_df      = pd.read_parquet("data\\validation-00000-of-00001.parquet")
test_df     = pd.read_parquet("data\\test-00000-of-00001.parquet")

# Преобразование pandas DataFrame в формат Hugging Face datasets
train_dataset   = Dataset.from_pandas(train_df)
val_dataset     = Dataset.from_pandas(val_df)
test_dataset    = Dataset.from_pandas(test_df)

# Инициализация токенизатора и модели
tokenizer = T5Tokenizer.from_pretrained("t5-small")
model = T5ForConditionalGeneration.from_pretrained("t5-small")

def compute_metrics(eval_pred):
    predictions, labels = eval_pred
    
    # Decode generated summaries into text
    decoded_preds = tokenizer.batch_decode(predictions, skip_special_tokens=True)
    
    # Replace -100 in the labels as we can't decode them
    labels = np.where(labels != -100, labels, tokenizer.pad_token_id)
    
    # Decode reference summaries into text
    decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)
    
    # ROUGE expects a newline after each sentence
    decoded_preds = ["\n".join(sent_tokenize(pred.strip())) for pred in decoded_preds]
    decoded_labels = ["\n".join(sent_tokenize(label.strip())) for label in decoded_labels]
    
    # Compute ROUGE scores
    result = rouge_score.compute(predictions=decoded_preds, references=decoded_labels, use_stemmer=True)
    
    return {k: round(v, 4) for k, v in result.items()}

# Подготовка данных
def preprocess_function(examples):
    # Исходный текст
    model_inputs = tokenizer(examples["info"],
                             max_length=512,
                             truncation=True)

    # Подготовка меток (столбец с рефератом)
    with tokenizer.as_target_tokenizer():
        labels = tokenizer(examples["summary"],
                           max_length=128,
                           truncation=True)

    model_inputs["labels"] = labels["input_ids"]
    return model_inputs

# Применение функции предобработки к датасетам
train_dataset = train_dataset.map(preprocess_function, batched=True)
val_dataset = val_dataset.map(preprocess_function, batched=True)
test_dataset = test_dataset.map(preprocess_function, batched=True)

# Настройка аргументов обучения
training_args = Seq2SeqTrainingArguments(
    output_dir="./results",
    evaluation_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    weight_decay=0.01,
    save_total_limit=3,
    num_train_epochs=3,
    predict_with_generate=True,
    push_to_hub=False,
    report_to="none",
)

# Инициализация тренера
trainer = Seq2SeqTrainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    tokenizer=tokenizer,
)

# Запуск обучения
trainer.train()