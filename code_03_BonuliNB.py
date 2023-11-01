import pandas as pd
from sklearn import model_selection
from sklearn import naive_bayes
from sklearn import metrics
import matplotlib.pyplot as plt
import seaborn as sns
evaluation = pd.read_csv('豆瓣短评_1849031_前11页.csv')#读取数据
print(evaluation.shape)#查看表的行列
print(list(evaluation.columns))#查看表抬头
print(evaluation.head(10))#输出前10行数据
evaluation.Content = evaluation.Content.str.replace('[0 9a zA Z]','',regex=True)#去掉数字和英文
print(evaluation.head(10))
import jieba
jieba.load_userdict('dict.txt')# 加载自定义词库
with open('stop_words.txt', encoding='UTF 8') as words:# 读入停止词
    stop_words = [i.strip() for i in words.readlines()]
def cut_word(sentence):# 构造切词的自定义函数，并在切词过程中删除停止词
    words = [i for i in jieba.lcut(sentence) if i not in stop_words]
    result = ' '.join(words)# 切完的词用空格隔开
    return(result)
words = evaluation.Content.apply(cut_word)# 调用自定义函数，并对评论内容进行批量切词
print(words[:10])# 前 5 行内容的切词效果

from sklearn.feature_extraction.text import CountVectorizer# 导入第三方包
counts = CountVectorizer(min_df = 0.01)# 计算每个词在各评论内容中的次数，并将稀疏度为 99% 以上的词删除
dtm_counts = counts.fit_transform(words).toarray()# 文档词条矩阵
columns = counts.get_feature_names_out()# 矩阵的列名称
X = pd.DataFrame(dtm_counts, columns=columns)# 将矩阵转换为数据框 即 X 变量
y = evaluation.Type# 为情感标签变量
print(X.head(10))
#print(y)
#
# 将数据集拆分为训练集和测试集
X_train,X_test,y_train,y_test =model_selection.train_test_split(X,y ,test_size =0.25,random_state=1)
# 构建伯努利贝叶斯分类器
bnb =naive_bayes.BernoulliNB(alpha = 0.0005)
# 模型在训练数据集上的拟合
bnb.fit(X_train,y_train)
# 模型在测试数据集上的预测
bnb_pred = bnb.predict(X_test)
# 构建混淆矩阵
cm = pd.crosstab(bnb_pred,y_test)#预测值与测试值
# 绘制混淆矩阵图
sns.heatmap(cm, annot=True, cmap='GnBu', fmt='d')
# 去除 x 轴和 y 轴标签
plt.xlabel('Real')
plt.ylabel('Predict')
# 显示图形
plt.show()
# 模型的预测准确率
print(' 模型的准确率为： n',metrics.accuracy_score(y_test, bnb_pred))
print(' 模型的评估报告： n',metrics.classification_report(y_test, bnb_pred))
#
# 计算正例 Positive 所对应的概率，用于 生成 ROC 曲线的数据
y_score = bnb.predict_proba(X_test)[:,1]
y_true=y_test.map({'Negative':0,'Positive':1})
fpr,tpr,threshold = metrics.roc_curve(y_true, y_score)
# 计算 AUC 的值
roc_auc = metrics.auc(fpr,tpr)
# 绘制面积图
plt.stackplot(fpr, tpr, color='steelblue', alpha = 0.5, edgecolor = 'black')
# 添加边际线
plt.plot(fpr, tpr, color='black', lw = 1)
# 添加对角线
plt.plot([0,1],[0,1], color = 'red', linestyle = '--')
# 添加文本信息
plt.text(0.5,0.3,'ROC curve (area = %0.2f)' % roc_auc)
# 添加 x 轴与 y 轴标签
plt.xlabel('1-Specificity')
plt.ylabel('Sensitivity')
# 显示图形
plt.show()