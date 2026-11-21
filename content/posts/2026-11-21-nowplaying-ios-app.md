---
title: SpotifyとApple Musicの #NowPlaying を投稿するiOSアプリを作った
date: 2026-11-21T00:00:00+09:00
draft: true
summary: ショートカットで作っていた #NowPlaying 投稿ツールをiOSアプリにした。GitHub Actionsで署名なしビルドする流れ、ジャケ写マッチングの改善、MediaRemoteの壁など。
categories:
    - 開発
tags:
    - iOS
    - Swift
    - GitHub Actions
    - Spotify
---

ショートカットで作っていた #NowPlaying の投稿ツールを、iOSアプリにした。リポジトリはGitHubの aoiro-labo/nowplaying-ios。

## 経緯

元はiOSショートカット版で、SpotifyのWeb APIから再生中の曲を取ってXに投稿するものだった。動いてはいたが、ショートカットではウィジェットに今の曲を出すようなことができない。話が広がって、ちゃんとしたアプリにすることにした。

手元のMacにはXcodeが入っていないし、容量も足りない。なのでビルドはGitHub Actionsに任せて、署名なしの .ipa を作り、SideStore / LiveContainer でiPhoneに入れる方式にした。開発はAI（Muse）に壁打ちしながら、都度こちらで動作確認して進めた。

## ビルドの流れ

- ソースはSwift + SwiftUI。プロジェクトファイルはXcodeGenの project.yml から生成する
- GitHubにpushするとActions（macos-15）が走り、署名なしでビルドして NowPlaying.ipa をArtifactsに上げる
- v* のタグを打つと、リリースにも .ipa が添付される
- 手元ではLiveContainerでそのまま実行して確認する

署名なしなのでApp Storeには出せないし、SideStoreで入れ直す場合は7日ごとの更新が要る。自分しか使わないので、それで割り切っている。

## 工夫したところ

### auto判定

取得元はSpotify / Apple Music / Last.fm から選べる。autoのときは「この端末で再生中のもの」を優先する。他の端末で一時停止しているSpotifyを拾ってしまうことがあったので、/me/player でデバイス名と端末名を突き合わせて判定している。

### ジャケ写のマッチング

ここが一番苦労した。最初はiTunes検索の先頭の結果をそのまま使っていて、カラオケ版のジャケ写を掴むことが多かった。検索の並びは環境で変わるようで、こちらの回線ではカラオケ盤が大量に上位に来る。

最終的には、まずアルバム検索でアルバム名が一致するコレクションを特定して、lookupで収録曲一覧を引き、曲名が一致するものを選ぶ方式にした（v1.7.2）。ほかにMusicBrainzとYouTube Musicもジャケ写の取得元として足してあり、優先順位は設定で並び替えできる。

## ハマったところ

- Apple Musicの「現在の曲」は、状況によって「iTunesメディア」という名前で詳細が空のプレースホルダを返すことがある。アーティスト名が空なら採用しない、という判定を入れた
- MediaRemote.frameworkを直接叩いて再生情報を取る方法を試したが、entitlementの無いアプリには再生中でも nil しか返ってこなかった。サイドロードでは付けられないのでこの方法は使えない。試作コードだけ残っている
- ローカルとGitHub側でファイルの版がずれてビルドが落ちたことがある。以後はpush前に差分を見るようにした
- リリースに .ipa が添付されない問題は、build.yml に permissions: contents: write が無かったのが原因だった
- SideStoreで直接インストールしようとすると、LocalDevVPNに接続済みなのに「VPN未接続」と言われる。ペアリングファイルの再インポートが本命だが、まだ試していない

## 今の状態

現行はv1.8.1。Spotify / Apple Music / Last.fm からの取得、ジャケ写の候補ピッカー、Xアプリ・X API・Bluesky・Mastodon・Misskeyへの投稿、履歴（20件）あたりが入っている。

残っているのは、X API用の開発者アプリの作成（developer.x.com側の手続きが要る）と、SideStoreで通常インストールしたときのウィジェットの確認くらい。
