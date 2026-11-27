---
title: "Swarmチェックイン投稿ショートカット／SwarmX"
slug: swarmx
date: 2026-11-19T00:00:00+09:00
status: in_progress
summary: "Swarmのチェックインを取得してXなどへ投稿するiOSショートカットとAndroid版"
tech_stack:
    - iOSショートカット
    - Foursquare API
---

SwarmのチェックインをFoursquare APIから取得し、場所・写真付きで投稿文を組み立てるショートカット。土台は gecko655氏の「Swarm Share」。Android版のSwarmXもある。

導入は [iCloud共有リンク](https://www.icloud.com/shortcuts/8e4065867c2a4d6689a2d6a6ea5d8d68) から（SwarmX_v20）。

## 必要な設定

API方式で使うには、FoursquareのOAuthアクセストークンが要る。トークンと設定はショートカット本体には埋め込まず、Appleメモから読み込む。

1. メモアプリで、タイトルが「SwarmX Config」というメモを作る（旧タイトル「SwarmX Token」でも読める）
2. メモにFoursquareのアクセストークンを貼る（32文字以上の英数字の並びをトークンとして自動で拾う）
3. 必要なら設定行を足す（行頭に書く。# で始まる行はコメント扱い）

設定行は全部任意で、無い行は既定値になる。

- `past: on` — I'm at ではなく I was at にする
- `long: on` — 長文テンプレートで投稿する
- `msg: on` — メッセージ形式にする（優先順位は long > msg > 短文）
- `shorturl: on` — URLを swarmapp の短い形式にする
- `separator: newline / - / slash` — 本文とURLの区切り（既定は時制で変わる）
- `photo: off` — 写真を付けない（短文形式のみ）
- `api: off` — APIを使わず、共有ページから作る方式に固定する

トークンが無い場合は、共有ページから投稿文を作る方式に自動で切り替わる。Android版はトークンと設定をアプリ内に持つ。
