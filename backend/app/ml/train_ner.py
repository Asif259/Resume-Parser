import argparse
from pathlib import Path

from app.ml.config import (
    MODEL_DIR,
    NUM_EPOCHS,
    BATCH_SIZE,
    LEARNING_RATE,
    MAX_LENGTH,
    get_device,
)
from app.ml.trainer import train_ner_model

def main():
    parser = argparse.ArgumentParser(description="Fine-tune DistilBERT on Resume Entities")
    parser.add_argument("--epochs", type=int, default=NUM_EPOCHS, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE, help="Batch size per device")
    parser.add_argument("--lr", type=float, default=LEARNING_RATE, help="Learning rate")
    parser.add_argument("--max-length", type=int, default=MAX_LENGTH, help="Maximum sequence length")
    parser.add_argument("--output-dir", type=str, default=str(MODEL_DIR), help="Output directory")

    args = parser.parse_args()

    print(f"=== Starting Resume NER Model Fine-tuning ===")
    print(f"Device: {get_device()}")
    print(f"Epochs: {args.epochs}, Batch Size: {args.batch_size}, LR: {args.lr}")
    print(f"Output directory: {args.output_dir}")

    summary = train_ner_model(
        output_dir=Path(args.output_dir),
        num_epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr,
        max_length=args.max_length,
    )

    print("\n=== Training Completed Successfully ===")
    print(f"Train Loss:     {summary.get('train_loss', 0.0):.4f}")
    print(f"Test Precision: {summary.get('test_precision', 0.0):.4f}")
    print(f"Test Recall:    {summary.get('test_recall', 0.0):.4f}")
    print(f"Test F1:        {summary.get('test_f1', 0.0):.4f}")
    print(f"Model saved to: {args.output_dir}")

if __name__ == "__main__":
    main()

