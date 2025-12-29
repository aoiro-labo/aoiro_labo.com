import { S3Client, PutObjectCommand } from "@aws-sdk/client-s3";
import fs from "node:fs";
import path from "node:path";
import "dotenv/config";

const {
  R2_ACCESS_KEY_ID,
  R2_SECRET_ACCESS_KEY,
  R2_ENDPOINT,
  R2_BUCKET_NAME,
  R2_PUBLIC_DOMAIN,
} = process.env;

// S3クライアントの初期化（Cloudflare R2互換）
const s3Client = new S3Client({
  endpoint: R2_ENDPOINT,
  region: "auto",
  credentials: {
    accessKeyId: R2_ACCESS_KEY_ID,
    secretAccessKey: R2_SECRET_ACCESS_KEY,
  },
});

async function main() {
  // Front Matter CMSから渡される引数
  // process.argv[2]: 画像のフルパス ([[filePath]])
  // process.argv[3]: 記事のスラグ ([[slug]])
  const filePath = process.argv[2];
  const articleSlug = process.argv[3] || "general"; // スラグがない場合はgeneralフォルダへ

  if (!filePath) {
    console.error("No file path provided.");
    process.exit(1);
  }

  const fileName = path.basename(filePath);
  
  // R2内での保存パスを組み立て (例: posts/my-first-post/image.png)
  // 必要に応じて 'posts/' の部分は変更してください
  const objectKey = `posts/${articleSlug}/${fileName}`;

  try {
    const fileContent = fs.readFileSync(filePath);
    
    const command = new PutObjectCommand({
      Bucket: R2_BUCKET_NAME,
      Key: objectKey,
      Body: fileContent,
      ContentType: getMimeType(fileName),
    });

    await s3Client.send(command);

    // 公開URLの組み立て
    const baseUrl = R2_PUBLIC_DOMAIN.replace(/\/$/, "");
    const publicUrl = `${baseUrl}/${objectKey}`;

    // Front Matter CMSはこの標準出力を受け取ってMarkdownに挿入します
    console.log(publicUrl);

  } catch (error) {
    console.error("Upload error:", error.message);
    process.exit(1);
  }
}

/**
 * 拡張子からMIMEタイプを判定
 */
function getMimeType(fileName) {
  const ext = path.extname(fileName).toLowerCase();
  const map = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".gif": "image/gif",
    ".svg": "image/svg+xml",
  };
  return map[ext] || "application/octet-stream";
}

main();