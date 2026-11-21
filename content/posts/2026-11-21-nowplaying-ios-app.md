---
title: "SpotifyとApple Musicの #NowPlaying を投稿するiOSアプリを作った"
date: 2026-11-21T00:00:00+09:00
draft: true
summary: "ショートカットで作っていた #NowPlaying 投稿ツールをiOSアプリにした。GitHub Actionsで署名なしビルドする流れ、ジャケ写マッチングの改善、MediaRemoteの壁など。"
categories:
    - 開発
tags:
    - iOS
    - Swift
    - GitHub Actions
    - Spotify
---

ショートカットで作っていた「#NowPlaying」投稿ツールを、iOSアプリにした。リポジトリは[aoiro-labo/nowplaying-ios](https://github.com/aoiro-labo/nowplaying-ios)。

## 経緯

元はiOSショートカット版で、SpotifyのWeb APIから再生中の曲を取り、文面を作ってXの投稿画面に渡すものだった。v10まで作り込んで実用になっていたが、ショートカットでは「ウィジェットに今の曲を出す」みたいなことができない。話が広がって、ちゃんとしたアプリにすることにした。

手元のMacにはXcodeが入っていないし、空き容量も足りない（掃除して15GBまで空けた）。なのでビルドはGitHub Actionsに任せ、署名なしの .ipa を作ってSideStore / LiveContainer でiPhoneに入れる方式にした。開発はAI（Muse）に壁打ちしながら、都度こちらで実機確認して進めた。

## ビルドの流れ

- ソースはSwift + SwiftUI。プロジェクトファイルはXcodeGenの project.yml から生成する
- GitHubにpushするとActions（macos-15）が走り、署名なしでビルドして NowPlaying.ipa をArtifactsに上げる
- v* のタグを打つと、リリースにも .ipa が添付される
- 手元ではLiveContainerでそのまま実行して確認する

連携の都合で、リポジトリの作成とワークフローファイル（.github/workflows/build.yml）の作成は、GitHubのWeb側で手作業した。アプリアイコンのPNGみたいなバイナリもAPI経由ではpushできないので、Webからアップロードしている。

署名なしなのでApp Storeには出せないし、SideStoreで通常インストールする場合は7日ごとの更新が要る。自分しか使わないので、それで割り切っている。

## バージョンごとの流れ

- v1.0：初回ビルド成功。LiveContainerに入れて、Spotify / Apple Music 両方の取得を確認
- v1.1：autoの優先順位を修正
- v1.2：配布用の整備。設定の一般化、日英ローカライズ、READMEとライセンス
- v1.3：MediaRemoteを直接叩くプローブを追加（後述の理由で不採用が確定）
- v1.4：直接投稿を追加。X API（OAuth 1.0a、画像付き）、Bluesky、Mastodon、Misskey
- v1.5：文面の編集欄、Xの重み付け文字数カウント、取得履歴（20件）、フォーマットプリセット、App Shortcuts、コントロールセンター用ウィジェット（iOS 18+）
- v1.6.0：UIをカード基調に刷新。Last.fm連携（取得元として追加＋スクロブル）
- v1.7.0：ジャケ写のマッチングを段階制に。MusicBrainz追加、候補ピッカー
- v1.7.2：ジャケ写をアルバム検索＋lookup方式に変更（後述）
- v1.8.0：YouTube Musicをデータソースに追加。ジャケ写ソースの優先順位を設定で並び替え可能に
- v1.8.1：SNS等のアイコンを公式ブランドロゴ（Simple Icons）に差し替え

## 工夫したところ

### auto判定は「この端末」を優先

取得元はSpotify / Apple Music / Last.fm から選べる。autoのときの優先順位は、(1) Spotifyがこの端末で再生中、(2) Apple Musicが再生中、(3) Spotifyがこの端末で一時停止、(4) Apple Musicの一時停止曲、(5) 他端末のSpotify、の順。他の端末で一時停止しているSpotifyを拾ってしまうことがあったので、/me/player のデバイス名と端末名を突き合わせて判定している。

