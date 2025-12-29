import { S3Client, PutObjectCommand } from "@aws-sdk/client-s3";
import { readFileSync } from "fs";
import { basename, extname } from "path";
import dotenv from "dotenv";

// .envファイルを読み込む
dotenv.config();

const {
  R2_ACCESS_KEY_ID,
  R2_SECRET_ACCESS_KEY,
  R2_ENDPOINT,
  R2_BUCKET_NAME,
  R2_PUBLIC_DOMAIN
} = process.env;

// 設定チェック
if (!R2_ACCESS_KEY_ID || !R2_SECRET_ACCESS_KEY || !R2_ENDPOINT || !R2_BUCKET_NAME) {
  console.error("Error: Missing R2 configuration in .env file.");
  process.exit(1);
}

// コマンドライン引数からファイルパスを取得
const filePath = process.argv[2];
if (!filePath) {
  console.error("Error: No file path provided.");
  process.exit(1);
}

const s3Client = new S3Client({
  region: "auto",
  endpoint: R2_ENDPOINT,
  credentials: {
    accessKeyId: R2_ACCESS_KEY_ID,
    secretAccessKey: R2_SECRET_ACCESS_KEY,
  },
});

async function uploadFile() {
  try {
    const fileContent = readFileSync(filePath);
    const fileName = basename(filePath);
    const extension = extname(filePath).toLowerCase();

    // Content-Typeの簡易判定
    let contentType = "application/octet-stream";
    if (extension === ".png") contentType = "image/png";
    if (extension === ".jpg" || extension === ".jpeg") contentType = "image/jpeg";
    if (extension === ".gif") contentType = "image/gif";
    if (extension === ".webp") contentType = "image/webp";

    const uploadParams = {
      Bucket: R2_BUCKET_NAME,
      Key: `blog/${fileName}`, // R2内の保存先パス（適宜変更してください）
      Body: fileContent,
      ContentType: contentType,
    };

    await s3Client.send(new PutObjectCommand(uploadParams));

    // アップロード成功時のURLを出力（Front Matter CMSがこれを読み取ります）
    const publicUrl = `${R2_PUBLIC_DOMAIN}/blog/${fileName}`;
    console.log(publicUrl);
  } catch (err) {
    console.error("Upload Error:", err);
    process.exit(1);
  }
}

uploadFile();