# VC Client Connector (for VOICEVOX)

[VOICEVOX](https://voicevox.hiroshiba.jp/)に[VC Client](https://github.com/w-okada/voice-changer)を接続し、RVCなどを反映させるVOICEVOXエンジンです。  
これを使うことでVOICEVOX上で反映後の音声をプレビューしたり、そのまま音声を保存することが出来るようになります。  
マルチエンジン機能に対応しており、他のVOICEVOX互換エンジンに対して使用することも出来ます。  

## 使用方法

1. 以下をダウンロードして、解凍もしくはインストールをしてください。
- [VOICEVOX](https://voicevox.hiroshiba.jp/)
- [VC Client](https://github.com/w-okada/voice-changer)

2. [こちら](https://github.com/NON906/vcc_converter/releases)から最新の「vcc_converter_vX.X.X_win.vvpp」ファイルをダウンロードしてください。

3. VOICEVOXを起動し、メニューバーの「設定→オプション」で、「マルチエンジン機能」を有効にしてください。

4. メニューバーの「エンジン→エンジンの管理」を開き、「追加」ボタンをクリックし、2.の「vcc_converter_vX.X.X_win.vvpp」を指定して追加してください。

5. VOICEVOXを再起動すると設定画面が表示されるので、以下を行ってください。
- 「VC Clientのパス」にVC Clientのstart_http.batファイルのパスを指定し、「設定を反映」ボタンをクリックしてください。
- 「話者の設定」から以下を入力し、追加してください（全て入力した後に「追加/更新」ボタンをクリックしてください）。
  - 話者：（新規作成）
  - 名前：表示させたい名前を入力
  - VOICEVOXエンジン側の対象：VOICEVOX側で使用したい話者を設定

6. VOICEVOXを再度、再起動してください。

7. 再起動すると、5.の話者が追加されているので、その話者に切り替えてください。

8. 話者を切り替えるとVC Clientが起動するので、変換したい内容に設定してください。

上記を行うと、生成される音声がVC Clientによって変換されるようになります。

## リポジトリからのインストール方法（知識のある人向け）

1. このリポジトリをクローンして、以下のコマンドを入力してください

```
conda create -n vv2vcc
conda activate vv2vcc
pip install -r requirements.txt
```

2. VOICEVOXを起動し、メニューバーの「設定→オプション」で、「マルチエンジン機能」を有効にしてください。

3. メニューバーの「エンジン→エンジンの管理」を開き、「追加」ボタンをクリックし、「既存エンジン」からこのリポジトリを指定して追加してください。
