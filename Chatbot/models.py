from django.db import models

class DATA_WORKER(models.Model):
    WORKER_ID = models.CharField(max_length=50, primary_key=True)
    WORKER_NAME = models.CharField(max_length=50, null=True)

class DATA_IMAGE(models.Model):
    IMAGE_ID = models.AutoField(primary_key=True)
    IMAGE = models.CharField(max_length=200)
    WORKER_ID = models.ForeignKey(DATA_WORKER, on_delete=models.SET_NULL, null=True)
    STATUS = models.CharField(max_length=1, default='0')
    DATE_WORK = models.DateField(auto_now=True)

class QUESTION(models.Model):
    QUESTION_ID = models.AutoField(primary_key=True)
    IMAGE_ID = models.ForeignKey(DATA_IMAGE, on_delete=models.CASCADE)
    QUESTION = models.CharField(max_length=1000)
    STATUS = models.CharField(max_length=1, default='0')
    QUESTION_CNT = models.IntegerField()

class ANSWER(models.Model):
    ANSWER_ID = models.AutoField(primary_key=True)
    QUESTION_ID = models.ForeignKey(QUESTION, on_delete=models.CASCADE)
    ANSWER = models.CharField(max_length=1000)