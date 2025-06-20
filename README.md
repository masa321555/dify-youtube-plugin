# YouTube Channel Video Analyzer Plugin

YouTubeチャンネルの特定期間内の動画情報を抽出・分析するDifyプラグインです。

## 🚀 機能

- **チャンネル情報の取得**: チャンネル名、登録者数、総動画数などの基本情報
- **期間指定での動画抽出**: 開始日と終了日を指定して対象期間の動画を取得
- **詳細統計情報**: 各動画の再生回数、いいね数、コメント数を取得
- **構造化データ出力**: JSON形式で分析しやすいデータを提供

## 📊 取得できるデータ

### チャンネル情報
- チャンネル名
- チャンネル説明
- 登録者数
- 総動画数
- 総再生回数

### 動画情報（期間内の各動画）
- 動画タイトル
- 公開日
- 再生回数
- いいね数
- コメント数
- 動画URL
- サムネイル画像URL

## 🛠 セットアップ

### 1. YouTube Data API キーの取得

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. 新しいプロジェクトを作成するか、既存のプロジェクトを選択
3. **YouTube Data API v3** を有効化
   - 「APIとサービス」→「ライブラリ」から検索
4. 認証情報でAPIキーを作成
   - 「APIとサービス」→「認証情報」→「+ 認証情報を作成」→「APIキー」

詳細手順: [YouTube Data API v3 Getting Started](https://developers.google.com/youtube/v3/getting-started)

### 2. プラグインのインストール

#### Dify環境でのインストール
1. Difyの管理画面で「プラグイン」セクションに移動
2. 「GitHub経由でプラグインをインストール」を選択
3. このリポジトリのURLを入力
4. 最新バージョンを選択してインストール

### 3. APIキーの設定

1. インストール後、プラグイン設定画面で「YouTube Data API Key」に取得したAPIキーを入力
2. 設定を保存

## 📖 使用方法

### 基本的な使用例

```json
{
  "channel_id": "UCxxxxxxxxxxxxxxxxxxxxxx",
  "start_date": "2024-01-01",
  "end_date": "2024-01-31"
}
```

### パラメータ説明

| パラメータ | 型 | 必須 | 説明 | 例 |
|-----------|---|------|------|---|
| `channel_id` | string | ✅ | YouTubeチャンネルID | `UCxxxxxxxxxxxxxxxxxxxxxx` |
| `start_date` | string | ✅ | 取得開始日（YYYY-MM-DD） | `2024-01-01` |
| `end_date` | string | ✅ | 取得終了日（YYYY-MM-DD） | `2024-01-31` |

### チャンネルIDの見つけ方

1. **チャンネルページのURLから**:
   - `https://www.youtube.com/channel/UCxxxxxxxxxxxxxxxxxxxxxx`
   - 「UC」で始まる部分がチャンネルID

2. **カスタムURLの場合**:
   - `https://www.youtube.com/@channelname`
   - `@channelname` をそのまま使用可能

3. **動画ページから**:
   - 任意の動画ページでチャンネル名をクリック
   - URLからチャンネルIDを確認

## 📋 出力例

```json
{
  "channel_info": {
    "channel_id": "UCxxxxxxxxxxxxxxxxxxxxxx",
    "title": "サンプルチャンネル",
    "description": "チャンネルの説明文...",
    "published_at": "2020-01-01T00:00:00Z",
    "subscriber_count": "1000000",
    "video_count": "500",
    "view_count": "50000000"
  },
  "date_range": {
    "start_date": "2024-01-01",
    "end_date": "2024-01-31"
  },
  "total_videos": 10,
  "videos": [
    {
      "video_id": "xxxxxxxxxxx",
      "title": "動画タイトル",
      "description": "動画の説明...",
      "published_date": "2024-01-15",
      "published_datetime": "2024-01-15T10:00:00Z",
      "view_count": 50000,
      "like_count": 1500,
      "comment_count": 200,
      "thumbnail_url": "https://i.ytimg.com/vi/xxxxxxxxxxx/mqdefault.jpg",
      "video_url": "https://www.youtube.com/watch?v=xxxxxxxxxxx"
    }
  ]
}
```

## 🎯 活用例

### 1. コンテンツ戦略分析
```
指定期間の動画パフォーマンスを分析し、人気コンテンツの傾向を把握
```

### 2. 競合分析
```
競合チャンネルの投稿頻度や人気動画の特徴を調査
```

### 3. レポート生成
```
月次・週次でのチャンネル成長レポートの自動生成
```

### 4. AIエージェントとの連携
```
取得したデータをもとにAIがコンテンツ改善案を提案
```

## ⚠️ 制限事項

- **API制限**: YouTube Data API v3のクォータ制限（1日10,000ユニット）
- **取得件数**: 一度に最大200件の動画まで取得
- **過去データ**: チャンネルが公開設定している動画のみ取得可能
- **リアルタイム性**: API経由のため、最新の統計情報に数時間の遅延がある場合があります

## 🔧 トラブルシューティング

### よくあるエラー

#### 1. 「チャンネルIDが見つかりません」
- チャンネルIDが正しいか確認
- プライベートチャンネルの場合は取得不可
- `@ユーザー名` 形式でも試行

#### 2. 「API Key が無効です」
- Google Cloud ConsoleでAPIキーが正しく作成されているか確認
- YouTube Data API v3が有効化されているか確認
- APIキーに適切な権限が設定されているか確認

#### 3. 「クォータ制限に達しました」
- 1日のAPI使用量が上限（10,000ユニット）に達している
- 翌日まで待つか、Google Cloud Consoleで追加クォータを申請

#### 4. 「動画が見つかりません」
- 指定期間に公開された動画がない
- 動画が非公開または限定公開に設定されている
- 日付範囲を広げて再試行

### デバッグのヒント

1. **短期間でテスト**: まず1週間程度の短い期間で動作確認
2. **人気チャンネルで確認**: 動画数が多いチャンネルで正常に動作するか確認
3. **日付形式の確認**: YYYY-MM-DD形式が正しく入力されているか確認

## 🤝 貢献

バグ報告や機能要望は、GitHubのIssuesでお知らせください。プルリクエストも歓迎です。

## 📄 ライセンス

MIT License

## 📧 お問い合わせ

- GitHub: [@masa321555](https://github.com/masa321555)
- Issues: [プロジェクトのIssuesページ](../../issues)

---

**注意**: このプラグインを使用する際は、YouTubeの利用規約とYouTube Data APIの利用規約を遵守してください。