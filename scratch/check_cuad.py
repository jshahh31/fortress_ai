from datasets import load_dataset
ds = load_dataset("theatticusproject/cuad", split="train", verification_mode="no_checks")
print("Column names:", ds.column_names)
print("First example:", ds[0])
