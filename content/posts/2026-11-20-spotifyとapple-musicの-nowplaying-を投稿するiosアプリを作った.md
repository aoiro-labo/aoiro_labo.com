---
title: "SpotifyとApple Musicの #NowPlaying を投稿するiOSアプリを作った"
date: 2026-11-21T00:00:00+09:00
draft: true
summary: "ショートカットで作っていた #NowPlaying 投稿ツールをiOSアプリにした。GitHub Actionsで署名なしビルドする流れ、ジャケ写マッチングの改善、Apple MusicとiOSの制約など。"
categories:
    - 開発
tags:
    - iOS
    - Swift
    - GitHub Actions
    - Spotify
---

ショートカットで作っていた「#NowPlaying」投稿ツールを、iOSアプリにした。

{{< button text="GitHubリポジトリ" url="https://github.com/aoiro-labo/nowplaying-ios" icon="github" target="_blank" />}}
{{< button text="v1.8.1 リリース" url="https://github.com/aoiro-labo/nowplaying-ios/releases/tag/v1.8.1" icon="link" target="_blank" />}}

## 経緯

元はiOSショートカット版で、SpotifyのWeb APIから再生中の曲を取り、文面を作ってXの投稿画面に渡すものだった。v10まで作り込んで実用レベルに達していたが、ショートカットでは「ウィジェットに今の曲を出す」みたいなことができない。話が広がって、ちゃんとしたアプリにすることにした。

手元のMacにはXcodeが入っていないので、ビルドはGitHub Actionsに任せ、署名なしの.ipaを作ってSideStore / LiveContainerでiPhoneに入れる方式にした。開発はAI（Muse）に壁打ちしながら、都度こちらで実機確認して進めた。

{{< x user="aoiro_labo" id="2123623813191733301" >}}

## 既にあるのに、なぜ作ったのか

再生中の曲を投稿するアプリ自体は既にある。iOSだとこの辺。

{{< link title="NowPlaying - 再生中の音楽をツイート" url="https://apps.apple.com/jp/app/nowplaying-%E5%86%8D%E7%94%9F%E4%B8%AD%E3%81%AE%E9%9F%B3%E6%A5%BD%E3%82%92%E3%83%84%E3%82%A4%E3%83%BC%E3%83%88/id482604258" description="App Store" icon="link" >}}
{{< link title="NowPlaying - 起動するだけでポスト" url="https://apps.apple.com/jp/app/nowplaying-%E8%B5%B7%E5%8B%95%E3%81%99%E3%82%8B%E3%81%A0%E3%81%91%E3%81%A7%E3%83%9D%E3%82%B9%E3%83%88/id1289764391" description="App Store" icon="link" >}}
{{< link title="なうぷれ NowPlaying - 再生中の音楽を共有" url="https://apps.apple.com/jp/app/%E3%81%AA%E3%81%86%E3%81%B7%E3%82%8C-nowplaying-%E5%86%8D%E7%94%9F%E4%B8%AD%E3%81%AE%E9%9F%B3%E6%A5%BD%E3%82%92%E5%85%B1%E6%9C%89/id6760329811" description="App Store" icon="link" >}}

AndroidにはNowPlaying4Droidという理想形もある。ただ、そもそもSpotifyに対応したものが殆どない。大半は端末内で再生中の曲を読む方式で、Spotifyの再生は端末内からは拾えない。広告が多かったり、課金しないと機能に制限がかかったりするものも多い。曲のURLを付けられないものも多い。文面も、#Nowplaying の綴りや、アーティストの区切り、「 - Single」まで付くアルバム表記など、自分の形式とは違う。どれも自分の使い方には合わなかった。

参考に、挙げた3つのアプリで同じ曲（Luna say maybe）を開いた画面を並べておく。