### ジャケ写のマッチング

ここが一番苦労した。最初はiTunes検索の先頭の結果をそのまま使っていて、カラオケ版のジャケ写を掴むことが多かった（「檄! 帝国華撃団 - 改」でカラオケ版になったのがきっかけで、[Issue #1](https://github.com/aoiro-labo/nowplaying-ios/issues/1) が立った）。検索の並びは環境で変わるようで、こちらの回線ではカラオケ盤が大量に上位に来る。検索件数を増やす対策（v1.7.1）はむしろ逆効果だった。

最終的には、まずアルバム検索（entity=album）でアルバム名が一致するコレクションを特定し、lookupで収録曲一覧を引いて曲名が一致するものを選ぶ方式にした（v1.7.2）。これで実機でも正しいジャケ写になるようになった。ほかにMusicBrainzとYouTube Music、再生元（Spotify等）のジャケ写も候補にできて、優先順位は設定で並び替えできる。候補ピッカーから手で選ぶこともできるし、「正解として報告」でIssueに送る導線も付けた。

### そのほか

- 文面は {track} {artist} {album} {url} のマクロで組み立てる。プリセットと編集欄は一本化してある（編集するとプリセット自体が書き換わる）
- Spotifyのrefresh tokenはローテーションで新しいものが返ってくることがあるので、返ってきたら保存し直す
- Last.fmは取得時に updateNowPlaying を送り、投稿のタイミングで scrobble する
- 履歴は同じ曲＋同じ文面なら全体から重複を除いて先頭に移す。ジャケ写のサムネイルが無い場合は前のものを引き継ぐ

## ハマったところ・ミス

- Apple Musicの「現在の曲」は、状況によって「iTunesメディア」という名前で詳細が空のプレースホルダを返すことがある。アーティスト名が空なら採用しない、という健全性ゲートを入れた。iPhone側の詰まりもあって、同じような状態でも正常／プレースホルダ／エラーの3通りを返す
- MediaRemote.frameworkを直接叩くプローブを作ったが、entitlement（com.apple.mediaremote.now-playing-read-access）の無いアプリには、再生中でも info が nil で返ってきた。サイドロードでは付けられないし、TrollStoreもiOS 17.0までで手元のiOS 27では使えない。この方法は使えないと確定した。プローブのコードは死にコードとして残っている
- 開発側のミスで、Trackの初期化を思い込みで書いてビルドを落としたことがある。既存の型は実物を見てから書く、という当たり前の話
- ローカルとGitHub側でファイルの版がずれてビルドが落ちた（run #15）。古いファイルがリモートに残っていたのが原因で、以後はpush前に差分を見るようにした
- build.yml にタグ用のトリガーを足したとき、インデントの都合でpushトリガーが消えたことがある
- リリースに .ipa が添付されない問題は、build.yml に permissions: contents: write が無かったのが原因だった
- LiveContainerではバージョンが「1.0」と表示されたまま＆アイコンが真っ白、という問題があった。project.yml にバージョンを明示して、アプリアイコンのアセットを入れて対処した（v1.5.1）
- SideStoreで直接インストールしようとすると、LocalDevVPNに接続済みなのに「VPN未接続」と言われる。ペアリングファイルの再インポートが本命だが、まだ試していない

## 今の状態

現行は[v1.8.1](https://github.com/aoiro-labo/nowplaying-ios/releases/tag/v1.8.1)。 .ipa もリリースに付いている。

残っているのは、X API用の開発者アプリの作成（developer.x.com側でアプリ作成とRead and Write権限、アクセストークンの発行が要る）と、SideStoreで通常インストールしたときのウィジェットの確認くらい。ウィジェットはLiveContainer内では拡張が登録されないので未確認のまま。
