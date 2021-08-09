# 導入方法

- discordのbotを作成しtokenを取得後、利用したいサーバーに招待する
- private_sample.pyを参考に`private.py`作成し、tokenとvoice_channel_idを定義する
  - tokenは[ここ](https://discord.com/developers/applications)からMy Applications -> Botで確認できる
  - voice_channel_idはdiscordのボイスチャンネルを右クリック -> IDをコピー
- 必要なライブラリをインストール
    - pip install git+https://github.com/Nkyoku/pyvcroid2.git
    - pip install git+https://github.com/Rapptz/discord.py.git
      - 2.0.0a3267+gd30fea5bで動作確認済み
    - pip install -r requirements.txt
- `python main.py`

## 注意

- aitalkedが64bitか32bitかでPythonインタプリタのbit数も合わせないと動作しない。