{{< masonry maxColumns="3" >}}
![再生中の曲とジャケ写が表示された既存アプリの画面。Xでシェアするボタンと使い方ガイドがある](https://images.aoiro-labo.com/blog/nowplaying-existing-1.jpg "既存アプリの画面 1")
![再生中の曲名が表示された既存アプリの画面。ジャケ写の位置は音符のイラストで、下部に広告がある](https://images.aoiro-labo.com/blog/nowplaying-existing-2.jpg "既存アプリの画面 2")
![円形に切り抜かれたジャケ写と、生成された投稿文が表示された既存アプリの画面。投稿先のボタンが並んでいる](https://images.aoiro-labo.com/blog/nowplaying-existing-3.jpg "既存アプリの画面 3")
{{< /masonry >}}

- 出発点がショートカットだった。既製品を探して乗り換える前に、自分の道具の方が先に育っていた。アプリはその延長で、文面マクロの仕様はショートカット版から引き継いでいる
- 文面の形式。#NowPlaying の後に曲名、アーティストはクレジット全員、最後にアルバム名でURLはなし、という自分の形式をそのまま使いたかった
- ジャケ写のマッチング。「検索の1件目」で済ませる方式ではカラオケ版が混ざる問題が残る。ここは自分で方式を決めたかった
- 投稿先（Xアプリ／X API／Bluesky／Mastodon／Misskey）とLast.fmのスクロブルまで、自分の使い方に寄せたかった

作る手段があったのも大きい。AIに壁打ちしながら作る形で、仕様を自分で決められるところまで来ていた。

## ビルドの流れ

```mermaid
flowchart LR
    A["ソースをpush"] --> B["GitHub Actions<br/>macos-15 でビルド"]
    B --> C["NowPlaying.ipa"]
    C --> D["Artifacts / リリース"]
    D --> E["LiveContainerで実行"]
```

- ソースはSwift + SwiftUI。プロジェクトファイルはXcodeGenの project.yml から生成する
- v* のタグを打つと、リリースにも.ipaが添付される
- 署名なしなのでApp Storeには出せないし、SideStoreで通常インストールする場合は7日ごとの更新が要る

## バージョン履歴

| バージョン | 主な内容 |
| :-- | :-- |
| v1.0 | 初回ビルド成功。LiveContainerに入れて、Spotify / Apple Music 両方の取得を確認 |
| v1.1 | autoの優先順位を修正 |
| v1.2 | 配布用の整備。設定の一般化、日英ローカライズ、READMEとライセンス |
| v1.3 | MediaRemoteを直接叩くプローブを追加（後述の理由で不採用が確定） |
| v1.4 | 直接投稿を追加。X API（OAuth 1.0a、画像付き）、Bluesky、Mastodon、Misskey |
| v1.5 | 文面の編集欄、Xの重み付け文字数カウント、取得履歴（20件）、フォーマットプリセット、App Shortcuts、コントロールセンター用ウィジェット（iOS 18+） |
| v1.5.1 | LiveContainerでバージョンが「1.0」表示で、アイコン真っ白だった問題に対処 |
| v1.6.0 | UIをカード基調に刷新。Last.fm連携（取得元として追加＋スクロブル） |
| v1.6.1〜1.6.5 | 取得／投稿ボタンの下部固定、履歴の重複排除、設定画面の整理、ジャケ写の間違い報告 |
| v1.7.0 | ジャケ写のマッチングを段階制に。MusicBrainz追加、候補ピッカー |
| v1.7.1 | ジャケ写の検索増量＋カラオケ除外（逆効果、後述） |
| v1.7.2 | ジャケ写をアルバム検索＋lookup方式に変更（後述） |
| v1.8.0 | YouTube Musicをデータソースに追加。ジャケ写ソースの優先順位を設定で並び替え可能に |
| v1.8.1 | SNS等のアイコンを公式ブランドロゴ（Simple Icons）に差し替え |

## 工夫したところ

### 「この端末」を優先するauto判定

取得元はSpotify / Apple Music / Last.fm から選べる。autoのときは「この端末で再生中のもの」を優先する。他の端末で一時停止しているSpotifyを拾ってしまうことがあったので、/me/player のデバイス名と端末名を突き合わせて判定している。

| 優先 | 条件 | 取得元 |
| :-- | :-- | :-- |
| 1 | Spotifyがこの端末で再生中 | Spotify |
| 2 | Apple Musicが再生中 | Apple Music |
| 3 | Spotifyがこの端末で一時停止 | Spotify |
| 4 | Apple Musicが一時停止中 | Apple Music |
| 5 | 他の端末で再生・停止中 | Spotify |

### ジャケ写のマッチング

ここが一番苦労した。最初はiTunes検索の先頭の結果をそのまま使っていて、カラオケ版のジャケ写を掴むことが多かった。「檄! 帝国華撃団 - 改」でカラオケ版になったのがきっかけで、アプリの報告機能を試すついでに、自分で [Issue #1](https://github.com/aoiro-labo/nowplaying-ios/issues/1) を立てた。

厄介だったのは、検索の並びが環境で変わること。手元の回線ではカラオケ盤が大量に上位に来る一方、検証環境では再現しないので、「直った」ように見えてしまう。

| バージョン | 方式 | 結果 |
| :-- | :-- | :-- |
| 初期〜v1.6 | iTunes検索の先頭を採用 | カラオケ版を掴むことがある |
| v1.7.0 | 曲名・アルバム・アーティストの段階制マッチング＋候補ピッカー | まだカラオケ盤が残る |
| v1.7.1 | 検索を2クエリ×25件に増量＋カラオケ除外 | 逆にカラオケが増えた |
| v1.7.2 | アルバム検索でコレクションを特定し、lookupで収録曲から選択 | 実機で正しいジャケ写になった |

順位に頼るのをやめて、アルバム名の一致で盤を特定してから曲を引く、という順番にしたのが効いた。ほかにMusicBrainzとYouTube Music、再生元（Spotify等）のジャケ写も候補にできて、優先順位は設定で並び替えできる。候補ピッカーから手で選ぶこともできるし、「正解として報告」でIssueに送る導線も付けた。

同じ「檄! 帝国華撃団 - 改」で、カラオケ版を掴んだ状態（左）、Apple Musicで表示される本来のジャケ写（中）、修正後のアプリ（右）。

{{< masonry maxColumns="3" >}}
![カラオケ版のジャケ写を選んでしまったアプリの画面](https://images.aoiro-labo.com/blog/nowplaying-geki-karaoke.jpg "カラオケ版を掴んだ状態")
![Apple Musicで表示される「檄! 帝国華撃団 - 改」の本来のジャケ写](https://images.aoiro-labo.com/blog/nowplaying-applemusic-geki.jpg "本来のジャケ写（Apple Music）")
![修正後、正しいジャケ写が表示されているアプリの画面](https://images.aoiro-labo.com/blog/nowplaying-geki-fixed.jpg "修正後")
{{< /masonry >}}

### 文面の組み立て

文面は `{track}` `{artist}` `{album}` `{url}` のマクロで組み立てる。自分の既定はURLなしで、こうなる。

```text {filename="文面の例"}
#NowPlaying 真っ白いページと水彩の主人公 - 初星学園, 佐藤貴文, 花海佑芽 (真っ白いページと水彩の主人公)
```

プリセットと編集欄は一本化してあって、編集すると選択中のプリセット自体が書き換わる。

実際の画面はこんな感じで、投稿文と履歴が並ぶ。

![生成された投稿文と、取得履歴が並ぶアプリの画面](https://images.aoiro-labo.com/blog/nowplaying-post-history.jpg "投稿文と履歴")

実際に投稿した例がこれ。「ワールドイズマイン」はショートカット時代にジャケ写とURLが壊れた曲で、アプリでは正しい盤のものが出るようになった。

{{< x user="aoiro_labo" id="2123615772572618844" >}}

### そのほか

- Spotifyのrefresh tokenはローテーションで新しいものが返ってくることがあるので、返ってきたら保存し直す
- Last.fmは取得時に updateNowPlaying を送り、投稿のタイミングでスクロブルする
- 履歴は同じ曲＋同じ文面なら全体から重複を除いて先頭に移す。ジャケ写のサムネイルが無い場合は前のものを引き継ぐ

## Apple MusicとiOSの制約

Spotifyは公式のWeb APIがあるので、再生情報をサーバー側から引っ張って解決できた。Apple側はそうはいかない。開発中にぶつかった制約を並べると、だいたいAppleの仕様の話になる。

{{< x user="aoiro_labo" id="2123636617365844440" >}}
{{< x user="aoiro_labo" id="2123637077967573322" >}}

### 端末内の再生曲はApple Musicしか取れない

iOSでは、他のアプリが今何を再生しているかを知る公開APIがない。MediaPlayerで取れるのはミュージックアプリ（Apple Music）の再生曲だけで、Spotifyアプリの再生状態は端末内からは見えない。だからSpotifyはWeb API経由、という設計になっている。YouTube Musicに至っては再生状態を見る公式API自体がないので、v1.8.0で足したのもジャケ写などのメタデータ取得だけだった。

### 「iTunesメディア」というプレースホルダ

Apple Musicの「現在の曲」は、状況によって「iTunesメディア」という名前で詳細が空のプレースホルダを返すことがある。アーティスト名が空なら採用しない、という健全性ゲートを入れた。同じような状態でも正常／プレースホルダ／エラーの3通りを返すので、ショートカット版の頃から引きずっている問題でもある。

### MediaRemoteの壁

MediaRemote.frameworkを直接叩いて再生情報を取るプローブを作って試した。

> [!NOTE]
> entitlement（com.apple.mediaremote.now-playing-read-access）の無いアプリには、再生中でも info が nil で返ってくる。サイドロードでは付けられないし、TrollStoreもiOS 17.0までで手元のiOS 27では使えない。この方法は使えないと確定した。

プローブのコードは死にコードとして残っている。

### 金の話

まともに配布しようとするとApple Developer Program（年99ドル）が要る。やめればアプリも消える。無料の範囲だと署名の有効期限が7日で、SideStoreで更新し続けるしかない。個人で使うだけの道具に年額を払う気はないので、野良.ipaのままにしている。

## ハマったところ・ミス

- 開発側のミスで、Trackの初期化を思い込みで書いてビルドを落としたことがある。既存の型は実物を見てから書く、という当たり前の話だった
- LiveContainerではバージョンが「1.0」と表示されたままで、アイコンが真っ白という問題があった。project.yml にバージョンを明示して、アプリアイコンのアセットを入れて対処した（v1.5.1）

## 今の状態

現行はv1.8.1で、.ipaもリリースに付いている。リポジトリは公開している。

{{< x user="aoiro_labo" id="2123783147074842997" >}}
{{< x user="aoiro_labo" id="2123784780236149198" >}}

残っているのは、X API用の開発者アプリの作成（developer.x.com側でアプリ作成とRead and Write権限、アクセストークンの発行が要る）と、SideStoreで通常インストールしたときのウィジェットの確認くらい。ウィジェットはLiveContainer内では拡張が登録されないので未確認のまま。
