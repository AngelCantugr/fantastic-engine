"""
Beginner Example: Full Fine-Tuning
===================================

This script demonstrates basic full fine-tuning of GPT-2 for sentiment analysis.
We'll fine-tune all parameters of the model on the IMDB movie review dataset.

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
from sklearn.metrics import accuracy_score, precision_recall_fscore_support


def main():
    print("=" * 50)
    print("Full Fine-Tuning - Beginner Example")
    print("=" * 50)

    # ============================================
    # 1. Load Model and Tokenizer
    # ============================================
    print("\n[1/6] Loading model and tokenizer...")

    model_name = "gpt2"
    print(f"Model: {model_name}")

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    # GPT-2 doesn't have a padding token, so we set it to EOS token
    tokenizer.pad_token = tokenizer.eos_token

    # Load model for sequence classification (2 classes: positive/negative)
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name,
        num_labels=2,
    )

    # Set padding token in model config
    model.config.pad_token_id = model.config.eos_token_id

    # Print model size
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"Total parameters: {total_params:,}")
    print(f"Trainable parameters: {trainable_params:,} ({trainable_params/total_params*100:.1f}%)")

    # ============================================
    # 2. Load and Prepare Dataset
    # ============================================
    print("\n[2/6] Loading dataset...")

    # Load IMDB dataset (movie reviews)
    dataset = load_dataset("imdb")

    print(f"Train samples: {len(dataset['train'])}")
    print(f"Test samples: {len(dataset['test'])}")

    # Use smaller subset for faster training (remove these lines for full dataset)
    dataset["train"] = dataset["train"].select(range(1000))
    dataset["test"] = dataset["test"].select(range(200))
    print(f"\nUsing subset for demo:")
    print(f"  Train: {len(dataset['train'])} samples")
    print(f"  Test: {len(dataset['test'])} samples")

    # ============================================
    # 3. Tokenize Dataset
    # ============================================
    print("\n[3/6] Tokenizing dataset...")

    def tokenize_function(examples):
        """Tokenize the texts"""
        return tokenizer(
            examples["text"],
            padding="max_length",
            truncation=True,
            max_length=512,  # GPT-2 can handle up to 1024, but 512 is faster
        )

    # Tokenize datasets
    tokenized_datasets = dataset.map(
        tokenize_function,
        batched=True,
        remove_columns=["text"],  # Remove original text column
    )

    # Rename label column to labels (required by Trainer)
    tokenized_datasets = tokenized_datasets.rename_column("label", "labels")

    print("Tokenization complete!")

    # ============================================
    # 4. Define Training Arguments
    # ============================================
    print("\n[4/6] Setting up training configuration...")

    training_args = TrainingArguments(
        output_dir="./results",                     # Output directory
        learning_rate=2e-5,                         # Learning rate
        per_device_train_batch_size=8,              # Batch size for training
        per_device_eval_batch_size=8,               # Batch size for evaluation
        num_train_epochs=3,                         # Number of epochs
        weight_decay=0.01,                          # Weight decay for regularization
        evaluation_strategy="epoch",                # Evaluate after each epoch
        save_strategy="epoch",                      # Save after each epoch
        load_best_model_at_end=True,                # Load best model at end
        metric_for_best_model="accuracy",           # Use accuracy to determine best model
        logging_dir="./logs",                       # Logging directory
        logging_steps=50,                           # Log every 50 steps
        report_to="none",                           # Don't report to wandb/tensorboard
    )

    print("Training configuration:")
    print(f"  Learning rate: {training_args.learning_rate}")
    print(f"  Batch size: {training_args.per_device_train_batch_size}")
    print(f"  Epochs: {training_args.num_train_epochs}")

    # ============================================
    # 5. Define Metrics
    # ============================================
    def compute_metrics(eval_pred):
        """Compute metrics for evaluation"""
        logits, labels = eval_pred
        predictions = np.argmax(logits, axis=-1)

        # Calculate metrics
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
    # 6. Create Trainer and Train
    # ============================================
    print("\n[5/6] Creating trainer and starting training...")
    print("This may take 10-20 minutes depending on your hardware...\n")

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
    # 7. Evaluate on Test Set
    # ============================================
    print("\n[6/6] Evaluating on test set...")

    eval_results = trainer.evaluate()

    print("\nFinal Results:")
    print(f"  Accuracy: {eval_results['eval_accuracy']:.4f}")
    print(f"  Precision: {eval_results['eval_precision']:.4f}")
    print(f"  Recall: {eval_results['eval_recall']:.4f}")
    print(f"  F1 Score: {eval_results['eval_f1']:.4f}")

    # ============================================
    # 8. Save Model
    # ============================================
    print("\nSaving model...")

    output_dir = "./gpt2-imdb-classifier"
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)

    print(f"Model saved to: {output_dir}")

    # ============================================
    # 9. Test Predictions
    # ============================================
    print("\n" + "=" * 50)
    print("Testing Predictions")
    print("=" * 50)

    # Example texts
    test_texts = [
        "This movie was absolutely fantastic! I loved every minute of it.",
        "Terrible film. Complete waste of time. Do not watch.",
        "It was okay, nothing special but not terrible either.",
    ]

    for text in test_texts:
        # Tokenize
        inputs = tokenizer(
            text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512,
        )

        # Predict
        outputs = model(**inputs)
        predictions = outputs.logits.softmax(dim=-1)

        # Get predicted class
        predicted_class = predictions.argmax().item()
        confidence = predictions[0][predicted_class].item()

        sentiment = "Positive" if predicted_class == 1 else "Negative"

        print(f"\nText: {text}")
        print(f"Prediction: {sentiment} (confidence: {confidence:.2f})")
        print(f"  Negative: {predictions[0][0]:.4f}")
        print(f"  Positive: {predictions[0][1]:.4f}")

    print("\n" + "=" * 50)
    print("All done! 🎉")
    print("=" * 50)
    print("\nNext steps:")
    print("1. Try the LoRA example for more efficient fine-tuning")
    print("2. Experiment with different hyperparameters")
    print("3. Use your own dataset")


if __name__ == "__main__":
    main()
