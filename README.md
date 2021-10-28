# FreeCAD Macro & WorkBentch for DEXCS Launcher

## これは何か
OpenFOAMを使った仮想風洞試験を、ボタンを順番に押していくだけで実行できるようにしたDEXCSランチャー（FreeCADのマクロとワークベンチファイル）の一式とセットアップツール。
DEXCS for OpenFOAM で、DEXCS2021より実装されているもので、DEXCS2020に搭載したもの（dfc-0.2）より大幅な変更がある。今後マクロに変更が加えられたら、
変更部分だけを更新しても良いし、同梱のセットアップツールで全体のアップデートも可能。

## 注意事項
とりあえず、DEXCS2021 for OpenFOAM に同梱された内容をそのまま収納したもので、能書きのセットアップ方法や、本ドキュメントの記述内容がそのまま通用するかどうかの検証は未実施である。
DEXCSランチャーのうち、DEXCSツールバー中のTreeFoamのサブセット（GridEditorなど）を起動するメニューは、インストール先の環境によっては動かない場合もある点はお断りしておく。
## セットアップ方法

同梱のonfigDexcs というファイル中で定義してある3つのパラメタ( cfMesh, TreeFoam, dexcs )の内容(行頭に # の有る行はコメント行)を、インストール先の環境に合致させておいてから、同梱の updateDexcsLauncher.sh を端末上で実行する。その際、既存の user.cfg を上書きするかどうかの質問があるので、上書きして良ければ「 Y 」を入力してアップデートは完了。

上書きの可否は、インストール先の FreeCAD の利用環境で自身でカスタマイズしたマクロやツールバーの有無次第
で判断されたい。上書きしてしまうと、それらの情報が無くなってしまうということである。「 N 」を入力した場合に
は、マクロファイルがアップデートされるだけなので、ツールボタンを自身で作り直す作業が必要になる。作り直す方法については、

http://mogura7.zenno.info/~et/wordpress/ocse/?p=12722

の記事を参照されたい。


なお、上書きした場合でも、元の user.cfg ファイルは、 user.cfr.<user>.orig という名前で残すようにしてあるので復
元は可能。またテキストファイルなので、内容を理解した上での新旧ファイル間での組み合わせ改変は可能である。

## FreeCADの更新

DEXCS2018以前では、FreeCADを最新のAppImage版（FreeCAD_0.19-24276-Linux-Conda_glibc2.12-x86_64.AppImage）に更新する必要がある。更新方法はダウンロードしたAppImage版の収納されたフォルダにて、
管理者権限にて、たとえば以下のコマンドを入力すれば良い。
<code>
 cp FreeCAD_0.19-24276-Linux-Conda_glibc2.12-x86_64.AppImage /opt/
 ln -s /opt/FreeCAD_0.19-24276-Linux-Conda_glibc2.12-x86_64.AppImage /opt/freecad 
 mv /usr/bin/freecad /usr/bin/freecad.orig
 ln -s /opt/freecad /usr/bin/freecad
 mv /usr/bin/freecad-daily /usr/bin/freecad-daily.orig
 ln -s /opt/freecad /usr/bin/freecad-daily
</code>
元々インストールされてあった/usr/bin/freecad なり、/usr/bin/freecad-dailyは、.orig の拡張子を付けて残すようにしてあるので、戻したい場合はこれを使えば良い。 


## 動作を確認できているDEXCS for OpenFOAM

- DEXCS2021
- DEXCS2020
- DEXCS2019
- DEXCS2018
- DEXCS2017
- DEXCS2016
- DEXCS2015
（但し、DEXCS2019以前では、DEXCSツールバー中、TreeFoamのサブセット機能は使えないものがある）

## DEXCS 以外のプラットフォームで動作させる為の要件

DEXCS で構築したシステムでなくとも、 TreeFoam が動く環境であれば、若干のファイル追加で動作するは
ずなので、その要件と追加方法について記しておく。
（但し、実際に動作確認している訳ではないので、不具合があればレポートをお願いします）
CentOS7上で動作確認した以下の記事も参照されたい。

http://mogura7.zenno.info/~et/wordpress/ocse/?p=13506

- cfMesh ( cartesianMesh )がインストールされており、 configDecs 中に、これを起動する為の(ビルドした)
OpenFOAM の環境情報が記してある事。
- TreeFoam がインストールされており( +dexcsSwak 版でなくとも可)、 configDecs 中に configTreeFoam のイ
ンストール場所が記されている事。
- configDecs 中に dexcs 指定フォルダを定義しておき、指定したフォルダ下に SWAK というフォルダと template
というフォルダを作成。 SWAK フォルダ下に pyDexcsSwak.py という空ファイルを作成。 template フォルダ
下には、 dexcs という名前で OpenFOAM のケースフォルダを収納しておく。ケースフォルダの中身は、ケース
ファイルとして有効な内容であれば何でも良いが、 FreeCAD モデルが OpenFOAM のケースフォルダでない場
所でメッシュ作成する際の雛形フォルダとして使われることになる。
