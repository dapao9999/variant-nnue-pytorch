import argparse
import model as M
import nnue_dataset
import nnue_bin_dataset
import pytorch_lightning as pl
import halfkp
from pytorch_lightning import loggers as pl_loggers
from torch.utils.data import DataLoader, Dataset

class FixedNumBatchesDataset(Dataset):
  def __init__(self, dataset, num_batches):
    super(FixedNumBatchesDataset, self).__init__()
    self.dataset = dataset;
    self.iter = iter(self.dataset)
    self.num_batches = num_batches

  def __len__(self):
    return self.num_batches

  def __getitem__(self, idx):
    return next(self.iter)

def data_loader_cc(train_filename, val_filename):
  # Epoch size is set to dataset size manually for now.
  epoch_size = 300000000
  train_batch_size = 8192
  train_infinite = nnue_dataset.SparseBatchDataset(halfkp.NAME, train_filename, train_batch_size)
  # num_workers has to be 0 for sparse, and 1 for dense
  # it currently cannot work in parallel mode but it shouldn't need to
  train = DataLoader(FixedNumBatchesDataset(train_infinite, (epoch_size + train_batch_size - 1) // train_batch_size), batch_size=None, batch_sampler=None)
  val = DataLoader(nnue_bin_dataset.NNUEBinData(val_filename), batch_size=32)
  return train, val

def data_loader_py(train_filename, val_filename):
  train = DataLoader(nnue_bin_dataset.NNUEBinData(train_filename), batch_size=128, shuffle=True, num_workers=4)
  val = DataLoader(nnue_bin_dataset.NNUEBinData(val_filename), batch_size=32)
  return train, val

def main():
  parser = argparse.ArgumentParser(description="Trains the network.")
  parser.add_argument("train", help="Training data (.bin or .binpack)")
  parser.add_argument("val", help="Validation data (.bin or .binpack)")
  parser.add_argument("--gpus", help="Number of GPUs to train on (default=0 for CPU)", default=0)
  parser.add_argument("--py-data", action="store_true", help="Use python data loader (default=False)")
  args = parser.parse_args()

  nnue = M.NNUE(halfkp)

  if args.py_data:
    print('Using python data loader')
    train, val = data_loader_py(args.train, args.val)
  else:
    print('Using c++ data loader')
    train, val = data_loader_cc(args.train, args.val)

  tb_logger = pl_loggers.TensorBoardLogger('logs/')
  trainer = pl.Trainer(logger=tb_logger, gpus=args.gpus)
  trainer.fit(nnue, train, val)

if __name__ == '__main__':
  main()
