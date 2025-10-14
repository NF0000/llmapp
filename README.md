# ローカルLLMチャット
ローカルにLMStudioでサーバを起動し、利用できるアプリケーションです。
## 使用時
`.env`をローカルで作成してください。
内容は以下のとおりです。
```.env.sample
LMSTUDIO_API=http://ローカルLLMのIPアドレス/v1/chat/completions
MODEL_NAME=モデルの名前
```