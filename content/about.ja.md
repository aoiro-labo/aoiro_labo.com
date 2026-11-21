---
title: "このサイトについて"
layout: "about"
summary: "aoiro-labo の技術スタックと運営環境について"
date: 2025-12-30T00:00:00+09:00
links:

- name: "Hugo"
  url: "https://gohugo.io/"
  icon: "https://gohugo.io/favicon.ico"
  description: "世界最速の静的サイトジェネレーター"

- name: "Cloudflare R2"
  url: "https://www.cloudflare.com/ja-jp/developer-platform/r2/"
  icon: "https://www.cloudflare.com/favicon.ico"
  description: "エグレス料金無料の S3 互換オブジェクトストレージ"

- name: "Giscus"
  url: "https://giscus.app/ja"
  icon: "https://giscus.app/favicon.ico"
  description: "GitHub Discussions を利用したコメントシステム"

- name: "GitHub"
  url: "https://github.com/aoiro-labo/aoiro_labo.com"
  icon: "https://github.com/fluidicon.png"
  description: "このサイトのソースコードを管理しているリポジトリ"
---
## aoiro-labo について

放送、アニメ、バーチャル関係の趣味と、作業中に調べた技術情報を置いている個人ブログ。
あとで自分が読み返せるように、検証した手順や結果を記録している。

## 技術スタック

サイトはHugoで生成し、Cloudflare Pagesで公開している。

- SSG: Hugo Extended
- Theme: hugo-narrow (Minimalist 1-column theme)
- Infrastructure: Cloudflare Pages (Hosting)
- Object Storage: Cloudflare R2 (Images & Assets)
- Comments: Giscus (via GitHub Discussions)
- Design: Tailwind CSS 4.0

## 画像管理について
記事の画像はCloudflare R2に保存し、images.aoiro-labo.comから配信している。GitHubリポジトリには原則として画像を置かない。例外はサイト共通の画像で、アバター、ファビコン、OG画像、PWA用のアイコンはstatic/に置いてリポジトリで管理している。
