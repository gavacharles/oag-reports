# FA vs LDA Benchmark (Side-by-Side)

## Corpus
- Rows: 1233
- Label column: driver_label_expanded
- Components/topics: 6

## Metric Summary

```
model  n_components  topic_diversity  umass_coherence  label_alignment_nmi  latent_cls_accuracy  latent_cls_macro_f1  reconstruction_mse  perplexity  log_likelihood
   FA             6         0.458333        -2.189047             0.051260             0.245955             0.123118            0.001848         NaN             NaN
  LDA             6         0.833333        -1.803662             0.124751             0.271845             0.171713                 NaN  269.411269  -131119.881968
```

## Quick Interpretation
- Better topic coherence (UMass): **LDA**
- Better latent-feature classification (macro F1): **LDA**

## Notes
- FA branch uses TF-IDF + `sklearn.decomposition.FactorAnalysis`.
- LDA branch uses CountVectorizer + `sklearn.decomposition.LatentDirichletAllocation`.
- UMass coherence is computed from top 12 terms per component/topic.
