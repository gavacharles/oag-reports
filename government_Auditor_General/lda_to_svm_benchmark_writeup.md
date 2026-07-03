# LDA to SVM Benchmark

Rows: 1233 | Label column: driver_label_expanded | Topics: 6

## Summary

```
             model  accuracy  macro_f1  weighted_f1  n_train  n_test             label_col  n_topics
         SVM_TFIDF  0.754045  0.736101     0.756769      924     309 driver_label_expanded         6
    SVM_LDA_TOPICS  0.271845  0.171713     0.258921      924     309 driver_label_expanded         6
SVM_TFIDF_PLUS_LDA  0.734628  0.697214     0.737231      924     309 driver_label_expanded         6
```

## Interpretation
Best pipeline by macro-F1: **SVM_TFIDF**

## How LDA feeds SVM
1. Fit LDA on document-term counts.
2. Transform each sentence to topic-proportion vector.
3. Use those vectors as SVM features (LDA-only), or concatenate with TF-IDF (hybrid).
