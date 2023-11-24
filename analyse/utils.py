import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

def create_heatmap(similarity, labels, title, cmap = "YlGnBu"):
  df = pd.DataFrame(similarity)
  df.columns = labels
  df.index = labels
  fig, ax = plt.subplots(figsize=(5,5))
  ax.set_title(title)
  sns.heatmap(df, cmap=cmap)

def tokenize(text: str):
  return ''.join([i if ord(i) < 128 else ' ' for i in text])