"""
Beginner Example: LoRA Fine-Tuning
===================================

This script demonstrates LoRA (Low-Rank Adaptation) fine-tuning of GPT-2 for
sentiment analysis. We train only small adapter matrices while keeping the
base model frozen.

Author: fantastic-engine
License: MIT
"""

import numpy as np
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
)
from peft import LoraConfig, get_peft_model, TaskType
from sklearn.metrics import accuracy_score, precision_recall_fscore_support


def main():
    print("=" * 50)
    print("LoRA Fine-Tuning - Beginner Example")
    print("=" * 50)

    # ============================================
    # 1. Load Model and Tokenizer
    # ============================================
    print("\n[1/7] Loading model and tokenizer...")

    model_name = "gpt2"
    print(f"Model: {model_name}")

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.pad_token = tokenizer.eos_token

    # Load base model
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name,
        num_labels=2,
    )
    model.config.pad_token_id = model.config.eos_token_id

    # Print base model size
    total_params = sum(p.numel() for p in model.parameters())
    print(f"Base model parameters: {total_params:,}")

    # ============================================
    # 2. Configure and Apply LoRA
    # ============================================
    print("\n[2/7] Configuring LoRA...")

    # LoRA configuration
    lora_config = LoraConfig(
        r=8,                          # Rank of the low-rank matrices
        lora_alpha=16,                # Scaling factor (alpha/r is the final scaling)
        target_modules=["c_attn"],    # Apply LoRA to attention layers
        lora_dropout=0.05,            # Dropout for regularization
        bias="none",                  # Don't train bias parameters
        task_type=TaskType.SEQ_CLS,   # Sequence classification task
    )

    print("LoRA Configuration:")
    print(f"  Rank (r): {lora_config.r}")
    print(f"  Alpha: {lora_config.lora_alpha}")
    print(f"  Target modules: {lora_config.target_modules}")
    print(f"  Dropout: {lora_config.lora_dropout}")

    # Wrap model with LoRA
    model = get_peft_model(model, lora_config)

    # Print trainable parameters
    print("\nModel after adding LoRA:")
    model.print_trainable_parameters()

    # ============================================
    # 3. Load and Prepare Dataset
    # ============================================
    print("\n[3/7] Loading dataset...")

    # Load IMDB dataset
    dataset = load_dataset("imdb")

    # Use subset for demo (remove for full dataset)
    dataset["train"] = dataset["train"].select(range(1000))
    dataset["test"] = dataset["test"].select(range(200))

    print(f"Train samples: {len(dataset['train'])}")
    print(f"Test samples: {len(dataset['test'])}")

    # ============================================
    # 4. Tokenize Dataset
    # ============================================
    print("\n[4/7] Tokenizing dataset...")

    def tokenize_function(examples):
        """Tokenize the texts"""
        return tokenizer(
            examples["text"],
            padding="max_length",
            truncation=True,
            max_length=512,
        )

    # Tokenize datasets
    tokenized_datasets = dataset.map(
        tokenize_function,
        batched=True,
        remove_columns=["text"],
    )

    # Rename label to labels
    tokenized_datasets = tokenized_datasets.rename_column("label", "labels")

    print("Tokenization complete!")

    # ============================================
    # 5. Define Training Arguments
    # ============================================
    print("\n[5/7] Setting up training configuration...")

    training_args = TrainingArguments(
        output_dir="./results",
        learning_rate=3e-4,                    # Higher LR for LoRA (3-10x higher)
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        num_train_epochs=3,
        weight_decay=0.01,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="accuracy",
        logging_dir="./logs",
        logging_steps=50,
        report_to="none",
    )

    print("Training configuration:")
    print(f"  Learning rate: {training_args.learning_rate} (higher than full FT!)")
    print(f"  Batch size: {training_args.per_device_train_batch_size}")
    print(f"  Epochs: {training_args.num_train_epochs}")

    # ============================================
    # 6. Define Metrics
    # ============================================
    def compute_metrics(eval_pred):
        """Compute metrics for evaluation"""
        logits, labels = eval_pred
        predictions = np.argmax(logits, axis=-1)

        accuracy = accuracy_score(labels, predictions)
        precision, recall, f1, _ = precision_recall_fscore_support(
            labels, predictions, average="binary"
        )

        return {
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1": f1,
        }

    # ============================================
    # 7. Create Trainer and Train
    # ============================================
    print("\n[6/7] Creating trainer and starting training...")
    print("Training only LoRA adapters (base model is frozen)...")
    print("This should be faster than full fine-tuning!\n")

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_datasets["train"],
        eval_dataset=tokenized_datasets["test"],
        compute_metrics=compute_metrics,
    )

    # Train the model
    train_result = trainer.train()

    # Print training results
    print("\n" + "=" * 50)
    print("Training Complete!")
    print("=" * 50)
    print(f"Training time: {train_result.metrics['train_runtime']:.2f} seconds")
    print(f"Training samples/second: {train_result.metrics['train_samples_per_second']:.2f}")

    # ============================================
    # 8. Evaluate on Test Set
    # ============================================
    print("\n[7/7] Evaluating on test set...")

    eval_results = trainer.evaluate()

    print("\nFinal Results:")
    print(f"  Accuracy: {eval_results['eval_accuracy']:.4f}")
    print(f"  Precision: {eval_results['eval_precision']:.4f}")
    print(f"  Recall: {eval_results['eval_recall']:.4f}")
    print(f"  F1 Score: {eval_results['eval_f1']:.4f}")

    # ============================================
    # 9. Save LoRA Adapters
    # ============================================
    print("\nSaving LoRA adapters...")

    output_dir = "./gpt2-imdb-lora"
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)

    print(f"LoRA adapters saved to: {output_dir}")
    print("Note: Only adapter weights are saved (~2MB), not the full model!")

    # ============================================
    # 10. Demo: Loading and Using LoRA Model
    # ============================================
    print("\n" + "=" * 50)
    print("Loading LoRA Model Demo")
    print("=" * 50)

    from peft import AutoPeftModelForSequenceClassification

    # Load model with LoRA adapters
    loaded_model = AutoPeftModelForSequenceClassification.from_pretrained(output_dir)

    print("Model loaded successfully!")

    # ============================================
    # 11. Test Predictions
    # ============================================
    print("\n" + "=" * 50)
    print("Testing Predictions")
    print("=" * 50)

    test_texts = [
        "This movie was absolutely fantastic! I loved every minute of it.",
        "Terrible film. Complete waste of time. Do not watch.",
        "It was okay, nothing special but not terrible either.",
    ]

    for text in test_texts:
        inputs = tokenizer(
            text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512,
        )

        outputs = loaded_model(**inputs)
        predictions = outputs.logits.softmax(dim=-1)

        predicted_class = predictions.argmax().item()
        confidence = predictions[0][predicted_class].item()
        sentiment = "Positive" if predicted_class == 1 else "Negative"

        print(f"\nText: {text}")
        print(f"Prediction: {sentiment} (confidence: {confidence:.2f})")
        print(f"  Negative: {predictions[0][0]:.4f}")
        print(f"  Positive: {predictions[0][1]:.4f}")

    # ============================================
    # 12. Compare with Full Fine-Tuning
    # ============================================
    print("\n" + "=" * 50)
    print("LoRA vs Full Fine-Tuning Comparison")
    print("=" * 50)

    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    trainable_percent = (trainable_params / total_params) * 100

    print("\nLoRA Benefits:")
    print(f"  ✅ Trainable params: {trainable_params:,} ({trainable_percent:.2f}%)")
    print(f"  ✅ Model size: ~2 MB (vs ~500 MB for full model)")
    print(f"  ✅ Training time: {train_result.metrics['train_runtime']:.0f}s")
    print(f"  ✅ Memory efficient: Can train on smaller GPUs")
    print(f"  ✅ Fast switching: Multiple adapters for different tasks")

    print("\nAccuracy:")
    print(f"  LoRA: {eval_results['eval_accuracy']:.4f}")
    print(f"  (Full FT typically: ~0.87)")
    print(f"  Difference: ~2-5% accuracy for 99%+ parameter savings!")

    print("\n" + "=" * 50)
    print("All done! 🎉")
    print("=" * 50)
    print("\nNext steps:")
    print("1. Compare this with the full fine-tuning example")
    print("2. Try different LoRA configurations (rank, target modules)")
    print("3. Try QLoRA for even more memory efficiency")
    print("4. Train multiple adapters for different tasks")


if __name__ == "__main__":
    main()
