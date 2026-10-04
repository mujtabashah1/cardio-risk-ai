import numpy as np
from sklearn.metrics import accuracy_score,balanced_accuracy_score,precision_score,recall_score,f1_score,roc_auc_score,average_precision_score,brier_score_loss,log_loss,confusion_matrix

def metrics(y,p,threshold=.5):
    y=np.asarray(y,dtype=int);p=np.asarray(p,dtype=float);label=p>=threshold
    tn,fp,fn,tp=confusion_matrix(y,label,labels=[0,1]).ravel();bins=np.minimum((p*10).astype(int),9)
    ece=sum(np.mean(bins==b)*abs(np.mean(y[bins==b])-np.mean(p[bins==b])) for b in range(10) if np.any(bins==b))
    both=len(np.unique(y))==2
    return dict(accuracy=float(accuracy_score(y,label)),balanced_accuracy=float(balanced_accuracy_score(y,label)),precision=float(precision_score(y,label,zero_division=0)),recall=float(recall_score(y,label,zero_division=0)),specificity=float(tn/(tn+fp)) if tn+fp else None,f1=float(f1_score(y,label,zero_division=0)),roc_auc=float(roc_auc_score(y,p)) if both else None,pr_auc=float(average_precision_score(y,p)) if np.any(y==1) else None,brier=float(brier_score_loss(y,p)),log_loss=float(log_loss(y,np.column_stack([1-p,p]),labels=[0,1])),ece=float(ece),TP=int(tp),TN=int(tn),FP=int(fp),FN=int(fn),threshold=float(threshold),rows=len(y),positive_count=int(y.sum()),positive_prevalence=float(y.mean()))
